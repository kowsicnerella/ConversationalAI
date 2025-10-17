"""
Goal Achievement Models
Tracks user goals, goal types, certificates, and level progression
"""

from app.models import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


class GoalType(db.Model):
    """Predefined goal types with templates"""

    __tablename__ = "goal_types"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(100), unique=True, nullable=False
    )  # basic_conversation, workplace_english, fluency
    display_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Material-UI icon name
    difficulty_level = db.Column(db.String(50))  # beginner, intermediate, advanced
    estimated_duration_days = db.Column(db.Integer)  # How long it typically takes

    # Goal criteria template (JSON)
    criteria = db.Column(
        JSON
    )  # {activities_count: 20, vocabulary_count: 100, streak_days: 7, assessment_score: 80}

    # Rewards
    points_reward = db.Column(db.Integer, default=0)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id"))

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user_goals = db.relationship("AchievementGoal", backref="goal_type", lazy="dynamic")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "icon": self.icon,
            "difficulty_level": self.difficulty_level,
            "estimated_duration_days": self.estimated_duration_days,
            "criteria": self.criteria,
            "points_reward": self.points_reward,
            "badge_id": self.badge_id,
        }


class AchievementGoal(db.Model):
    """User's achievement goals (Month 1/3/6 milestones) - different from daily learning goals in personalization.py"""

    __tablename__ = "achievement_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_type_id = db.Column(db.Integer, db.ForeignKey("goal_types.id"))

    # Goal details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_custom = db.Column(db.Boolean, default=False)  # Custom vs template-based

    # Timeline
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Status
    status = db.Column(
        db.String(50), default="active"
    )  # active, completed, abandoned, paused
    progress_percentage = db.Column(db.Float, default=0.0)

    # Goal criteria (can be customized from template)
    criteria = db.Column(JSON)  # Same structure as GoalType.criteria
    current_progress = db.Column(
        JSON
    )  # Tracks actual progress {activities_count: 15, vocabulary_count: 80, ...}

    # Rewards (earned upon completion)
    points_earned = db.Column(db.Integer, default=0)
    badge_earned_id = db.Column(db.Integer, db.ForeignKey("badges.id"))
    certificate_url = db.Column(db.String(500))

    # Sub-milestones
    milestones_completed = db.Column(db.Integer, default=0)
    milestones_total = db.Column(db.Integer, default=0)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "goal_type_id": self.goal_type_id,
            "goal_type": self.goal_type.to_dict() if self.goal_type else None,
            "title": self.title,
            "description": self.description,
            "is_custom": self.is_custom,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "status": self.status,
            "progress_percentage": round(self.progress_percentage, 1),
            "criteria": self.criteria,
            "current_progress": self.current_progress,
            "points_earned": self.points_earned,
            "badge_earned_id": self.badge_earned_id,
            "certificate_url": self.certificate_url,
            "milestones_completed": self.milestones_completed,
            "milestones_total": self.milestones_total,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "days_active": (
                (datetime.utcnow() - self.start_date).days if self.start_date else 0
            ),
            "is_completed": self.status == "completed",
            "is_overdue": (
                self.target_date
                and datetime.utcnow() > self.target_date
                and self.status != "completed"
                if self.target_date
                else False
            ),
        }


class Certificate(db.Model):
    """Certificates awarded for goal completion"""

    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("user_goals.id"))

    # Certificate details
    certificate_type = db.Column(db.String(100))  # completion, achievement, mastery
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Certificate data
    certificate_number = db.Column(db.String(50), unique=True)  # Unique certificate ID
    issued_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Certificate file
    pdf_url = db.Column(db.String(500))  # Path to generated PDF
    thumbnail_url = db.Column(db.String(500))

    # Metadata
    level_achieved = db.Column(db.String(50))  # beginner, intermediate, advanced
    score = db.Column(db.Integer)  # Final assessment score if applicable
    skills_mastered = db.Column(JSON)  # List of skills mastered

    # Sharing
    is_public = db.Column(db.Boolean, default=True)
    share_count = db.Column(db.Integer, default=0)
    verification_url = db.Column(db.String(500))  # Public verification URL

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "goal_id": self.goal_id,
            "certificate_type": self.certificate_type,
            "title": self.title,
            "description": self.description,
            "certificate_number": self.certificate_number,
            "issued_date": self.issued_date.isoformat() if self.issued_date else None,
            "pdf_url": self.pdf_url,
            "thumbnail_url": self.thumbnail_url,
            "level_achieved": self.level_achieved,
            "score": self.score,
            "skills_mastered": self.skills_mastered,
            "is_public": self.is_public,
            "share_count": self.share_count,
            "verification_url": self.verification_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LevelProgression(db.Model):
    """Tracks user level changes and progression history"""

    __tablename__ = "level_progressions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Level info
    from_level = db.Column(db.String(50))  # Previous level
    to_level = db.Column(db.String(50))  # New level
    level_number = db.Column(db.Integer)  # Numeric level (1, 2, 3, ...)

    # Progression trigger
    trigger_type = db.Column(
        db.String(50)
    )  # goal_completion, assessment, points_threshold
    trigger_id = db.Column(
        db.Integer
    )  # ID of the trigger (goal_id, assessment_id, etc.)

    # Requirements met
    requirements_met = db.Column(JSON)  # What requirements were met to level up

    # Timestamp
    achieved_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "from_level": self.from_level,
            "to_level": self.to_level,
            "level_number": self.level_number,
            "trigger_type": self.trigger_type,
            "trigger_id": self.trigger_id,
            "requirements_met": self.requirements_met,
            "achieved_at": self.achieved_at.isoformat() if self.achieved_at else None,
        }
