"""
Enhanced Gamification Models for AI-Powered Learning Platform (Phase 9)
Includes: Daily Challenges, Achievements, Leaderboards, Streaks, Milestones, Social Features

Note: Uses 'Phase9' prefix for model names to avoid conflicts with existing models
"""

from datetime import datetime, timedelta
from app.models.user import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Index, UniqueConstraint


class GamificationChallenge(db.Model):
    """AI-generated daily challenges personalized to user level"""
    __tablename__ = "gamification_challenges"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    
    # Challenge Details (AI-generated)
    challenge_type = db.Column(db.String(50), nullable=False)  # vocabulary, grammar, reading, writing, speaking, listening, mixed
    difficulty_level = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Challenge Requirements
    target_metric = db.Column(db.String(100), nullable=False)  # e.g., "complete_5_activities", "earn_100_points", "study_30_minutes"
    target_value = db.Column(db.Integer, nullable=False)
    current_progress = db.Column(db.Integer, default=0)
    
    # Rewards
    points_reward = db.Column(db.Integer, nullable=False)
    bonus_multiplier = db.Column(db.Float, default=1.0)  # Streak bonus multiplier
    badge_reward = db.Column(db.String(100))  # Optional special badge
    
    # Status
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    is_streak_bonus = db.Column(db.Boolean, default=False)  # Extra challenge for maintaining streak
    
    # Personalization Context
    skill_focus = db.Column(JSON)  # Skills this challenge focuses on
    weak_areas_targeted = db.Column(JSON)  # Weak areas this addresses
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)  # Challenge expires at end of day
    
    # Relationships
    user = db.relationship('User', backref='daily_challenges')
    
    # Indexes
    __table_args__ = (
        Index('idx_user_challenge_date', 'user_id', 'challenge_date'),
        Index('idx_challenge_active', 'user_id', 'is_completed', 'expires_at'),
        UniqueConstraint('user_id', 'challenge_date', 'challenge_type', name='uq_user_daily_challenge'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'challenge_date': self.challenge_date.isoformat() if self.challenge_date else None,
            'challenge_type': self.challenge_type,
            'difficulty_level': self.difficulty_level,
            'title': self.title,
            'description': self.description,
            'target_metric': self.target_metric,
            'target_value': self.target_value,
            'current_progress': self.current_progress,
            'progress_percentage': round((self.current_progress / self.target_value * 100), 1) if self.target_value > 0 else 0,
            'points_reward': self.points_reward,
            'bonus_multiplier': self.bonus_multiplier,
            'badge_reward': self.badge_reward,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_streak_bonus': self.is_streak_bonus,
            'skill_focus': self.skill_focus,
            'weak_areas_targeted': self.weak_areas_targeted,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'time_remaining_hours': self._calculate_time_remaining(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def _calculate_time_remaining(self):
        """Calculate hours remaining until expiry"""
        if self.expires_at and datetime.utcnow() < self.expires_at:
            delta = self.expires_at - datetime.utcnow()
            return round(delta.total_seconds() / 3600, 1)
        return 0
    
    def update_progress(self, progress_value):
        """Update challenge progress"""
        self.current_progress = min(progress_value, self.target_value)
        if self.current_progress >= self.target_value and not self.is_completed:
            self.complete_challenge()
    
    def complete_challenge(self):
        """Mark challenge as completed"""
        self.is_completed = True
        self.completed_at = datetime.utcnow()


class GamificationAchievement(db.Model):
    """Achievement/Badge definitions (50+ achievements)"""
    __tablename__ = "gamification_achievements"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Achievement Identity
    achievement_key = db.Column(db.String(100), unique=True, nullable=False)  # unique identifier
    category = db.Column(db.String(50), nullable=False)  # skill, milestone, streak, social, special
    subcategory = db.Column(db.String(50))  # vocabulary, grammar, reading, etc.
    
    # Display Information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100))  # Icon/emoji for the achievement
    badge_image = db.Column(db.String(200))  # Path to badge image
    
    # Achievement Criteria
    unlock_criteria = db.Column(JSON, nullable=False)  # Conditions to unlock
    # Example: {"type": "activity_count", "value": 100, "skill": "vocabulary"}
    
    # Rarity & Value
    rarity = db.Column(db.String(20), default='common')  # common, uncommon, rare, epic, legendary, secret
    points_value = db.Column(db.Integer, default=0)  # Points awarded on unlock
    
    # Special Properties
    is_secret = db.Column(db.Boolean, default=False)  # Hidden until unlocked
    is_repeatable = db.Column(db.Boolean, default=False)  # Can be earned multiple times
    prerequisite_achievement = db.Column(db.String(100))  # Must unlock this first
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_achievement_category', 'category', 'subcategory'),
        Index('idx_achievement_rarity', 'rarity', 'is_active'),
    )
    
    def to_dict(self, is_unlocked=False, unlocked_at=None):
        """Convert to dictionary, hiding details if secret and not unlocked"""
        if self.is_secret and not is_unlocked:
            return {
                'id': self.id,
                'achievement_key': self.achievement_key,
                'category': self.category,
                'title': '???',
                'description': 'Secret achievement - unlock to reveal!',
                'icon': '🔒',
                'rarity': 'secret',
                'is_secret': True,
                'is_unlocked': False
            }
        
        return {
            'id': self.id,
            'achievement_key': self.achievement_key,
            'category': self.category,
            'subcategory': self.subcategory,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'badge_image': self.badge_image,
            'unlock_criteria': self.unlock_criteria,
            'rarity': self.rarity,
            'points_value': self.points_value,
            'is_secret': self.is_secret,
            'is_repeatable': self.is_repeatable,
            'prerequisite_achievement': self.prerequisite_achievement,
            'is_unlocked': is_unlocked,
            'unlocked_at': unlocked_at.isoformat() if unlocked_at else None
        }


class UserAchievement(db.Model):
    """Track user achievement unlocks"""
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    
    # Unlock Details
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    progress_when_unlocked = db.Column(JSON)  # Snapshot of user progress
    
    # For Repeatable Achievements
    unlock_count = db.Column(db.Integer, default=1)
    last_unlock_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Display
    is_showcased = db.Column(db.Boolean, default=False)  # Display on profile
    is_notified = db.Column(db.Boolean, default=False)  # User has seen unlock notification
    
    # Relationships
    user = db.relationship('User', backref='achievements')
    achievement = db.relationship('Achievement')
    
    # Indexes
    __table_args__ = (
        Index('idx_user_achievement', 'user_id', 'achievement_id'),
        Index('idx_user_showcased', 'user_id', 'is_showcased'),
        UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
    
    def to_dict(self):
        achievement_dict = self.achievement.to_dict(is_unlocked=True, unlocked_at=self.unlocked_at)
        achievement_dict.update({
            'user_achievement_id': self.id,
            'unlock_count': self.unlock_count,
            'last_unlock_at': self.last_unlock_at.isoformat() if self.last_unlock_at else None,
            'is_showcased': self.is_showcased,
            'is_notified': self.is_notified
        })
        return achievement_dict


class LeaderboardEntry(db.Model):
    """Leaderboard rankings across multiple categories"""
    __tablename__ = 'leaderboard_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Leaderboard Category
    category = db.Column(db.String(50), nullable=False)  # overall, vocabulary, grammar, reading, etc.
    time_period = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, all_time
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Ranking Metrics
    score = db.Column(db.Integer, nullable=False)  # Primary ranking metric
    rank = db.Column(db.Integer)  # Current rank (calculated)
    previous_rank = db.Column(db.Integer)  # Rank from previous period
    
    # Additional Stats
    activities_completed = db.Column(db.Integer, default=0)
    study_time_minutes = db.Column(db.Integer, default=0)
    accuracy_percentage = db.Column(db.Float, default=0.0)
    streak_days = db.Column(db.Integer, default=0)
    
    # Metadata
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='leaderboard_entries')
    
    # Indexes
    __table_args__ = (
        Index('idx_leaderboard_category_period', 'category', 'time_period', 'period_start'),
        Index('idx_leaderboard_ranking', 'category', 'time_period', 'score', 'rank'),
        UniqueConstraint('user_id', 'category', 'time_period', 'period_start', name='uq_leaderboard_entry'),
    )
    
    def to_dict(self, include_user_info=True):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'time_period': self.time_period,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'score': self.score,
            'rank': self.rank,
            'previous_rank': self.previous_rank,
            'rank_change': self._calculate_rank_change(),
            'activities_completed': self.activities_completed,
            'study_time_minutes': self.study_time_minutes,
            'accuracy_percentage': round(self.accuracy_percentage, 1),
            'streak_days': self.streak_days,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user_info and self.user:
            result['user_info'] = {
                'username': self.user.username,
                'display_name': self.user.name if hasattr(self.user, 'name') else self.user.username,
                'avatar': self.user.avatar if hasattr(self.user, 'avatar') else None
            }
        
        return result
    
    def _calculate_rank_change(self):
        """Calculate rank change from previous period"""
        if self.rank and self.previous_rank:
            return self.previous_rank - self.rank  # Positive = moved up
        return 0


class GamificationStreak(db.Model):
    """Track user learning streaks with freeze/recovery features"""
    __tablename__ = "gamification_streaks"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Current Streak
    current_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    streak_start_date = db.Column(db.Date)
    
    # Historical Streaks
    longest_streak = db.Column(db.Integer, default=0)
    longest_streak_start = db.Column(db.Date)
    longest_streak_end = db.Column(db.Date)
    
    # Streak Freezes (Allow missing days without breaking streak)
    freeze_count = db.Column(db.Integer, default=0)  # Available freezes
    max_freezes = db.Column(db.Integer, default=2)  # Max freezes user can have
    freezes_used = db.Column(db.Integer, default=0)  # Total freezes used ever
    last_freeze_earned = db.Column(db.Date)
    
    # Streak Recovery (Special challenge to restore broken streak)
    is_recovery_available = db.Column(db.Boolean, default=False)
    recovery_challenge_completed = db.Column(db.Boolean, default=False)
    recovery_expires_at = db.Column(db.DateTime)
    
    # Milestones
    milestone_7_reached = db.Column(db.Boolean, default=False)
    milestone_30_reached = db.Column(db.Boolean, default=False)
    milestone_100_reached = db.Column(db.Boolean, default=False)
    milestone_365_reached = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('streak', uselist=False))
    
    # Index
    __table_args__ = (
        Index('idx_user_streak', 'user_id', 'current_streak'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_streak': self.current_streak,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'streak_start_date': self.streak_start_date.isoformat() if self.streak_start_date else None,
            'longest_streak': self.longest_streak,
            'longest_streak_start': self.longest_streak_start.isoformat() if self.longest_streak_start else None,
            'longest_streak_end': self.longest_streak_end.isoformat() if self.longest_streak_end else None,
            'freeze_count': self.freeze_count,
            'max_freezes': self.max_freezes,
            'freezes_used': self.freezes_used,
            'is_recovery_available': self.is_recovery_available,
            'recovery_challenge_completed': self.recovery_challenge_completed,
            'recovery_expires_at': self.recovery_expires_at.isoformat() if self.recovery_expires_at else None,
            'milestones': {
                '7_days': self.milestone_7_reached,
                '30_days': self.milestone_30_reached,
                '100_days': self.milestone_100_reached,
                '365_days': self.milestone_365_reached
            },
            'streak_status': self._calculate_streak_status(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def _calculate_streak_status(self):
        """Determine current streak status"""
        if not self.last_activity_date:
            return 'inactive'
        
        today = datetime.utcnow().date()
        days_since_activity = (today - self.last_activity_date).days
        
        if days_since_activity == 0:
            return 'active_today'
        elif days_since_activity == 1:
            return 'at_risk'  # Need to study today to maintain
        else:
            return 'broken'
    
    def update_streak(self, activity_date=None):
        """Update streak based on activity"""
        if activity_date is None:
            activity_date = datetime.utcnow().date()
        
        if not self.last_activity_date:
            # First activity
            self.current_streak = 1
            self.streak_start_date = activity_date
        else:
            days_diff = (activity_date - self.last_activity_date).days
            
            if days_diff == 0:
                # Same day activity
                pass
            elif days_diff == 1:
                # Consecutive day - increase streak
                self.current_streak += 1
            elif days_diff == 2 and self.freeze_count > 0:
                # Missed one day but can use freeze
                self.freeze_count -= 1
                self.freezes_used += 1
                self.current_streak += 1
            else:
                # Streak broken
                self._break_streak()
                self.current_streak = 1
                self.streak_start_date = activity_date
        
        self.last_activity_date = activity_date
        self._check_milestones()
        self._update_longest_streak()
    
    def _break_streak(self):
        """Handle streak break and offer recovery"""
        if self.current_streak >= 3:  # Only offer recovery for streaks >= 3
            self.is_recovery_available = True
            self.recovery_expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def _check_milestones(self):
        """Check and update milestone achievements"""
        if self.current_streak >= 7:
            self.milestone_7_reached = True
        if self.current_streak >= 30:
            self.milestone_30_reached = True
        if self.current_streak >= 100:
            self.milestone_100_reached = True
        if self.current_streak >= 365:
            self.milestone_365_reached = True
    
    def _update_longest_streak(self):
        """Update longest streak if current streak is longer"""
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
            self.longest_streak_start = self.streak_start_date
            self.longest_streak_end = self.last_activity_date


class ProgressMilestone(db.Model):
    """Track progress milestones and celebrations"""
    __tablename__ = 'progress_milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Milestone Type
    milestone_type = db.Column(db.String(50), nullable=False)  # level_up, skill_mastery, hours_milestone, activity_count
    milestone_key = db.Column(db.String(100), nullable=False)  # Unique identifier
    
    # Milestone Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    
    # Progress Tracking
    target_value = db.Column(db.Integer, nullable=False)
    achieved_value = db.Column(db.Integer, nullable=False)
    
    # Rewards
    points_awarded = db.Column(db.Integer, default=0)
    badge_awarded = db.Column(db.String(100))
    
    # Status
    is_completed = db.Column(db.Boolean, default=True)  # Milestones are created when reached
    reached_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    celebrated = db.Column(db.Boolean, default=False)  # User has seen celebration
    
    # Context
    related_data = db.Column(JSON)  # Additional context about the milestone
    
    # Relationships
    user = db.relationship('User', backref='progress_milestones')
    
    # Indexes
    __table_args__ = (
        Index('idx_user_milestone', 'user_id', 'milestone_type'),
        Index('idx_milestone_key', 'user_id', 'milestone_key'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'milestone_type': self.milestone_type,
            'milestone_key': self.milestone_key,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'target_value': self.target_value,
            'achieved_value': self.achieved_value,
            'points_awarded': self.points_awarded,
            'badge_awarded': self.badge_awarded,
            'is_completed': self.is_completed,
            'reached_at': self.reached_at.isoformat() if self.reached_at else None,
            'celebrated': self.celebrated,
            'related_data': self.related_data
        }


class SocialConnection(db.Model):
    """User social connections (friends, study partners)"""
    __tablename__ = 'social_connections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    connected_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Connection Type
    connection_type = db.Column(db.String(20), nullable=False)  # friend, study_partner, practice_partner
    status = db.Column(db.String(20), default='pending')  # pending, accepted, blocked
    
    # Study Partner Matching
    matched_by_ai = db.Column(db.Boolean, default=False)  # AI-suggested match
    match_score = db.Column(db.Float)  # Compatibility score
    common_interests = db.Column(JSON)  # Shared learning goals
    
    # Activity
    last_interaction = db.Column(db.DateTime)
    interaction_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='connections')
    connected_user = db.relationship('User', foreign_keys=[connected_user_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_user_connections', 'user_id', 'status'),
        Index('idx_connection_pair', 'user_id', 'connected_user_id'),
        UniqueConstraint('user_id', 'connected_user_id', name='uq_user_connection'),
    )
    
    def to_dict(self, include_user_info=True):
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'connected_user_id': self.connected_user_id,
            'connection_type': self.connection_type,
            'status': self.status,
            'matched_by_ai': self.matched_by_ai,
            'match_score': self.match_score,
            'common_interests': self.common_interests,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'interaction_count': self.interaction_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None
        }
        
        if include_user_info and self.connected_user:
            result['connected_user_info'] = {
                'username': self.connected_user.username,
                'display_name': self.connected_user.name if hasattr(self.connected_user, 'name') else self.connected_user.username,
                'avatar': self.connected_user.avatar if hasattr(self.connected_user, 'avatar') else None,
                'current_level': self.connected_user.current_level if hasattr(self.connected_user, 'current_level') else None
            }
        
        return result


class SharedAchievement(db.Model):
    """Track shared achievements in social feed"""
    __tablename__ = 'shared_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    
    # Share Details
    caption = db.Column(db.Text)
    visibility = db.Column(db.String(20), default='friends')  # public, friends, private
    
    # Engagement
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    shared_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='shared_achievements')
    achievement = db.relationship('Achievement')
    
    # Index
    __table_args__ = (
        Index('idx_shared_feed', 'visibility', 'shared_at'),
        Index('idx_user_shares', 'user_id', 'shared_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement': self.achievement.to_dict(is_unlocked=True) if self.achievement else None,
            'caption': self.caption,
            'visibility': self.visibility,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'shared_at': self.shared_at.isoformat() if self.shared_at else None,
            'user_info': {
                'username': self.user.username if self.user else None,
                'display_name': self.user.name if hasattr(self.user, 'name') and self.user else None
            }
        }
