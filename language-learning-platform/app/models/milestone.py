from app.models import db
from datetime import datetime


class Milestone(db.Model):
    """Model for tracking user milestones and achievements in their learning journey"""

    __tablename__ = "milestones"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    milestone_type = db.Column(db.String(50), nullable=False)
    # Types: 'first_assessment', 'first_path_started', 'mastery_25', 'mastery_50',
    #        'mastery_75', 'mastery_100', 'perfect_lesson', 'week_streak', 'month_streak'

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    telugu_title = db.Column(db.String(200))
    telugu_description = db.Column(db.Text)

    achieved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    milestone_data = db.Column(db.JSON)  # Additional data about the achievement

    # Display properties
    icon = db.Column(db.String(50))  # Icon name for UI
    color = db.Column(db.String(20))  # Color scheme for display
    points_awarded = db.Column(db.Integer, default=0)

    # Relationship
    user = db.relationship(
        "User",
        backref=db.backref("milestones", lazy="dynamic", cascade="all, delete-orphan"),
    )

    def to_dict(self):
        """Convert milestone to dictionary for API responses"""
        return {
            "id": self.id,
            "milestone_type": self.milestone_type,
            "title": self.title,
            "description": self.description,
            "telugu_title": self.telugu_title,
            "telugu_description": self.telugu_description,
            "achieved_at": self.achieved_at.isoformat() if self.achieved_at else None,
            "milestone_data": self.milestone_data,
            "icon": self.icon,
            "color": self.color,
            "points_awarded": self.points_awarded,
        }

    def __repr__(self):
        return f"<Milestone {self.title} for User {self.user_id}>"


class LessonReview(db.Model):
    """Model for storing AI-generated lesson reviews"""

    __tablename__ = "lesson_reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    activity_log_id = db.Column(
        db.Integer, db.ForeignKey("user_activity_logs.id"), nullable=False
    )
    learning_path_id = db.Column(db.Integer, db.ForeignKey("learning_paths.id"))

    # Review content
    performance_score = db.Column(db.Float)  # Overall performance (0-100)
    strengths = db.Column(db.JSON)  # List of identified strengths
    weaknesses = db.Column(db.JSON)  # List of areas needing improvement
    feedback_english = db.Column(db.Text)  # Detailed feedback in English
    feedback_telugu = db.Column(db.Text)  # Detailed feedback in Telugu

    # AI recommendations
    next_lesson_recommendation = db.Column(db.JSON)  # What should user do next
    difficulty_adjustment = db.Column(db.String(20))  # increase, decrease, maintain
    focus_areas = db.Column(db.JSON)  # Specific skills to focus on

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ai_model_used = db.Column(db.String(50), default="gemini-2.0-flash-exp")

    # Relationships
    user = db.relationship("User", backref=db.backref("lesson_reviews", lazy="dynamic"))
    activity_log = db.relationship(
        "UserActivityLog", backref=db.backref("review", uselist=False)
    )

    def to_dict(self):
        """Convert lesson review to dictionary for API responses"""
        return {
            "id": self.id,
            "performance_score": self.performance_score,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "feedback_english": self.feedback_english,
            "feedback_telugu": self.feedback_telugu,
            "next_lesson_recommendation": self.next_lesson_recommendation,
            "difficulty_adjustment": self.difficulty_adjustment,
            "focus_areas": self.focus_areas,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "ai_model_used": self.ai_model_used,
        }

    def __repr__(self):
        return (
            f"<LessonReview for User {self.user_id} - Activity {self.activity_log_id}>"
        )
