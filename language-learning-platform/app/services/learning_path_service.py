"""
Learning Path Service
Handles enrollment, progress tracking, chapter unlocking, and certificate generation.
"""

from app.models.user import db
from app.models.course import LearningPath
from app.models.chapter import Chapter
from app.models.enrollment import UserEnrollment, ChapterProgress, ActivityProgress, PathCertificate
from app.models.learning_session import LearningSession
from datetime import datetime, timedelta
import secrets
from sqlalchemy import func


class LearningPathService:
    """Service for managing learning path enrollments and progress"""
    
    @staticmethod
    def get_all_paths(difficulty_level=None, category=None, is_active=True):
        """
        Get all available learning paths with optional filters.
        
        Args:
            difficulty_level: Filter by difficulty (beginner, intermediate, advanced)
            category: Filter by category
            is_active: Only show active paths
        
        Returns:
            List of learning paths with metadata
        """
        query = LearningPath.query.filter_by(is_active=is_active, is_adaptive=False)
        
        if difficulty_level:
            query = query.filter_by(difficulty_level=difficulty_level)
        if category:
            query = query.filter_by(category=category)
        
        paths = query.all()
        
        result = []
        for path in paths:
            # Count chapters and activities
            chapters = Chapter.query.filter_by(learning_path_id=path.id, is_active=True).order_by(Chapter.chapter_number).all()
            total_activities = sum(len(chapter.activities or []) for chapter in chapters)
            
            # Get enrollment count
            enrollment_count = UserEnrollment.query.filter_by(learning_path_id=path.id).count()
            
            result.append({
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'category': path.category,
                'difficulty_level': path.difficulty_level,
                'estimated_duration_hours': path.estimated_duration_hours,
                'learning_objectives': path.learning_objectives or [],
                'prerequisites': path.prerequisites or [],
                'total_chapters': len(chapters),
                'total_activities': total_activities,
                'enrollment_count': enrollment_count,
                'success_rate': path.success_rate,
                'average_completion_time': path.average_completion_time,
                'difficulty_rating': path.difficulty_rating,
                'created_at': path.created_at.isoformat() if path.created_at else None
            })
        
        return result
    
    @staticmethod
    def get_path_detail(path_id, user_id=None):
        """
        Get detailed information about a learning path including chapters and activities.
        
        Args:
            path_id: Learning path ID
            user_id: Optional user ID to include enrollment status
        
        Returns:
            Detailed path information with chapters and activities
        """
        path = LearningPath.query.get(path_id)
        if not path:
            return None
        
        # Get chapters ordered by chapter_number
        chapters = Chapter.query.filter_by(learning_path_id=path_id, is_active=True).order_by(Chapter.chapter_number).all()
        
        # Check if user is enrolled
        enrollment = None
        if user_id:
            enrollment = UserEnrollment.query.filter_by(user_id=user_id, learning_path_id=path_id).first()
        
        # Build chapter data with activities
        chapters_data = []
        for chapter in chapters:
            # Get activities for this chapter (assuming they're stored in sessions)
            activities = LearningSession.query.filter_by(chapter_id=chapter.id).order_by(LearningSession.created_at).all()
            
            chapter_info = {
                'id': chapter.id,
                'chapter_number': chapter.chapter_number,
                'title': chapter.title,
                'description': chapter.description,
                'difficulty_level': chapter.difficulty_level,
                'topic': chapter.topic,
                'subtopics': chapter.subtopics or [],
                'estimated_duration_minutes': chapter.estimated_duration_minutes,
                'prerequisites': chapter.prerequisites or [],
                'total_activities': len(activities),
                'activities': []
            }
            
            # Add activities
            for idx, activity in enumerate(activities):
                chapter_info['activities'].append({
                    'id': activity.id,
                    'activity_index': idx,
                    'activity_type': activity.activity_type,
                    'difficulty': activity.difficulty,
                    'estimated_duration': 15  # Default 15 minutes per activity
                })
            
            # If user is enrolled, add progress info
            if enrollment:
                chapter_progress = ChapterProgress.query.filter_by(
                    enrollment_id=enrollment.id,
                    chapter_id=chapter.id
                ).first()
                
                if chapter_progress:
                    chapter_info['progress'] = chapter_progress.to_dict()
                else:
                    chapter_info['progress'] = {
                        'status': 'locked',
                        'is_unlocked': False,
                        'is_completed': False
                    }
            
            chapters_data.append(chapter_info)
        
        return {
            'id': path.id,
            'title': path.title,
            'description': path.description,
            'category': path.category,
            'difficulty_level': path.difficulty_level,
            'estimated_duration_hours': path.estimated_duration_hours,
            'learning_objectives': path.learning_objectives or [],
            'prerequisites': path.prerequisites or [],
            'chapters': chapters_data,
            'total_chapters': len(chapters_data),
            'total_activities': sum(ch['total_activities'] for ch in chapters_data),
            'enrollment': enrollment.to_dict() if enrollment else None,
            'is_enrolled': enrollment is not None
        }
    
    @staticmethod
    def enroll_user(user_id, path_id):
        """
        Enroll a user in a learning path.
        Creates enrollment record and unlocks Chapter 1.
        
        Args:
            user_id: User ID
            path_id: Learning path ID
        
        Returns:
            Enrollment object and success status
        """
        # Check if already enrolled
        existing = UserEnrollment.query.filter_by(user_id=user_id, learning_path_id=path_id).first()
        if existing:
            return {
                'success': False,
                'message': 'User already enrolled in this learning path',
                'message_telugu': 'వినియోగదారుడు ఇప్పటికే ఈ నేర్చుకునే మార్గంలో నమోదు చేసుకున్నారు',
                'enrollment': existing.to_dict()
            }
        
        # Get path and chapters
        path = LearningPath.query.get(path_id)
        if not path:
            return {
                'success': False,
                'message': 'Learning path not found',
                'message_telugu': 'నేర్చుకునే మార్గం కనుగొనబడలేదు'
            }
        
        chapters = Chapter.query.filter_by(learning_path_id=path_id, is_active=True).order_by(Chapter.chapter_number).all()
        if not chapters:
            return {
                'success': False,
                'message': 'No chapters found in this learning path',
                'message_telugu': 'ఈ నేర్చుకునే మార్గంలో అధ్యాయాలు కనుగొనబడలేదు'
            }
        
        # Count total activities
        total_activities = 0
        for chapter in chapters:
            activity_count = LearningSession.query.filter_by(chapter_id=chapter.id).count()
            total_activities += activity_count
        
        # Create enrollment
        enrollment = UserEnrollment(
            user_id=user_id,
            learning_path_id=path_id,
            status='active',
            enrolled_at=datetime.utcnow(),
            current_chapter_id=chapters[0].id,  # Start with first chapter
            total_chapters=len(chapters),
            completed_chapters=0,
            total_activities=total_activities,
            completed_activities=0,
            completion_percentage=0.0
        )
        
        db.session.add(enrollment)
        db.session.flush()  # Get enrollment ID
        
        # Create chapter progress records for all chapters
        for idx, chapter in enumerate(chapters):
            activity_count = LearningSession.query.filter_by(chapter_id=chapter.id).count()
            
            is_first_chapter = idx == 0
            chapter_progress = ChapterProgress(
                enrollment_id=enrollment.id,
                chapter_id=chapter.id,
                status='unlocked' if is_first_chapter else 'locked',
                is_unlocked=is_first_chapter,
                is_completed=False,
                unlocked_at=datetime.utcnow() if is_first_chapter else None,
                total_activities=activity_count,
                completed_activities=0,
                current_activity_index=0
            )
            db.session.add(chapter_progress)
        
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Successfully enrolled in learning path',
            'message_telugu': 'నేర్చుకునే మార్గంలో విజయవంతంగా నమోదు చేసుకున్నారు',
            'enrollment': enrollment.to_dict()
        }
    
    @staticmethod
    def get_user_enrollments(user_id, status=None):
        """
        Get all enrollments for a user.
        
        Args:
            user_id: User ID
            status: Optional status filter (active, paused, completed, dropped)
        
        Returns:
            List of enrollments with path details
        """
        query = UserEnrollment.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        
        enrollments = query.order_by(UserEnrollment.last_accessed.desc()).all()
        
        result = []
        for enrollment in enrollments:
            path = enrollment.learning_path
            enrollment_data = enrollment.to_dict()
            enrollment_data['learning_path'] = {
                'id': path.id,
                'title': path.title,
                'description': path.description,
                'difficulty_level': path.difficulty_level,
                'category': path.category,
                'estimated_duration_hours': path.estimated_duration_hours
            }
            result.append(enrollment_data)
        
        return result
    
    @staticmethod
    def get_path_progress(user_id, path_id):
        """
        Get detailed progress for a user's enrollment in a learning path.
        Includes chapters, activities, and completion status.
        
        Args:
            user_id: User ID
            path_id: Learning path ID
        
        Returns:
            Detailed progress information
        """
        enrollment = UserEnrollment.query.filter_by(user_id=user_id, learning_path_id=path_id).first()
        if not enrollment:
            return {
                'success': False,
                'message': 'User not enrolled in this learning path',
                'message_telugu': 'వినియోగదారుడు ఈ నేర్చుకునే మార్గంలో నమోదు చేసుకోలేదు'
            }
        
        # Get all chapter progress
        chapter_progresses = ChapterProgress.query.filter_by(enrollment_id=enrollment.id).all()
        
        # Build detailed progress data
        chapters_progress = []
        for cp in chapter_progresses:
            chapter = cp.chapter
            
            # Get activity progress
            activity_progresses = ActivityProgress.query.filter_by(chapter_progress_id=cp.id).order_by(ActivityProgress.activity_index).all()
            
            chapters_progress.append({
                'chapter': {
                    'id': chapter.id,
                    'chapter_number': chapter.chapter_number,
                    'title': chapter.title,
                    'description': chapter.description,
                    'topic': chapter.topic
                },
                'progress': cp.to_dict(),
                'activities': [ap.to_dict() for ap in activity_progresses]
            })
        
        # Sort by chapter number
        chapters_progress.sort(key=lambda x: x['chapter']['chapter_number'])
        
        return {
            'success': True,
            'enrollment': enrollment.to_dict(),
            'learning_path': {
                'id': enrollment.learning_path.id,
                'title': enrollment.learning_path.title,
                'description': enrollment.learning_path.description,
                'difficulty_level': enrollment.learning_path.difficulty_level
            },
            'chapters': chapters_progress,
            'overall_progress': {
                'completion_percentage': enrollment.completion_percentage,
                'completed_chapters': enrollment.completed_chapters,
                'total_chapters': enrollment.total_chapters,
                'completed_activities': enrollment.completed_activities,
                'total_activities': enrollment.total_activities,
                'points_earned': enrollment.points_earned,
                'average_score': enrollment.average_score
            }
        }
    
    @staticmethod
    def complete_activity(user_id, path_id, chapter_id, session_id, score, points_earned, time_spent):
        """
        Mark an activity as completed and update progress.
        Unlocks next activity or chapter if applicable.
        
        Args:
            user_id: User ID
            path_id: Learning path ID
            chapter_id: Chapter ID
            session_id: Learning session ID
            score: Activity score (0-100)
            points_earned: Points from gamification
            time_spent: Time spent in minutes
        
        Returns:
            Updated progress and unlock information
        """
        enrollment = UserEnrollment.query.filter_by(user_id=user_id, learning_path_id=path_id).first()
        if not enrollment:
            return {
                'success': False,
                'message': 'User not enrolled in this learning path'
            }
        
        chapter_progress = ChapterProgress.query.filter_by(enrollment_id=enrollment.id, chapter_id=chapter_id).first()
        if not chapter_progress:
            return {
                'success': False,
                'message': 'Chapter progress not found'
            }
        
        # Get or create activity progress
        activity_progress = ActivityProgress.query.filter_by(
            chapter_progress_id=chapter_progress.id,
            learning_session_id=session_id
        ).first()
        
        if not activity_progress:
            # Create new activity progress
            activity_progress = ActivityProgress(
                chapter_progress_id=chapter_progress.id,
                learning_session_id=session_id,
                activity_type=LearningSession.query.get(session_id).activity_type,
                activity_index=chapter_progress.current_activity_index,
                is_unlocked=True,
                unlocked_at=datetime.utcnow()
            )
            db.session.add(activity_progress)
        
        # Mark activity as completed
        activity_progress.status = 'completed'
        activity_progress.is_completed = True
        activity_progress.completed_at = datetime.utcnow()
        activity_progress.score = score
        activity_progress.time_spent_minutes = time_spent
        activity_progress.points_earned = points_earned
        activity_progress.attempts += 1
        
        # Update chapter progress
        if not chapter_progress.started_at:
            chapter_progress.started_at = datetime.utcnow()
        chapter_progress.status = 'in_progress'
        chapter_progress.completed_activities += 1
        chapter_progress.time_spent_minutes += time_spent
        chapter_progress.points_earned += points_earned
        chapter_progress.last_accessed = datetime.utcnow()
        
        # Update average score
        scores = [ap.score for ap in chapter_progress.activity_progress.filter(ActivityProgress.is_completed == True).all()]
        chapter_progress.average_score = sum(scores) / len(scores) if scores else 0.0
        
        # Check if chapter is completed
        chapter_completed = False
        next_chapter_unlocked = None
        
        if chapter_progress.completed_activities >= chapter_progress.total_activities:
            chapter_progress.status = 'completed'
            chapter_progress.is_completed = True
            chapter_progress.completed_at = datetime.utcnow()
            chapter_completed = True
            
            # Update enrollment
            enrollment.completed_chapters += 1
            enrollment.last_accessed = datetime.utcnow()
            
            # Unlock next chapter
            chapter = Chapter.query.get(chapter_id)
            next_chapter = Chapter.query.filter_by(
                learning_path_id=path_id,
                chapter_number=chapter.chapter_number + 1,
                is_active=True
            ).first()
            
            if next_chapter:
                next_chapter_progress = ChapterProgress.query.filter_by(
                    enrollment_id=enrollment.id,
                    chapter_id=next_chapter.id
                ).first()
                
                if next_chapter_progress and not next_chapter_progress.is_unlocked:
                    next_chapter_progress.status = 'unlocked'
                    next_chapter_progress.is_unlocked = True
                    next_chapter_progress.unlocked_at = datetime.utcnow()
                    enrollment.current_chapter_id = next_chapter.id
                    next_chapter_unlocked = {
                        'id': next_chapter.id,
                        'chapter_number': next_chapter.chapter_number,
                        'title': next_chapter.title
                    }
        else:
            # Unlock next activity in current chapter
            chapter_progress.current_activity_index += 1
        
        # Update enrollment progress
        enrollment.completed_activities += 1
        enrollment.total_time_spent_minutes += time_spent
        enrollment.points_earned += points_earned
        enrollment.completion_percentage = (enrollment.completed_activities / enrollment.total_activities * 100) if enrollment.total_activities > 0 else 0
        
        # Update average score
        all_scores = []
        for cp in enrollment.chapter_progress.all():
            for ap in cp.activity_progress.filter(ActivityProgress.is_completed == True).all():
                all_scores.append(ap.score)
        enrollment.average_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Check if path is completed
        path_completed = False
        certificate = None
        
        if enrollment.completed_chapters >= enrollment.total_chapters:
            enrollment.status = 'completed'
            enrollment.completed_at = datetime.utcnow()
            path_completed = True
            
            # Generate certificate
            certificate = LearningPathService._generate_certificate(enrollment)
        
        db.session.commit()
        
        return {
            'success': True,
            'activity_completed': True,
            'chapter_completed': chapter_completed,
            'path_completed': path_completed,
            'next_chapter_unlocked': next_chapter_unlocked,
            'certificate': certificate.to_dict() if certificate else None,
            'progress': {
                'completion_percentage': round(enrollment.completion_percentage, 2),
                'completed_activities': enrollment.completed_activities,
                'total_activities': enrollment.total_activities,
                'completed_chapters': enrollment.completed_chapters,
                'total_chapters': enrollment.total_chapters
            }
        }
    
    @staticmethod
    def _generate_certificate(enrollment):
        """Generate a certificate for path completion"""
        # Check if certificate already exists
        existing = PathCertificate.query.filter_by(enrollment_id=enrollment.id).first()
        if existing:
            return existing
        
        # Calculate completion time
        completion_time = (enrollment.completed_at - enrollment.enrolled_at).days
        
        # Generate unique certificate number
        cert_number = f"CERT-{enrollment.learning_path_id}-{enrollment.user_id}-{secrets.token_hex(4).upper()}"
        
        certificate = PathCertificate(
            enrollment_id=enrollment.id,
            user_id=enrollment.user_id,
            learning_path_id=enrollment.learning_path_id,
            certificate_number=cert_number,
            issued_at=datetime.utcnow(),
            final_score=enrollment.average_score,
            completion_time_days=completion_time,
            total_points_earned=enrollment.points_earned,
            certificate_data={
                'path_title': enrollment.learning_path.title,
                'difficulty_level': enrollment.learning_path.difficulty_level,
                'total_chapters': enrollment.total_chapters,
                'total_activities': enrollment.total_activities
            }
        )
        
        db.session.add(certificate)
        enrollment.certificate_issued = True
        
        return certificate
    
    @staticmethod
    def unenroll_user(user_id, path_id):
        """
        Unenroll a user from a learning path.
        Marks enrollment as dropped but preserves progress data.
        
        Args:
            user_id: User ID
            path_id: Learning path ID
        
        Returns:
            Success status
        """
        enrollment = UserEnrollment.query.filter_by(user_id=user_id, learning_path_id=path_id).first()
        if not enrollment:
            return {
                'success': False,
                'message': 'User not enrolled in this learning path'
            }
        
        enrollment.status = 'dropped'
        enrollment.last_accessed = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Successfully unenrolled from learning path',
            'message_telugu': 'నేర్చుకునే మార్గం నుండి విజయవంతంగా నిష్క్రమించారు'
        }
