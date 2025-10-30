# 🎯 FRONTEND PAGE FLOW & NAVIGATION ARCHITECTURE

**Date**: October 22, 2025  
**Status**: Complete Reference Guide  
**Audience**: Frontend Developers & QA

---

## 📱 COMPLETE USER JOURNEY MAP

### Phase 1: Discovery & Authentication
```
Landing Page
    ↓
Login / Register / Forgot Password
    ↓
[Auth Success - Token Stored]
    ↓
Redirect to Assessment or Dashboard
```

### Phase 2: Onboarding (First Time Users)
```
Initial Assessment
  ├─ Conversational Assessment
  ├─ Grammar Test
  ├─ Vocabulary Test
  ├─ Reading Comprehension
  ├─ Writing Sample
  └─ Listening Test
    ↓
Assessment Results
  ├─ Overall CEFR Level
  ├─ Skill Breakdown (Listening, Speaking, Reading, Writing, Vocab, Grammar)
  ├─ Strengths & Weaknesses
  └─ Recommendations
    ↓
Goal Setting
  ├─ Select Learning Goals (e.g., "Learn Conversational English")
  ├─ Choose Target Level (A1 → C2)
  ├─ Set Timeline
  └─ Select Learning Preferences
    ↓
Learning Path Selector
  ├─ Show Available Paths
  ├─ Display Curriculum Preview
  ├─ Estimate Time to Completion
  └─ Enroll in Path
    ↓
Vocabulary Baseline
  ├─ Test Initial Vocabulary Knowledge
  └─ Setup Spaced Repetition
    ↓
Dashboard Ready ✓
```

### Phase 3: Main Learning Experience
```
Dashboard (Main Hub)
  ├─ Next Recommended Activity (AI Orchestrated)
  ├─ Vocabulary Review (Spaced Repetition Due)
  ├─ Active Goals & Progress
  ├─ Learning Streak Tracker
  ├─ Recent Achievements
  ├─ Quick Statistics
  └─ Quick Action Buttons
    ↓
Activities (AI-Generated)
  ├─ Quiz Activity
  │   ├─ Multiple choice questions
  │   ├─ Real-time feedback
  │   └─ Performance tracking
  ├─ Flashcards Activity
  │   ├─ Spaced repetition
  │   ├─ Word mastery tracking
  │   └─ Context learning
  ├─ Reading Comprehension
  │   ├─ Adaptive text difficulty
  │   ├─ Vocabulary highlighting
  │   └─ Comprehension questions
  ├─ Writing Exercise
  │   ├─ Grammar checking
  │   ├─ Style feedback
  │   └─ AI evaluation
  ├─ Role-Play Scenario
  │   ├─ Conversational practice
  │   ├─ Real-world situations
  │   └─ Speech recording (optional)
  └─ [More activity types]
    ↓
Activity Complete
  ├─ Call /learning-path/complete-activity
  ├─ Update Performance Metrics
  ├─ Award Gamification Points
  ├─ Check Achievement Unlock
  └─ Difficulty Adjustment (if needed)
    ↓
Return to Dashboard OR Continue Learning
```

### Phase 4: Deep Learning Paths
```
Learning Paths
  ├─ Show All Available Paths
  └─ Current User Paths
    ↓
Learning Path Detail
  ├─ CEFR Level A1 → A2 → B1 → B2 → C1 → C2
  ├─ Learning Nodes (atomic units)
  │   ├─ Prerequisites
  │   ├─ Learning Objectives
  │   ├─ Estimated Time
  │   ├─ Mastery Threshold
  │   └─ Related Activities
  ├─ Progress Tracking
  ├─ Chapters / Milestones
  └─ Enroll / Continue Button
    ↓
Learning Node Detail
  ├─ Learning Objective
  ├─ Key Concepts
  ├─ Prerequisite Check
  ├─ Available Activities
  ├─ Required Mastery: [████░░]
  └─ Start Activity Button
```

### Phase 5: Vocabulary Mastery (Phase 5)
```
Vocabulary Hub
  ├─ Spaced Repetition Due (Urgent)
  │   ├─ SM-2 Algorithm Review Schedule
  │   ├─ Practice Interface
  │   └─ Track Ease Factor
  ├─ All Vocabulary Words
  │   ├─ Filter by Level (A1-C2)
  │   ├─ Sort by Mastery
  │   ├─ Search & Filter
  │   └─ Word Details
  ├─ Vocabulary Stats
  │   ├─ Total Words Known
  │   ├─ Words by Level
  │   ├─ Mastery Distribution
  │   ├─ Learning Velocity (words/week)
  │   └─ Retention Rate
  └─ Word Network
      ├─ Related Words
      ├─ Synonyms & Antonyms
      ├─ Collocations
      └─ Usage Examples
```

### Phase 6: Practice Sessions
```
Practice Hub
  ├─ Start New Session
  │   ├─ Select Topic
  │   ├─ Choose Difficulty
  │   ├─ Set Duration
  │   └─ Select Question Types
  ├─ Practice Recommendations
  │   ├─ Weak Area Focus
  │   ├─ Strength Reinforcement
  │   └─ Balanced Practice
  ├─ Active Sessions
  │   ├─ Resume Session
  │   └─ Session Progress
  ├─ Practice History
  │   ├─ Recent Sessions
  │   ├─ Performance Trends
  │   └─ Streaks & Consistency
  └─ Practice Analytics
      ├─ Accuracy Over Time
      ├─ Topic Mastery
      └─ Time Spent
```

### Phase 7: Goals & Milestones
```
Goals Page
  ├─ Available Goal Templates
  │   ├─ Conversational English
  │   ├─ Business English
  │   ├─ Academic English
  │   ├─ Exam Preparation
  │   └─ [More goals]
  ├─ My Active Goals
  │   ├─ Goal Title
  │   ├─ Target Level
  │   ├─ Progress Bar [████░░]
  │   ├─ Time Remaining
  │   ├─ Milestone Checklist
  │   └─ Certificate Preview (when completed)
  ├─ Goal Detail
  │   ├─ Milestones
  │   │   ├─ Milestone 1: [✓ Complete]
  │   │   ├─ Milestone 2: [→ In Progress]
  │   │   └─ Milestone 3: [○ Locked]
  │   ├─ Progress History
  │   ├─ Learning Path Alignment
  │   └─ Estimated Completion Date
  └─ Certificates
      ├─ Earned Certificates
      ├─ Certificate Details
      └─ Download / Share
```

### Phase 8: Analytics & Insights (Phase 4)
```
Analytics Dashboard
  ├─ Overall Statistics
  │   ├─ Total Learning Hours
  │   ├─ Activities Completed
  │   ├─ Current Level & Target
  │   └─ Streak Information
  ├─ Performance Trends
  │   ├─ Line Chart: Accuracy Over Time
  │   ├─ Learning Velocity (activities/week)
  │   └─ Difficulty Progression
  ├─ Skill Breakdown (Radar Chart)
  │   ├─ Listening: [████░░] 75%
  │   ├─ Speaking: [███░░░░] 50%
  │   ├─ Reading: [█████░░] 85%
  │   ├─ Writing: [████░░░] 60%
  │   ├─ Vocabulary: [██████░] 90%
  │   └─ Grammar: [████░░░] 70%
  ├─ Learning Patterns
  │   ├─ Heatmap: Best Learning Times
  │   ├─ Day of Week Analysis
  │   └─ Optimal Session Length
  ├─ Error Analysis
  │   ├─ Common Mistakes
  │   ├─ Weak Concepts
  │   └─ Recommended Focus Areas
  ├─ Predictive Analytics
  │   ├─ Est. Time to Next Level
  │   ├─ Skill Mastery Prediction
  │   └─ Goal Completion Estimate
  └─ Export Report
      └─ Download Progress Report PDF
```

### Phase 9: Gamification & Community (Phase 9)
```
Gamification Hub
  ├─ Points & Levels
  │   ├─ Current Points: [50,000 pts]
  │   ├─ Level 12 [███████░░░] 75%
  │   ├─ Points by Activity Type
  │   └─ Multiplier Bonuses (streak, challenges)
  ├─ Badges & Achievements
  │   ├─ Recent Achievements
  │   ├─ Achievement Gallery (All)
  │   │   ├─ 🥇 Gold Badges (Rare)
  │   │   ├─ 🥈 Silver Badges (Common)
  │   │   └─ 🥉 Bronze Badges (Starter)
  │   ├─ Achievement Progress
  │   └─ Secret Achievements Teaser
  ├─ Daily Challenges
  │   ├─ Today's Challenge (AI-Generated)
  │   ├─ Difficulty: [Easy/Medium/Hard]
  │   ├─ Reward: [1000 points]
  │   ├─ Start Challenge Button
  │   └─ Past 7 Days Completion Rate
  ├─ Leaderboard
  │   ├─ Global Leaderboard (Top 100)
  │   ├─ Level-Based Leaderboard
  │   ├─ Friend Leaderboard
  │   ├─ Your Rank & Score
  │   └─ Time Period Filter (Week/Month/All-time)
  ├─ Streaks
  │   ├─ Current Streak: [14 days]
  │   ├─ Longest Streak: [42 days]
  │   ├─ Streak Freezes: [2 remaining]
  │   ├─ Daily Streak Progress
  │   └─ Streak Recovery Challenges
  └─ Social Features
      ├─ Activity Feed
      ├─ Friend Activity
      ├─ Share Achievements
      └─ Learning Groups
```

### Phase 10: Settings & Profile
```
Profile Page
  ├─ User Information
  │   ├─ Avatar
  │   ├─ Name
  │   ├─ Member Since
  │   └─ Learning Statistics
  ├─ Language Learning Profile
  │   ├─ Current Level: B1
  │   ├─ Native Language: Telugu
  │   ├─ Learning Goals
  │   ├─ Learning Style Preference
  │   └─ Pace: Medium
  ├─ Achievements Summary
  │   ├─ Total Points
  │   ├─ Badges Earned
  │   ├─ Goals Completed
  │   └─ Current Streak
  └─ Action Buttons
      ├─ Edit Profile
      └─ Change Password

Settings Page
  ├─ Account Settings
  │   ├─ Email
  │   ├─ Password
  │   ├─ Language
  │   ├─ Timezone
  │   └─ Delete Account
  ├─ Learning Preferences
  │   ├─ Difficulty Level (Auto/Manual)
  │   ├─ Preferred Activity Types
  │   ├─ Learning Pace
  │   ├─ Daily Target (minutes)
  │   └─ Preferred Study Time
  ├─ Notification Settings
  │   ├─ Email Notifications
  │   ├─ Push Notifications
  │   ├─ In-App Notifications
  │   ├─ Frequency Settings
  │   └─ Notification Types
  ├─ Privacy Settings
  │   ├─ Profile Visibility
  │   ├─ Share Progress with Friends
  │   ├─ Leaderboard Visibility
  │   └─ Data Collection Preferences
  └─ Accessibility
      ├─ Dark Mode
      ├─ Font Size
      ├─ High Contrast
      └─ Screen Reader Support

Notification Center
  ├─ Recent Notifications
  │   ├─ Achievement Unlocked
  │   ├─ Daily Challenge Available
  │   ├─ Goal Milestone Reached
  │   ├─ Vocabulary Review Due
  │   └─ Friend Started Learning
  ├─ Filter by Type
  ├─ Mark as Read
  └─ Notification Preferences Link
```

---

## 🔄 COMPONENT RELATIONSHIPS

### Data Flow Hierarchy
```
Dashboard (Root Hub)
  ├─ Fetches /personalization/dashboard
  ├─ Displays:
  │   ├─ Next Activity (from /learning-path/next-activity)
  │   ├─ Goals Progress (from /goals/my-goals)
  │   ├─ Vocabulary Due (from /vocabulary/spaced-repetition)
  │   ├─ Gamification (from /gamification/stats)
  │   ├─ Learning Streak (calculated from activities)
  │   ├─ Analytics Summary (from /analytics/dashboard-summary)
  │   └─ Notifications (from /notifications)
  └─ Links to all sub-pages

Activities (AI Orchestrator Hub)
  ├─ Calls /learning-path/next-activity
  ├─ Routes to Activity Type Components
  │   ├─ QuizActivity → /activities/quiz/:id
  │   ├─ FlashcardsActivity → /activities/flashcards/:id
  │   ├─ ReadingActivity → /activities/reading/:id
  │   ├─ WritingActivity → /activities/writing/:id
  │   ├─ RolePlayActivity → /activities/roleplay/:id
  │   └─ [More activity types]
  └─ On Completion:
      ├─ Calls /learning-path/complete-activity
      ├─ Calls /adaptive/adjust-difficulty (if needed)
      ├─ Awards gamification points
      └─ Returns to Activities or Dashboard

Analytics (Data Hub)
  ├─ Calls all 6 analytics endpoints in parallel
  ├─ Displays:
  │   ├─ Performance Trends (line chart)
  │   ├─ Skill Breakdown (radar chart)
  │   ├─ Difficulty Progression (bar chart)
  │   ├─ Learning Patterns (heatmap)
  │   ├─ Activity Performance (table)
  │   └─ Predictions (text/statistics)
  └─ Exports report via /analytics/export/progress-report

Learning Paths (Curriculum Hub)
  ├─ Calls /learning-path/curriculum
  ├─ Shows:
  │   ├─ CEFR Levels (A1-C2)
  │   ├─ Learning Nodes per Level
  │   ├─ Prerequisites & Mastery Status
  │   └─ Available Activities
  └─ Routes to LearningPathDetail
      └─ Shows node details & activities

Practice (Session Hub)
  ├─ Calls /practice/start
  ├─ Calls /practice/:id/generate-questions
  ├─ For each question:
  │   └─ Calls /practice/:id/submit-answer
  └─ On completion:
      ├─ Calls /practice/:id/complete
      └─ Shows /practice/:id/results

Goals (Milestone Hub)
  ├─ Calls /goals/my-goals
  ├─ For each goal:
  │   ├─ Calls /goals/:id/progress-history
  │   └─ Displays:
  │       ├─ Progress bar
  │       ├─ Milestones
  │       ├─ Timeline
  │       └─ Certificate preview (if near completion)
  └─ On milestone completion:
      └─ Calls /goals/milestones/:id/complete

Vocabulary (Mastery Hub)
  ├─ Calls /vocabulary/spaced-repetition (PRIORITY)
  ├─ Shows:
  │   ├─ Words due for review
  │   ├─ All words (with filters)
  │   ├─ Word networks
  │   └─ Stats dashboard
  └─ On practice:
      ├─ Calls /vocabulary/:id/practice-result
      ├─ Updates SM-2 interval
      └─ Tracks mastery progression
```

---

## 🗂️ ROUTER CONFIGURATION REFERENCE

```jsx
// See src/App.jsx for full routing configuration

Public Routes:
/                          → LandingPage
/login                     → Login
/register                  → Register
/forgot-password           → ForgotPassword

Protected Routes (Onboarding):
/assessment                → InitialAssessment
/assessment-results        → AssessmentResults
/onboarding                → Onboarding

Protected Routes (Main App):
/dashboard                 → Dashboard
/activities                → Activities (AI Orchestrator)
/activities/:id            → ActivityDetail
/activities/quiz/:id       → QuizActivity
/activities/flashcards/:id → FlashcardsActivity
/activities/reading/:id    → ReadingActivity

/learning-paths            → LearningPaths
/learning-paths/:id        → LearningPathDetail

/vocabulary                → Vocabulary
/vocabulary-mastery        → VocabularyMastery

/practice                  → Practice

/goals                     → Goals

/analytics                 → Analytics
/analytics-dashboard       → AnalyticsDashboard

/leaderboard               → Leaderboard

/gamification              → Gamification

/profile                   → Profile

/settings                  → Settings
/settings/notifications    → NotificationSettings

/notifications             → NotificationCenter
/notification-settings     → NotificationSettings_NEW

/chat                      → Chat
/chat-tutor                → ChatTutor

/image-learning            → ImageLearning

/lesson/:lessonId          → LessonView
/lesson                    → LessonView

/mastery                   → MasteryDashboard

/activity-history          → ActivityHistory

/auth-test                 → AuthTest (Debug)
```

---

## 🎨 COMPONENT ARCHITECTURE MATRIX

| Page | Main Components | Sub-Components | Backend Calls |
|------|---|---|---|
| Dashboard | StatCard, HoverCard, DailyChallengeCard, StreakTracker, GamificationSummary | ResumeActivities, ReviewNotification | `/personalization/dashboard`, `/learning-path/next-activity`, `/vocabulary/spaced-repetition` |
| Activities | ActivityCard, DifficultyBadge | ActivityDetail, Activity Type Components | `/learning-path/next-activity`, `/learning-path/complete-activity` |
| QuizActivity | QuizInterface | QuestionCard, AnswerOptions, Feedback | `/activities/quiz/submit` |
| Vocabulary | VocabularyCard, VocabularyStats | SpacedRepetitionReview, WordNetworkGraph | `/vocabulary/spaced-repetition`, `/vocabulary/stats` |
| LearningPaths | LearningPathSelector | LearningNodeCard, LevelProgressBar | `/learning-path/curriculum`, `/learning-path/nodes` |
| Practice | PracticeInterface | QuestionCard, AnswerSubmission | `/practice/start`, `/practice/:id/generate-questions` |
| Goals | GoalCard, MilestoneProgress | CreateGoalModal, GoalDetailModal | `/goals/my-goals`, `/goals/:id/progress-history` |
| Analytics | LineChart, BarChart, RadarChart | SkillRadarChart, ComparisonChart | `/analytics/dashboard-summary`, `/analytics/learning-trends` |
| Gamification | BadgeDisplay, LeaderboardPanel, PointsVisualization | StreakTracker, AchievementDisplay | `/gamification/badges`, `/gamification/leaderboard` |

---

## 📊 STATE MANAGEMENT FLOW

```
App (Root)
├─ AuthContext (User auth, token)
├─ Dashboard
│   ├─ dashboardData
│   ├─ nextActivity
│   ├─ vocabularyDue
│   └─ gamificationStats
├─ Activities
│   ├─ currentActivity
│   ├─ orchestratorMessage
│   ├─ activityList
│   └─ performanceMetrics
├─ Analytics
│   ├─ analyticsData (trends, performance, patterns)
│   ├─ selectedTimeRange
│   └─ skillBreakdown
├─ Vocabulary
│   ├─ vocabularyDue
│   ├─ allVocabulary
│   ├─ practiceMode
│   └─ masteryStats
└─ Goals
    ├─ myGoals
    ├─ goalProgress
    └─ milestones
```

---

## 🔐 Route Guards & Protection

```
OnboardingGuard
├─ Checks: user.onboarding_phase
├─ Routes Protected:
│   ├─ /assessment (Phase: assessment)
│   ├─ /assessment-results (Phase: assessment)
│   ├─ /onboarding (Phase: onboarding)
│   └─ All other routes (Phase: completed)
└─ Redirects:
    ├─ Not authenticated → /login
    ├─ On boarding incomplete → /assessment
    └─ Completed → /dashboard
```

---

## 📱 Responsive Design Breakpoints

```
Mobile (xs):   < 600px   (Stacked layout, drawer navigation)
Tablet (sm):   600-960px (Single column, sidebar)
Laptop (md):   960-1280px (Two column layout)
Desktop (lg):  1280-1920px (Three column, full features)
XL (xl):       > 1920px  (Expanded multi-panel layout)
```

---

## 🎯 CRITICAL SUCCESS METRICS

### Page Load Times
- Dashboard: < 2 seconds
- Activities: < 1.5 seconds
- Analytics: < 2.5 seconds
- Vocabulary: < 1 second

### API Response Times
- /learning-path/next-activity: < 500ms
- /analytics/dashboard-summary: < 1 second
- /vocabulary/spaced-repetition: < 500ms
- /gamification/stats: < 300ms

### User Engagement
- Session Duration: > 20 minutes
- Daily Active Users: High retention
- Feature Usage: All major features used weekly
- Completion Rate: > 80% of activities started are completed

---

**Document Version**: 1.0  
**Last Updated**: October 22, 2025  
**Status**: Complete Reference
