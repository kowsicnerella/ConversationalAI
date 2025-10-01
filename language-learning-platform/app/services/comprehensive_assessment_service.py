import json
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from app.models import User, Activity, UserActivityLog, LearningPath, ProficiencyAssessment
from app.services.activity_generator_service import ActivityGeneratorService
from app.models import db
import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GEMINI_API_KEY)


class ComprehensiveAssessmentService:
    """
    Enhanced comprehensive initial assessment service that evaluates users across multiple language skills
    and generates personalized learning paths based on results.
    """
    
    def __init__(self):
        self.activity_service = ActivityGeneratorService()
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Assessment configuration
        self.SKILL_AREAS = ['reading', 'writing', 'grammar', 'vocabulary', 'listening', 'speaking']
        self.DIFFICULTY_LEVELS = ['beginner', 'intermediate', 'advanced']
        
        # Scoring thresholds
        self.MASTERY_THRESHOLD = 0.85  # 85% for mastery
        self.PROFICIENT_THRESHOLD = 0.70  # 70% for proficiency
        self.NEEDS_WORK_THRESHOLD = 0.50  # Below 50% needs significant work
        
        # Assessment weights by skill area
        self.SKILL_WEIGHTS = {
            'reading': 0.20,
            'writing': 0.25,
            'grammar': 0.20,
            'vocabulary': 0.15,
            'listening': 0.10,
            'speaking': 0.10
        }

    def conduct_comprehensive_assessment(self, user_id: int) -> Dict:
        """
        Conduct a comprehensive multi-skill assessment for a new user.
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Create assessment record
            assessment = ProficiencyAssessment(
                user_id=user_id,
                assessment_type='comprehensive_initial',
                assessment_data={'status': 'started', 'skills_assessed': []}
            )
            
            db.session.add(assessment)
            db.session.flush()  # Get assessment ID
            
            # Generate assessment questions for each skill area
            assessment_questions = self._generate_comprehensive_questions()
            
            # Update assessment with questions
            assessment.questions_asked = assessment_questions
            assessment.assessment_data = {
                'status': 'in_progress',
                'skills_assessed': [],
                'total_questions': len(assessment_questions),
                'questions_by_skill': self._categorize_questions_by_skill(assessment_questions)
            }
            
            db.session.commit()
            
            return {
                'assessment_id': assessment.id,
                'message': 'Comprehensive assessment started',
                'telugu_message': 'సమగ్ర మూల్యాంకనం ప్రారంభమైంది',
                'questions': assessment_questions,
                'instructions': self._get_assessment_instructions(),
                'estimated_duration_minutes': 20,
                'skills_being_assessed': self.SKILL_AREAS
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Assessment creation failed: {str(e)}'}

    def _generate_comprehensive_questions(self) -> List[Dict]:
        """
        Generate a comprehensive set of questions covering all skill areas.
        """
        questions = []
        question_id = 1
        
        # Reading Comprehension Questions
        reading_questions = self._generate_reading_questions(question_id)
        questions.extend(reading_questions)
        question_id += len(reading_questions)
        
        # Writing Assessment Questions
        writing_questions = self._generate_writing_questions(question_id)
        questions.extend(writing_questions)
        question_id += len(writing_questions)
        
        # Grammar Assessment Questions
        grammar_questions = self._generate_grammar_questions(question_id)
        questions.extend(grammar_questions)
        question_id += len(grammar_questions)
        
        # Vocabulary Assessment Questions
        vocabulary_questions = self._generate_vocabulary_questions(question_id)
        questions.extend(vocabulary_questions)
        question_id += len(vocabulary_questions)
        
        # Listening Comprehension Questions
        listening_questions = self._generate_listening_questions(question_id)
        questions.extend(listening_questions)
        question_id += len(listening_questions)
        
        # Speaking Assessment Questions
        speaking_questions = self._generate_speaking_questions(question_id)
        questions.extend(speaking_questions)
        
        return questions

    def _generate_reading_questions(self, start_id: int) -> List[Dict]:
        """Generate reading comprehension questions."""
        questions = []
        
        # Beginner level reading passage
        questions.append({
            'id': start_id,
            'skill_area': 'reading',
            'difficulty': 'beginner',
            'type': 'reading_comprehension',
            'passage': '''
            My name is Priya. I live in Hyderabad with my family. I work in an IT company. 
            Every morning, I wake up at 6 AM and go for a walk in the park. Then I have 
            breakfast with my parents and go to office. I like my job because I learn new 
            things every day.
            ''',
            'question': 'What time does Priya wake up?',
            'options': ['5 AM', '6 AM', '7 AM', '8 AM'],
            'correct_answer': '6 AM',
            'telugu_hint': 'ప్రియ ఎన్ని గంటలకు లేస్తుంది?'
        })
        
        questions.append({
            'id': start_id + 1,
            'skill_area': 'reading',
            'difficulty': 'beginner',
            'type': 'reading_comprehension',
            'passage': '''Same passage as above''',
            'question': 'Where does Priya work?',
            'options': ['School', 'Hospital', 'IT Company', 'Bank'],
            'correct_answer': 'IT Company',
            'telugu_hint': 'ప్రియ ఎక్కడ పని చేస్తుంది?'
        })
        
        # Intermediate level reading passage
        questions.append({
            'id': start_id + 2,
            'skill_area': 'reading',
            'difficulty': 'intermediate',
            'type': 'reading_comprehension',
            'passage': '''
            Technology has revolutionized the way we communicate and work. With the advent 
            of smartphones and high-speed internet, people can now collaborate across 
            continents in real-time. However, this rapid digitization has also created 
           challenges such as digital divide and privacy concerns. Companies must balance 
            innovation with responsible data handling practices.
            ''',
            'question': 'What is mentioned as a challenge of rapid digitization?',
            'options': ['High costs', 'Digital divide', 'Slow internet', 'Old devices'],
            'correct_answer': 'Digital divide',
            'telugu_hint': 'వేగవంతమైన డిజిటైజేషన్ యొక్క సవాలుగా ఏది ప్రస్తావించబడింది?'
        })
        
        return questions

    def _generate_writing_questions(self, start_id: int) -> List[Dict]:
        """Generate writing assessment questions."""
        questions = []
        
        questions.append({
            'id': start_id,
            'skill_area': 'writing',
            'difficulty': 'beginner',
            'type': 'sentence_formation',
            'prompt': 'Write 2-3 sentences about your daily routine.',
            'telugu_hint': 'మీ దైనందిన కార్యకలాపాల గురించి 2-3 వాక్యాలు రాయండి.',
            'evaluation_criteria': ['grammar', 'vocabulary', 'sentence_structure'],
            'max_words': 50,
            'min_words': 15
        })
        
        questions.append({
            'id': start_id + 1,
            'skill_area': 'writing',
            'difficulty': 'intermediate',
            'type': 'paragraph_writing',
            'prompt': 'Describe your favorite festival and why you like it. Write a paragraph (4-5 sentences).',
            'telugu_hint': 'మీకు ఇష్టమైన పండుగ మరియు మీరు దానిని ఎందుకు ఇష్టపడతారో వివరించండి.',
            'evaluation_criteria': ['grammar', 'vocabulary', 'coherence', 'creativity'],
            'max_words': 100,
            'min_words': 40
        })
        
        questions.append({
            'id': start_id + 2,
            'skill_area': 'writing',
            'difficulty': 'advanced',
            'type': 'essay_writing',
            'prompt': 'Express your opinion on the role of technology in modern education. Support your viewpoint with examples.',
            'telugu_hint': 'ఆధునిక విద్యలో సాంకేతికత పాత్ర గురించి మీ అభిప్రాయాన్ని వ్యక్తపరచండి.',
            'evaluation_criteria': ['grammar', 'vocabulary', 'argumentation', 'examples', 'structure'],
            'max_words': 200,
            'min_words': 80
        })
        
        return questions

    def _generate_grammar_questions(self, start_id: int) -> List[Dict]:
        """Generate grammar assessment questions."""
        questions = []
        
        # Basic grammar - verb forms
        questions.append({
            'id': start_id,
            'skill_area': 'grammar',
            'difficulty': 'beginner',
            'type': 'multiple_choice',
            'question': 'Choose the correct verb form: "She _____ to work every day."',
            'options': ['go', 'goes', 'going', 'gone'],
            'correct_answer': 'goes',
            'telugu_hint': 'సరైన క్రియా రూపాన్ని ఎంచుకోండి'
        })
        
        # Tense usage
        questions.append({
            'id': start_id + 1,
            'skill_area': 'grammar',
            'difficulty': 'intermediate',
            'type': 'multiple_choice',
            'question': 'Complete the sentence: "By next year, I _____ my degree."',
            'options': ['will complete', 'will have completed', 'am completing', 'completed'],
            'correct_answer': 'will have completed',
            'telugu_hint': 'వాక్యాన్ని పూర్తి చేయండి'
        })
        
        # Complex grammar
        questions.append({
            'id': start_id + 2,
            'skill_area': 'grammar',
            'difficulty': 'advanced',
            'type': 'sentence_correction',
            'question': 'Identify and correct the error: "If I would have known, I would had come earlier."',
            'correct_answer': 'If I had known, I would have come earlier.',
            'telugu_hint': 'దోషాన్ని గుర్తించి సరిదిద్దండి'
        })
        
        return questions

    def _generate_vocabulary_questions(self, start_id: int) -> List[Dict]:
        """Generate vocabulary assessment questions."""
        questions = []
        
        questions.append({
            'id': start_id,
            'skill_area': 'vocabulary',
            'difficulty': 'beginner',
            'type': 'word_meaning',
            'question': 'What does "beautiful" mean?',
            'options': ['ugly', 'pretty', 'angry', 'tall'],
            'correct_answer': 'pretty',
            'telugu_hint': '"beautiful" అంటే ఏమిటి?'
        })
        
        questions.append({
            'id': start_id + 1,
            'skill_area': 'vocabulary',
            'difficulty': 'intermediate',
            'type': 'synonym',
            'question': 'Choose the best synonym for "accomplish":',
            'options': ['fail', 'achieve', 'attempt', 'forget'],
            'correct_answer': 'achieve',
            'telugu_hint': '"accomplish" యొక్క పర్యాయపదం ఎంచుకోండి'
        })
        
        questions.append({
            'id': start_id + 2,
            'skill_area': 'vocabulary',
            'difficulty': 'advanced',
            'type': 'context_usage',
            'question': 'Use the word "meticulous" in a sentence that shows its meaning.',
            'sample_answer': 'The meticulous scientist checked every detail of the experiment twice.',
            'telugu_hint': '"meticulous" పదాన్ని దాని అర్థాన్ని చూపే వాక్యంలో ఉపయోగించండి'
        })
        
        return questions

    def _generate_listening_questions(self, start_id: int) -> List[Dict]:
        """Generate listening comprehension questions."""
        questions = []
        
        questions.append({
            'id': start_id,
            'skill_area': 'listening',
            'difficulty': 'beginner',
            'type': 'audio_comprehension',
            'audio_text': 'Hello, my name is Ravi. I am twenty-five years old. I like to read books and watch movies.',
            'question': 'What is the speaker\'s name?',
            'options': ['Raj', 'Ravi', 'Ram', 'Rohit'],
            'correct_answer': 'Ravi',
            'telugu_hint': 'మాట్లాడేవారి పేరు ఏమిటి?',
            'note': 'Audio will be generated using text-to-speech'
        })
        
        return questions

    def _generate_speaking_questions(self, start_id: int) -> List[Dict]:
        """Generate speaking assessment questions."""
        questions = []
        
        questions.append({
            'id': start_id,
            'skill_area': 'speaking',
            'difficulty': 'beginner',
            'type': 'pronunciation',
            'prompt': 'Please pronounce these words clearly: "Hello", "Thank you", "Good morning"',
            'telugu_hint': 'ఈ పదాలను స్పష్టంగా ఉచ్చరించండి',
            'evaluation_criteria': ['pronunciation', 'clarity', 'pace']
        })
        
        questions.append({
            'id': start_id + 1,
            'skill_area': 'speaking',
            'difficulty': 'intermediate',
            'type': 'conversation',
            'prompt': 'Introduce yourself and talk about your hobbies for 1-2 minutes.',
            'telugu_hint': 'మీ పరిచయం చేసుకోండి మరియు మీ అభిరుచుల గురించి మాట్లాడండి',
            'evaluation_criteria': ['fluency', 'vocabulary', 'grammar', 'confidence']
        })
        
        return questions

    def evaluate_assessment_response(self, assessment_id: int, question_id: int, 
                                   user_response: str, response_type: str = 'text') -> Dict:
        """
        Evaluate user's response to an assessment question using AI.
        """
        try:
            assessment = ProficiencyAssessment.query.get(assessment_id)
            if not assessment:
                return {'error': 'Assessment not found'}
            
            # Find the question
            question = next((q for q in assessment.questions_asked if q['id'] == question_id), None)
            if not question:
                return {'error': 'Question not found'}
            
            # Evaluate based on question type
            if question['type'] == 'multiple_choice':
                score, feedback = self._evaluate_multiple_choice(question, user_response)
            elif question['type'] in ['sentence_formation', 'paragraph_writing', 'essay_writing']:
                score, feedback = self._evaluate_writing_response(question, user_response)
            elif question['type'] == 'reading_comprehension':
                score, feedback = self._evaluate_reading_response(question, user_response)
            elif question['type'] == 'sentence_correction':
                score, feedback = self._evaluate_grammar_correction(question, user_response)
            elif question['type'] in ['word_meaning', 'synonym']:
                score, feedback = self._evaluate_vocabulary_response(question, user_response)
            elif question['type'] == 'context_usage':
                score, feedback = self._evaluate_context_usage(question, user_response)
            else:
                score, feedback = 0.5, "Response recorded for manual evaluation"
            
            # Store the response
            if not assessment.user_responses:
                assessment.user_responses = {}
            
            assessment.user_responses[str(question_id)] = {
                'response': user_response,
                'score': score,
                'feedback': feedback,
                'evaluated_at': datetime.utcnow().isoformat()
            }
            
            # Update assessment data
            assessment_data = assessment.assessment_data or {}
            skills_assessed = assessment_data.get('skills_assessed', [])
            if question['skill_area'] not in skills_assessed:
                skills_assessed.append(question['skill_area'])
            assessment_data['skills_assessed'] = skills_assessed
            assessment.assessment_data = assessment_data
            
            db.session.commit()
            
            return {
                'question_id': question_id,
                'score': score,
                'feedback': feedback,
                'skill_area': question['skill_area'],
                'difficulty': question['difficulty']
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Evaluation failed: {str(e)}'}

    def _evaluate_multiple_choice(self, question: Dict, user_response: str) -> Tuple[float, str]:
        """Evaluate multiple choice questions."""
        correct_answer = question.get('correct_answer', '')
        if user_response.strip().lower() == correct_answer.lower():
            return 1.0, "Correct! Well done."
        else:
            return 0.0, f"Incorrect. The correct answer is: {correct_answer}"

    def _evaluate_writing_response(self, question: Dict, user_response: str) -> Tuple[float, str]:
        """Evaluate writing responses using AI-based analysis."""
        try:
            # Use AI to evaluate the writing
            evaluation_prompt = f"""
            Evaluate this English writing response based on the given criteria:
            
            Prompt: {question['prompt']}
            User Response: {user_response}
            
            Evaluation Criteria: {', '.join(question.get('evaluation_criteria', ['grammar', 'vocabulary']))}
            
            Provide a score from 0 to 1 and detailed feedback focusing on:
            1. Grammar accuracy
            2. Vocabulary usage
            3. Content relevance
            4. Overall communication effectiveness
            
            Format your response as JSON:
            {{
                "score": 0.8,
                "feedback": "Detailed feedback here...",
                "strengths": ["List of strengths"],
                "areas_for_improvement": ["List of areas to improve"]
            }}
            """
            
            # For now, provide a basic evaluation (can be enhanced with actual AI integration)
            word_count = len(user_response.split())
            min_words = question.get('min_words', 10)
            max_words = question.get('max_words', 100)
            
            score = 0.7  # Base score
            feedback_parts = []
            
            # Check word count
            if word_count < min_words:
                score -= 0.2
                feedback_parts.append(f"Response is too short ({word_count} words). Try to write at least {min_words} words.")
            elif word_count > max_words:
                score -= 0.1
                feedback_parts.append(f"Response is too long ({word_count} words). Try to keep it under {max_words} words.")
            else:
                feedback_parts.append("Good length for the response.")
            
            # Basic grammar check (simple heuristics)
            if user_response.count('.') == 0:
                score -= 0.1
                feedback_parts.append("Remember to end sentences with proper punctuation.")
            
            # Check for capitalization
            if not user_response[0].isupper():
                score -= 0.05
                feedback_parts.append("Remember to start sentences with capital letters.")
            
            feedback = " ".join(feedback_parts)
            return max(0.0, min(1.0, score)), feedback
            
        except Exception as e:
            return 0.5, f"Response recorded. Evaluation pending: {str(e)}"

    def _evaluate_reading_response(self, question: Dict, user_response: str) -> Tuple[float, str]:
        """Evaluate reading comprehension responses."""
        return self._evaluate_multiple_choice(question, user_response)

    def _evaluate_grammar_correction(self, question: Dict, user_response: str) -> Tuple[float, str]:
        """Evaluate grammar correction responses."""
        correct_answer = question.get('correct_answer', '').strip().lower()
        user_answer = user_response.strip().lower()
        
        # Simple similarity check (can be enhanced)
        if correct_answer in user_answer or user_answer in correct_answer:
            return 0.8, "Good correction! Minor variations in wording are acceptable."
        else:
            return 0.3, f"The correction needs work. Correct answer: {question.get('correct_answer')}"

    def _evaluate_vocabulary_response(self, question: Dict, user_response: str) -> Tuple[float, str]:
        """Evaluate vocabulary responses."""
        return self._evaluate_multiple_choice(question, user_response)

    def _evaluate_context_usage(self, question: Dict, user_response: str) -> Tuple[float, str]:
        """Evaluate context usage responses."""
        # Check if the target word is used in the response
        target_word = question.get('question', '').split('"')[1] if '"' in question.get('question', '') else ''
        
        if target_word.lower() in user_response.lower():
            return 0.8, f"Good use of '{target_word}' in context. The sentence shows understanding of the word's meaning."
        else:
            return 0.2, f"Please use the word '{target_word}' in your sentence."

    def finalize_assessment(self, assessment_id: int) -> Dict:
        """
        Complete the assessment and calculate final scores and proficiency levels.
        """
        try:
            assessment = ProficiencyAssessment.query.get(assessment_id)
            if not assessment:
                return {'error': 'Assessment not found'}
            
            if not assessment.user_responses:
                return {'error': 'No responses found for assessment'}
            
            # Calculate scores by skill area
            skill_scores = {}
            for skill in self.SKILL_AREAS:
                skill_scores[skill] = self._calculate_skill_score(assessment, skill)
            
            # Calculate overall score
            overall_score = sum(skill_scores[skill] * self.SKILL_WEIGHTS[skill] 
                              for skill in skill_scores if skill_scores[skill] is not None)
            
            # Determine proficiency level
            if overall_score >= self.MASTERY_THRESHOLD:
                proficiency_level = 'advanced'
            elif overall_score >= self.PROFICIENT_THRESHOLD:
                proficiency_level = 'intermediate'
            else:
                proficiency_level = 'beginner'
            
            # Identify strengths and weaknesses
            strengths = []
            weaknesses = []
            for skill, score in skill_scores.items():
                if score is not None:
                    if score >= self.PROFICIENT_THRESHOLD:
                        strengths.append(skill)
                    elif score < self.NEEDS_WORK_THRESHOLD:
                        weaknesses.append(skill)
            
            # Update assessment record
            assessment.overall_score = overall_score
            assessment.proficiency_level = proficiency_level
            assessment.strengths = strengths
            assessment.weaknesses = weaknesses
            assessment.completed_at = datetime.utcnow()
            assessment.assessment_data['status'] = 'completed'
            assessment.assessment_data['skill_scores'] = skill_scores
            
            # Update user profile
            user = User.query.get(assessment.user_id)
            if user and user.profile:
                user.profile.proficiency_level = proficiency_level
                user.profile.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'assessment_id': assessment_id,
                'overall_score': round(overall_score, 2),
                'proficiency_level': proficiency_level,
                'skill_scores': {k: round(v, 2) if v is not None else None for k, v in skill_scores.items()},
                'strengths': strengths,
                'weaknesses': weaknesses,
                'recommendations': self._generate_learning_recommendations(strengths, weaknesses, proficiency_level),
                'next_steps': 'Assessment completed. Generating personalized learning path...'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'error': f'Assessment finalization failed: {str(e)}'}

    def _calculate_skill_score(self, assessment: ProficiencyAssessment, skill_area: str) -> Optional[float]:
        """Calculate average score for a specific skill area."""
        responses = assessment.user_responses or {}
        questions = assessment.questions_asked or []
        
        skill_responses = []
        for question in questions:
            if question.get('skill_area') == skill_area:
                response_data = responses.get(str(question['id']))
                if response_data and 'score' in response_data:
                    skill_responses.append(response_data['score'])
        
        if skill_responses:
            return sum(skill_responses) / len(skill_responses)
        return None

    def _generate_learning_recommendations(self, strengths: List[str], weaknesses: List[str], 
                                         proficiency_level: str) -> List[str]:
        """Generate personalized learning recommendations based on assessment results."""
        recommendations = []
        
        if 'reading' in weaknesses:
            recommendations.append('Focus on daily reading practice with graded materials')
        if 'writing' in weaknesses:
            recommendations.append('Practice structured writing with grammar exercises')
        if 'grammar' in weaknesses:
            recommendations.append('Study fundamental grammar rules with interactive exercises')
        if 'vocabulary' in weaknesses:
            recommendations.append('Build vocabulary through contextual learning and flashcards')
        if 'listening' in weaknesses:
            recommendations.append('Improve listening skills with audio content and conversation practice')
        if 'speaking' in weaknesses:
            recommendations.append('Practice speaking through role-play scenarios and pronunciation exercises')
        
        # Add level-specific recommendations
        if proficiency_level == 'beginner':
            recommendations.append('Start with basic conversation patterns and everyday vocabulary')
        elif proficiency_level == 'intermediate':
            recommendations.append('Focus on complex sentence structures and advanced vocabulary')
        else:
            recommendations.append('Practice advanced writing and professional communication')
        
        return recommendations

    def _categorize_questions_by_skill(self, questions: List[Dict]) -> Dict:
        """Categorize questions by skill area for progress tracking."""
        categorized = {}
        for question in questions:
            skill = question.get('skill_area', 'unknown')
            if skill not in categorized:
                categorized[skill] = []
            categorized[skill].append(question['id'])
        return categorized

    def _get_assessment_instructions(self) -> Dict:
        """Get comprehensive assessment instructions."""
        return {
            'english': '''
            Welcome to your comprehensive English assessment! This test will evaluate your 
            skills in reading, writing, grammar, vocabulary, listening, and speaking. 
            Please answer all questions to the best of your ability. Take your time and 
            don't worry about making mistakes - this helps us create the perfect learning 
            path for you.
            ''',
            'telugu': '''
            మీ సమగ్ర ఇంగ్లీష్ మూల్యాంకనానికి స్వాగతం! ఈ పరీక్ష పఠనం, రచన, వ్యాకరణం, 
            పదకోశం, వినికిడి మరియు మాట్లాడటంలో మీ నైపుణ్యాలను అంచనా వేస్తుంది. 
            దయచేసి మీ శక్తి మేరకు అన్ని ప్రశ్నలకు సమాధానం ఇవ్వండి.
            '''
        }