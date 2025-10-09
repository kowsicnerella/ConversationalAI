import axios from 'axios';

// API base URL
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    console.log('🔑 Request interceptor - Token present:', !!token);
    console.log('🔑 Token length:', token?.length);
    console.log('🔑 Token preview:', token?.substring(0, 20) + '...');
    console.log('📡 Request URL:', config.url);
    console.log('📡 Request Method:', config.method);
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('✅ Authorization header set');
    } else {
      console.warn('⚠️ No token found in localStorage');
    }
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response) => {
    console.log('✅ Response received:', response.config.url, response.status);
    return response;
  },
  (error) => {
    console.error('❌ Response error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers,
    });
    
    if (error.response?.status === 401) {
      console.warn('🔒 401 Unauthorized - Clearing auth and redirecting to login');
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    } else if (error.response?.status === 422) {
      console.error('⚠️ 422 Unprocessable Entity - Likely JWT validation issue');
      console.error('Response data:', error.response?.data);
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;

// API Endpoints - Complete mapping of all backend routes
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  
  // User Management
  USER: {
    PROFILE: '/user/profile',
    UPDATE_PROFILE: '/user/profile',
    SETTINGS: '/user/settings',
    CHANGE_PASSWORD: '/user/change-password',
    STATISTICS: '/user/statistics',
    DELETE_ACCOUNT: '/user/delete-account',
    HISTORY: (userId) => `/user/history/${userId}`,
    LEARNING_PATHS: (userId) => `/user/learning-paths/${userId}`,
    CREATE_LEARNING_PATH: '/user/learning-paths',
    ACTIVITY_COMPLETION: '/user/activity-completion',
    DASHBOARD: (userId) => `/user/dashboard/${userId}`,
  },
  
  // Activities
  ACTIVITIES: {
    // New Activity System (Quiz, Flashcards, Writing & Role-Play)
    GENERATE_QUIZ: '/activities/generate-quiz',
    GENERATE_FLASHCARDS: '/activities/generate-flashcards',
    GENERATE_WRITING_PROMPT: '/activities/generate-writing-prompt',
    GENERATE_ROLEPLAY: '/activities/generate-role-play',
    CONVERSATION: '/activities/conversation',
    COMPLETE_ROLEPLAY: '/activities/complete-roleplay',
    SUBMIT: '/activities/submit',
    TOPICS: '/activities/topics',
    HISTORY: '/activities/history',
    
    // Legacy Generation endpoints
    GENERATE_READING: '/activity/generate/reading',
    GENERATE_WRITING: '/activity/generate/writing-prompt',
    LEGACY_GENERATE_ROLEPLAY: '/activity/generate/role-play',
    
    // Activity management
    LIST: '/activity/all',
    DETAIL: (id) => `/activity/${id}/details`,
    SUBMIT_LEGACY: (id) => `/activity/${id}/submit`,
    UPDATE: (id) => `/activity/${id}/update`,
    DELETE: (id) => `/activity/${id}/delete`,
    SAVE: '/activity/save',
    
    // Activity queries
    BY_TYPE: (type) => `/activity/by-type/${type}`,
    BY_PATH: (pathId) => `/activity/path/${pathId}`,
    USER_ACTIVITIES: '/activity/user-activities',
    MY_GENERATED: '/activity/my-generated',
    NEXT_ACTIVITY: '/activity/next-activity',
    
    // Learning path activities
    LEARNING_PATH_ACTIVITIES: (pathId) => `/activity/learning-path/${pathId}/activities`,
    
    // Progress
    PROGRESS_SUMMARY: '/activity/user-progress/summary',
    
    // Other
    ANALYZE_IMAGE: '/activity/analyze-image',
    CHAT: '/activity/chat',
    FEEDBACK: '/activity/feedback',
  },
  
  // Courses & Learning Paths
  COURSES: {
    LEARNING_PATHS: '/courses/learning-paths',
    PATH_DETAIL: (id) => `/courses/learning-paths/${id}`,
    ENROLL: '/courses/enroll',
    ENROLL_PATH: (id) => `/courses/learning-paths/${id}/enroll`,
    PROGRESS: (id) => `/courses/enrollment/${id}/progress`,
    MY_PATHS: '/courses/my-learning-paths',
    START_ACTIVITY: '/courses/start-activity',
    START_ACTIVITY_BY_ID: (id) => `/courses/activities/${id}/start`,
    COMPLETE_ACTIVITY: (id) => `/courses/activities/${id}/complete`,
  },
  
  // Learning Path Advanced
  LEARNING_PATHS: {
    PERSONALIZED_RECOMMENDATION: '/learning-paths/personalized-recommendation',
    CREATE_CUSTOM: '/learning-paths/create-custom-path',
    ADAPTIVE_DIFFICULTY: '/learning-paths/adaptive-difficulty',
    PROGRESS_ANALYSIS: (id) => `/learning-paths/progress-analysis/${id}`,
  },
  
  // Chat & Conversations
  CHAT: {
    CONVERSATIONS: '/chat/conversations',
    MESSAGES: (id) => `/chat/conversations/${id}/messages`,
    SEND_MESSAGE: (id) => `/chat/conversations/${id}/message`,
    QUICK_CHAT: '/chat/quick-chat',
    SEND: '/chat/send-message',
    FEEDBACK: (id) => `/chat/conversations/${id}/feedback`,
    POST_FEEDBACK: '/chat/feedback',
    SUGGESTIONS: '/chat/suggestions',
    CHAT_SUGGESTIONS: '/chat/chat-suggestions',
    PRACTICE_ASSISTANT: '/chat/practice-assistant',
    PRACTICE_CHAT: (id) => `/chat/practice-assistant/${id}/chat`,
  },
  
  // Gamification (Updated for new backend implementation)
  GAMIFICATION: {
    // Core endpoints (JWT-protected)
    POINTS: '/gamification/points',                    // GET - User's total points & rank
    BADGES: '/gamification/badges',                    // GET - Earned + available badges with progress
    LEADERBOARD: '/gamification/leaderboard',          // GET - Ranked user list (query: timeframe, limit)
    STATS: '/gamification/stats',                      // GET - Comprehensive gamification stats
    ACHIEVEMENTS: '/gamification/achievements',        // GET - Achievement history
    DAILY_CHALLENGE: '/gamification/daily-challenge',  // GET/POST - Get or complete daily challenge
    
    // Legacy endpoints (for backward compatibility)
    USER_BADGES: (userId) => `/gamification/badges/${userId}`,
    USER_STATS: (userId) => `/gamification/stats/${userId}`,
    CHECK_ACHIEVEMENTS: (userId) => `/gamification/check-achievements/${userId}`,
    UPDATE_STREAK: (userId) => `/gamification/streak/${userId}`,
    PROFILE: '/gamification/profile',
    REWARD: (id) => `/gamification/rewards/${id}`,
  },
  
  // Vocabulary
  VOCABULARY: {
    WORDS: '/vocabulary/words',
    WORD_DETAIL: (id) => `/vocabulary/words/${id}`,
    UPDATE_WORD: (id) => `/vocabulary/words/${id}`,
    DELETE_WORD: (id) => `/vocabulary/words/${id}`,
    EXAMPLES: (id) => `/vocabulary/words/${id}/examples`,
    PRACTICE_RESULT: (id) => `/vocabulary/words/${id}/practice-result`,
    STATS: '/vocabulary/stats',
    PRACTICE_FLASHCARDS: '/vocabulary/practice-flashcards',
    LIST: '/vocabulary',
    SEARCH: '/vocabulary/search',
    PRACTICE: '/vocabulary/practice',
    SPACED_REPETITION: '/vocabulary/spaced-repetition',
  },
  
  // Analytics
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard-summary',
    PERFORMANCE_TRENDS: '/analytics/learning-trends',
    LEARNING_STREAKS: '/analytics/learning-trends',
    SKILL_BREAKDOWN: '/analytics/performance-analysis',
    TIME_SPENT: '/analytics/engagement-analytics',
    DIFFICULTY_PROGRESSION: '/analytics/difficulty-progression',
    LEARNING_TIMELINE: '/analytics/learning-pattern-recognition',
    COMPREHENSIVE_REPORT: '/analytics/export/progress-report',
    PROGRESS: '/analytics/dashboard-summary',
    PERFORMANCE: '/analytics/performance-analysis',
    LEARNING_PATTERNS: '/analytics/learning-pattern-recognition',
    VOCABULARY_ANALYTICS: '/analytics/vocabulary-analytics',
    ACTIVITY_PERFORMANCE: '/analytics/activity-performance-analysis',
    PREDICTIVE: '/analytics/predictive-analytics',
  },
  
  // Enhanced Analytics
  ENHANCED_ANALYTICS: {
    PERFORMANCE_TRENDS: '/enhanced-analytics/performance-trends',
    LEARNING_STREAKS: '/enhanced-analytics/learning-streaks',
    SKILL_BREAKDOWN: '/enhanced-analytics/skill-breakdown',
    TIME_SPENT: '/enhanced-analytics/time-spent',
    DIFFICULTY_PROGRESSION: '/enhanced-analytics/difficulty-progression',
    LEARNING_TIMELINE: '/enhanced-analytics/learning-timeline',
    COMPREHENSIVE_REPORT: '/enhanced-analytics/comprehensive-report',
  },
  
  // Enhanced Assessment
  ENHANCED_ASSESSMENT: {
    QUESTION_ANALYSIS: (id) => `/enhanced-assessment/${id}/question-analysis`,
    COMPARATIVE_REPORT: (id) => `/enhanced-assessment/${id}/comparative-report`,
    SKILL_PROGRESSION: '/enhanced-assessment/skill-progression',
  },
  
  // Enhanced Activity
  ENHANCED_ACTIVITY: {
    QUESTION_BREAKDOWN: (id) => `/enhanced-activity/${id}/question-breakdown`,
    PERFORMANCE_HISTORY: '/enhanced-activity/performance-history',
  },
  
  // Personalization
  PERSONALIZATION: {
    GOALS: '/personalization/goals',
    START_ASSESSMENT: '/personalization/assessment/start',
    RESPOND_ASSESSMENT: (id) => `/personalization/assessment/${id}/respond`,
    COMPLETE_ASSESSMENT: (id) => `/personalization/assessment/${id}/complete`,
    DASHBOARD: '/personalization/dashboard',
    START_SESSION: '/personalization/session/start',
    END_SESSION: (id) => `/personalization/session/${id}/end`,
    TRACK_VOCABULARY: '/personalization/vocabulary/track',
    VOCABULARY: '/personalization/vocabulary',
    PRACTICE_VOCABULARY: (id) => `/personalization/vocabulary/${id}/practice`,
    INSIGHTS: '/personalization/insights',
    PREFERENCES: '/personalization/preferences',
  },
  
  // Adaptive Learning
  ADAPTIVE: {
    RECOMMENDATIONS: '/adaptive/recommendations',
    LEARNING_PROFILE: '/adaptive/learning-profile',
    ADJUST_DIFFICULTY: '/adaptive/adjust-difficulty',
    LEARNING_PACE: '/adaptive/learning-pace',
  },
  
  // Chapters
  CHAPTERS: {
    LIST: (pathId) => `/chapters/learning-path/${pathId}`,
    DETAIL: (id) => `/chapters/${id}`,
    PROGRESS: (id) => `/chapters/${id}/progress`,
    START: (id) => `/chapters/${id}/start`,
    COMPLETE: (id) => `/chapters/${id}/complete`,
  },
  
  // Practice
  PRACTICE: {
    GENERATE_QUESTIONS: '/practice/generate-questions',
    SUBMIT_ANSWER: '/practice/submit-answer',
    COMPLETE: (id) => `/practice/${id}/complete`,
    SESSIONS: '/practice/sessions',
    START: '/practice/start',
    SUBMIT: '/practice/submit',
  },
  
  // Tests & Assessments
  TESTS: {
    CREATE: '/tests/create',
    START: (id) => `/tests/${id}/start`,
    SUBMIT: (id) => `/tests/${id}/submit`,
    RESULTS: (id) => `/tests/${id}/results`,
    HISTORY: '/tests/history',
  },
  
  // Assessment
  ASSESSMENT: {
    GENERATE: '/assessment/generate',
    START: '/assessment/start',
    INITIAL: '/assessment/initial',
    SUBMIT_ANSWER: (id) => `/assessment/${id}/submit-answer`,
    COMPLETE: (id) => `/assessment/${id}/complete`,
    RESULTS: (id) => `/assessment/${id}/results`,
    SUBMIT: '/assessment/submit',
  },
  
  // Media
  MEDIA: {
    UPLOAD_IMAGE: '/media/upload/image',
    UPLOAD_AUDIO: '/media/upload/audio',
    RECORD_VOICE: '/media/record/voice',
    GENERATE_PRONUNCIATION: '/media/generate/pronunciation-exercise',
    FILES: (filename) => `/media/files/${filename}`,
    MY_UPLOADS: '/media/my-uploads',
    UPLOAD: '/media/upload',
    ANALYZE: '/media/analyze',
  },
  
  // Notifications
  NOTIFICATIONS: {
    LIST: '/notifications',
    MARK_READ: (id) => `/notifications/mark-read/${id}`,
    MARK_ALL_READ: '/notifications/mark-all-read',
    PREFERENCES: '/notifications/preferences',
    SEND: '/notifications/send',
    CREATE_SAMPLES: (userId) => `/notifications/create-samples/${userId}`,
  },
  
  // Onboarding Workflow
  ONBOARDING: {
    STATUS: '/onboarding/status',
    UPDATE_STATUS: '/onboarding/status',
    COMPLETE: '/onboarding/complete',
    PROGRESS_SNAPSHOT: '/onboarding/progress/snapshot',
  },
  
  // Lesson Management
  LESSON: {
    COMPLETE: '/lesson/complete',
    REVIEW: (id) => `/lesson/review/${id}`,
    REVIEWS: '/lesson/reviews',
    NEXT: '/lesson/next',
  },
};
