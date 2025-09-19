from app.models import (
    db, User, Profile, UserGoal, ProficiencyAssessment, 
    VocabularyWord, MistakePattern, LearningSession,
    DailyChallenge, UserDailyChallengeCompletion
)
from app.services.activity_generator_service import ActivityGeneratorService
from datetime import datetime, date, timedelta
from sqlalchemy import func
import json
import re

class PersonalizationService:
    """
    Service for handling personalized learning experiences, assessments, and adaptive content.
    """
    
    def __init__(self):
        self.activity_service = ActivityGeneratorService()
    
    # Phase 1: Personalization Setup
    
    def create_user_goal(self, user_id, daily_time_goal, learning_focus='conversation'):
        """
        Set up user's daily learning goals during onboarding.
        """
        try:
            # Deactivate any existing goals
            existing_goals = UserGoal.query.filter_by(user_id=user_id, is_active=True).all()
            for goal in existing_goals:
                goal.is_active = False
            
            # Create new goal
            user_goal = UserGoal(
                user_id=user_id,
                daily_time_goal_minutes=daily_time_goal,
                learning_focus=learning_focus
            )
            
            db.session.add(user_goal)
            db.session.commit()
            
            return user_goal
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def conduct_proficiency_assessment(self, user_id):
        """
        Conduct a conversational proficiency assessment.
        """
        try:
            # Generate assessment questions based on user profile
            assessment_questions = self._generate_assessment_questions()
            
            assessment = ProficiencyAssessment(
                user_id=user_id,
                assessment_type='initial',
                questions_asked=assessment_questions
            )
            
            db.session.add(assessment)
            db.session.commit()
            
            return {
                'assessment_id': assessment.id,
                'questions': assessment_questions,
                'instructions': 'మీ ఇంగ్లీష్ స్థాయిని అంచనా వేయడానికి కొన్ని సాధారణ ప్రశ్నలు అడుగుతున్నాం. దయచేసి సహజంగా సమాధానం ఇవ్వండి.'
            }
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def _generate_assessment_questions(self):
        """
        Generate personalized assessment questions.
        """
        questions = [
            {
                'id': 1,
                'type': 'introduction',
                'question': 'Can you tell me a little about yourself? What is your name and where are you from?',
                'telugu_hint': 'మీ గురించి కొంచెం చెప్పగలరా? మీ పేరు ఏమిటి మరియు మీరు ఎక్కడ నుండి వచ్చారు?'
            },
            {
                'id': 2,
                'type': 'daily_life',
                'question': 'What do you usually do in the morning?',
                'telugu_hint': 'మీరు సాధారణంగా ఉదయం ఏమి చేస్తారు?'
            },
            {
                'id': 3,
                'type': 'future_goals',
                'question': 'Why do you want to learn English? What are your goals?',
                'telugu_hint': 'మీరు ఇంగ్లీష్ ఎందుకు నేర్చుకోవాలని అనుకుంటున్నారు? మీ లక్ష్యాలు ఏమిటి?'
            }
        ]
        
        return questions
    
    def evaluate_assessment_response(self, assessment_id, question_id, user_response):
        """
        Evaluate user's response to assessment question using AI.
        """
        try:
            assessment = ProficiencyAssessment.query.get(assessment_id)
            if not assessment:
                return {'error': 'Assessment not found'}
            
            # Get AI evaluation of the response
            evaluation_prompt = f"""
            Evaluate this Telugu speaker's English response for proficiency assessment.
            
            Question: {assessment.questions_asked[question_id-1]['question']}
            User Response: "{user_response}"
            
            Provide evaluation in JSON format:
            {{
                "proficiency_level": "beginner/intermediate/advanced",
                "confidence_score": 0.0-1.0,
                "grammar_score": 0.0-1.0,
                "vocabulary_score": 0.0-1.0,
                "fluency_score": 0.0-1.0,
                "mistakes": ["list of mistakes"],
                "strengths": ["list of strengths"],
                "feedback": "Encouraging feedback in English with Telugu translation"
            }}
            """
            
            ai_response = self.activity_service.model.generate_content(evaluation_prompt)
            evaluation = self._extract_json_from_response(ai_response.text)
            
            # Store the response and evaluation
            current_responses = assessment.user_responses or []
            current_responses.append({
                'question_id': question_id,
                'user_response': user_response,
                'evaluation': evaluation,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            assessment.user_responses = current_responses
            db.session.commit()
            
            return {
                'evaluation': evaluation,
                'next_question': self._get_next_assessment_question(assessment, question_id)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def finalize_assessment(self, assessment_id):
        """
        Complete the assessment and determine final proficiency level.
        """
        try:
            assessment = ProficiencyAssessment.query.get(assessment_id)
            if not assessment or not assessment.user_responses:
                return {'error': 'Assessment not found or incomplete'}
            
            # Calculate overall proficiency based on all responses
            total_confidence = 0
            total_grammar = 0
            total_vocabulary = 0
            total_fluency = 0
            all_strengths = []
            all_weaknesses = []
            
            for response in assessment.user_responses:
                eval_data = response.get('evaluation', {})
                total_confidence += eval_data.get('confidence_score', 0)
                total_grammar += eval_data.get('grammar_score', 0)
                total_vocabulary += eval_data.get('vocabulary_score', 0)
                total_fluency += eval_data.get('fluency_score', 0)
                all_strengths.extend(eval_data.get('strengths', []))
                all_weaknesses.extend(eval_data.get('mistakes', []))
            
            num_responses = len(assessment.user_responses)
            avg_confidence = total_confidence / num_responses
            avg_grammar = total_grammar / num_responses
            avg_vocabulary = total_vocabulary / num_responses
            avg_fluency = total_fluency / num_responses
            
            # Determine proficiency level
            overall_score = (avg_confidence + avg_grammar + avg_vocabulary + avg_fluency) / 4
            
            if overall_score >= 0.7:
                proficiency_level = 'intermediate'
            elif overall_score >= 0.4:
                proficiency_level = 'beginner'
            else:
                proficiency_level = 'absolute_beginner'
            
            # Update assessment
            assessment.proficiency_level = proficiency_level
            assessment.confidence_score = avg_confidence
            assessment.strengths = list(set(all_strengths))
            assessment.weaknesses = list(set(all_weaknesses))
            assessment.ai_evaluation = {
                'overall_score': overall_score,
                'grammar_score': avg_grammar,
                'vocabulary_score': avg_vocabulary,
                'fluency_score': avg_fluency
            }
            
            # Update user profile
            user = User.query.get(assessment.user_id)
            if user and user.profile:
                user.profile.proficiency_level = proficiency_level
            
            db.session.commit()
            
            return {
                'proficiency_level': proficiency_level,
                'confidence_score': avg_confidence,
                'strengths': assessment.strengths,
                'weaknesses': assessment.weaknesses,
                'recommendations': self._generate_learning_recommendations(assessment)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    # Phase 2: Core Learning Loop
    
    def get_personalized_dashboard(self, user_id):
        """
        Get personalized dashboard content for the user.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Get user goals and streak
            goal = UserGoal.query.filter_by(user_id=user_id, is_active=True).first()
            streak = user.profile.current_streak if user.profile else 0
            
            # Get today's progress
            today = date.today()
            today_sessions = LearningSession.query.filter(
                LearningSession.user_id == user_id,
                func.date(LearningSession.start_time) == today
            ).all()
            
            today_time_spent = sum([s.duration_minutes or 0 for s in today_sessions])
            daily_goal_minutes = goal.daily_time_goal_minutes if goal else 10
            
            # Get daily challenge
            daily_challenge = self._get_or_create_daily_challenge(user_id)
            
            # Get question of the day
            question_of_day = self._generate_question_of_day(user_id)
            
            # Get recent vocabulary words
            recent_vocab = VocabularyWord.query.filter_by(user_id=user_id)\
                .order_by(VocabularyWord.discovered_at.desc()).limit(3).all()
            
            return {
                'dashboard': {
                    'user_name': user.username,
                    'current_streak': streak,
                    'daily_goal_minutes': daily_goal_minutes,
                    'today_time_spent': today_time_spent,
                    'goal_progress_percentage': min(100, (today_time_spent / daily_goal_minutes) * 100),
                    'daily_challenge': daily_challenge,
                    'question_of_day': question_of_day,
                    'recent_vocabulary': [
                        {
                            'english': word.english_word,
                            'telugu': word.telugu_translation,
                            'context': word.context_sentence
                        } for word in recent_vocab
                    ],
                    'proficiency_level': user.profile.proficiency_level if user.profile else 'beginner'
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def start_learning_session(self, user_id, session_type='chat'):
        """
        Start a new learning session for the user.
        """
        try:
            session = LearningSession(
                user_id=user_id,
                session_type=session_type,
                start_time=datetime.utcnow()
            )
            
            db.session.add(session)
            db.session.commit()
            
            return {
                'session_id': session.id,
                'session_type': session_type,
                'start_time': session.start_time.isoformat(),
                'initial_message': self._get_session_starter(user_id, session_type)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    def end_learning_session(self, session_id, user_satisfaction=None):
        """
        End a learning session and generate summary.
        """
        try:
            session = LearningSession.query.get(session_id)
            if not session:
                return {'error': 'Session not found'}
            
            session.end_time = datetime.utcnow()
            session.duration_minutes = int((session.end_time - session.start_time).total_seconds() / 60)
            session.user_satisfaction = user_satisfaction
            
            # Generate AI summary
            summary = self._generate_session_summary(session)
            session.session_summary = summary
            
            # Check if daily goal is achieved
            user_goal = UserGoal.query.filter_by(user_id=session.user_id, is_active=True).first()
            if user_goal:
                today = date.today()
                today_total_time = db.session.query(func.sum(LearningSession.duration_minutes))\
                    .filter(LearningSession.user_id == session.user_id,
                           func.date(LearningSession.start_time) == today).scalar() or 0
                
                session.goals_achieved = today_total_time >= user_goal.daily_time_goal_minutes
            
            db.session.commit()
            
            return {
                'session_summary': summary,
                'duration_minutes': session.duration_minutes,
                'goals_achieved': session.goals_achieved,
                'new_words_learned': session.new_words_learned,
                'encouragement_message': self._generate_encouragement_message(session)
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    def track_vocabulary_learning(self, user_id, english_word, context_sentence, session_id=None):
        """
        Track when a user encounters and learns a new vocabulary word.
        """
        try:
            # Check if word already exists for user
            existing_word = VocabularyWord.query.filter_by(
                user_id=user_id, 
                english_word=english_word.lower()
            ).first()
            
            if existing_word:
                existing_word.times_encountered += 1
                existing_word.context_sentence = context_sentence  # Update with latest context
            else:
                # Generate Telugu translation using AI
                translation_prompt = f"""
                Translate the English word "{english_word}" to Telugu. 
                Provide only the Telugu translation, nothing else.
                Context: "{context_sentence}"
                """
                
                ai_response = self.activity_service.model.generate_content(translation_prompt)
                telugu_translation = ai_response.text.strip()
                
                # Create new vocabulary entry
                vocab_word = VocabularyWord(
                    user_id=user_id,
                    english_word=english_word.lower(),
                    telugu_translation=telugu_translation,
                    context_sentence=context_sentence,
                    source_activity_type='chat'  # Can be updated based on actual source
                )
                
                db.session.add(vocab_word)
                
                # Update session if provided
                if session_id:
                    session = LearningSession.query.get(session_id)
                    if session:
                        session.new_words_learned += 1
            
            db.session.commit()
            
            return {
                'english_word': english_word,
                'telugu_translation': telugu_translation if not existing_word else existing_word.telugu_translation,
                'is_new_word': existing_word is None
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}
    
    # Helper methods
    
    def _extract_json_from_response(self, text):
        """Extract JSON from AI response (imported from activity service)"""
        match = re.search(r"```json\n({.*?})\n```", text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = text
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON from response.", "raw_response": text}
    
    def _get_next_assessment_question(self, assessment, current_question_id):
        """Get the next question in the assessment"""
        if current_question_id < len(assessment.questions_asked):
            return assessment.questions_asked[current_question_id]
        return None
    
    def _generate_learning_recommendations(self, assessment):
        """Generate personalized learning recommendations based on assessment"""
        recommendations = []
        
        if 'grammar' in assessment.weaknesses:
            recommendations.append('Focus on basic grammar through guided conversations')
        if 'vocabulary' in assessment.weaknesses:
            recommendations.append('Build vocabulary through daily flashcard practice')
        if 'fluency' in assessment.weaknesses:
            recommendations.append('Practice speaking through role-play scenarios')
        
        return recommendations
    
    def _get_or_create_daily_challenge(self, user_id):
        """Get or create today's daily challenge"""
        today = date.today()
        challenge = DailyChallenge.query.filter_by(challenge_date=today).first()
        
        if not challenge:
            # Create today's challenge
            challenge_content = {
                'type': 'conversation_starter',
                'question': 'Tell me about something that made you happy today.',
                'telugu_hint': 'ఈ రోజు మీకు సంతోషం కలిగించిన విషయం గురించి చెప్పండి.',
                'expected_duration': 5
            }
            
            challenge = DailyChallenge(
                challenge_date=today,
                challenge_type='conversation_starter',
                challenge_content=challenge_content,
                estimated_time_minutes=5
            )
            
            db.session.add(challenge)
            db.session.commit()
        
        # Check if user completed today's challenge
        completion = UserDailyChallengeCompletion.query.filter_by(
            user_id=user_id, 
            challenge_id=challenge.id
        ).first()
        
        return {
            'challenge': challenge.challenge_content,
            'completed': completion is not None,
            'completion_time': completion.time_spent_minutes if completion else None
        }
    
    def _generate_question_of_day(self, user_id):
        """Generate a personalized question of the day"""
        user = User.query.get(user_id)
        proficiency = user.profile.proficiency_level if user.profile else 'beginner'
        
        questions = {
            'beginner': [
                "What is your favorite food? (మీకు ఇష్టమైన ఆహారం ఏమిటి?)",
                "How was your day today? (ఈ రోజు మీ రోజు ఎలా ఉంది?)",
                "What do you like to do on weekends? (వీకెండ్‌లలో మీరు ఏమి చేయాలని అనిపిస్తుంది?)"
            ],
            'intermediate': [
                "What are your plans for the next month?",
                "Describe a memorable experience from your childhood.",
                "What skills would you like to learn and why?"
            ]
        }
        
        import random
        return random.choice(questions.get(proficiency, questions['beginner']))
    
    def _get_session_starter(self, user_id, session_type):
        """Get an appropriate session starter based on type and user profile"""
        user = User.query.get(user_id)
        name = user.username if user else "friend"
        
        starters = {
            'chat': f"Hello {name}! How are you doing today? Ready for some English practice?",
            'guided_conversation': f"Hi {name}! Today let's have a guided conversation. I'll help you step by step.",
            'role_play': f"Welcome {name}! Let's do some role-playing. This will help you practice real-world English."
        }
        
        return starters.get(session_type, starters['chat'])
    
    def _generate_session_summary(self, session):
        """Generate AI-powered session summary"""
        summary_prompt = f"""
        Generate a brief, encouraging summary for a {session.duration_minutes}-minute English learning session.
        
        Session details:
        - Type: {session.session_type}
        - Duration: {session.duration_minutes} minutes
        - New words learned: {session.new_words_learned}
        - Messages exchanged: {session.messages_exchanged}
        
        Provide a JSON summary:
        {{
            "achievement": "What the user accomplished",
            "progress_note": "Encouraging note about progress",
            "telugu_message": "Encouraging message in Telugu",
            "next_suggestion": "Suggestion for next session"
        }}
        """
        
        try:
            ai_response = self.activity_service.model.generate_content(summary_prompt)
            return self._extract_json_from_response(ai_response.text)
        except:
            return {
                "achievement": f"Completed {session.duration_minutes} minutes of English practice!",
                "progress_note": "Great job staying consistent with your learning!",
                "telugu_message": "బాగా చేశారు! ఇలాగే కొనసాగించండి!",
                "next_suggestion": "Try a different activity type tomorrow for variety."
            }
    
    def _generate_encouragement_message(self, session):
        """Generate personalized encouragement based on session performance"""
        if session.duration_minutes >= 15:
            return "Excellent! You're really committed to learning. బాగా చేశారు! 🌟"
        elif session.duration_minutes >= 10:
            return "Great job completing your daily practice! రోజువారీ అభ్యాసం చేస్తున్నందుకు గర్వపడండి! 👏"
        else:
            return "Every minute counts! You're making progress. ప్రతి నిమిషం ముఖ్యం! మీరు మెరుగుపడుతున్నారు! 💪"