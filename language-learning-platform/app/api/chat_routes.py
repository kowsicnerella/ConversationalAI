from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    db, User, LearningSession, VocabularyWord, Chapter, 
    PracticeSession, UserNotes, AIConversationContext
)
from app.services.activity_generator_service import ActivityGeneratorService
from app.services.personalization_service import PersonalizationService
from datetime import datetime
import json

chat_bp = Blueprint('chat', __name__)
activity_service = ActivityGeneratorService()
personalization_service = PersonalizationService()

@chat_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    """
    Get user's conversation history with pagination.
    """
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        conversations = LearningSession.query.filter_by(
            user_id=user_id, 
            session_type='chat'
        ).order_by(LearningSession.start_time.desc())\
         .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'message': 'Conversations retrieved successfully!',
            'telugu_message': 'సంభాషణలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'conversations': [
                {
                    'id': session.id,
                    'start_time': session.start_time.isoformat(),
                    'end_time': session.end_time.isoformat() if session.end_time else None,
                    'duration_minutes': session.duration_minutes,
                    'messages_exchanged': session.messages_exchanged,
                    'new_words_learned': session.new_words_learned,
                    'session_summary': session.session_summary,
                    'user_satisfaction': session.user_satisfaction
                } for session in conversations.items
            ],
            'pagination': {
                'page': conversations.page,
                'per_page': conversations.per_page,
                'total': conversations.total,
                'pages': conversations.pages,
                'has_next': conversations.has_next,
                'has_prev': conversations.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversations: {str(e)}")
        return jsonify({
            'error': 'Failed to get conversations',
            'telugu_message': 'సంభాషణలు పొందడంలో విఫలం'
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_conversation_messages(conversation_id):
    """
    Get messages from a specific conversation.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Verify conversation belongs to user
        conversation = LearningSession.query.filter_by(
            id=conversation_id, 
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({
                'error': 'Conversation not found',
                'telugu_message': 'సంభాషణ కనుగొనబడలేదు'
            }), 404
        
        # In a real implementation, messages would be stored in a separate table
        # For now, we'll return sample structure
        messages = conversation.conversation_messages or []
        
        return jsonify({
            'message': 'Messages retrieved successfully!',
            'telugu_message': 'సందేశాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'conversation': {
                'id': conversation.id,
                'start_time': conversation.start_time.isoformat(),
                'duration_minutes': conversation.duration_minutes,
                'messages': messages
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversation messages: {str(e)}")
        return jsonify({
            'error': 'Failed to get messages',
            'telugu_message': 'సందేశాలు పొందడంలో విఫలం'
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>/message', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """
    Send a message in an active conversation and get AI response.
    
    Expected JSON:
    {
        "message": "Hello, how are you today?",
        "message_type": "text"  // "text", "voice_to_text", "image"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user_message = data.get('message')
        message_type = data.get('message_type', 'text')
        
        if not user_message:
            return jsonify({
                'error': 'Message is required',
                'telugu_message': 'సందేశం అవసరం'
            }), 400
        
        # Verify conversation belongs to user and is active
        conversation = LearningSession.query.filter_by(
            id=conversation_id, 
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({
                'error': 'Conversation not found',
                'telugu_message': 'సంభాషణ కనుగొనబడలేదు'
            }), 404
        
        if conversation.end_time:
            return jsonify({
                'error': 'Conversation has ended',
                'telugu_message': 'సంభాషణ ముగిసింది'
            }), 400
        
        # Get user profile for context
        user = User.query.get(user_id)
        proficiency_level = user.profile.proficiency_level if user.profile else 'beginner'
        
        # Prepare context for AI response
        conversation_context = f"""
        You are a friendly AI English tutor helping a Telugu speaker learn English.
        
        User Profile:
        - Native Language: Telugu
        - English Proficiency: {proficiency_level}
        - Learning Focus: Conversation practice
        
        Instructions:
        1. Respond naturally and encouragingly to the user's message
        2. Correct any grammar mistakes gently
        3. Introduce 1-2 new vocabulary words when appropriate
        4. Ask engaging follow-up questions
        5. Provide Telugu translations for difficult words in parentheses
        6. Keep responses conversational and supportive
        
        User's message: "{user_message}"
        
        Respond as the AI tutor in a natural conversation.
        """
        
        # Get AI response
        ai_response = activity_service.model.generate_content(conversation_context)
        ai_message = ai_response.text.strip()
        
        # Store messages in conversation
        current_messages = conversation.conversation_messages or []
        
        new_messages = [
            {
                'timestamp': datetime.utcnow().isoformat(),
                'sender': 'user',
                'message': user_message,
                'message_type': message_type
            },
            {
                'timestamp': datetime.utcnow().isoformat(),
                'sender': 'ai_tutor',
                'message': ai_message,
                'message_type': 'text'
            }
        ]
        
        current_messages.extend(new_messages)
        conversation.conversation_messages = current_messages
        conversation.messages_exchanged += 2
        
        # Extract vocabulary words from the conversation
        vocabulary_extraction_prompt = f"""
        Extract new English vocabulary words from this conversation that a Telugu speaker might not know.
        
        User message: "{user_message}"
        AI response: "{ai_message}"
        
        Return JSON array of vocabulary objects:
        [
            {{
                "english_word": "word",
                "context_sentence": "sentence where word appears"
            }}
        ]
        
        Only include words that are likely new for a {proficiency_level} English learner.
        Return empty array if no new vocabulary is found.
        """
        
        try:
            vocab_response = activity_service.model.generate_content(vocabulary_extraction_prompt)
            vocab_data = activity_service._extract_json_from_response(vocab_response.text)
            
            if isinstance(vocab_data, list) and len(vocab_data) > 0:
                for vocab in vocab_data:
                    if 'english_word' in vocab and 'context_sentence' in vocab:
                        personalization_service.track_vocabulary_learning(
                            user_id, 
                            vocab['english_word'], 
                            vocab['context_sentence'], 
                            conversation_id
                        )
        except Exception as e:
            current_app.logger.warning(f"Vocabulary extraction failed: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully!',
            'telugu_message': 'సందేశం విజయవంతంగా పంపబడింది!',
            'conversation': {
                'id': conversation.id,
                'latest_messages': new_messages,
                'total_messages': conversation.messages_exchanged
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending message: {str(e)}")
        return jsonify({
            'error': 'Failed to send message',
            'telugu_message': 'సందేశం పంపడంలో విఫలం'
        }), 500

@chat_bp.route('/quick-chat', methods=['POST'])
@jwt_required()
def quick_chat():
    """
    Send a quick message without starting a formal session.
    
    Expected JSON:
    {
        "message": "How do you say 'good morning' in English?",
        "context": "vocabulary_question"  // "vocabulary_question", "grammar_help", "translation", "casual_chat"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user_message = data.get('message')
        context = data.get('context', 'casual_chat')
        
        if not user_message:
            return jsonify({
                'error': 'Message is required',
                'telugu_message': 'సందేశం అవసరం'
            }), 400
        
        # Get user profile for context
        user = User.query.get(user_id)
        proficiency_level = user.profile.proficiency_level if user.profile else 'beginner'
        
        # Prepare context-specific prompt
        context_prompts = {
            'vocabulary_question': f"""
            The user is asking a vocabulary question. Provide a clear, helpful answer.
            Include Telugu translation and example sentences.
            User's proficiency: {proficiency_level}
            Question: "{user_message}"
            """,
            'grammar_help': f"""
            The user needs grammar help. Explain clearly with simple examples.
            Use Telugu translations for difficult concepts.
            User's proficiency: {proficiency_level}
            Question: "{user_message}"
            """,
            'translation': f"""
            The user wants a translation. Provide accurate English translation 
            and explain any cultural context if relevant.
            User's proficiency: {proficiency_level}
            Question: "{user_message}"
            """,
            'casual_chat': f"""
            Engage in casual conversation. Be encouraging and ask follow-up questions.
            Introduce new vocabulary naturally. Correct mistakes gently.
            User's proficiency: {proficiency_level}
            Message: "{user_message}"
            """
        }
        
        prompt = context_prompts.get(context, context_prompts['casual_chat'])
        
        # Get AI response
        ai_response = activity_service.model.generate_content(prompt)
        ai_message = ai_response.text.strip()
        
        # Track this as a quick interaction (no formal session)
        interaction_data = {
            'user_message': user_message,
            'ai_response': ai_message,
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'message': 'Response generated successfully!',
            'telugu_message': 'సమాధానం విజయవంతంగా రూపొందించబడింది!',
            'response': ai_message,
            'context': context,
            'follow_up_suggestion': "Would you like to start a full learning session to practice more?"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in quick chat: {str(e)}")
        return jsonify({
            'error': 'Failed to generate response',
            'telugu_message': 'సమాధానం రూపొందించడంలో విఫలం'
        }), 500

@chat_bp.route('/send-message', methods=['POST'])
@jwt_required()
def send_simple_message():
    """
    Send a message and get an AI response. Creates a new conversation if needed.
    
    Expected JSON:
    {
        "message": "Hello, how do I say 'good morning' in English?",
        "conversation_id": 1  // Optional, creates new conversation if not provided
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user_message = data.get('message')
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return jsonify({
                'error': 'Message is required',
                'telugu_message': 'సందేశం అవసరం'
            }), 400
        
        # Get or create conversation
        if conversation_id:
            conversation = LearningSession.query.filter_by(
                id=conversation_id, 
                user_id=user_id,
                session_type='chat'
            ).first()
            if not conversation:
                return jsonify({
                    'error': 'Conversation not found',
                    'telugu_message': 'సంభాషణ కనుగొనబడలేదు'
                }), 404
        else:
            # Create new conversation
            conversation = LearningSession(
                user_id=user_id,
                session_type='chat',
                start_time=datetime.utcnow(),
                conversation_messages=json.dumps([])
            )
            db.session.add(conversation)
            db.session.flush()  # Get the ID
        
        # Get user profile for context
        user = User.query.get(user_id)
        proficiency_level = user.profile.proficiency_level if user.profile else 'beginner'
        
        # Generate AI response
        prompt = f"""
        You are a helpful Telugu-English learning assistant. Respond to this message from a Telugu speaker learning English.
        User's proficiency level: {proficiency_level}
        
        Provide a helpful, encouraging response. Include:
        - Direct answer to their question
        - Any relevant grammar or vocabulary tips
        - Telugu translation for difficult concepts if needed
        
        User message: "{user_message}"
        """
        
        ai_response = activity_service.model.generate_content(prompt)
        ai_message = ai_response.text.strip()
        
        # Update conversation
        current_messages = json.loads(conversation.conversation_messages) if conversation.conversation_messages else []
        new_messages = [
            {
                'sender': 'user',
                'message': user_message,
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'sender': 'ai',
                'message': ai_message,
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        current_messages.extend(new_messages)
        
        conversation.conversation_messages = json.dumps(current_messages)
        conversation.messages_exchanged = (conversation.messages_exchanged or 0) + 2
        
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully!',
            'telugu_message': 'సందేశం విజయవంతంగా పంపబడింది!',
            'conversation_id': conversation.id,
            'response': ai_message,
            'messages': new_messages
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending message: {str(e)}")
        return jsonify({
            'error': 'Failed to send message',
            'telugu_message': 'సందేశం పంపడంలో విఫలం'
        }), 500

@chat_bp.route('/conversations/<int:conversation_id>/feedback', methods=['POST'])
@jwt_required()
def provide_conversation_feedback(conversation_id):
    """
    Provide feedback on a conversation.
    
    Expected JSON:
    {
        "rating": 4,  // 1-5 rating
        "feedback": "The conversation was helpful",
        "areas_for_improvement": ["grammar", "vocabulary"]
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        rating = data.get('rating')
        feedback = data.get('feedback', '')
        areas_for_improvement = data.get('areas_for_improvement', [])
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({
                'error': 'Rating must be between 1 and 5',
                'telugu_message': 'రేటింగ్ 1 నుండి 5 మధ్య ఉండాలి'
            }), 400
        
        # Verify conversation belongs to user
        conversation = LearningSession.query.filter_by(
            id=conversation_id, 
            user_id=user_id
        ).first()
        
        if not conversation:
            return jsonify({
                'error': 'Conversation not found',
                'telugu_message': 'సంభాషణ కనుగొనబడలేదు'
            }), 404
        
        # Update conversation with feedback
        conversation.user_satisfaction = rating
        feedback_data = {
            'rating': rating,
            'feedback': feedback,
            'areas_for_improvement': areas_for_improvement,
            'feedback_timestamp': datetime.utcnow().isoformat()
        }
        
        conversation.user_feedback = feedback_data
        db.session.commit()
        
        return jsonify({
            'message': 'Feedback recorded successfully!',
            'telugu_message': 'ఫీడ్‌బ్యాక్ విజయవంతంగా రికార్డ్ చేయబడింది!',
            'thanks_message': 'Thank you for your feedback! It helps us improve your learning experience.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error recording feedback: {str(e)}")
        return jsonify({
            'error': 'Failed to record feedback',
            'telugu_message': 'ఫీడ్‌బ్యాక్ రికార్డ్ చేయడంలో విఫలం'
        }), 500

@chat_bp.route('/chat-suggestions', methods=['GET'])
@jwt_required()
def get_chat_suggestions():
    """
    Get personalized conversation starters and topic suggestions.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Get user profile for personalization
        user = User.query.get(user_id)
        proficiency_level = user.profile.proficiency_level if user.profile else 'beginner'
        
        # Generate topic suggestions based on proficiency
        topic_suggestions = {
            'beginner': [
                "Tell me about your family (మీ కుటుంబం గురించి చెప్పండి)",
                "What did you eat for breakfast? (అల్పాహారానికి ఏమి తిన్నారు?)",
                "Describe your favorite color (మీకు ఇష్టమైన రంగు గురించి చెప్పండి)",
                "What is the weather like today? (ఈ రోజు వాతావరణం ఎలా ఉంది?)"
            ],
            'intermediate': [
                "What are your plans for the weekend?",
                "Tell me about a place you would like to visit",
                "Describe your ideal job",
                "What new skill would you like to learn?"
            ],
            'advanced': [
                "What is your opinion on remote work?",
                "How has technology changed your daily life?",
                "Describe a challenge you overcame recently",
                "What advice would you give to someone learning English?"
            ]
        }
        
        current_suggestions = topic_suggestions.get(proficiency_level, topic_suggestions['beginner'])
        
        # Add some grammar practice suggestions
        grammar_practice = [
            "Let's practice using past tense - tell me what you did yesterday",
            "Practice asking questions - ask me about my hobbies",
            "Let's work on future tense - what will you do tomorrow?",
            "Practice making comparisons - compare two cities you know"
        ]
        
        return jsonify({
            'message': 'Chat suggestions retrieved successfully!',
            'telugu_message': 'చాట్ సూచనలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'suggestions': {
                'conversation_starters': current_suggestions[:3],
                'grammar_practice': grammar_practice[:2],
                'quick_help': [
                    "How do you say '___' in English?",
                    "Is this sentence correct: '___'?",
                    "What's the difference between '___' and '___'?"
                ]
            },
            'tip': "Pick a topic that interests you - you'll learn better when you're engaged!"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting chat suggestions: {str(e)}")
        return jsonify({
            'error': 'Failed to get chat suggestions',
            'telugu_message': 'చాట్ సూచనలు పొందడంలో విఫలం'
        }), 500

@chat_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def get_topic_suggestions():
    """
    Get specific topic-based conversation suggestions.
    
    Query Parameters:
    - topic: Topic category (greetings, family, food, etc.)
    - level: Proficiency level (beginner, intermediate, advanced)
    - count: Number of suggestions (default: 5)
    """
    try:
        topic = request.args.get('topic', 'general')
        level = request.args.get('level', 'beginner')
        count = int(request.args.get('count', 5))
        
        # Topic-specific suggestions
        topic_suggestions = {
            'greetings': {
                'beginner': [
                    "How do you say 'hello' in different situations?",
                    "What's the difference between 'Good morning' and 'Good day'?",
                    "How do you greet someone you meet for the first time?",
                    "When should I say 'How are you?' vs 'How do you do?'",
                    "What are some casual greetings I can use with friends?"
                ],
                'intermediate': [
                    "How do professional greetings differ from casual ones?",
                    "What are some regional variations in English greetings?",
                    "How do you respond to 'How's it going?' appropriately?",
                    "What's the etiquette for greeting in business meetings?",
                    "How do you greet someone after a long time?"
                ],
                'advanced': [
                    "How do cultural contexts affect greeting styles in English-speaking countries?",
                    "What are the nuances between formal and informal introductions?",
                    "How do you navigate greeting customs in international business?",
                    "What are some sophisticated ways to acknowledge someone?",
                    "How do you handle greetings in multicultural environments?"
                ]
            },
            'family': {
                'beginner': [
                    "How do you introduce your family members?",
                    "What are the names for different family relationships?",
                    "How do you talk about your family size?",
                    "What questions can you ask about someone's family?",
                    "How do you describe your family members?"
                ],
                'intermediate': [
                    "How do you discuss family traditions and customs?",
                    "What's the difference between nuclear and extended family?",
                    "How do you talk about family roles and responsibilities?",
                    "How do you describe family gatherings and celebrations?",
                    "What are some common family-related idioms?"
                ],
                'advanced': [
                    "How do family dynamics vary across cultures?",
                    "How do you discuss complex family relationships?",
                    "What are the nuances of family hierarchy in conversation?",
                    "How do you navigate sensitive family topics?",
                    "How do modern families differ from traditional ones?"
                ]
            },
            'food': {
                'beginner': [
                    "How do you order food at a restaurant?",
                    "What are common food names and cooking methods?",
                    "How do you express food preferences and allergies?",
                    "How do you describe taste and flavors?",
                    "What's the difference between meals (breakfast, lunch, dinner)?"
                ],
                'intermediate': [
                    "How do you discuss cooking techniques and recipes?",
                    "What are regional food specialties in English-speaking countries?",
                    "How do you navigate dietary restrictions in conversation?",
                    "How do you describe food texture and presentation?",
                    "What are common food-related expressions and idioms?"
                ],
                'advanced': [
                    "How do culinary traditions reflect cultural identity?",
                    "How do you engage in sophisticated food criticism?",
                    "What are the nuances of fine dining etiquette?",
                    "How do you discuss food sustainability and ethics?",
                    "How do global food trends influence local cuisines?"
                ]
            },
            'general': {
                'beginner': [
                    "How do you introduce yourself to new people?",
                    "What are basic conversation starters?",
                    "How do you ask for help politely?",
                    "How do you express likes and dislikes?",
                    "What are common daily activities to discuss?"
                ],
                'intermediate': [
                    "How do you engage in small talk effectively?",
                    "What are strategies for keeping conversations flowing?",
                    "How do you express opinions respectfully?",
                    "How do you handle disagreements in conversation?",
                    "What are some common conversation topics?"
                ],
                'advanced': [
                    "How do you engage in intellectual discussions?",
                    "What are techniques for persuasive communication?",
                    "How do you navigate complex social conversations?",
                    "How do you adapt your communication style to different audiences?",
                    "What are advanced conversation management skills?"
                ]
            }
        }
        
        # Get suggestions for the requested topic and level
        suggestions = topic_suggestions.get(topic, topic_suggestions['general'])
        level_suggestions = suggestions.get(level, suggestions['beginner'])
        
        # Limit to requested count
        selected_suggestions = level_suggestions[:count]
        
        return jsonify({
            'message': 'Topic suggestions retrieved successfully!',
            'telugu_message': 'టాపిక్ సూచనలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'topic': topic,
            'level': level,
            'count': len(selected_suggestions),
            'suggestions': selected_suggestions,
            'available_topics': list(topic_suggestions.keys()),
            'tip': f"These {topic} suggestions are tailored for {level} level learners!"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting topic suggestions: {str(e)}")
        return jsonify({
            'error': 'Failed to get topic suggestions',
            'telugu_message': 'టాపిక్ సూచనలు పొందడంలో విఫలం'
        }), 500

@chat_bp.route('/feedback', methods=['POST'])
@jwt_required()
def submit_general_feedback():
    """
    Submit general feedback about the chat system or learning experience.
    
    Expected JSON:
    {
        "feedback_type": "suggestion",  // "bug", "suggestion", "praise", "complaint"
        "rating": 4,                    // 1-5 rating (optional)
        "message": "The chat responses are very helpful!",
        "category": "chat_quality",     // "chat_quality", "ui_ux", "content", "performance"
        "session_context": "quick_chat" // "quick_chat", "conversation", "practice", "general"
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        feedback_type = data.get('feedback_type', 'general')
        rating = data.get('rating')
        message = data.get('message', '')
        category = data.get('category', 'general')
        session_context = data.get('session_context', 'general')
        
        if not message:
            return jsonify({
                'error': 'Feedback message is required',
                'telugu_message': 'ఫీడ్‌బ్యాక్ సందేశం అవసరం'
            }), 400
        
        if rating and (rating < 1 or rating > 5):
            return jsonify({
                'error': 'Rating must be between 1 and 5',
                'telugu_message': 'రేటింగ్ 1 నుండి 5 మధ్య ఉండాలి'
            }), 400
        
        # Store feedback (you might want to create a Feedback model for this)
        feedback_data = {
            'user_id': user_id,
            'feedback_type': feedback_type,
            'rating': rating,
            'message': message,
            'category': category,
            'session_context': session_context,
            'timestamp': datetime.utcnow().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }
        
        # Log feedback for now (in production, you'd save to database)
        current_app.logger.info(f"User feedback received: {feedback_data}")
        
        # Generate appropriate response based on feedback type
        response_messages = {
            'bug': {
                'message': 'Thank you for reporting this issue! Our team will investigate.',
                'telugu_message': 'ఈ సమస్యను రిపోర్ట్ చేసినందుకు ధన్యవాదాలు! మా బృందం దర్యాప్తు చేస్తుంది.'
            },
            'suggestion': {
                'message': 'Thank you for your suggestion! We appreciate your input.',
                'telugu_message': 'మీ సూచనకు ధన్యవాదాలు! మేము మీ ఇన్‌పుట్‌ను అభినందిస్తున్నాము.'
            },
            'praise': {
                'message': 'Thank you for your kind words! We\'re glad you\'re enjoying the experience.',
                'telugu_message': 'మీ మంచి మాటలకు ధన్యవాదాలు! మీరు అనుభవాన్ని ఆనందిస్తున్నారని మేము సంతోషిస్తున్నాము.'
            },
            'complaint': {
                'message': 'We\'re sorry to hear about your experience. We\'ll work to improve.',
                'telugu_message': 'మీ అనుభవం గురించి వినడానికి మేము చింతిస్తున్నాము. మేము మెరుగుపరచడానికి కృషి చేస్తాము.'
            }
        }
        
        response = response_messages.get(feedback_type, response_messages['suggestion'])
        
        return jsonify({
            'message': response['message'],
            'telugu_message': response['telugu_message'],
            'feedback_id': f"fb_{user_id}_{int(datetime.utcnow().timestamp())}",
            'status': 'received',
            'next_steps': 'Your feedback has been recorded and will be reviewed by our team.',
            'telugu_next_steps': 'మీ ఫీడ్‌బ్యాక్ రికార్డ్ చేయబడింది మరియు మా బృందం దీనిని సమీక్షిస్తుంది.'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({
            'error': 'Failed to submit feedback',
            'telugu_message': 'ఫీడ్‌బ్యాక్ సమర్పించడంలో విఫలం'
        }), 500

@chat_bp.route('/practice-assistant', methods=['POST'])
@jwt_required()
def general_practice_assistant():
    """
    General practice assistant for learning help without a specific session.
    
    Expected JSON:
    {
        "message": "How do I use past tense correctly?",
        "assistance_type": "grammar",      // "grammar", "vocabulary", "pronunciation", "conversation", "general"
        "difficulty_level": "beginner",   // "beginner", "intermediate", "advanced"
        "topic": "past_tense"            // optional specific topic
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user_message = data.get('message')
        assistance_type = data.get('assistance_type', 'general')
        difficulty_level = data.get('difficulty_level', 'beginner')
        topic = data.get('topic', '')
        
        if not user_message:
            return jsonify({
                'error': 'Message is required',
                'telugu_message': 'సందేశం అవసరం'
            }), 400
        
        # Get user profile for personalization
        user = User.query.get(user_id)
        user_proficiency = user.profile.proficiency_level if user.profile else 'beginner'
        
        # Create context-specific prompts
        assistance_prompts = {
            'grammar': f"""
            You are a helpful English grammar tutor for Telugu speakers. The user is at {user_proficiency} level.
            
            User's grammar question: "{user_message}"
            Difficulty level requested: {difficulty_level}
            {f"Specific topic: {topic}" if topic else ""}
            
            Provide:
            1. Clear explanation of the grammar rule
            2. Simple examples with Telugu translations
            3. Common mistakes to avoid
            4. Practice suggestions
            
            Keep explanations appropriate for {user_proficiency} level learners.
            """,
            
            'vocabulary': f"""
            You are a vocabulary building assistant for Telugu speakers learning English.
            User's proficiency: {user_proficiency}
            
            User's vocabulary question: "{user_message}"
            Difficulty level: {difficulty_level}
            {f"Topic area: {topic}" if topic else ""}
            
            Provide:
            1. Clear word definitions with Telugu translations
            2. Example sentences in context
            3. Synonyms and related words
            4. Tips for remembering the words
            5. Common usage patterns
            """,
            
            'pronunciation': f"""
            You are a pronunciation coach for Telugu speakers learning English.
            User level: {user_proficiency}
            
            User's pronunciation question: "{user_message}"
            Difficulty: {difficulty_level}
            
            Provide:
            1. Phonetic breakdown of sounds
            2. Comparison with similar Telugu sounds
            3. Common pronunciation mistakes for Telugu speakers
            4. Practice tips and exercises
            5. Word stress patterns
            """,
            
            'conversation': f"""
            You are a conversation practice assistant for Telugu speakers.
            User proficiency: {user_proficiency}
            
            User's conversation question: "{user_message}"
            Level: {difficulty_level}
            
            Provide:
            1. Natural conversation responses
            2. Alternative ways to express the same idea
            3. Cultural context when relevant
            4. Follow-up questions to continue conversation
            5. Polite and appropriate language suggestions
            """,
            
            'general': f"""
            You are a friendly English learning assistant for Telugu speakers.
            User level: {user_proficiency}
            
            User's question: "{user_message}"
            Requested difficulty: {difficulty_level}
            
            Provide helpful, encouraging guidance on their English learning question.
            Include Telugu translations for difficult concepts and give practical examples.
            """
        }
        
        prompt = assistance_prompts.get(assistance_type, assistance_prompts['general'])
        
        # Get AI response
        ai_response = activity_service.model.generate_content(prompt)
        ai_message = ai_response.text.strip()
        
        # Generate follow-up suggestions based on assistance type
        follow_up_suggestions = {
            'grammar': [
                "Would you like to practice this grammar rule with exercises?",
                "Do you want to see more examples of this grammar in use?",
                "Should we practice identifying this grammar in sentences?"
            ],
            'vocabulary': [
                "Would you like to practice using these words in sentences?",
                "Should we explore more words related to this topic?",
                "Do you want to practice word associations and memory techniques?"
            ],
            'pronunciation': [
                "Would you like to practice pronunciation with tongue twisters?",
                "Should we work on similar sounds that might be confusing?",
                "Do you want tips for improving your accent?"
            ],
            'conversation': [
                "Would you like to continue this conversation practice?",
                "Should we practice more conversation scenarios?",
                "Do you want to work on specific conversation skills?"
            ],
            'general': [
                "Is there a specific area you'd like to focus on?",
                "Would you like more detailed explanations?",
                "Should we practice what we just discussed?"
            ]
        }
        
        suggestions = follow_up_suggestions.get(assistance_type, follow_up_suggestions['general'])
        
        return jsonify({
            'message': 'Practice assistance provided successfully!',
            'telugu_message': 'ప్రాక్టీస్ సహాయం విజయవంతంగా అందించబడింది!',
            'response': ai_message,
            'assistance_type': assistance_type,
            'difficulty_level': difficulty_level,
            'follow_up_suggestions': suggestions[:2],  # Limit to 2 suggestions
            'tip': f"Keep practicing {assistance_type} regularly to improve your English skills!",
            'telugu_tip': f"మీ ఆంగ్ల నైపుణ్యాలను మెరుగుపరచుకోవడానికి {assistance_type} ని క్రమం తప్పకుండా అభ్యసించండి!"
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in practice assistant: {str(e)}")
        return jsonify({
            'error': 'Failed to provide practice assistance',
            'telugu_message': 'ప్రాక్టీస్ సహాయం అందించడంలో విఫలం'
        }), 500

@chat_bp.route('/practice-assistant/<int:practice_session_id>/chat', methods=['POST'])
@jwt_required()
def chat_with_practice_assistant(practice_session_id):
    """
    Chat with AI assistant during a practice session for help and guidance.
    
    Expected JSON:
    {
        "message": "I don't understand this grammar rule",
        "context": "question_help",  // question_help, explanation_request, general_guidance
        "current_question_id": "q_1"  // optional
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        user_message = data.get('message')
        context_type = data.get('context', 'general_guidance')
        current_question_id = data.get('current_question_id')
        
        if not user_message:
            return jsonify({
                'error': 'Message is required',
                'telugu_message': 'సందేశం అవసరం'
            }), 400
        
        # Verify practice session exists and belongs to user
        practice_session = PracticeSession.query.filter_by(
            id=practice_session_id, user_id=user_id
        ).first()
        
        if not practice_session:
            return jsonify({
                'error': 'Practice session not found',
                'telugu_message': 'అభ్యాస సెషన్ కనుగొనబడలేదు'
            }), 404
        
        # Get or create conversation context
        conv_context = AIConversationContext.query.filter_by(
            user_id=user_id, 
            practice_session_id=practice_session_id,
            context_type='practice_assistance'
        ).first()
        
        if not conv_context:
            conv_context = AIConversationContext(
                user_id=user_id,
                chapter_id=practice_session.chapter_id,
                practice_session_id=practice_session_id,
                context_type='practice_assistance',
                conversation_history=[],
                current_topic=f'Practice assistance for chapter {practice_session.chapter_id}'
            )
            db.session.add(conv_context)
        
        # Get chapter and current question context
        chapter = Chapter.query.get(practice_session.chapter_id)
        current_question = None
        
        if current_question_id:
            questions = practice_session.questions_data or []
            current_question = next((q for q in questions if q.get('id') == current_question_id), None)
        
        # Generate context-aware AI response
        ai_response = _generate_practice_assistant_response(
            user_message, context_type, chapter, current_question, conv_context, practice_session
        )
        
        # Update conversation history
        conversation_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_message': user_message,
            'ai_response': ai_response,
            'context_type': context_type,
            'question_id': current_question_id
        }
        
        history = conv_context.conversation_history or []
        history.append(conversation_entry)
        conv_context.conversation_history = history
        conv_context.last_interaction = datetime.utcnow()
        
        # Also store in practice session for continuity
        session_messages = practice_session.conversation_messages or []
        session_messages.append(conversation_entry)
        practice_session.conversation_messages = session_messages
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assistant response generated successfully!',
            'telugu_message': 'సహాయకుడి సమాధానం విజయవంతంగా రూపొందించబడింది!',
            'assistant_response': ai_response,
            'context_maintained': True,
            'conversation_id': conv_context.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in practice assistant chat: {str(e)}")
        return jsonify({
            'error': 'Failed to get assistant response',
            'telugu_message': 'సహాయకుడి సమాధానం పొందడంలో విఫలం'
        }), 500

@chat_bp.route('/notes', methods=['POST'])
@jwt_required()
def create_note():
    """
    Create a note during learning session.
    
    Expected JSON:
    {
        "note_content": "This is my note about verb tenses",  // or "content"
        "title": "Verb Tenses",  // optional title
        "note_type": "grammar",  // general, vocabulary, grammar, mistake
        "chapter_id": 1,  // optional
        "practice_session_id": 5,  // optional
        "tags": ["verbs", "tenses"],  // optional
        "is_important": true  // optional
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Accept both 'note_content' and 'content' for flexibility
        note_content = data.get('note_content') or data.get('content')
        title = data.get('title', '')
        note_type = data.get('note_type', 'general')
        chapter_id = data.get('chapter_id')
        practice_session_id = data.get('practice_session_id')
        tags = data.get('tags', [])
        is_important = data.get('is_important', False)
        
        if not note_content:
            return jsonify({
                'error': 'Note content is required',
                'telugu_message': 'నోట్ కంటెంట్ అవసరం'
            }), 400
        
        # If title is provided, prepend it to the content
        final_content = f"Title: {title}\n\n{note_content}" if title else note_content
        
        # Create the note
        note = UserNotes(
            user_id=user_id,
            chapter_id=chapter_id,
            practice_session_id=practice_session_id,
            note_content=final_content,
            note_type=note_type,
            tags=tags,
            is_important=is_important
        )
        
        db.session.add(note)
        db.session.commit()
        
        return jsonify({
            'message': 'Note created successfully!',
            'telugu_message': 'నోట్ విజయవంతంగా సృష్టించబడింది!',
            'note': {
                'id': note.id,
                'note_content': note.note_content,
                'note_type': note.note_type,
                'tags': note.tags,
                'is_important': note.is_important,
                'created_at': note.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating note: {str(e)}")
        return jsonify({
            'error': 'Failed to create note',
            'telugu_message': 'నోట్ సృష్టించడంలో విఫలం'
        }), 500

@chat_bp.route('/notes', methods=['GET'])
@jwt_required()
def get_user_notes():
    """
    Get user's notes with filtering options.
    """
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        note_type = request.args.get('note_type')
        chapter_id = request.args.get('chapter_id', type=int)
        important_only = request.args.get('important_only', type=bool)
        search = request.args.get('search')
        
        # Build query
        query = UserNotes.query.filter_by(user_id=user_id)
        
        if note_type:
            query = query.filter_by(note_type=note_type)
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        if important_only:
            query = query.filter_by(is_important=True)
        if search:
            query = query.filter(UserNotes.note_content.contains(search))
        
        notes = query.order_by(UserNotes.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        notes_data = []
        for note in notes.items:
            note_info = {
                'id': note.id,
                'note_content': note.note_content,
                'note_type': note.note_type,
                'tags': note.tags,
                'is_important': note.is_important,
                'created_at': note.created_at.isoformat(),
                'updated_at': note.updated_at.isoformat(),
                'chapter_id': note.chapter_id,
                'practice_session_id': note.practice_session_id
            }
            
            # Add chapter title if available
            if note.chapter_id:
                chapter = Chapter.query.get(note.chapter_id)
                if chapter:
                    note_info['chapter_title'] = chapter.title
            
            notes_data.append(note_info)
        
        return jsonify({
            'message': 'Notes retrieved successfully!',
            'telugu_message': 'నోట్స్ విజయవంతంగా తీసుకోబడ్డాయి!',
            'notes': notes_data,
            'pagination': {
                'page': notes.page,
                'per_page': notes.per_page,
                'total': notes.total,
                'pages': notes.pages,
                'has_next': notes.has_next,
                'has_prev': notes.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting notes: {str(e)}")
        return jsonify({
            'error': 'Failed to get notes',
            'telugu_message': 'నోట్స్ పొందడంలో విఫలం'
        }), 500

@chat_bp.route('/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    """
    Update an existing note.
    
    Expected JSON:
    {
        "note_content": "Updated note content",
        "tags": ["updated", "tags"],
        "is_important": false
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        note = UserNotes.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return jsonify({
                'error': 'Note not found',
                'telugu_message': 'నోట్ కనుగొనబడలేదు'
            }), 404
        
        # Update note fields
        if 'note_content' in data:
            note.note_content = data['note_content']
        if 'tags' in data:
            note.tags = data['tags']
        if 'is_important' in data:
            note.is_important = data['is_important']
        
        note.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Note updated successfully!',
            'telugu_message': 'నోట్ విజయవంతంగా నవీకరించబడింది!',
            'note': {
                'id': note.id,
                'note_content': note.note_content,
                'tags': note.tags,
                'is_important': note.is_important,
                'updated_at': note.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating note: {str(e)}")
        return jsonify({
            'error': 'Failed to update note',
            'telugu_message': 'నోట్ నవీకరించడంలో విఫలం'
        }), 500

@chat_bp.route('/conversation-context/<int:context_id>', methods=['GET'])
@jwt_required()
def get_conversation_context(context_id):
    """
    Get conversation context for continued assistance.
    """
    try:
        user_id = int(get_jwt_identity())
        
        context = AIConversationContext.query.filter_by(
            id=context_id, user_id=user_id
        ).first()
        
        if not context:
            return jsonify({
                'error': 'Conversation context not found',
                'telugu_message': 'సంభాషణ సందర్భం కనుగొనబడలేదు'
            }), 404
        
        return jsonify({
            'message': 'Conversation context retrieved successfully!',
            'telugu_message': 'సంభాషణ సందర్భం విజయవంతంగా తీసుకోబడింది!',
            'context': {
                'id': context.id,
                'context_type': context.context_type,
                'current_topic': context.current_topic,
                'conversation_history': context.conversation_history[-10:],  # Last 10 messages
                'chapter_id': context.chapter_id,
                'practice_session_id': context.practice_session_id,
                'last_interaction': context.last_interaction.isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversation context: {str(e)}")
        return jsonify({
            'error': 'Failed to get conversation context',
            'telugu_message': 'సంభాషణ సందర్భం పొందడంలో విఫలం'
        }), 500

def _generate_practice_assistant_response(user_message, context_type, chapter, current_question, conv_context, practice_session):
    """
    Generate context-aware AI assistant response during practice.
    """
    try:
        # Build comprehensive context for AI
        context_info = {
            'user_message': user_message,
            'context_type': context_type,
            'chapter_title': chapter.title if chapter else 'Unknown',
            'chapter_topic': chapter.topic if chapter else 'General',
            'current_question': current_question,
            'conversation_history': conv_context.conversation_history[-5:] if conv_context.conversation_history else [],
            'practice_session_progress': {
                'total_questions': practice_session.total_questions,
                'current_score': practice_session.score_percentage,
                'questions_answered': len(practice_session.user_responses or [])
            }
        }
        
        prompt = f"""
        You are a helpful AI English tutor assistant for Telugu speakers. The user is currently in a practice session and needs assistance.
        
        Context:
        - User Message: "{user_message}"
        - Context Type: {context_type}
        - Chapter: {context_info['chapter_title']} ({context_info['chapter_topic']})
        - Current Question: {current_question.get('question_text', 'None') if current_question else 'None'}
        - Session Progress: {context_info['practice_session_progress']['questions_answered']}/{context_info['practice_session_progress']['total_questions']} questions, {context_info['practice_session_progress']['current_score']:.1f}% score
        
        Previous Conversation:
        {json.dumps(context_info['conversation_history'][-3:], indent=2) if context_info['conversation_history'] else 'None'}
        
        Instructions:
        1. Be helpful, encouraging, and supportive
        2. Provide clear explanations in both English and Telugu when needed
        3. If asking about a specific question, provide hints without giving the direct answer
        4. Maintain context from previous conversation
        5. Adapt your response to the context type:
           - question_help: Provide hints and guidance for the current question
           - explanation_request: Explain concepts clearly with examples
           - general_guidance: Offer study tips and motivation
        
        Respond naturally and helpfully as an AI tutor assistant.
        """
        
        response = activity_service.model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        current_app.logger.error(f"Error generating assistant response: {str(e)}")
        return {
            'message': "I'm here to help! Could you please rephrase your question?",
            'telugu_message': "నేను సహాయం చేయడానికి ఇక్కడ ఉన్నాను! దయచేసి మీ ప్రశ్నను మళ్లీ చెప్పగలరా?",
            'type': 'fallback'
        }