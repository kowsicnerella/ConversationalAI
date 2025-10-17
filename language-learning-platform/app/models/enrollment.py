"""
User Enrollment Models for Learning Paths
Tracks user enrollment, progress, and completion of structured learning paths with chapters.
"""

from .user import db
from datetime import datetime
from sqlalchemy import UniqueConstraint


class UserEnrollment(db.Model):
    """
    Tracks user enrollment in learning paths with detailed progress tracking.
    One enrollment per user per learning path.
    """

    __tablename__ = "user_enrollments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    learning_path_id = db.Column(
        db.Integer, db.ForeignKey("learning_paths.id"), nullable=False
    )

    # Enrollment status
    status = db.Column(
        db.String(20), default="active"
    )  # active, paused, completed, dropped
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

    # Progress tracking
    current_chapter_id = db.Column(
        db.Integer, db.ForeignKey("chapters.id")
    )  # Current chapter user is on
    total_chapters = db.Column(db.Integer, default=0)
    completed_chapters = db.Column(db.Integer, default=0)
    completion_percentage = db.Column(
        db.Float, default=0.0
    )  # Overall path completion %

    # Activity tracking
    total_activities = db.Column(db.Integer, default=0)
    completed_activities = db.Column(db.Integer, default=0)

    # Time tracking
    total_time_spent_minutes = db.Column(db.Integer, default=0)
    estimated_time_remaining_minutes = db.Column(db.Integer)

    # Performance metrics
    average_score = db.Column(
        db.Float, default=0.0
    )  # Average score across all completed activities
    quiz_accuracy = db.Column(db.Float, default=0.0)
    writing_score = db.Column(db.Float, default=0.0)

    # Gamification integration
    points_earned = db.Column(db.Integer, default=0)  # Total points earned in this path
    badges_earned = db.Column(
        db.JSON, default=list
    )  # List of badge IDs earned in this path
    certificate_issued = db.Column(db.Boolean, default=False)
    certificate_url = db.Column(db.String(500))  # URL to certificate if completed

    # Adaptive learning
    difficulty_adjustments = db.Column(
        db.JSON, default=list
    )  # History of difficulty changes
    recommended_next_activities = db.Column(db.JSON, default=list)  # AI recommendations

    # Metadata
    enrollment_metadata = db.Column(db.JSON)  # Additional enrollment data
    notes = db.Column(db.Text)  # User notes about the path

    # Unique constraint: one enrollment per user per path
    __table_args__ = (
        UniqueConstraint(
            "user_id", "learning_path_id", name="unique_user_learning_path"
        ),
    )

    # Relationships
    user = db.relationship("User", backref="enrollments")
    learning_path = db.relationship("LearningPath", backref="enrollments")
    current_chapter = db.relationship("Chapter", foreign_keys=[current_chapter_id])
    chapter_progress = db.relationship(
        "ChapterProgress",
        backref="enrollment",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<UserEnrollment User:{self.user_id} Path:{self.learning_path_id} Status:{self.status}>"

    def to_dict(self):
        """Convert enrollment to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "learning_path_id": self.learning_path_id,
            "status": self.status,
            "enrolled_at": self.enrolled_at.isoformat() if self.enrolled_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "current_chapter_id": self.current_chapter_id,
            "total_chapters": self.total_chapters,
            "completed_chapters": self.completed_chapters,
            "completion_percentage": round(self.completion_percentage, 2),
            "total_activities": self.total_activities,
            "completed_activities": self.completed_activities,
            "total_time_spent_minutes": self.total_time_spent_minutes,
            "average_score": (
                round(self.average_score, 2) if self.average_score else 0.0
            ),
            "points_earned": self.points_earned,
            "certificate_issued": self.certificate_issued,
            "certificate_url": self.certificate_url,
        }


class ChapterProgress(db.Model):
    """
    Tracks user progress through individual chapters within an enrolled learning path.
    """

    __tablename__ = "chapter_progress"

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(
        db.Integer, db.ForeignKey("user_enrollments.id"), nullable=False
    )
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"), nullable=False)

    # Progress status
    status = db.Column(
        db.String(20), default="locked"
    )  # locked, unlocked, in_progress, completed
    is_unlocked = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)

    # Timestamps
    unlocked_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime)

    # Activity tracking
    total_activities = db.Column(db.Integer, default=0)
    completed_activities = db.Column(db.Integer, default=0)
    current_activity_index = db.Column(
        db.Integer, default=0
    )  # Index of current activity

    # Performance
    average_score = db.Column(db.Float, default=0.0)
    time_spent_minutes = db.Column(db.Integer, default=0)

    # Gamification
    points_earned = db.Column(db.Integer, default=0)

    # Unique constraint: one progress record per enrollment per chapter
    __table_args__ = (
        UniqueConstraint(
            "enrollment_id", "chapter_id", name="unique_enrollment_chapter"
        ),
    )

    # Relationships
    chapter = db.relationship("Chapter", backref="user_progress_records")
    activity_progress = db.relationship(
        "ActivityProgress",
        backref="chapter_progress",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<ChapterProgress Enrollment:{self.enrollment_id} Chapter:{self.chapter_id} Status:{self.status}>"

    def to_dict(self):
        """Convert chapter progress to dictionary"""
        return {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "status": self.status,
            "is_unlocked": self.is_unlocked,
            "is_completed": self.is_completed,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "total_activities": self.total_activities,
            "completed_activities": self.completed_activities,
            "current_activity_index": self.current_activity_index,
            "average_score": (
                round(self.average_score, 2) if self.average_score else 0.0
            ),
            "time_spent_minutes": self.time_spent_minutes,
            "points_earned": self.points_earned,
        }


class ActivityProgress(db.Model):
    """
    Tracks user progress through individual activities within a chapter.
    """

    __tablename__ = "activity_progress"

    id = db.Column(db.Integer, primary_key=True)
    chapter_progress_id = db.Column(
        db.Integer, db.ForeignKey("chapter_progress.id"), nullable=False
    )
    learning_session_id = db.Column(
        db.Integer, db.ForeignKey("learning_sessions.id"), nullable=False
    )

    # Activity details
    activity_type = db.Column(
        db.String(50), nullable=False
    )  # quiz, flashcard, reading, writing, roleplay
    activity_index = db.Column(
        db.Integer, nullable=False
    )  # Order within chapter (0, 1, 2, ...)

    # Progress status
    status = db.Column(
        db.String(20), default="locked"
    )  # locked, unlocked, in_progress, completed
    is_unlocked = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)

    # Timestamps
    unlocked_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Performance
    score = db.Column(db.Float, default=0.0)
    time_spent_minutes = db.Column(db.Integer, default=0)
    attempts = db.Column(db.Integer, default=0)

    # Gamification
    points_earned = db.Column(db.Integer, default=0)

    # Unique constraint: one progress record per chapter_progress per session
    __table_args__ = (
        UniqueConstraint(
            "chapter_progress_id", "learning_session_id", name="unique_chapter_activity"
        ),
    )

    # Relationships
    learning_session = db.relationship(
        "LearningSession", backref="activity_progress_record"
    )

    def __repr__(self):
        return f"<ActivityProgress ChapterProgress:{self.chapter_progress_id} Session:{self.learning_session_id} Status:{self.status}>"

    def to_dict(self):
        """Convert activity progress to dictionary"""
        return {
            "id": self.id,
            "learning_session_id": self.learning_session_id,
            "activity_type": self.activity_type,
            "activity_index": self.activity_index,
            "status": self.status,
            "is_unlocked": self.is_unlocked,
            "is_completed": self.is_completed,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "score": round(self.score, 2) if self.score else 0.0,
            "time_spent_minutes": self.time_spent_minutes,
            "attempts": self.attempts,
            "points_earned": self.points_earned,
        }


class PathCertificate(db.Model):
    """
    Certificates awarded upon learning path completion.
    """

    __tablename__ = "path_certificates"

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(
        db.Integer, db.ForeignKey("user_enrollments.id"), nullable=False, unique=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    learning_path_id = db.Column(
        db.Integer, db.ForeignKey("learning_paths.id"), nullable=False
    )

    # Certificate details
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Performance summary
    final_score = db.Column(db.Float)  # Average score across all activities
    completion_time_days = db.Column(db.Integer)  # Days taken to complete
    total_points_earned = db.Column(db.Integer)

    # Certificate file
    certificate_url = db.Column(db.String(500))  # URL to PDF certificate
    certificate_data = db.Column(db.JSON)  # Certificate metadata

    # Relationships
    enrollment = db.relationship("UserEnrollment", backref="certificate")
    user = db.relationship("User", backref="path_certificates")
    learning_path = db.relationship("LearningPath", backref="certificates")

    def __repr__(self):
        return f"<PathCertificate {self.certificate_number} User:{self.user_id} Path:{self.learning_path_id}>"

    def to_dict(self):
        """Convert certificate to dictionary"""
        return {
            "id": self.id,
            "certificate_number": self.certificate_number,
            "issued_at": self.issued_at.isoformat(),
            "final_score": round(self.final_score, 2) if self.final_score else 0.0,
            "completion_time_days": self.completion_time_days,
            "total_points_earned": self.total_points_earned,
            "certificate_url": self.certificate_url,
        }
