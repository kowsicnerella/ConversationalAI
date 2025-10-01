from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import (
    db, User, Chapter, UserChapterProgress, PracticeSession, 
    UserNotes, TestAssessment, ChapterDependency, AIConversationContext
)
from app.services.activity_generator_service import ActivityGeneratorService
from app.services.personalization_service import PersonalizationService
from datetime import datetime
import json

chapter_bp = Blueprint('chapters', __name__)
activity_service = ActivityGeneratorService()
personalization_service = PersonalizationService()

@chapter_bp.route('/chapters', methods=['GET'])
@jwt_required()
def get_all_chapters():
    """
    Get all available chapters with user progress information.
    """
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        difficulty = request.args.get('difficulty')
        
        # Get chapters with optional filtering
        query = Chapter.query.filter_by(is_active=True)
        if difficulty:
            query = query.filter_by(difficulty_level=difficulty)
        
        chapters = query.order_by(Chapter.chapter_number).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get user progress for these chapters
        chapter_ids = [ch.id for ch in chapters.items]
        user_progress = {
            prog.chapter_id: prog for prog in 
            UserChapterProgress.query.filter_by(user_id=user_id)
            .filter(UserChapterProgress.chapter_id.in_(chapter_ids)).all()
        }
        
        chapters_data = []
        for chapter in chapters.items:
            progress = user_progress.get(chapter.id)
            
            # Check if chapter is unlocked (prerequisites met)
            is_unlocked = _check_chapter_prerequisites(user_id, chapter.id)
            
            chapters_data.append({
                'id': chapter.id,
                'title': chapter.title,
                'description': chapter.description,
                'chapter_number': chapter.chapter_number,
                'difficulty_level': chapter.difficulty_level,
                'topic': chapter.topic,
                'subtopics': chapter.subtopics,
                'estimated_duration_minutes': chapter.estimated_duration_minutes,
                'required_score_to_pass': chapter.required_score_to_pass,
                'is_unlocked': is_unlocked,
                'user_progress': {
                    'status': progress.status if progress else 'not_started',
                    'best_score': progress.best_score if progress else 0.0,
                    'average_score': progress.average_score if progress else 0.0,
                    'total_attempts': progress.total_attempts if progress else 0,
                    'time_spent_minutes': progress.time_spent_minutes if progress else 0,
                    'last_accessed': progress.last_accessed.isoformat() if progress and progress.last_accessed else None
                }
            })
        
        return jsonify({
            'message': 'Chapters retrieved successfully!',
            'telugu_message': 'అధ్యాయాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'chapters': chapters_data,
            'pagination': {
                'page': chapters.page,
                'per_page': chapters.per_page,
                'total': chapters.total,
                'pages': chapters.pages,
                'has_next': chapters.has_next,
                'has_prev': chapters.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting chapters: {str(e)}")
        return jsonify({
            'error': 'Failed to get chapters',
            'telugu_message': 'అధ్యాయాలు పొందడంలో విఫలం'
        }), 500

@chapter_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_chapters_simple():
    """
    Get all available chapters - simple alias for /chapters endpoint.
    Same functionality as get_all_chapters() but with simpler URL.
    """
    return get_all_chapters()

@chapter_bp.route('/<int:chapter_id>', methods=['GET'])
@jwt_required()
def get_chapter_by_id(chapter_id):
    """
    Get detailed information about a specific chapter - simple URL format.
    Same functionality as get_chapter_details() but with simpler URL.
    """
    return get_chapter_details(chapter_id)

@chapter_bp.route('/<int:chapter_id>/start-practice', methods=['POST'])
@jwt_required()
def start_practice_simple(chapter_id):
    """
    Start a new practice session for a chapter - simple URL format.
    Same functionality as start_practice_session() but with simpler URL.
    """
    return start_practice_session(chapter_id)

@chapter_bp.route('/<int:chapter_id>/progress', methods=['PUT'])
@jwt_required()
def update_progress_simple(chapter_id):
    """
    Update user's progress in a chapter - simple URL format.
    Same functionality as update_chapter_progress() but with simpler URL.
    """
    return update_chapter_progress(chapter_id)

@chapter_bp.route('/progress-graph', methods=['GET'])
@jwt_required()
def get_progress_graph_simple():
    """
    Get the learning path graph showing all chapters and user progress - simple URL format.
    Same functionality as get_progress_graph() but with simpler URL.
    """
    return get_progress_graph()

@chapter_bp.route('/chapters/<int:chapter_id>', methods=['GET'])
@jwt_required()
def get_chapter_details(chapter_id):
    """
    Get detailed information about a specific chapter.
    """
    try:
        user_id = int(get_jwt_identity())
        
        chapter = Chapter.query.get(chapter_id)
        if not chapter or not chapter.is_active:
            return jsonify({
                'error': 'Chapter not found',
                'telugu_message': 'అధ్యాయం కనుగొనబడలేదు'
            }), 404
        
        # Check if chapter is unlocked
        is_unlocked = _check_chapter_prerequisites(user_id, chapter_id)
        if not is_unlocked:
            return jsonify({
                'error': 'Chapter is locked. Complete prerequisites first.',
                'telugu_message': 'అధ్యాయం లాక్ చేయబడింది. మొదట అవసరమైన అధ్యాయాలు పూర్తి చేయండి.'
            }), 403
        
        # Get or create user progress
        progress = UserChapterProgress.query.filter_by(
            user_id=user_id, chapter_id=chapter_id
        ).first()
        
        if not progress:
            progress = UserChapterProgress(
                user_id=user_id,
                chapter_id=chapter_id,
                status='not_started',
                started_at=datetime.utcnow()
            )
            db.session.add(progress)
            db.session.commit()
        
        # Update last accessed time
        progress.last_accessed = datetime.utcnow()
        db.session.commit()
        
        # Get recent practice sessions
        recent_sessions = PracticeSession.query.filter_by(
            user_id=user_id, chapter_id=chapter_id
        ).order_by(PracticeSession.start_time.desc()).limit(5).all()
        
        return jsonify({
            'message': 'Chapter details retrieved successfully!',
            'telugu_message': 'అధ్యాయ వివరాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'chapter': {
                'id': chapter.id,
                'title': chapter.title,
                'description': chapter.description,
                'chapter_number': chapter.chapter_number,
                'difficulty_level': chapter.difficulty_level,
                'topic': chapter.topic,
                'subtopics': chapter.subtopics,
                'estimated_duration_minutes': chapter.estimated_duration_minutes,
                'required_score_to_pass': chapter.required_score_to_pass,
                'content': chapter.content,
                'prerequisites': chapter.prerequisites
            },
            'user_progress': {
                'status': progress.status,
                'best_score': progress.best_score,
                'average_score': progress.average_score,
                'total_attempts': progress.total_attempts,
                'time_spent_minutes': progress.time_spent_minutes,
                'notes': progress.notes
            },
            'recent_sessions': [
                {
                    'id': session.id,
                    'session_type': session.session_type,
                    'start_time': session.start_time.isoformat(),
                    'duration_minutes': session.duration_minutes,
                    'score_percentage': session.score_percentage,
                    'total_questions': session.total_questions,
                    'correct_answers': session.correct_answers
                } for session in recent_sessions
            ]
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting chapter details: {str(e)}")
        return jsonify({
            'error': 'Failed to get chapter details',
            'telugu_message': 'అధ్యాయ వివరాలు పొందడంలో విఫలం'
        }), 500

@chapter_bp.route('/chapters/<int:chapter_id>/start-practice', methods=['POST'])
@jwt_required()
def start_practice_session(chapter_id):
    """
    Start a new practice session for a chapter.
    
    Expected JSON:
    {
        "session_type": "practice",  // practice, test, review
        "difficulty_override": "intermediate"  // optional
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json() or {}
        
        session_type = data.get('session_type', 'practice')
        difficulty_override = data.get('difficulty_override')
        
        chapter = Chapter.query.get(chapter_id)
        if not chapter or not chapter.is_active:
            return jsonify({
                'error': 'Chapter not found',
                'telugu_message': 'అధ్యాయం కనుగొనబడలేదు'
            }), 404
        
        # Check if chapter is unlocked
        is_unlocked = _check_chapter_prerequisites(user_id, chapter_id)
        if not is_unlocked:
            return jsonify({
                'error': 'Chapter is locked',
                'telugu_message': 'అధ్యాయం లాక్ చేయబడింది'
            }), 403
        
        # Check for existing active session
        active_session = PracticeSession.query.filter_by(
            user_id=user_id, chapter_id=chapter_id, is_completed=False
        ).first()
        
        if active_session:
            return jsonify({
                'message': 'Resuming existing practice session',
                'telugu_message': 'ఇప్పటికే ఉన్న అభ్యాస సెషన్‌ను కొనసాగిస్తున్నాం',
                'session': {
                    'id': active_session.id,
                    'session_type': active_session.session_type,
                    'start_time': active_session.start_time.isoformat(),
                    'current_questions': len(active_session.questions_data or []),
                    'score_percentage': active_session.score_percentage
                }
            }), 200
        
        # Create new practice session
        practice_session = PracticeSession(
            user_id=user_id,
            chapter_id=chapter_id,
            session_type=session_type,
            questions_data=[],
            user_responses=[],
            conversation_messages=[]
        )
        
        db.session.add(practice_session)
        db.session.commit()
        
        # Update user progress status
        progress = UserChapterProgress.query.filter_by(
            user_id=user_id, chapter_id=chapter_id
        ).first()
        
        if progress and progress.status == 'not_started':
            progress.status = 'in_progress'
            db.session.commit()
        
        return jsonify({
            'message': 'Practice session started successfully!',
            'telugu_message': 'అభ్యాస సెషన్ విజయవంతంగా ప్రారంభించబడింది!',
            'session': {
                'id': practice_session.id,
                'session_type': practice_session.session_type,
                'start_time': practice_session.start_time.isoformat(),
                'chapter_title': chapter.title,
                'chapter_topic': chapter.topic
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error starting practice session: {str(e)}")
        return jsonify({
            'error': 'Failed to start practice session',
            'telugu_message': 'అభ్యాస సెషన్ ప్రారంభించడంలో విఫలం'
        }), 500

def _check_chapter_prerequisites(user_id, chapter_id):
    """
    Check if user has met prerequisites for a chapter.
    """
    try:
        # Get all prerequisites for this chapter
        dependencies = ChapterDependency.query.filter_by(chapter_id=chapter_id).all()
        
        if not dependencies:
            return True  # No prerequisites
        
        # Check each prerequisite
        for dep in dependencies:
            if dep.is_strict:
                # Must have completed prerequisite chapter
                progress = UserChapterProgress.query.filter_by(
                    user_id=user_id, 
                    chapter_id=dep.prerequisite_chapter_id
                ).first()
                
                if not progress or progress.status not in ['completed', 'mastered']:
                    return False
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error checking prerequisites: {str(e)}")
        return False

@chapter_bp.route('/chapters/<int:chapter_id>/progress', methods=['PUT'])
@jwt_required()
def update_chapter_progress(chapter_id):
    """
    Update user's progress in a chapter.
    
    Expected JSON:
    {
        "notes": "My notes for this chapter",
        "status": "completed"  // optional
    }
    """
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        progress = UserChapterProgress.query.filter_by(
            user_id=user_id, chapter_id=chapter_id
        ).first()
        
        if not progress:
            return jsonify({
                'error': 'Progress record not found',
                'telugu_message': 'పురోగతి రికార్డ్ కనుగొనబడలేదు'
            }), 404
        
        # Update notes if provided
        if 'notes' in data:
            progress.notes = data['notes']
        
        # Update status if provided
        if 'status' in data and data['status'] in ['not_started', 'in_progress', 'completed', 'mastered']:
            progress.status = data['status']
            if data['status'] == 'completed':
                progress.completed_at = datetime.utcnow()
        
        progress.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated successfully!',
            'telugu_message': 'పురోగతి విజయవంతంగా నవీకరించబడింది!',
            'progress': {
                'status': progress.status,
                'notes': progress.notes,
                'last_accessed': progress.last_accessed.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating progress: {str(e)}")
        return jsonify({
            'error': 'Failed to update progress',
            'telugu_message': 'పురోగతిని నవీకరించడంలో విఫలం'
        }), 500

@chapter_bp.route('/chapters/progress-graph', methods=['GET'])
@jwt_required()
def get_progress_graph():
    """
    Get the learning path graph showing all chapters and user progress.
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Get all chapters
        chapters = Chapter.query.filter_by(is_active=True).order_by(Chapter.chapter_number).all()
        
        # Get user progress for all chapters
        user_progress = {
            prog.chapter_id: prog for prog in 
            UserChapterProgress.query.filter_by(user_id=user_id).all()
        }
        
        # Get chapter dependencies
        dependencies = ChapterDependency.query.all()
        
        # Build the graph structure
        graph_nodes = []
        graph_edges = []
        
        for chapter in chapters:
            progress = user_progress.get(chapter.id)
            is_unlocked = _check_chapter_prerequisites(user_id, chapter.id)
            
            node = {
                'id': chapter.id,
                'title': chapter.title,
                'chapter_number': chapter.chapter_number,
                'difficulty_level': chapter.difficulty_level,
                'topic': chapter.topic,
                'is_unlocked': is_unlocked,
                'status': progress.status if progress else 'not_started',
                'best_score': progress.best_score if progress else 0.0,
                'completion_percentage': _calculate_completion_percentage(progress)
            }
            graph_nodes.append(node)
        
        for dep in dependencies:
            edge = {
                'from': dep.prerequisite_chapter_id,
                'to': dep.chapter_id,
                'is_strict': dep.is_strict
            }
            graph_edges.append(edge)
        
        return jsonify({
            'message': 'Progress graph retrieved successfully!',
            'telugu_message': 'పురోగతి గ్రాఫ్ విజయవంతంగా తీసుకోబడింది!',
            'graph': {
                'nodes': graph_nodes,
                'edges': graph_edges
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting progress graph: {str(e)}")
        return jsonify({
            'error': 'Failed to get progress graph',
            'telugu_message': 'పురోగతి గ్రాఫ్ పొందడంలో విఫలం'
        }), 500

def _calculate_completion_percentage(progress):
    """
    Calculate completion percentage based on user progress.
    """
    if not progress:
        return 0.0
    
    if progress.status == 'not_started':
        return 0.0
    elif progress.status == 'in_progress':
        return min(50.0, progress.best_score * 100)
    elif progress.status == 'completed':
        return max(70.0, progress.best_score * 100)
    elif progress.status == 'mastered':
        return 100.0
    
    return progress.best_score * 100

# ===== ADVANCED CHAPTER MANAGEMENT ENDPOINTS =====

@chapter_bp.route('/chapters/create-custom', methods=['POST'])
@jwt_required()
def create_custom_chapter():
    """Create a custom chapter based on user specifications"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Chapter specifications required',
                'telugu_message': 'అధ్యాయ వివరణలు అవసరం'
            }), 400
        
        title = data.get('title')
        topic = data.get('topic')
        difficulty_level = data.get('difficulty_level', 'beginner')
        subtopics = data.get('subtopics', [])
        
        if not title or not topic:
            return jsonify({
                'error': 'Title and topic are required',
                'telugu_message': 'శీర్షిక మరియు అంశం అవసరం'
            }), 400
        
        # Generate custom chapter content using AI
        generation_prompt = f"""
        Create a comprehensive English learning chapter for Telugu speakers.
        
        Specifications:
        - Title: {title}
        - Topic: {topic}
        - Difficulty Level: {difficulty_level}
        - Subtopics: {', '.join(subtopics)}
        
        Generate a structured chapter with:
        1. Detailed description
        2. Learning objectives
        3. Content breakdown
        4. Practice exercises outline
        5. Assessment criteria
        
        Return in JSON format:
        ```json
        {{
            "description": "Comprehensive chapter covering...",
            "learning_objectives": ["Objective 1", "Objective 2"],
            "content_sections": [
                {{
                    "section_title": "Introduction to Topic",
                    "content": "Detailed explanation...",
                    "telugu_notes": "తెలుగు వివరణ..."
                }}
            ],
            "practice_types": ["reading", "writing", "speaking", "listening"],
            "assessment_criteria": {{
                "vocabulary_mastery": 30,
                "grammar_understanding": 25,
                "practical_application": 45
            }},
            "estimated_duration_minutes": 45
        }}
        ```
        """
        
        response = activity_service.model.generate_content(generation_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        chapter_content = _extract_json_from_response(response.text)
        
        # Create new chapter
        new_chapter = Chapter(
            title=title,
            description=chapter_content.get('description', f'Custom chapter on {topic}'),
            chapter_number=9999,  # Custom chapters get high numbers
            difficulty_level=difficulty_level,
            topic=topic,
            subtopics=subtopics,
            estimated_duration_minutes=chapter_content.get('estimated_duration_minutes', 45),
            required_score_to_pass=0.7,
            is_active=True,
            is_custom=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_chapter)
        db.session.commit()
        
        return jsonify({
            'message': 'Custom chapter created successfully!',
            'telugu_message': 'అనుకూల అధ్యాయం విజయవంతంగా సృష్టించబడింది!',
            'chapter': {
                'id': new_chapter.id,
                'title': new_chapter.title,
                'description': new_chapter.description,
                'difficulty_level': new_chapter.difficulty_level,
                'topic': new_chapter.topic,
                'subtopics': new_chapter.subtopics
            },
            'generated_content': chapter_content
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create custom chapter',
            'telugu_message': 'అనుకూల అధ్యాయం సృష్టించడంలో విఫలం',
            'details': str(e)
        }), 500

@chapter_bp.route('/chapters/<int:chapter_id>/adaptive-content', methods=['GET'])
@jwt_required()
def get_adaptive_chapter_content(chapter_id):
    """Get chapter content adapted to user's current skill level"""
    try:
        user_id = int(get_jwt_identity())
        
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({
                'error': 'Chapter not found',
                'telugu_message': 'అధ్యాయం కనుగొనబడలేదు'
            }), 404
        
        # Get user's progress and performance data
        user_progress = UserChapterProgress.query.filter_by(
            user_id=user_id, chapter_id=chapter_id
        ).first()
        
        # Get user's overall performance
        user = User.query.get(user_id)
        
        # Generate adaptive content based on user performance
        adaptation_prompt = f"""
        Adapt chapter content for a Telugu speaker learning English based on their performance.
        
        Chapter: {chapter.title}
        Topic: {chapter.topic}
        Difficulty: {chapter.difficulty_level}
        
        User Performance Data:
        - Best Score: {user_progress.best_score if user_progress else 0.0}
        - Total Attempts: {user_progress.total_attempts if user_progress else 0}
        - Status: {user_progress.status if user_progress else 'not_started'}
        
        Adapt the content by:
        1. Adjusting complexity based on performance
        2. Adding reinforcement for weak areas
        3. Providing appropriate challenge level
        4. Including Telugu explanations as needed
        
        Return adapted content in JSON format:
        ```json
        {{
            "adapted_content": {{
                "introduction": {{
                    "english": "Welcome to this chapter...",
                    "telugu": "ఈ అధ్యాయానికి స్వాగతం...",
                    "difficulty_note": "Content adjusted for your level"
                }},
                "main_lessons": [
                    {{
                        "title": "Lesson 1",
                        "content": "Adapted lesson content...",
                        "exercises": ["Exercise 1", "Exercise 2"],
                        "telugu_support": "Additional Telugu explanations..."
                    }}
                ],
                "practice_recommendations": [
                    "Focus on vocabulary building",
                    "Practice sentence formation"
                ]
            }},
            "adaptation_notes": {{
                "level_adjustment": "Content simplified for better understanding",
                "focus_areas": ["vocabulary", "basic_grammar"],
                "estimated_time": 30
            }}
        }}
        ```
        """
        
        response = activity_service.model.generate_content(adaptation_prompt)
        from app.services.activity_generator_service import _extract_json_from_response
        adaptive_content = _extract_json_from_response(response.text)
        
        return jsonify({
            'message': 'Adaptive chapter content generated successfully!',
            'telugu_message': 'అనుకూల అధ్యాయ కంటెంట్ విజయవంతంగా రూపొందించబడింది!',
            'chapter_info': {
                'id': chapter.id,
                'title': chapter.title,
                'topic': chapter.topic,
                'difficulty_level': chapter.difficulty_level
            },
            'user_performance': {
                'best_score': user_progress.best_score if user_progress else 0.0,
                'status': user_progress.status if user_progress else 'not_started',
                'total_attempts': user_progress.total_attempts if user_progress else 0
            },
            'adaptive_content': adaptive_content
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate adaptive content',
            'telugu_message': 'అనుకూల కంటెంట్ రూపొందించడంలో విఫలం',
            'details': str(e)
        }), 500

@chapter_bp.route('/chapters/learning-path/<int:learning_path_id>', methods=['GET'])
@jwt_required()
def get_chapters_by_learning_path(learning_path_id):
    """Get all chapters associated with a specific learning path"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get chapters that belong to this learning path (via activities)
        from app.models import Activity, LearningPath
        
        learning_path = LearningPath.query.get(learning_path_id)
        if not learning_path:
            return jsonify({
                'error': 'Learning path not found',
                'telugu_message': 'అభ్యాస మార్గం కనుగొనబడలేదు'
            }), 404
        
        # Get activities in this learning path
        activities = Activity.query.filter_by(learning_path_id=learning_path_id).all()
        
        # For now, create a mapping based on activity types and topics
        # In a more advanced system, you'd have direct chapter-learning_path relationships
        related_chapters = Chapter.query.filter(
            Chapter.topic.in_([activity.title.split()[0] for activity in activities if activity.title])
        ).filter_by(is_active=True).all()
        
        # Get user progress for these chapters
        chapter_ids = [ch.id for ch in related_chapters]
        user_progress = {
            prog.chapter_id: prog for prog in 
            UserChapterProgress.query.filter_by(user_id=user_id)
            .filter(UserChapterProgress.chapter_id.in_(chapter_ids)).all()
        }
        
        chapters_data = []
        for chapter in related_chapters:
            progress = user_progress.get(chapter.id)
            is_unlocked = _check_chapter_prerequisites(user_id, chapter.id)
            
            chapters_data.append({
                'id': chapter.id,
                'title': chapter.title,
                'description': chapter.description,
                'chapter_number': chapter.chapter_number,
                'difficulty_level': chapter.difficulty_level,
                'topic': chapter.topic,
                'estimated_duration_minutes': chapter.estimated_duration_minutes,
                'is_unlocked': is_unlocked,
                'user_progress': {
                    'status': progress.status if progress else 'not_started',
                    'best_score': progress.best_score if progress else 0.0,
                    'total_attempts': progress.total_attempts if progress else 0,
                    'completion_percentage': _calculate_completion_percentage(progress)
                }
            })
        
        return jsonify({
            'message': 'Learning path chapters retrieved successfully!',
            'telugu_message': 'అభ్యాస మార్గ అధ్యాయాలు విజయవంతంగా తీసుకోబడ్డాయి!',
            'learning_path': {
                'id': learning_path.id,
                'title': learning_path.title,
                'category': learning_path.category,
                'difficulty_level': learning_path.difficulty_level
            },
            'chapters': chapters_data,
            'summary': {
                'total_chapters': len(chapters_data),
                'completed_chapters': len([ch for ch in chapters_data if ch['user_progress']['status'] == 'completed']),
                'unlocked_chapters': len([ch for ch in chapters_data if ch['is_unlocked']])
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get learning path chapters',
            'telugu_message': 'అభ్యాస మార్గ అధ్యాయాలు పొందడంలో విఫలం',
            'details': str(e)
        }), 500

@chapter_bp.route('/chapters/unlock-next', methods=['POST'])
@jwt_required()
def unlock_next_chapter():
    """Unlock the next chapter based on user's current progress"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        current_chapter_id = data.get('current_chapter_id') if data else None
        
        # Get user's current progress
        user_progress = UserChapterProgress.query.filter_by(user_id=user_id).all()
        completed_chapters = [p.chapter_id for p in user_progress if p.status in ['completed', 'mastered']]
        
        # Find next unlockable chapter
        if current_chapter_id:
            current_chapter = Chapter.query.get(current_chapter_id)
            if not current_chapter:
                return jsonify({
                    'error': 'Current chapter not found',
                    'telugu_message': 'ప్రస్తుత అధ్యాయం కనుగొనబడలేదు'
                }), 404
            
            # Find next chapter in sequence
            next_chapter = Chapter.query.filter(
                Chapter.chapter_number > current_chapter.chapter_number,
                Chapter.difficulty_level == current_chapter.difficulty_level,
                Chapter.is_active == True
            ).order_by(Chapter.chapter_number).first()
        else:
            # Find the first uncompleted chapter
            next_chapter = Chapter.query.filter(
                ~Chapter.id.in_(completed_chapters),
                Chapter.is_active == True
            ).order_by(Chapter.chapter_number).first()
        
        if not next_chapter:
            return jsonify({
                'message': 'All chapters completed! Excellent progress!',
                'telugu_message': 'అన్ని అధ్యాయాలు పూర్తయ్యాయి! అద్భుతమైన పురోగతి!',
                'next_chapter': None
            }), 200
        
        # Check if prerequisites are met
        is_unlocked = _check_chapter_prerequisites(user_id, next_chapter.id)
        
        unlock_status = {
            'chapter': {
                'id': next_chapter.id,
                'title': next_chapter.title,
                'description': next_chapter.description,
                'chapter_number': next_chapter.chapter_number,
                'difficulty_level': next_chapter.difficulty_level,
                'topic': next_chapter.topic,
                'estimated_duration_minutes': next_chapter.estimated_duration_minutes
            },
            'is_unlocked': is_unlocked,
            'unlock_message': 'Chapter unlocked! Ready to start.' if is_unlocked else 'Complete prerequisites to unlock.',
            'telugu_unlock_message': 'అధ్యాయం అన్‌లాక్ చేయబడింది! ప్రారంభించడానికి సిద్ధం.' if is_unlocked else 'అన్‌లాక్ చేయడానికి ముందుగా అవసరమైన అధ్యాయాలు పూర్తి చేయండి.'
        }
        
        if is_unlocked:
            # Create initial progress entry
            existing_progress = UserChapterProgress.query.filter_by(
                user_id=user_id, chapter_id=next_chapter.id
            ).first()
            
            if not existing_progress:
                new_progress = UserChapterProgress(
                    user_id=user_id,
                    chapter_id=next_chapter.id,
                    status='not_started',
                    best_score=0.0,
                    average_score=0.0,
                    total_attempts=0,
                    time_spent_minutes=0,
                    last_accessed=datetime.utcnow()
                )
                db.session.add(new_progress)
                db.session.commit()
        
        return jsonify({
            'message': 'Next chapter status retrieved successfully!',
            'telugu_message': 'తదుపరి అధ్యాయ స్థితి విజయవంతంగా తీసుకోబడింది!',
            'unlock_status': unlock_status
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to unlock next chapter',
            'telugu_message': 'తదుపరి అధ్యాయం అన్‌లాక్ చేయడంలో విఫలం',
            'details': str(e)
        }), 500