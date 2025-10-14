from .user import db, User, Profile
from .course import LearningPath, Course
from .activity import Activity, UserActivityLog, ConceptMastery, AdaptiveLearningPathProgress, AdaptiveLearningSession
from .gamification import Badge, UserBadge, Achievement
from .enrollment import UserEnrollment, ChapterProgress, ActivityProgress, PathCertificate
from .personalization import (
    UserGoal, ProficiencyAssessment, VocabularyWord, 
    MistakePattern, LearningSession, DailyChallenge, UserDailyChallengeCompletion
)
from .chapter import (
    Chapter, UserChapterProgress, PracticeSession, UserNotes, 
    TestAssessment, ChapterDependency, AIConversationContext
)
from .analytics import (
    AssessmentQuestionResponse, ActivityQuestionResponse, UserAnalytics,
    LearningStreak, AIGeneratedContent, UserLearningTimeline, PerformanceTrend
)
from .milestone import Milestone, LessonReview
from .image_learning import ImageLearning, ImageObjectVocabulary
from .chat import ChatConversation, ChatMessage
from .notification import NotificationType, Notification, UserNotificationSettings
from .goal import GoalType, AchievementGoal, Certificate, LevelProgression

__all__ = [
    'db', 'User', 'Profile', 'LearningPath', 'Course', 
    'Activity', 'UserActivityLog', 'ConceptMastery', 'AdaptiveLearningPathProgress', 'AdaptiveLearningSession',
    'Badge', 'UserBadge', 'Achievement',
    'UserEnrollment', 'ChapterProgress', 'ActivityProgress', 'PathCertificate',
    'UserGoal', 'ProficiencyAssessment', 'VocabularyWord', 
    'MistakePattern', 'LearningSession', 'DailyChallenge', 'UserDailyChallengeCompletion',
    'Chapter', 'UserChapterProgress', 'PracticeSession', 'UserNotes', 
    'TestAssessment', 'ChapterDependency', 'AIConversationContext',
    'AssessmentQuestionResponse', 'ActivityQuestionResponse', 'UserAnalytics',
    'LearningStreak', 'AIGeneratedContent', 'UserLearningTimeline', 'PerformanceTrend',
    'Milestone', 'LessonReview',
    'ImageLearning', 'ImageObjectVocabulary',
    'ChatConversation', 'ChatMessage',
    'NotificationType', 'Notification', 'UserNotificationSettings',
    'GoalType', 'AchievementGoal', 'Certificate', 'LevelProgression'
]