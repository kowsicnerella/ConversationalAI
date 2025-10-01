
from app import create_app
from app.models import db
app = create_app('development')

@app.shell_context_processor
def make_shell_context():
    from app.models import (
        User, Profile, Activity, UserActivityLog, Badge, UserBadge, 
        LearningPath, Achievement, UserGoal, ProficiencyAssessment,
        VocabularyWord, MistakePattern, LearningSession, DailyChallenge,
        UserDailyChallengeCompletion, Chapter, UserChapterProgress, 
        PracticeSession, UserNotes, TestAssessment, ChapterDependency, 
        AIConversationContext
    )
    return dict(
        db=db, 
        User=User, 
        Profile=Profile, 
        Activity=Activity, 
        UserActivityLog=UserActivityLog,
        Badge=Badge, 
        UserBadge=UserBadge, 
        LearningPath=LearningPath,
        Achievement=Achievement,
        UserGoal=UserGoal,
        ProficiencyAssessment=ProficiencyAssessment,
        VocabularyWord=VocabularyWord,
        MistakePattern=MistakePattern,
        LearningSession=LearningSession,
        DailyChallenge=DailyChallenge,
        UserDailyChallengeCompletion=UserDailyChallengeCompletion,
        Chapter=Chapter,
        UserChapterProgress=UserChapterProgress,
        PracticeSession=PracticeSession,
        UserNotes=UserNotes,
        TestAssessment=TestAssessment,
        ChapterDependency=ChapterDependency,
        AIConversationContext=AIConversationContext
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
