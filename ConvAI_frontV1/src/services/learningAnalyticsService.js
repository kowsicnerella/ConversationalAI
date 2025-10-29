/**
 * Learning Analytics Service - Phase 7
 * Frontend API integration for comprehensive Learning Analytics & Insights
 * 
 * This is separate from the basic analyticsService.js (Phase 4)
 * 
 * Provides methods to interact with all 17 Phase 7 analytics endpoints:
 * - Weekly reports with AI insights
 * - Progress visualization
 * - Predictions (level completion, skill mastery)
 * - Comparisons (peer, self, expected)
 * - Velocity tracking
 * - AI insights
 * - Study sessions
 * - Progress snapshots
 * 
 * @author GitHub Copilot
 * @date October 20, 2025
 * @phase 7 - Learning Analytics & Insights
 */

import axios from 'axios';

// eslint-disable-next-line no-undef
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const ANALYTICS_BASE = `${API_BASE_URL}/api/learning-analytics`;

/**
 * Get JWT token from localStorage
 * @returns {string|null} JWT token
 */
const getAuthToken = () => {
  return localStorage.getItem('token') || sessionStorage.getItem('token');
};

/**
 * Create axios instance with auth headers
 * @returns {object} Axios instance
 */
const createAuthRequest = () => {
  const token = getAuthToken();
  return axios.create({
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
};

/**
 * Handle API errors consistently
 * @param {Error} error - Axios error object
 * @param {string} context - Context for error message
 * @throws {Error} Formatted error
 */
const handleError = (error, context) => {
  console.error(`${context}:`, error);
  
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.error || error.response.data?.message || 'Server error';
    throw new Error(`${context}: ${message}`);
  } else if (error.request) {
    // Request made but no response
    throw new Error(`${context}: No response from server`);
  } else {
    // Error setting up request
    throw new Error(`${context}: ${error.message}`);
  }
};

// ============================================================
// WEEKLY REPORTS
// ============================================================

/**
 * Get weekly learning report
 * @param {number} weekOffset - 0 for current week, -1 for last week, etc.
 * @returns {Promise<object>} Weekly report data
 * 
 * @example
 * const currentWeek = await learningAnalyticsService.getWeeklyReport(0);
 * const lastWeek = await learningAnalyticsService.getWeeklyReport(-1);
 */
export const getWeeklyReport = async (weekOffset = 0) => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/weekly-report`, {
      params: { week_offset: weekOffset },
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch weekly report');
  }
};

/**
 * Get historical weekly reports
 * @param {number} limit - Number of reports to return (max 52)
 * @returns {Promise<object>} List of weekly reports
 * 
 * @example
 * const reports = await learningAnalyticsService.getWeeklyReports(10);
 */
export const getWeeklyReports = async (limit = 10) => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/weekly-reports`, {
      params: { limit },
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch weekly reports');
  }
};

// ============================================================
// PROGRESS VISUALIZATION
// ============================================================

/**
 * Get progress visualization data
 * @param {string} timeRange - '7d', '30d', '90d', '1y', 'all'
 * @returns {Promise<object>} Visualization data (timeline, skills, velocity, milestones)
 * 
 * @example
 * const data = await learningAnalyticsService.getProgressVisualization('30d');
 * // Returns: { timeline: [...], skills: {...}, velocity: [...], milestones: [...] }
 */
export const getProgressVisualization = async (timeRange = '30d') => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/progress-visualization`, {
      params: { time_range: timeRange },
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch progress visualization');
  }
};

/**
 * Get skill proficiency for radar chart
 * @returns {Promise<object>} Skill proficiency for all 6 skills
 * 
 * @example
 * const skills = await learningAnalyticsService.getSkillRadar();
 * // Returns: { listening: 75.5, speaking: 60.2, reading: 80.1, ... }
 */
export const getSkillRadar = async () => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/skill-radar`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch skill radar data');
  }
};

// ============================================================
// PREDICTIONS
// ============================================================

/**
 * Predict when user will reach next CEFR level
 * @returns {Promise<object>} Prediction with date, confidence, days remaining
 * 
 * @example
 * const prediction = await learningAnalyticsService.predictLevelCompletion();
 * // Returns: {
 * //   current_level: 'A2',
 * //   next_level: 'B1',
 * //   predicted_date: '2025-12-15',
 * //   confidence: 0.85,
 * //   days_remaining: 45
 * // }
 */
export const predictLevelCompletion = async () => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/predictions/level-completion`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to predict level completion');
  }
};

/**
 * Predict when user will master a specific skill (reach 90%)
 * @param {string} skill - listening, speaking, reading, writing, grammar, vocabulary
 * @returns {Promise<object>} Prediction with date and confidence
 * 
 * @example
 * const prediction = await learningAnalyticsService.predictSkillMastery('listening');
 * // Returns: {
 * //   skill: 'listening',
 * //   current_proficiency: 75.5,
 * //   predicted_date: '2025-11-30',
 * //   confidence: 0.80
 * // }
 */
export const predictSkillMastery = async (skill) => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/predictions/skill-mastery/${skill}`);
    return response.data;
  } catch (error) {
    handleError(error, `Failed to predict ${skill} mastery`);
  }
};

// ============================================================
// COMPARISONS
// ============================================================

/**
 * Get comprehensive comparison insights
 * @returns {Promise<object>} Comparisons vs self, peers, and expected curve
 * 
 * @example
 * const comparisons = await learningAnalyticsService.getComparisons();
 * // Returns: { vs_self: {...}, vs_peers: {...}, vs_expected: {...} }
 */
export const getComparisons = async () => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/comparisons`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch comparison insights');
  }
};

/**
 * Get percentile ranking for a specific metric
 * @param {string} metric - total_study_time, weekly_velocity, etc.
 * @returns {Promise<object>} Percentile ranking and peer statistics
 * 
 * @example
 * const ranking = await learningAnalyticsService.getPercentile('weekly_velocity');
 * // Returns: {
 * //   metric: 'weekly_velocity',
 * //   user_value: 12.5,
 * //   percentile: 75.0,
 * //   cohort_mean: 10.2
 * // }
 */
export const getPercentile = async (metric) => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/percentile/${metric}`);
    return response.data;
  } catch (error) {
    handleError(error, `Failed to fetch percentile for ${metric}`);
  }
};

// ============================================================
// VELOCITY & MOMENTUM
// ============================================================

/**
 * Get learning velocity and momentum
 * @param {string} period - 'week' or 'month'
 * @returns {Promise<object>} Velocity, acceleration, momentum, trend
 * 
 * @example
 * const velocity = await learningAnalyticsService.getVelocity('week');
 * // Returns: {
 * //   current_velocity: 12.5,
 * //   average_velocity: 10.2,
 * //   acceleration: 2.3,
 * //   momentum: 'increasing',
 * //   trend: 'positive'
 * // }
 */
export const getVelocity = async (period = 'week') => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/velocity`, {
      params: { period },
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch learning velocity');
  }
};

/**
 * Get optimal study schedule based on historical performance
 * @returns {Promise<object>} Optimal time slots with engagement scores
 * 
 * @example
 * const schedule = await learningAnalyticsService.getStudySchedule();
 * // Returns: {
 * //   optimal_time_slots: [
 * //     { time: '09:00 - 10:00', engagement_score: 0.92, session_count: 15 },
 * //     ...
 * //   ],
 * //   recommendation: 'Your peak learning time is around 09:00'
 * // }
 */
export const getStudySchedule = async () => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/study-schedule`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch optimal study schedule');
  }
};

// ============================================================
// INSIGHTS
// ============================================================

/**
 * Get personalized AI-generated insights
 * @returns {Promise<object>} List of insights with type, category, priority
 * 
 * @example
 * const insights = await learningAnalyticsService.getInsights();
 * // Returns: {
 * //   insights: [
 * //     {
 * //       type: 'strength',
 * //       category: 'listening',
 * //       title: 'Listening Excellence',
 * //       description: '...',
 * //       priority: 'high',
 * //       confidence: 0.95
 * //     },
 * //     ...
 * //   ],
 * //   count: 5
 * // }
 */
export const getInsights = async () => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/insights`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch AI insights');
  }
};

/**
 * Identify learning patterns and behaviors
 * @returns {Promise<object>} Learning patterns (preferred days, times, consistency)
 * 
 * @example
 * const patterns = await learningAnalyticsService.getLearningPatterns();
 * // Returns: {
 * //   preferred_study_days: ['Monday', 'Wednesday', 'Friday'],
 * //   average_session_length: 45,
 * //   most_active_time: 'Morning',
 * //   consistency_level: 'Excellent',
 * //   engagement_trend: 'Increasing'
 * // }
 */
export const getLearningPatterns = async () => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/patterns`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch learning patterns');
  }
};

// ============================================================
// STUDY SESSIONS
// ============================================================

/**
 * Get study session history
 * @param {number} days - Number of days to look back (max 365)
 * @returns {Promise<object>} List of study sessions
 * 
 * @example
 * const sessions = await learningAnalyticsService.getStudySessions(30);
 * // Returns: {
 * //   sessions: [
 * //     {
 * //       id: 123,
 * //       session_start: '2025-10-20T14:00:00',
 * //       duration_minutes: 45,
 * //       activities_completed: 5,
 * //       ...
 * //     },
 * //     ...
 * //   ],
 * //   count: 20
 * // }
 */
export const getStudySessions = async (days = 30) => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/study-sessions`, {
      params: { days },
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch study sessions');
  }
};

/**
 * Track a completed study session
 * @param {object} sessionData - Session data
 * @param {string} sessionData.session_start - ISO 8601 datetime
 * @param {string} sessionData.session_end - ISO 8601 datetime
 * @param {number[]} sessionData.activities - Optional array of activity IDs
 * @returns {Promise<object>} Created session data
 * 
 * @example
 * const session = await learningAnalyticsService.trackStudySession({
 *   session_start: '2025-10-20T14:00:00',
 *   session_end: '2025-10-20T15:00:00',
 *   activities: [123, 456, 789]
 * });
 */
export const trackStudySession = async (sessionData) => {
  try {
    const api = createAuthRequest();
    const response = await api.post(`${ANALYTICS_BASE}/study-sessions`, sessionData);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to track study session');
  }
};

// ============================================================
// PROGRESS SNAPSHOTS
// ============================================================

/**
 * Get progress snapshot history
 * @param {number} days - Number of days to look back (max 365)
 * @returns {Promise<object>} List of progress snapshots
 * 
 * @example
 * const snapshots = await learningAnalyticsService.getSnapshots(90);
 * // Returns: {
 * //   snapshots: [
 * //     {
 * //       snapshot_date: '2025-10-20',
 * //       listening: 75.5,
 * //       speaking: 60.2,
 * //       ...
 * //     },
 * //     ...
 * //   ],
 * //   count: 90
 * // }
 */
export const getSnapshots = async (days = 90) => {
  try {
    const api = createAuthRequest();
    const response = await api.get(`${ANALYTICS_BASE}/snapshots`, {
      params: { days },
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch progress snapshots');
  }
};

/**
 * Create daily progress snapshot
 * @returns {Promise<object>} Created snapshot data
 * 
 * @example
 * const snapshot = await learningAnalyticsService.createSnapshot();
 */
export const createSnapshot = async () => {
  try {
    const api = createAuthRequest();
    const response = await api.post(`${ANALYTICS_BASE}/snapshots/create`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to create progress snapshot');
  }
};

// ============================================================
// HEALTH CHECK
// ============================================================

/**
 * Health check for analytics service
 * @returns {Promise<object>} Service health status
 * 
 * @example
 * const health = await learningAnalyticsService.checkHealth();
 * // Returns: { status: 'healthy', service: 'learning_analytics', version: '1.0.0' }
 */
export const checkHealth = async () => {
  try {
    const response = await axios.get(`${ANALYTICS_BASE}/health`);
    return response.data;
  } catch (error) {
    handleError(error, 'Analytics service health check failed');
  }
};

// ============================================================
// BATCH OPERATIONS (Convenience Methods)
// ============================================================

/**
 * Get all dashboard data in one batch
 * Fetches multiple endpoints concurrently for dashboard initialization
 * @returns {Promise<object>} All dashboard data
 * 
 * @example
 * const dashboardData = await learningAnalyticsService.getDashboardData();
 * // Returns: {
 * //   weeklyReport: {...},
 * //   skills: {...},
 * //   velocity: {...},
 * //   insights: {...},
 * //   prediction: {...}
 * // }
 */
export const getDashboardData = async () => {
  try {
    const [
      weeklyReport,
      skills,
      velocity,
      insights,
      prediction,
    ] = await Promise.all([
      getWeeklyReport(0),
      getSkillRadar(),
      getVelocity('week'),
      getInsights(),
      predictLevelCompletion(),
    ]);

    return {
      weeklyReport: weeklyReport.report,
      skills: skills.skills,
      velocity: velocity.velocity,
      insights: insights.insights,
      prediction: prediction.prediction,
    };
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
    throw error;
  }
};

/**
 * Get all skill predictions
 * Fetches mastery predictions for all 6 skills concurrently
 * @returns {Promise<object>} Predictions for all skills
 * 
 * @example
 * const predictions = await learningAnalyticsService.getAllSkillPredictions();
 * // Returns: {
 * //   listening: {...},
 * //   speaking: {...},
 * //   reading: {...},
 * //   writing: {...},
 * //   grammar: {...},
 * //   vocabulary: {...}
 * // }
 */
export const getAllSkillPredictions = async () => {
  try {
    const skills = ['listening', 'speaking', 'reading', 'writing', 'grammar', 'vocabulary'];
    
    const predictions = await Promise.all(
      skills.map(skill => predictSkillMastery(skill))
    );

    return skills.reduce((acc, skill, index) => {
      acc[skill] = predictions[index].prediction;
      return acc;
    }, {});
  } catch (error) {
    console.error('Failed to fetch skill predictions:', error);
    throw error;
  }
};

// ============================================================
// DEFAULT EXPORT (Service Object)
// ============================================================

const learningAnalyticsService = {
  // Weekly Reports
  getWeeklyReport,
  getWeeklyReports,
  
  // Progress Visualization
  getProgressVisualization,
  getSkillRadar,
  
  // Predictions
  predictLevelCompletion,
  predictSkillMastery,
  
  // Comparisons
  getComparisons,
  getPercentile,
  
  // Velocity & Momentum
  getVelocity,
  getStudySchedule,
  
  // Insights
  getInsights,
  getLearningPatterns,
  
  // Study Sessions
  getStudySessions,
  trackStudySession,
  
  // Progress Snapshots
  getSnapshots,
  createSnapshot,
  
  // Health
  checkHealth,
  
  // Batch Operations
  getDashboardData,
  getAllSkillPredictions,
};

export default learningAnalyticsService;
