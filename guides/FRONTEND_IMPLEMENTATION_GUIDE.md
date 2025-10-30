# 🚀 FRONTEND-BACKEND INTEGRATION IMPLEMENTATION GUIDE

**Date**: October 22, 2025  
**Status**: Step-by-step Implementation Plan  
**Priority**: Critical - All endpoints must be connected

---

## 📋 PHASE 1: DASHBOARD ENHANCEMENT (Week 1)

### File: `src/pages/Dashboard.jsx`

#### Current State
```jsx
// Currently shows basic stats only
// NOT calling /learning-path/next-activity
// NOT showing recommended activity from AI orchestrator
```

#### Required Changes

**Step 1: Add New Imports**
```jsx
// Add to existing imports:
import { learningPathService } from '../services/learningPathService';
import ActivityCardWithAction from '../components/common/ActivityCard';
import { API_ENDPOINTS } from '../config/api';
```

**Step 2: Add State for Next Activity**
```jsx
const [nextActivity, setNextActivity] = useState(null);
const [orchestratorMessage, setOrchestratorMessage] = useState('');
const [loadingNextActivity, setLoadingNextActivity] = useState(false);
```

**Step 3: Add useEffect to Fetch Next Activity**
```jsx
useEffect(() => {
  fetchNextRecommendedActivity();
}, [user?.id]);

const fetchNextRecommendedActivity = async () => {
  try {
    setLoadingNextActivity(true);
    
    // Call the AI orchestrator endpoint
    const response = await learningPathService.getNextActivity({
      user_id: user?.id,
      context: {
        device: 'web',
        time_available: 30, // minutes
        current_streak: dashboardData?.streak || 0
      }
    });
    
    console.log('Next Activity from Orchestrator:', response);
    setNextActivity(response.activity);
    setOrchestratorMessage(response.message || 'Personalized activity selected for you');
  } catch (error) {
    console.error('Error fetching next activity:', error);
  } finally {
    setLoadingNextActivity(false);
  }
};
```

**Step 4: Add UI Component to Display Next Activity**
```jsx
// Add to JSX return statement (after Stats section):

{nextActivity && (
  <Grid item xs={12}>
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
    >
      <Card sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        mb: 3
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 'bold' }}>
            🎯 Your Next Activity
          </Typography>
          <Typography variant="body2" sx={{ mb: 2, opacity: 0.9 }}>
            {orchestratorMessage}
          </Typography>
          
          <Box sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 2,
            flexWrap: 'wrap'
          }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                {nextActivity.title}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label={nextActivity.type} size="small" color="primary" />
                <Chip label={`${nextActivity.difficulty || 'medium'}`} size="small" />
                <Chip label={`${nextActivity.estimated_time} min`} size="small" />
              </Box>
            </Box>
            
            <Button
              variant="contained"
              sx={{
                background: 'white',
                color: '#667eea',
                fontWeight: 'bold',
                '&:hover': {
                  background: '#f5f5f5'
                }
              }}
              onClick={() => navigate(`/activities/activity-type/${nextActivity.id}`)}
            >
              Start Activity →
            </Button>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  </Grid>
)}
```

---

## 📋 PHASE 2: ACTIVITIES PAGE ENHANCEMENT (Week 1)

### File: `src/pages/Activities.jsx`

#### Current State
```jsx
// Currently fetches activities but doesn't use AI orchestrator
// Mock data being displayed
```

#### Required Changes

**Step 1: Update Activity Fetching**
```jsx
const fetchNextActivity = async () => {
  try {
    setLoading(true);
    setError('');
    
    // REPLACE the current implementation with:
    const response = await axiosInstance.post(
      API_ENDPOINTS.LEARNING_PATH.NEXT_ACTIVITY,
      {
        user_id: userId,
        session_context: {
          device: 'web',
          time_available: availableTime || 30,
          current_streak: userStreak || 0,
          preferred_activities: userPreferences?.activityTypes
        }
      }
    );
    
    console.log('AI Orchestrator Response:', response.data);
    
    if (response.data && response.data.activity) {
      setNextActivity(response.data.activity);
      setCurrentNode(response.data.learning_node);
      setOrchestratorMessage(response.data.recommendation_reason);
    }
  } catch (error) {
    console.error('Error from Learning Path Orchestrator:', error);
    setError('Failed to get personalized activity');
  } finally {
    setLoading(false);
  }
};
```

**Step 2: Add Activity Type Routing**
```jsx
const handleStartActivity = (activity) => {
  switch(activity.type) {
    case 'quiz':
      navigate(`/activities/quiz/${activity.id}`);
      break;
    case 'flashcards':
      navigate(`/activities/flashcards/${activity.id}`);
      break;
    case 'reading':
      navigate(`/activities/reading/${activity.id}`);
      break;
    case 'writing':
      navigate(`/activities/writing/${activity.id}`);
      break;
    case 'roleplay':
      navigate(`/activities/roleplay/${activity.id}`);
      break;
    case 'listening':
      navigate(`/activities/listening/${activity.id}`);
      break;
    default:
      navigate(`/activities/${activity.id}`);
  }
};
```

**Step 3: Add Difficulty Adjustment**
```jsx
const handleActivityComplete = async (activityId, performance) => {
  try {
    // Call /learning-path/complete-activity
    const response = await axiosInstance.post(
      API_ENDPOINTS.LEARNING_PATH.COMPLETE_ACTIVITY,
      {
        activity_id: activityId,
        performance_data: performance,
        skill_improvements: calculateSkillImprovements(performance)
      }
    );
    
    // If difficulty needs adjustment
    if (response.data.adjust_difficulty) {
      await adjustDifficulty({
        activity_id: activityId,
        performance_score: performance.accuracy,
        response_time: performance.time_spent,
        error_patterns: performance.error_patterns
      });
    }
    
    // Refresh to get next activity
    setActivityComplete(true);
    setTimeout(() => fetchNextActivity(), 2000);
  } catch (error) {
    console.error('Error completing activity:', error);
  }
};
```

---

## 📋 PHASE 3: VOCABULARY PAGE (Week 2)

### File: `src/pages/Vocabulary.jsx`

#### Required Changes

**Step 1: Fetch Spaced Repetition Words**
```jsx
useEffect(() => {
  fetchSpacedRepetitionDue();
}, [user?.id]);

const fetchSpacedRepetitionDue = async () => {
  try {
    setLoadingReview(true);
    
    const response = await axiosInstance.get(
      API_ENDPOINTS.VOCABULARY.SPACED_REPETITION
    );
    
    // Prioritize words due for review
    const dueWords = response.data.filter(w => w.is_due);
    setVocabularyDue(dueWords);
    
    // Show notification
    if (dueWords.length > 0) {
      showNotification(
        `${dueWords.length} words due for review!`,
        'info'
      );
    }
  } catch (error) {
    console.error('Error fetching spaced repetition words:', error);
  } finally {
    setLoadingReview(false);
  }
};
```

**Step 2: Show Due Items Priority**
```jsx
// In render section, show due items first:
{vocabularyDue && vocabularyDue.length > 0 && (
  <Box sx={{ mb: 4 }}>
    <Typography variant="h6" sx={{ mb: 2, color: 'warning.main' }}>
      ⏰ Review Due ({vocabularyDue.length} words)
    </Typography>
    <Grid container spacing={2}>
      {vocabularyDue.map(word => (
        <SpacedRepetitionReview
          key={word.id}
          word={word}
          onComplete={handleVocabularyPractice}
        />
      ))}
    </Grid>
  </Box>
)}
```

**Step 3: Track Practice Results**
```jsx
const handleVocabularyPractice = async (wordId, result) => {
  try {
    await axiosInstance.post(
      API_ENDPOINTS.VOCABULARY.PRACTICE_RESULT(wordId),
      {
        performance_score: result.score,
        ease_factor: result.ease_factor,
        interval: result.next_review_interval,
        response_time: result.time_spent
      }
    );
    
    // Refresh vocabulary list
    fetchSpacedRepetitionDue();
  } catch (error) {
    console.error('Error tracking vocabulary practice:', error);
  }
};
```

---

## 📋 PHASE 4: ANALYTICS PAGES (Week 2)

### File: `src/pages/AnalyticsDashboard.jsx`

#### Required Changes

**Step 1: Add All Analytics Endpoints**
```jsx
useEffect(() => {
  fetchAllAnalytics();
}, [user?.id]);

const fetchAllAnalytics = async () => {
  try {
    setLoading(true);
    
    const [
      dashboard,
      trends,
      performance,
      patterns,
      difficulty,
      vocab
    ] = await Promise.all([
      axiosInstance.get(API_ENDPOINTS.ANALYTICS.DASHBOARD),
      axiosInstance.get(API_ENDPOINTS.ANALYTICS.PERFORMANCE_TRENDS),
      axiosInstance.get(API_ENDPOINTS.ANALYTICS.SKILL_BREAKDOWN),
      axiosInstance.get(API_ENDPOINTS.ANALYTICS.LEARNING_PATTERNS),
      axiosInstance.get(API_ENDPOINTS.ANALYTICS.DIFFICULTY_PROGRESSION),
      axiosInstance.get(API_ENDPOINTS.ANALYTICS.VOCABULARY_ANALYTICS)
    ]);
    
    setAnalyticsData({
      dashboard: dashboard.data,
      trends: trends.data,
      performance: performance.data,
      patterns: patterns.data,
      difficulty: difficulty.data,
      vocabulary: vocab.data
    });
  } catch (error) {
    console.error('Error fetching analytics:', error);
  } finally {
    setLoading(false);
  }
};
```

**Step 2: Display All Charts**
```jsx
// Skill Radar Chart
<SkillRadarChart data={analyticsData.performance.skills} />

// Performance Trends
<LineChart data={analyticsData.trends.data}>
  <Line dataKey="accuracy" stroke="#667eea" />
  <Line dataKey="difficulty" stroke="#764ba2" />
</LineChart>

// Difficulty Progression
<BarChart data={analyticsData.difficulty.progression}>
  <Bar dataKey="week" />
  <Bar dataKey="difficulty_level" fill="#667eea" />
</BarChart>

// Learning Patterns
<HeatmapChart data={analyticsData.patterns.hourly} />
```

---

## 📋 PHASE 5: LEARNING PATHS PAGE (Week 2)

### File: `src/pages/LearningPaths.jsx`

#### Required Changes

**Step 1: Fetch Curriculum Structure**
```jsx
useEffect(() => {
  fetchCurriculumStructure();
}, []);

const fetchCurriculumStructure = async () => {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.LEARNING_PATH.CURRICULUM
    );
    
    // Organize by CEFR levels
    const levels = response.data.levels;
    const nodes = response.data.nodes;
    
    setLevels(levels);
    setNodes(nodes);
  } catch (error) {
    console.error('Error fetching curriculum:', error);
  }
};
```

**Step 2: Show CEFR Levels**
```jsx
// Render levels: A1 → A2 → B1 → B2 → C1 → C2
{levels.map(level => (
  <Card key={level.id}>
    <CardContent>
      <Typography variant="h5">{level.cefr_level}: {level.name}</Typography>
      <Typography variant="body2">{level.description}</Typography>
      <LinearProgress 
        variant="determinate" 
        value={level.progress} 
      />
      
      {/* Show nodes for this level */}
      {nodes
        .filter(n => n.level_id === level.id)
        .map(node => (
          <LearningNodeCard key={node.id} node={node} />
        ))}
    </CardContent>
  </Card>
))}
```

---

## 📋 PHASE 6: GOALS PAGE (Week 3)

### File: `src/pages/Goals.jsx`

#### Required Changes

**Step 1: Fetch Goals with Progress**
```jsx
const fetchUserGoals = async () => {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.GOALS.MY_GOALS
    );
    
    // Get detailed progress for each goal
    const goalsWithProgress = await Promise.all(
      response.data.map(async (goal) => {
        const progressResponse = await axiosInstance.get(
          API_ENDPOINTS.GOALS.PROGRESS_HISTORY(goal.id)
        );
        return {
          ...goal,
          progress_history: progressResponse.data
        };
      })
    );
    
    setGoals(goalsWithProgress);
  } catch (error) {
    console.error('Error fetching goals:', error);
  }
};
```

**Step 2: Show Goal Progress**
```jsx
{goals.map(goal => (
  <GoalCard
    key={goal.id}
    goal={goal}
    onUpdateProgress={updateGoalProgress}
    onComplete={completeGoal}
  />
))}
```

**Step 3: Track Milestone Completion**
```jsx
const completeMilestone = async (milestoneId) => {
  try {
    await axiosInstance.post(
      API_ENDPOINTS.GOALS.COMPLETE_MILESTONE(milestoneId)
    );
    
    // Refresh goals
    fetchUserGoals();
    
    showNotification('Milestone completed!', 'success');
  } catch (error) {
    console.error('Error completing milestone:', error);
  }
};
```

---

## 📋 PHASE 7: PRACTICE SESSIONS PAGE (Week 3)

### File: `src/pages/Practice.jsx`

#### Required Changes

**Step 1: Start Practice Session**
```jsx
const startPracticeSession = async () => {
  try {
    const response = await axiosInstance.post(
      API_ENDPOINTS.PRACTICE.START_SESSION,
      {
        learning_path_id: selectedPath?.id,
        focus_area: focusSkill,
        duration_minutes: sessionDuration
      }
    );
    
    setCurrentSession(response.data);
    generateQuestionsForSession(response.data.id);
  } catch (error) {
    console.error('Error starting practice:', error);
  }
};
```

**Step 2: Generate and Display Questions**
```jsx
const generateQuestionsForSession = async (sessionId) => {
  try {
    const response = await axiosInstance.post(
      API_ENDPOINTS.PRACTICE.SESSION_GENERATE_QUESTIONS(sessionId),
      {
        count: 10,
        difficulty: estimatedDifficulty,
        topics: selectedTopics
      }
    );
    
    setQuestions(response.data.questions);
    setCurrentQuestionIndex(0);
  } catch (error) {
    console.error('Error generating questions:', error);
  }
};
```

**Step 3: Submit Answers**
```jsx
const submitAnswer = async (answer) => {
  try {
    const response = await axiosInstance.post(
      API_ENDPOINTS.PRACTICE.SESSION_SUBMIT_ANSWER(currentSession.id),
      {
        question_id: currentQuestion.id,
        user_answer: answer,
        time_taken: timeSpent
      }
    );
    
    setFeedback(response.data.feedback);
    setPerformanceScore(response.data.score);
    
    // Move to next question
    setTimeout(() => {
      setCurrentQuestionIndex(prev => prev + 1);
    }, 2000);
  } catch (error) {
    console.error('Error submitting answer:', error);
  }
};
```

---

## 📋 PHASE 8: ONBOARDING FLOW (Week 3)

### File: `src/pages/Onboarding.jsx`

#### Required Changes

**Step 1: Add Learning Path Selection**
```jsx
const [onboardingStep, setOnboardingStep] = useState(0);
// Steps: 0=assessment, 1=results, 2=goals, 3=path-select, 4=vocab-baseline, 5=complete

const handlePathSelection = async (pathId, level) => {
  try {
    await axiosInstance.post(
      API_ENDPOINTS.LEARNING_PATHS.ENROLL_PATH(pathId),
      { starting_level: level }
    );
    
    setSelectedPath({ id: pathId, level });
    setOnboardingStep(4);
  } catch (error) {
    console.error('Error selecting path:', error);
  }
};
```

**Step 2: Complete Onboarding**
```jsx
const completeOnboarding = async () => {
  try {
    await axiosInstance.post(
      API_ENDPOINTS.ONBOARDING.COMPLETE,
      {
        goals: selectedGoals,
        learning_path: selectedPath,
        preferences: userPreferences
      }
    );
    
    navigate('/dashboard');
  } catch (error) {
    console.error('Error completing onboarding:', error);
  }
};
```

---

## 🔄 SERVICE FILES TO UPDATE

### File: `src/services/learningPathService.js`

**Add This Method**:
```javascript
async getNextActivity(params = {}) {
  try {
    const response = await axiosInstance.post(
      API_ENDPOINTS.LEARNING_PATH.NEXT_ACTIVITY,
      params
    );
    return response.data;
  } catch (error) {
    console.error("Error getting next activity:", error);
    throw error;
  }
}

async completeActivity(data) {
  try {
    const response = await axiosInstance.post(
      API_ENDPOINTS.LEARNING_PATH.COMPLETE_ACTIVITY,
      data
    );
    return response.data;
  } catch (error) {
    console.error("Error completing activity:", error);
    throw error;
  }
}

async getCurriculum() {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.LEARNING_PATH.CURRICULUM
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching curriculum:", error);
    throw error;
  }
}
```

### File: `src/services/analyticsService.js`

**Add These Methods**:
```javascript
async getPerformanceTrends(days = 30) {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.ANALYTICS.PERFORMANCE_TRENDS,
      { params: { days } }
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching trends:", error);
    throw error;
  }
}

async getSkillBreakdown() {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.ANALYTICS.SKILL_BREAKDOWN
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching skill breakdown:", error);
    throw error;
  }
}

async getLearningPatterns() {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.ANALYTICS.LEARNING_PATTERNS
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching patterns:", error);
    throw error;
  }
}

async getDifficultyProgression(days = 30) {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.ANALYTICS.DIFFICULTY_PROGRESSION,
      { params: { days } }
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching difficulty progression:", error);
    throw error;
  }
}

async getVocabularyAnalytics() {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.ANALYTICS.VOCABULARY_ANALYTICS
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching vocabulary analytics:", error);
    throw error;
  }
}
```

### File: `src/services/vocabularyService.js`

**Add These Methods**:
```javascript
async getSpacedRepetitionDue() {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.VOCABULARY.SPACED_REPETITION
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching spaced repetition words:", error);
    throw error;
  }
}

async submitPracticeResult(wordId, data) {
  try {
    const response = await axiosInstance.post(
      API_ENDPOINTS.VOCABULARY.PRACTICE_RESULT(wordId),
      data
    );
    return response.data;
  } catch (error) {
    console.error("Error submitting practice result:", error);
    throw error;
  }
}

async getVocabularyStats() {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.VOCABULARY.STATS
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching vocabulary stats:", error);
    throw error;
  }
}
```

### File: `src/services/goalsService.js`

**Add These Methods**:
```javascript
async updateGoalProgress(goalId, data) {
  try {
    const response = await axiosInstance.post(
      API_ENDPOINTS.GOALS.UPDATE_PROGRESS(goalId),
      data
    );
    return response.data;
  } catch (error) {
    console.error("Error updating goal progress:", error);
    throw error;
  }
}

async getProgressHistory(goalId) {
  try {
    const response = await axiosInstance.get(
      API_ENDPOINTS.GOALS.PROGRESS_HISTORY(goalId)
    );
    return response.data;
  } catch (error) {
    console.error("Error fetching progress history:", error);
    throw error;
  }
}

async completeMilestone(milestoneId) {
  try {
    const response = await axiosInstance.post(
      API_ENDPOINTS.GOALS.COMPLETE_MILESTONE(milestoneId)
    );
    return response.data;
  } catch (error) {
    console.error("Error completing milestone:", error);
    throw error;
  }
}
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Week 1 (Critical - Core Flow)
- [ ] Dashboard shows next recommended activity from /learning-path/next-activity
- [ ] Activities page calls AI orchestrator
- [ ] Activity completion calls /learning-path/complete-activity
- [ ] Vocabulary page shows spaced repetition items
- [ ] learningPathService updated with new methods
- [ ] Test: Full activity start → complete → next activity flow

### Week 2 (High Priority - Data & Analytics)
- [ ] Analytics Dashboard calls all 6 endpoints
- [ ] Charts rendering real data
- [ ] LearningPaths page shows curriculum structure
- [ ] Practice page functional end-to-end
- [ ] analyticsService updated with all methods
- [ ] Test: All analytics data displaying correctly

### Week 3 (High Priority - User Experience)
- [ ] Goals page shows progress tracking
- [ ] Onboarding flow complete with path selection
- [ ] goalsService updated with progress methods
- [ ] practiceService fully functional
- [ ] No mock data in any production components
- [ ] Test: Full user journey from login to activity completion

---

## 🧪 TESTING COMMANDS

```bash
# Test all endpoints are reachable
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/learning-path/next-activity

# Test specific endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/analytics/dashboard-summary

# Check API connectivity
npm run test:api

# Run full integration tests
npm run test:integration
```

---

## 📞 TROUBLESHOOTING

### Common Issues

1. **401 Unauthorized Errors**
   - Ensure token is in localStorage
   - Check Authorization header in interceptor
   - Verify token not expired

2. **404 Endpoints Not Found**
   - Verify backend route exists
   - Check API_ENDPOINTS config mapping
   - Ensure Flask app registered route

3. **CORS Issues**
   - Check Flask CORS configuration
   - Verify API_BASE_URL in .env
   - Test with curl first

4. **Mock Data Still Showing**
   - Search for hardcoded mock data
   - Replace all mock data with API calls
   - Check state initialization

---

**Document Version**: 1.0  
**Status**: Ready to Implement  
**Last Updated**: October 22, 2025
