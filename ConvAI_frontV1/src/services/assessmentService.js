/**
 * Assessment Service - API integration for Intelligent Assessment System
 * 
 * Provides methods for:
 * - Assessment management (CRUD)
 * - Question management
 * - Taking assessments (adaptive & fixed)
 * - Results and diagnostics
 * - Analytics and comparisons
 * - Recommendations
 * 
 * @module assessmentService
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api/intelligent-assessment';

/**
 * Get authentication token from localStorage
 */
const getAuthToken = () => {
  return localStorage.getItem('token') || '';
};

/**
 * Get auth headers for API requests
 */
const getAuthHeaders = () => ({
  'Authorization': `Bearer ${getAuthToken()}`,
  'Content-Type': 'application/json'
});

// ================================================================
// ASSESSMENT MANAGEMENT
// ================================================================

/**
 * Create a new assessment
 * @param {Object} assessmentData - Assessment configuration
 * @returns {Promise<Object>} Created assessment
 */
export const createAssessment = async (assessmentData) => {
  const response = await axios.post(
    `${API_BASE_URL}/assessments/create`,
    assessmentData,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Get list of assessments with optional filtering
 * @param {Object} filters - Filter parameters
 * @returns {Promise<Object>} List of assessments
 */
export const getAssessments = async (filters = {}) => {
  const params = new URLSearchParams(filters).toString();
  const response = await axios.get(
    `${API_BASE_URL}/assessments${params ? '?' + params : ''}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Get detailed information about a specific assessment
 * @param {number} assessmentId - Assessment ID
 * @returns {Promise<Object>} Assessment details
 */
export const getAssessmentDetails = async (assessmentId) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/${assessmentId}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Update an assessment
 * @param {number} assessmentId - Assessment ID
 * @param {Object} updates - Fields to update
 * @returns {Promise<Object>} Updated assessment
 */
export const updateAssessment = async (assessmentId, updates) => {
  const response = await axios.put(
    `${API_BASE_URL}/assessments/${assessmentId}`,
    updates,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Delete an assessment (soft delete)
 * @param {number} assessmentId - Assessment ID
 * @returns {Promise<Object>} Success message
 */
export const deleteAssessment = async (assessmentId) => {
  const response = await axios.delete(
    `${API_BASE_URL}/assessments/${assessmentId}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// ================================================================
// QUESTION MANAGEMENT
// ================================================================

/**
 * Add a question to an assessment
 * @param {number} assessmentId - Assessment ID
 * @param {Object} questionData - Question data with IRT parameters
 * @returns {Promise<Object>} Created question
 */
export const addQuestion = async (assessmentId, questionData) => {
  const response = await axios.post(
    `${API_BASE_URL}/assessments/${assessmentId}/questions`,
    questionData,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Get question details
 * @param {number} questionId - Question ID
 * @returns {Promise<Object>} Question details
 */
export const getQuestion = async (questionId) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/questions/${questionId}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Update a question
 * @param {number} questionId - Question ID
 * @param {Object} updates - Fields to update
 * @returns {Promise<Object>} Updated question
 */
export const updateQuestion = async (questionId, updates) => {
  const response = await axios.put(
    `${API_BASE_URL}/assessments/questions/${questionId}`,
    updates,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Delete a question
 * @param {number} questionId - Question ID
 * @returns {Promise<Object>} Success message
 */
export const deleteQuestion = async (questionId) => {
  const response = await axios.delete(
    `${API_BASE_URL}/assessments/questions/${questionId}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Bulk import questions
 * @param {number} assessmentId - Assessment ID
 * @param {Array} questions - Array of question objects
 * @returns {Promise<Object>} Import results
 */
export const bulkImportQuestions = async (assessmentId, questions) => {
  const response = await axios.post(
    `${API_BASE_URL}/assessments/questions/bulk-import`,
    { assessment_id: assessmentId, questions },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// ================================================================
// TAKING ASSESSMENTS
// ================================================================

/**
 * Start a new assessment attempt
 * @param {number} assessmentId - Assessment ID
 * @param {number} initialTheta - Optional initial ability estimate
 * @returns {Promise<Object>} Attempt details with first question
 */
export const startAssessment = async (assessmentId, initialTheta = null) => {
  const response = await axios.post(
    `${API_BASE_URL}/assessments/${assessmentId}/start`,
    { initial_theta: initialTheta },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Get next question for an ongoing assessment
 * @param {number} attemptId - Attempt ID
 * @returns {Promise<Object>} Next question or completion status
 */
export const getNextQuestion = async (attemptId) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/attempts/${attemptId}/next-question`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Submit an answer to a question
 * @param {number} attemptId - Attempt ID
 * @param {number} questionId - Question ID
 * @param {string} userAnswer - User's answer
 * @param {number} timeSpentSeconds - Time taken to answer
 * @param {Array} hintsUsed - Hints that were viewed
 * @returns {Promise<Object>} Feedback with correctness and updated stats
 */
export const submitAnswer = async (
  attemptId,
  questionId,
  userAnswer,
  timeSpentSeconds = null,
  hintsUsed = []
) => {
  const response = await axios.post(
    `${API_BASE_URL}/assessments/attempts/${attemptId}/submit`,
    {
      question_id: questionId,
      user_answer: userAnswer,
      time_spent_seconds: timeSpentSeconds,
      hints_used: hintsUsed
    },
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Complete an assessment and get results
 * @param {number} attemptId - Attempt ID
 * @returns {Promise<Object>} Comprehensive results
 */
export const completeAssessment = async (attemptId) => {
  const response = await axios.post(
    `${API_BASE_URL}/assessments/attempts/${attemptId}/complete`,
    {},
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Get current status of an assessment attempt
 * @param {number} attemptId - Attempt ID
 * @returns {Promise<Object>} Attempt status and progress
 */
export const getAttemptStatus = async (attemptId) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/attempts/${attemptId}/status`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// ================================================================
// RESULTS AND DIAGNOSTICS
// ================================================================

/**
 * Get comprehensive results for a completed assessment
 * @param {number} attemptId - Attempt ID
 * @returns {Promise<Object>} Full results with all metrics
 */
export const getResults = async (attemptId) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/attempts/${attemptId}/results`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Get detailed skill diagnostics
 * @param {number} attemptId - Attempt ID
 * @returns {Promise<Object>} Skill-by-skill analysis
 */
export const getDiagnostics = async (attemptId) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/attempts/${attemptId}/diagnostics`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// ================================================================
// ANALYTICS AND HISTORY
// ================================================================

/**
 * Get user's assessment history
 * @param {number} assessmentId - Optional filter by assessment
 * @returns {Promise<Object>} List of completed attempts
 */
export const getMyHistory = async (assessmentId = null) => {
  const params = assessmentId ? `?assessment_id=${assessmentId}` : '';
  const response = await axios.get(
    `${API_BASE_URL}/assessments/my-history${params}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Get analytics for an assessment
 * @param {number} assessmentId - Assessment ID
 * @returns {Promise<Object>} Aggregate statistics
 */
export const getAssessmentAnalytics = async (assessmentId) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/${assessmentId}/analytics`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Compare two assessment attempts
 * @param {number} attemptId1 - First attempt ID (earlier)
 * @param {number} attemptId2 - Second attempt ID (later)
 * @returns {Promise<Object>} Comparison with improvements
 */
export const compareAttempts = async (attemptId1, attemptId2) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/compare/${attemptId1}/${attemptId2}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// ================================================================
// RECOMMENDATIONS AND ADVANCED FEATURES
// ================================================================

/**
 * Get recommended assessments for the user
 * @returns {Promise<Object>} Personalized recommendations
 */
export const getRecommendations = async () => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/recommendations`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Check if user is ready for certification
 * @param {string} certificationName - Certification name
 * @returns {Promise<Object>} Readiness assessment
 */
export const checkCertificationReadiness = async (certificationName) => {
  const response = await axios.get(
    `${API_BASE_URL}/assessments/certification-ready?certification_name=${encodeURIComponent(certificationName)}`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Health check for assessment system
 * @returns {Promise<Object>} System status
 */
export const healthCheck = async () => {
  const response = await axios.get(`${API_BASE_URL}/assessments/health`);
  return response.data;
};

// ================================================================
// UTILITY FUNCTIONS
// ================================================================

/**
 * Get proficiency level display info
 * @param {string} level - Proficiency level
 * @returns {Object} Display information
 */
export const getProficiencyInfo = (level) => {
  const proficiencyMap = {
    beginner: {
      label: 'Beginner',
      color: '#f44336',
      icon: '🌱',
      description: 'Just starting your learning journey',
      thetaRange: '-3.0 to -1.0'
    },
    elementary: {
      label: 'Elementary',
      color: '#ff9800',
      icon: '🌿',
      description: 'Building basic understanding',
      thetaRange: '-1.0 to 0.0'
    },
    intermediate: {
      label: 'Intermediate',
      color: '#2196f3',
      icon: '🌳',
      description: 'Average ability level',
      thetaRange: '0.0 to 1.0'
    },
    advanced: {
      label: 'Advanced',
      color: '#4caf50',
      icon: '🌲',
      description: 'Above average proficiency',
      thetaRange: '1.0 to 2.0'
    },
    expert: {
      label: 'Expert',
      color: '#9c27b0',
      icon: '🏆',
      description: 'Mastery level achievement',
      thetaRange: '2.0 to 3.0'
    }
  };
  
  return proficiencyMap[level] || proficiencyMap.beginner;
};

/**
 * Get assessment type display info
 * @param {string} type - Assessment type
 * @returns {Object} Display information
 */
export const getAssessmentTypeInfo = (type) => {
  const typeMap = {
    placement: {
      label: 'Placement Test',
      color: '#2196f3',
      icon: '📍',
      description: 'Determine your initial proficiency level'
    },
    progress: {
      label: 'Progress Check',
      color: '#4caf50',
      icon: '📈',
      description: 'Track your improvement over time'
    },
    mastery: {
      label: 'Mastery Assessment',
      color: '#ff9800',
      icon: '🎯',
      description: 'Verify topic mastery'
    },
    certification: {
      label: 'Certification Exam',
      color: '#9c27b0',
      icon: '🏅',
      description: 'Official certification test'
    }
  };
  
  return typeMap[type] || typeMap.placement;
};

/**
 * Format theta value for display
 * @param {number} theta - Theta value (-3 to +3)
 * @returns {string} Formatted string
 */
export const formatTheta = (theta) => {
  return theta >= 0 ? `+${theta.toFixed(2)}` : theta.toFixed(2);
};

/**
 * Calculate percentile from theta (approximation)
 * @param {number} theta - Theta value
 * @returns {number} Percentile (0-100)
 */
export const thetaToPercentile = (theta) => {
  // Using normal distribution approximation
  // This is a simplified version - backend provides actual percentile
  const z = theta;
  const percentile = 50 + 50 * Math.erf(z / Math.sqrt(2));
  return Math.max(0, Math.min(100, percentile));
};

/**
 * Get skill score color based on percentage
 * @param {number} score - Score percentage (0-100)
 * @returns {string} Color code
 */
export const getSkillScoreColor = (score) => {
  if (score >= 90) return '#4caf50'; // Green
  if (score >= 70) return '#2196f3'; // Blue
  if (score >= 50) return '#ff9800'; // Orange
  return '#f44336'; // Red
};

/**
 * Get recommendation priority color
 * @param {string} priority - Priority level
 * @returns {string} Color code
 */
export const getPriorityColor = (priority) => {
  const priorityMap = {
    high: '#f44336',
    medium: '#ff9800',
    low: '#4caf50'
  };
  return priorityMap[priority] || '#757575';
};

/**
 * Format duration in minutes to human-readable string
 * @param {number} minutes - Duration in minutes
 * @returns {string} Formatted string
 */
export const formatDuration = (minutes) => {
  if (!minutes) return 'Untimed';
  if (minutes < 60) return `${minutes} minutes`;
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (mins === 0) return `${hours} hour${hours > 1 ? 's' : ''}`;
  return `${hours}h ${mins}m`;
};

/**
 * Format date for display
 * @param {string} isoDate - ISO date string
 * @returns {string} Formatted date
 */
export const formatDate = (isoDate) => {
  if (!isoDate) return '';
  
  const date = new Date(isoDate);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Calculate progress percentage for adaptive tests
 * @param {number} theta_se - Standard error of theta
 * @param {number} target_se - Target standard error (default 0.3)
 * @returns {number} Progress percentage (0-100)
 */
export const calculateAdaptiveProgress = (theta_se, target_se = 0.3) => {
  // Initial SE is typically around 1.0, target is 0.3
  const initial_se = 1.0;
  const progress = ((initial_se - theta_se) / (initial_se - target_se)) * 100;
  return Math.max(0, Math.min(100, progress));
};

// =====================================================
// LEARNING PATH INTEGRATION
// =====================================================

/**
 * Get learning path recommendations based on assessment results
 * @param {number} attemptId - Assessment attempt ID
 * @returns {Promise} API response with recommended learning paths
 */
export const getLearningPathRecommendations = async (attemptId) => {
  const response = await axios.get(
    `${API_BASE_URL}/attempts/${attemptId}/learning-path-recommendations`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Create personalized learning path from assessment results
 * @param {number} attemptId - Assessment attempt ID
 * @returns {Promise} API response with created path ID
 */
export const createPersonalizedPath = async (attemptId) => {
  const response = await axios.post(
    `${API_BASE_URL}/attempts/${attemptId}/create-personalized-path`,
    {},
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Get suggested assessments for a learning path
 * @param {number} pathId - Learning path ID
 * @returns {Promise} API response with suggested assessments
 */
export const getSuggestedAssessments = async (pathId) => {
  const response = await axios.get(
    `${API_BASE_URL}/learning-paths/${pathId}/suggested-assessments`,
    { headers: getAuthHeaders() }
  );
  return response.data;
};

/**
 * Update adaptive learning path from progress assessment
 * @param {number} pathId - Learning path ID
 * @param {number} attemptId - Assessment attempt ID
 * @returns {Promise} API response with update details
 */
export const updatePathFromAssessment = async (pathId, attemptId) => {
  const response = await axios.post(
    `${API_BASE_URL}/learning-paths/${pathId}/update-from-assessment/${attemptId}`,
    {},
    { headers: getAuthHeaders() }
  );
  return response.data;
};

// Export all functions as named exports
export default {
  // Assessment Management
  createAssessment,
  getAssessments,
  getAssessmentDetails,
  updateAssessment,
  deleteAssessment,
  
  // Question Management
  addQuestion,
  getQuestion,
  updateQuestion,
  deleteQuestion,
  bulkImportQuestions,
  
  // Taking Assessments
  startAssessment,
  getNextQuestion,
  submitAnswer,
  completeAssessment,
  getAttemptStatus,
  
  // Results and Diagnostics
  getResults,
  getDiagnostics,
  
  // Analytics and History
  getMyHistory,
  getAssessmentAnalytics,
  compareAttempts,
  
  // Recommendations
  getRecommendations,
  checkCertificationReadiness,
  healthCheck,
  
  // Learning Path Integration
  getLearningPathRecommendations,
  createPersonalizedPath,
  getSuggestedAssessments,
  updatePathFromAssessment,
  
  // Utility Functions
  getProficiencyInfo,
  getAssessmentTypeInfo,
  formatTheta,
  thetaToPercentile,
  getSkillScoreColor,
  getPriorityColor,
  formatDuration,
  formatDate,
  calculateAdaptiveProgress
};
