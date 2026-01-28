import axios from 'axios';

// API base URL
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// ===== Request Deduplication Cache =====
// Tracks pending GET requests to prevent duplicate simultaneous requests
const requestCache = new Map();

// Create a key for caching based on method and URL
const getCacheKey = (config) => {
  return `${config.method.toUpperCase()}:${config.url}`;
};

// Create axios instance
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token and deduplicate requests
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

    // ===== Deduplication for GET requests =====
    if (config.method.toUpperCase() === 'GET') {
      const cacheKey = getCacheKey(config);
      
      // If a similar request is already pending, return that promise instead
      if (requestCache.has(cacheKey)) {
        console.log('🔄 DEDUPLICATING: Already fetching', cacheKey);
        config.adapter = () => requestCache.get(cacheKey);
      }
    }

    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and cache cleanup
axiosInstance.interceptors.response.use(
  (response) => {
    console.log('✅ Response received:', response.config.url, response.status);
    
    // Clean up cache after successful response
    if (response.config.method.toUpperCase() === 'GET') {
      const cacheKey = getCacheKey(response.config);
      requestCache.delete(cacheKey);
    }
    
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

    // Clean up cache on error
    if (error.config?.method?.toUpperCase() === 'GET') {
      const cacheKey = getCacheKey(error.config);
      requestCache.delete(cacheKey);
    }
    
    if (error.response?.status === 401) {
      console.warn('🔒 401 Unauthorized - Token invalid or expired');
      
      // Only redirect if:
      // 1. We actually HAD a token (this was a real auth failure, not just missing token)
      // 2. We're not already on the login page (prevent redirect loop)
      const hadToken = localStorage.getItem('access_token');
      const currentPath = window.location.pathname;
      
      // Clear auth data
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      
      // Only redirect if we had a token and we're not already on login/register
      if (hadToken && currentPath !== '/login' && currentPath !== '/register') {
        console.warn('🔒 Redirecting to login due to expired/invalid token');
        window.location.href = '/login';
      } else if (!hadToken) {
        console.log('ℹ️ No token present, skipping redirect (likely already logged out)');
      } else {
        console.log('ℹ️ Already on auth page, skipping redirect to prevent loop');
      }
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
    STATUS: '/user/status', // User onboarding and navigation status
    CAN_ACCESS: (routePath) => `/user/can-access/${routePath}`, // Route access check
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
    // Phase 9 Enhanced Gamification Core endpoints (JWT-protected, registered at /api/gamification-v2)
    POINTS: '/gamification-v2/points',                    // GET - User's total points & rank
    BADGES: '/gamification-v2/badges',                    // GET - Earned + available badges with progress
    LEADERBOARD: '/gamification-v2/leaderboard',          // GET - Ranked user list (query: timeframe, limit)
    STATS: '/gamification-v2/stats',                      // GET - Comprehensive gamification stats
    ACHIEVEMENTS: '/gamification-v2/achievements',        // GET - Achievement history
    DAILY_CHALLENGE: '/gamification-v2/daily-challenge',  // GET/POST - Get or complete daily challenge
    
    // Phase 9 Enhanced endpoints
    STREAK: '/gamification-v2/streak',                    // GET - User's streak information
    STREAK_FREEZE: '/gamification-v2/streak/freeze',      // POST - Use streak freeze
    STREAK_UPDATE: '/gamification-v2/streak/update',      // POST - Update streak
    SUMMARY: '/gamification-v2/summary',                  // GET - Comprehensive gamification summary
    
    // Legacy endpoints (for backward compatibility)
    USER_BADGES: (userId) => `/gamification-v2/badges/${userId}`,
    USER_STATS: (userId) => `/gamification-v2/stats/${userId}`,
    CHECK_ACHIEVEMENTS: (userId) => `/gamification-v2/check-achievements/${userId}`,
    UPDATE_STREAK: (userId) => `/gamification-v2/streak/${userId}`,
    PROFILE: '/gamification-v2/profile',
    REWARD: (id) => `/gamification-v2/rewards/${id}`,
  },
  
  // Vocabulary (Old API - backward compatible)
  VOCABULARY: {
    // Legacy endpoints (old API at /api/vocabulary)
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
  
  // Vocabulary Mastery v2 (Phase 5 - SM-2 Spaced Repetition)
  VOCABULARY_V2: {
    INTRODUCE: '/vocabulary-v2/introduce',
    INTRODUCE_FROM_TEXT: '/vocabulary-v2/introduce-from-text',
    ADD_TO_VOCABULARY: '/vocabulary-v2/add-to-my-vocabulary',
    WORDS_DUE: '/vocabulary-v2/words-due',
    REVIEW: '/vocabulary-v2/review',
    PRACTICE_SESSION_START: '/vocabulary-v2/practice-session/start',
    PRACTICE_SESSION_COMPLETE: (sessionId) => `/vocabulary-v2/practice-session/${sessionId}/complete`,
    PRACTICE_ACTIVITY: '/vocabulary-v2/practice-activity',
    MASTERY: '/vocabulary-v2/mastery',
    WORD_NETWORK: (itemId) => `/vocabulary-v2/word-network/${itemId}`,
    RELATED_WORDS: '/vocabulary-v2/related-words',
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
    RECOMMENDATIONS: '/adaptive/recommendations',              // GET - Personalized activity recommendations
    PERFORMANCE_ANALYSIS: '/adaptive/performance-analysis',    // GET - Performance analysis (query: days)
    NEXT_ACTIVITIES: '/adaptive/next-activities',             // GET - Next recommended activities
    LEARNING_GAPS: '/adaptive/learning-gaps',                 // GET - Identify learning gaps
    LEARNING_PROFILE: '/adaptive/learning-profile',           // GET - User learning profile
    ADJUST_DIFFICULTY: '/adaptive/adjust-difficulty',         // POST - Adjust difficulty dynamically
    LEARNING_PACE: '/adaptive/learning-pace',                 // GET - Learning pace analysis
  },
  
  // AI-Personalized Learning Path (New intelligent orchestrator system)
  LEARNING_PATH: {
    NEXT_ACTIVITY: '/learning-path/next-activity',           // POST - Get next personalized activity
    COMPLETE_ACTIVITY: '/learning-path/complete-activity',   // POST - Complete activity & update progress
    PROGRESS: (userId) => `/learning-path/progress/${userId}`, // GET - User learning path progress
    NODES: '/learning-path/nodes',                           // GET - All learning nodes
    LEVELS: '/learning-path/levels',                         // GET - All curriculum levels
    NODE_DETAIL: (nodeId) => `/learning-path/node/${nodeId}`, // GET - Learning node details
    STATS: '/learning-path/stats',                           // GET - Learning statistics
    CURRICULUM: '/learning-path/curriculum',                  // GET - Full curriculum structure
  },
  
  // Goals & Achievements
  GOALS: {
    AVAILABLE: '/goals/available',                              // GET - List all goal templates
    CREATE: '/goals/create',                                    // POST - Create new goal
    MY_GOALS: '/goals/my-goals',                               // GET - User's goals (query: status)
    DETAIL: (id) => `/goals/${id}`,                            // GET - Goal detail with milestones
    UPDATE_PROGRESS: (id) => `/goals/${id}/update-progress`,   // POST - Update goal progress
    COMPLETE: (id) => `/goals/${id}/complete`,                 // POST - Complete goal
    ABANDON: (id) => `/goals/${id}/abandon`,                   // POST - Abandon goal
    CREATE_MILESTONE: (id) => `/goals/${id}/milestones`,       // POST - Create milestone
    COMPLETE_MILESTONE: (milestoneId) => `/goals/milestones/${milestoneId}/complete`, // POST
    PROGRESS_HISTORY: (id) => `/goals/${id}/progress-history`, // GET - Progress timeline
    CERTIFICATES: '/goals/certificates',                        // GET - List certificates
    CERTIFICATE_DETAIL: (id) => `/goals/certificates/${id}`,   // GET - Certificate detail
    CERTIFICATE_DOWNLOAD: (id) => `/goals/certificates/${id}/download`, // GET - Download PDF
  },
  
  // Chapters
  CHAPTERS: {
    LIST: (pathId) => `/chapters/learning-path/${pathId}`,
    DETAIL: (id) => `/chapters/${id}`,
    PROGRESS: (id) => `/chapters/${id}/progress`,
    START: (id) => `/chapters/${id}/start`,
    COMPLETE: (id) => `/chapters/${id}/complete`,
  },
  
  // Practice Sessions
  PRACTICE: {
    GENERATE_QUESTIONS: '/practice/generate-questions',       // POST - Generate questions without session
    SUBMIT_ANSWER: '/practice/submit-answer',                 // POST - Submit answer without session
    START_SESSION: '/practice/start',                         // POST - Start practice session
    SESSION_GENERATE_QUESTIONS: (sessionId) => `/practice/practice/${sessionId}/generate-questions`, // POST
    SESSION_SUBMIT_ANSWER: (sessionId) => `/practice/practice/${sessionId}/submit-answer`,          // POST
    COMPLETE_SESSION: (sessionId) => `/practice/${sessionId}/complete`,  // POST - Complete session
    SESSION_RESULTS: (sessionId) => `/practice/${sessionId}/results`,    // GET - Get session results
    HISTORY: '/practice/history',                             // GET - Practice history
    SESSIONS: '/practice/sessions',                           // GET - All sessions
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
    GENERATE_AI_QUESTIONS: '/assessment/generate-ai-questions',
    REGENERATE: (id) => `/assessment/${id}/regenerate`,
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
