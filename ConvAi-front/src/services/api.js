import axios from 'axios';
import { useAuthStore } from '../store';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  refreshToken: (refreshToken) => api.post('/auth/refresh', {}, {
    headers: { Authorization: `Bearer ${refreshToken}` }
  }),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (newPassword, resetToken) => 
    api.post('/auth/reset-password', { new_password: newPassword }, {
      headers: { Authorization: `Bearer ${resetToken}` }
    }),
  logout: () => api.post('/auth/logout'),
};

// User API
export const userAPI = {
  getProfile: () => api.get('/user/profile'),
  updateProfile: (profileData) => api.put('/user/profile', profileData),
  getSettings: () => api.get('/user/settings'),
  updateSettings: (settings) => api.put('/user/settings', settings),
  changePassword: (passwords) => api.post('/user/change-password', passwords),
  getStatistics: () => api.get('/user/statistics'),
  deleteAccount: () => api.delete('/user/delete-account'),
  getDashboard: (userId) => api.get(`/user/dashboard/${userId}`),
  getProgress: (userId, pathId) => api.get(`/user/progress/${userId}/${pathId}`),
  getHistory: (userId) => api.get(`/user/history/${userId}`),
  getLearningPaths: (userId) => api.get(`/user/learning-paths/${userId}`),
  createLearningPath: (pathData) => api.post('/user/learning-paths', pathData),
  logActivityCompletion: (completionData) => api.post('/user/activity-completion', completionData),
};

export const coursesAPI = {
  getLearningPaths: () => api.get('/courses/learning-paths'),
  getLearningPathDetails: (id) => api.get(`/courses/learning-paths/${id}`),
  enroll: (learning_path_id) => api.post('/courses/enroll', { learning_path_id }),
  getEnrollmentProgress: (enrollment_id) => api.get(`/courses/enrollment/${enrollment_id}/progress`),
  startActivity: (enrollment_id, activity_id) => api.post('/courses/start-activity', { enrollment_id, activity_id }),
  completeActivity: (enrollment_id, activity_id, score, time_spent_minutes) =>
    api.post('/courses/complete-activity', { enrollment_id, activity_id, score, time_spent_minutes }),
};

// Activity API
export const activityAPI = {
  generateQuiz: (quizData) => api.post('/activity/generate/quiz', quizData),
  generateFlashcards: (flashcardData) => api.post('/activity/generate/flashcards', flashcardData),
  generateReading: (readingData) => api.post('/activity/generate/reading', readingData),
  generateWritingPrompt: (promptData) => api.post('/activity/generate/writing-prompt', promptData),
  generateRolePlay: (rolePlayData) => api.post('/activity/generate/role-play', rolePlayData),
  analyzeImage: (imageData) => api.post('/activity/analyze-image', imageData),
  getWritingFeedback: (writingData) => api.post('/activity/feedback', writingData),
  saveActivity: (activityData) => api.post('/activity/save', activityData),
  getPathActivities: (pathId) => api.get(`/activity/path/${pathId}`),
};

// Media API
export const mediaAPI = {
  uploadImage: (formData) => api.post('/media/upload/image', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  uploadAudio: (formData) => api.post('/media/upload/audio', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getMediaFiles: () => api.get('/media/files'),
  generatePronunciationExercise: (data) => api.post('/media/pronunciation-exercise', data),
  serveFile: (filename) => api.get(`/media/serve/${filename}`),
};

// Analytics API
export const analyticsAPI = {
  getDashboardSummary: () => api.get('/analytics/dashboard-summary'),
  getLearningTrends: (days = 30) => api.get(`/analytics/learning-trends?days=${days}`),
  getPerformanceAnalysis: () => api.get('/analytics/performance-analysis'),
  getVocabularyAnalytics: () => api.get('/analytics/vocabulary-analytics'),
  exportProgressReport: (type = 'summary') => api.get(`/analytics/export/progress-report?type=${type}`),
  getWeeklyReport: () => api.get('/analytics/weekly-report'),
  getMonthlyReport: () => api.get('/analytics/monthly-report'),
  getSkillProgress: () => api.get('/analytics/skill-progress'),
  getActivityBreakdown: () => api.get('/analytics/activity-breakdown'),
};

// Gamification API
export const gamificationAPI = {
  getUserBadges: (userId) => api.get(`/gamification/badges/${userId}`),
  getAvailableBadges: () => api.get('/gamification/badges/available'),
  checkAchievements: (userId) => api.post(`/gamification/check-achievements/${userId}`),
  updateStreak: (userId) => api.post(`/gamification/streak/${userId}`),
  getLeaderboard: () => api.get('/gamification/leaderboard'),
  getDailyChallenge: (userId) => api.get(`/gamification/daily-challenge/${userId}`),
  getAchievements: () => api.get('/gamification/achievements'),
  getGamificationStats: (userId) => api.get(`/gamification/stats/${userId}`),
};

// Chat API
export const chatAPI = {
  getConversations: () => api.get('/chat/conversations'),
  sendMessage: (message, conversation_id, conversation_type = 'learning_chat') =>
    api.post('/chat/send-message', { message, conversation_id, conversation_type }),
  quickChat: (message, context = '') => api.post('/chat/quick-chat', { message, context }),
  getSuggestions: (topic = '', level = '') => api.get(`/chat/suggestions?topic=${topic}&level=${level}`),
  startLearningSession: (sessionData) => api.post('/chat/learning-session/start', sessionData),
  endLearningSession: (sessionId, satisfaction) => api.post(`/chat/learning-session/${sessionId}/end`, { user_satisfaction: satisfaction }),
  getAIResponse: (messageData) => api.post('/chat/ai-response', messageData),
};

// Personalization API
export const personalizationAPI = {
  setGoals: (goals) => api.post('/personalization/goals', goals),
  startAssessment: () => api.post('/personalization/assessment/start'),
  respondToAssessment: (assessmentId, response) => 
    api.post(`/personalization/assessment/${assessmentId}/respond`, response),
  completeAssessment: (assessmentId) => 
    api.post(`/personalization/assessment/${assessmentId}/complete`),
  getDashboard: () => api.get('/personalization/dashboard'),
  startSession: (sessionData) => api.post('/personalization/session/start', sessionData),
  endSession: (sessionId, satisfaction) => 
    api.post(`/personalization/session/${sessionId}/end`, { user_satisfaction: satisfaction }),
  trackVocabulary: (vocabData) => api.post('/personalization/vocabulary/track', vocabData),
  getVocabulary: (page = 1, limit = 50) => 
    api.get(`/personalization/vocabulary?page=${page}&limit=${limit}`),
  practiceVocabulary: (vocabId, practiceData) => 
    api.post(`/personalization/vocabulary/${vocabId}/practice`, practiceData),
};

// Adaptive Learning API
export const adaptiveLearningAPI = {
  // Comprehensive Assessment
  startComprehensiveAssessment: () => api.post('/adaptive-learning/assessment/comprehensive/start'),
  submitAssessmentResponse: (assessmentId, response) => 
    api.post(`/adaptive-learning/assessment/${assessmentId}/respond`, response),
  completeAssessment: (assessmentId) => 
    api.post(`/adaptive-learning/assessment/${assessmentId}/complete`),
  getAssessmentResults: (assessmentId) => 
    api.get(`/adaptive-learning/assessment/${assessmentId}/results`),

  // Learning Path Generation
  generatePersonalizedPath: (assessmentResults) => 
    api.post('/adaptive-learning/learning-path/generate', assessmentResults),
  getPersonalizedPath: () => 
    api.get('/adaptive-learning/learning-path/current'),
  getNextActivity: (currentActivity = null) => 
    api.post('/adaptive-learning/activity/next', { current_activity: currentActivity }),

  // Real-time Performance Monitoring
  startLearningSession: (activityId, learningPathId = null) => 
    api.post('/adaptive-learning/session/start', {
      activity_id: activityId,
      learning_path_id: learningPathId
    }),
  trackUserInteraction: (sessionId, interactionData) => 
    api.post(`/adaptive-learning/session/${sessionId}/track`, interactionData),
  endLearningSession: (sessionId, results) => 
    api.post(`/adaptive-learning/session/${sessionId}/end`, results),
  getSessionPerformance: (sessionId) => 
    api.get(`/adaptive-learning/session/${sessionId}/performance`),

  // Progress and Analytics
  getAdaptiveProgress: () => 
    api.get('/adaptive-learning/progress'),
  getDetailedAnalytics: (timeframe = 'week') => 
    api.get(`/adaptive-learning/analytics?timeframe=${timeframe}`),
  getLearningRecommendations: () => 
    api.get('/adaptive-learning/recommendations'),
};

// Assessment API
export const assessmentAPI = {
  // Generate assessment
  generateAssessment: (assessmentType = 'comprehensive', skillArea = null) => 
    api.post('/assessment/generate', { 
      assessment_type: assessmentType,
      skill_area: skillArea 
    }),
  
  // Submit assessment answers
  submitAssessment: (assessmentId, answers) => 
    api.post(`/assessment/${assessmentId}/submit`, { answers }),
  
  // Get assessment history
  getHistory: () => api.get('/assessment/history'),
  
  // Get assessment details
  getDetails: (assessmentId) => api.get(`/assessment/${assessmentId}/details`),
  
  // Get assessment report
  getReport: (assessmentId) => api.get(`/assessment/${assessmentId}/report`),
  
  // Retake assessment
  retakeAssessment: (assessmentId) => api.post(`/assessment/${assessmentId}/retake`),
  
  // Get placement recommendations
  getPlacementRecommendations: () => api.get('/assessment/placement-recommendations'),
  
  // Quick proficiency check
  quickCheck: (skillArea) => api.post('/assessment/quick-check', { skill_area: skillArea }),
  
  // Validate answers
  validateAnswers: (questions, answers) => 
    api.post('/assessment/validate-answers', { questions, answers }),
  
  // Health check
  healthCheck: () => api.get('/assessment/health'),
};

// Test API
export const testAPI = {
  createTest: (testData) => api.post('/test/tests/create', testData),
  startTest: (testId) => api.post(`/test/tests/${testId}/start`),
  submitTest: (testId, answers) => api.post(`/test/tests/${testId}/submit`, { answers }),
  getTestResults: (testId) => api.get(`/test/tests/${testId}/results`),
  getTestHistory: () => api.get('/test/tests/history'),
};

// Vocabulary API
export const vocabularyAPI = {
  getWords: (params = {}) => {
    const queryParams = new URLSearchParams(params).toString();
    return api.get(`/vocabulary/words?${queryParams}`);
  },
  addWord: (wordData) => api.post('/vocabulary/words', wordData),
  updateWord: (wordId, wordData) => api.put(`/vocabulary/words/${wordId}`, wordData),
  deleteWord: (wordId) => api.delete(`/vocabulary/words/${wordId}`),
  getWordExamples: (wordId) => api.get(`/vocabulary/words/${wordId}/examples`),
  logPracticeResult: (wordId, resultData) => api.post(`/vocabulary/words/${wordId}/practice-result`, resultData),
  getStats: () => api.get('/vocabulary/stats'),
};

// Notifications API
export const notificationsAPI = {
  getNotifications: (params = {}) => {
    const queryParams = new URLSearchParams(params).toString();
    return api.get(`/notifications?${queryParams}`);
  },
  markAsRead: (notificationId) => api.post(`/notifications/mark-read/${notificationId}`),
  markAllAsRead: () => api.post('/notifications/mark-all-read'),
  getPreferences: () => api.get('/notifications/preferences'),
  updatePreferences: (preferences) => api.post('/notifications/preferences', preferences),
  sendNotification: (notificationData) => api.post('/notifications/send', notificationData),
  createSamples: (userId) => api.post(`/notifications/create-samples/${userId}`),
};

// Offline/Sync API
export const offlineAPI = {
  downloadContent: (contentType) => api.get(`/offline/download/${contentType}`),
  downloadAllContent: () => api.get('/offline/download/all'),
  syncProgress: (progressData) => api.post('/offline/sync/progress', progressData),
  syncAllData: (syncData) => api.post('/offline/sync/all', syncData),
  getOfflineManifest: () => api.get('/offline/manifest'),
  updateOfflineStatus: (statusData) => api.post('/offline/status', statusData),
  checkSyncStatus: () => api.get('/offline/sync/status'),
};

export default api;
