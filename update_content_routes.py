"""
Script to update content generation routes with save functionality
"""

# Map of activity types for the POST endpoints that need updating
activity_save_updates = {
    'flashcards': 'flashcard',
    'reading': 'reading',
    'writing': 'writing',
    'listening': 'listening',
    'speaking': 'speaking',
    'real_world': 'real_world',
    'pronunciation': 'pronunciation',
    'sentence_construction': 'sentence_construction',
    'dialogue_completion': 'dialogue_completion',
    'error_correction': 'error_correction',
    'story_sequencing': 'story_sequencing',
    'synonym_antonym': 'synonym_antonym',
    'dictation': 'dictation',
    'translation': 'translation'
}

# Template for adding save logic before return statement
save_template = """        # Save to database
        activity = save_generated_activity(
            activity_data=result,
            user_id=user_id,
            activity_type='{activity_type}',
            learning_path_id=data.get('learning_path_id')
        )
        
        result['activity_id'] = activity.id
        result['saved'] = True
        """

print("Update templates:")
print("="*60)
for endpoint, activity_type in activity_save_updates.items():
    print(f"\nEndpoint: /{endpoint}")
    print(f"Activity type: {activity_type}")
    print(f"Add before 'return jsonify(result), 201':")
    print(save_template.format(activity_type=activity_type))

print("\n" + "="*60)
print("\nGET Endpoints to add at the end of the file:")
print("="*60)

get_endpoints = """

# ============================================
# GET Endpoints - Retrieve Activities
# ============================================

@content_generation_bp.route('/activities', methods=['GET'])
@jwt_required()
def get_activities():
    '''
    Get all generated activities for the current user with filtering and pagination.
    
    GET /api/content-generation/activities
    Query params:
    - activity_type: Filter by type (quiz, flashcard, etc.)
    - difficulty_min: Minimum difficulty (0-1)
    - difficulty_max: Maximum difficulty (0-1)
    - skill_area: Filter by skill area
    - learning_path_id: Filter by learning path
    - limit: Results per page (default 20)
    - offset: Pagination offset (default 0)
    - sort_by: Sort field (created_at, difficulty_level, title)
    - sort_order: asc or desc (default desc)
    '''
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        activity_type = request.args.get('activity_type')
        difficulty_min = request.args.get('difficulty_min', type=float)
        difficulty_max = request.args.get('difficulty_max', type=float)
        skill_area = request.args.get('skill_area')
        learning_path_id = request.args.get('learning_path_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query - filter by activities generated for this user
        query = Activity.query.filter(
            Activity.generation_metadata['generated_for_user'].astext == str(user_id)
        )
        
        # Apply filters
        if activity_type:
            query = query.filter_by(activity_type=activity_type)
        if difficulty_min is not None:
            query = query.filter(Activity.difficulty_level >= difficulty_min)
        if difficulty_max is not None:
            query = query.filter(Activity.difficulty_level <= difficulty_max)
        if skill_area:
            query = query.filter_by(skill_area=skill_area)
        if learning_path_id:
            query = query.filter_by(learning_path_id=learning_path_id)
        
        # Apply sorting
        if hasattr(Activity, sort_by):
            if sort_order == 'asc':
                query = query.order_by(asc(getattr(Activity, sort_by)))
            else:
                query = query.order_by(desc(getattr(Activity, sort_by)))
        else:
            query = query.order_by(desc(Activity.created_at))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination
        activities = query.limit(limit).offset(offset).all()
        
        # Format response
        activities_data = []
        for activity in activities:
            activities_data.append({
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'activity_type': activity.activity_type,
                'difficulty_level': activity.difficulty_level,
                'skill_area': activity.skill_area,
                'concept_focus': activity.concept_focus,
                'estimated_duration_minutes': activity.estimated_duration_minutes,
                'points_reward': activity.points_reward,
                'created_at': activity.created_at.isoformat() if activity.created_at else None,
                'learning_path_id': activity.learning_path_id,
                'is_adaptive': activity.is_adaptive
            })
        
        return jsonify({
            'activities': activities_data,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_generation_bp.route('/activities/<int:activity_id>', methods=['GET'])
@jwt_required()
def get_activity(activity_id):
    '''
    Get a specific activity by ID with full content.
    
    GET /api/content-generation/activities/:id
    '''
    try:
        user_id = get_jwt_identity()
        
        # Get activity and verify it belongs to this user
        activity = Activity.query.get_or_404(activity_id)
        
        # Check if activity was generated for this user
        generated_for_user = activity.generation_metadata.get('generated_for_user') if activity.generation_metadata else None
        if generated_for_user != user_id:
            # Allow access if user has completed this activity (collaborative paths)
            log = UserActivityLog.query.filter_by(
                user_id=user_id,
                activity_id=activity_id
            ).first()
            if not log:
                return jsonify({'error': 'Access denied'}), 403
        
        # Return full activity with content
        return jsonify({
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'activity_type': activity.activity_type,
            'difficulty_level': activity.difficulty_level,
            'skill_area': activity.skill_area,
            'concept_focus': activity.concept_focus,
            'content': activity.content,
            'estimated_duration_minutes': activity.estimated_duration_minutes,
            'points_reward': activity.points_reward,
            'created_at': activity.created_at.isoformat() if activity.created_at else None,
            'learning_path_id': activity.learning_path_id,
            'is_adaptive': activity.is_adaptive,
            'generation_metadata': activity.generation_metadata
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_generation_bp.route('/activities/by-type/<activity_type>', methods=['GET'])
@jwt_required()
def get_activities_by_type(activity_type):
    '''
    Get all activities of a specific type for the current user.
    
    GET /api/content-generation/activities/by-type/:activity_type
    Query params:
    - limit: Results per page (default 20)
    - offset: Pagination offset (default 0)
    '''
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Query activities of this type for this user
        query = Activity.query.filter(
            Activity.activity_type == activity_type,
            Activity.generation_metadata['generated_for_user'].astext == str(user_id)
        ).order_by(desc(Activity.created_at))
        
        total_count = query.count()
        activities = query.limit(limit).offset(offset).all()
        
        activities_data = [{
            'id': a.id,
            'title': a.title,
            'description': a.description,
            'difficulty_level': a.difficulty_level,
            'skill_area': a.skill_area,
            'created_at': a.created_at.isoformat() if a.created_at else None,
            'estimated_duration_minutes': a.estimated_duration_minutes
        } for a in activities]
        
        return jsonify({
            'activity_type': activity_type,
            'activities': activities_data,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_generation_bp.route('/activities/stats', methods=['GET'])
@jwt_required()
def get_activity_stats():
    '''
    Get statistics about user's generated activities.
    
    GET /api/content-generation/activities/stats
    '''
    try:
        user_id = get_jwt_identity()
        
        # Get all activities for this user
        activities = Activity.query.filter(
            Activity.generation_metadata['generated_for_user'].astext == str(user_id)
        ).all()
        
        if not activities:
            return jsonify({
                'total_activities': 0,
                'by_type': {},
                'by_skill_area': {},
                'average_difficulty': 0,
                'total_estimated_time_minutes': 0
            }), 200
        
        # Calculate statistics
        by_type = {}
        by_skill_area = {}
        total_difficulty = 0
        total_time = 0
        
        for activity in activities:
            # Count by type
            activity_type = activity.activity_type
            by_type[activity_type] = by_type.get(activity_type, 0) + 1
            
            # Count by skill area
            if activity.skill_area:
                by_skill_area[activity.skill_area] = by_skill_area.get(activity.skill_area, 0) + 1
            
            # Sum difficulty and time
            if activity.difficulty_level:
                total_difficulty += activity.difficulty_level
            if activity.estimated_duration_minutes:
                total_time += activity.estimated_duration_minutes
        
        return jsonify({
            'total_activities': len(activities),
            'by_type': by_type,
            'by_skill_area': by_skill_area,
            'average_difficulty': total_difficulty / len(activities) if activities else 0,
            'total_estimated_time_minutes': total_time
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_generation_bp.route('/activities/<int:activity_id>/history', methods=['GET'])
@jwt_required()
def get_activity_history(activity_id):
    '''
    Get completion history for a specific activity.
    
    GET /api/content-generation/activities/:id/history
    '''
    try:
        user_id = get_jwt_identity()
        
        # Get all completion logs for this activity by this user
        logs = UserActivityLog.query.filter_by(
            user_id=user_id,
            activity_id=activity_id
        ).order_by(desc(UserActivityLog.completed_at)).all()
        
        history_data = []
        for log in logs:
            history_data.append({
                'id': log.id,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'score': log.score,
                'max_score': log.max_score,
                'time_spent_minutes': log.time_spent_minutes,
                'accuracy_score': log.accuracy_score,
                'attempt_number': log.attempt_number,
                'is_completed': log.is_completed,
                'mastery_level': log.mastery_level
            })
        
        return jsonify({
            'activity_id': activity_id,
            'total_attempts': len(history_data),
            'history': history_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""

print(get_endpoints)
