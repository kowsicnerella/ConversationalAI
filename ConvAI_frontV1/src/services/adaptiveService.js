import axiosInstance, { API_ENDPOINTS } from '../config/api';

/**
 * Adaptive Learning Service
 * Handles personalized recommendations and difficulty adjustments
 */

const adaptiveService = {
  /**
   * Get personalized activity recommendations
   * @param {Object} params - Optional parameters
   * @param {number} params.learning_path_id - Specific learning path
   * @param {number} params.count - Number of recommendations
   * @returns {Promise} Personalized recommendations
   */
  getRecommendations: async (params = {}) => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ADAPTIVE.RECOMMENDATIONS, {
        params
      });
      return response.data;
    } catch (error) {
      console.error('Error getting recommendations:', error);
      throw error;
    }
  },

  /**
   * Get performance analysis
   * @param {number} days - Number of days to analyze (1-90)
   * @returns {Promise} Performance analysis data
   */
  getPerformanceAnalysis: async (days = 7) => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ADAPTIVE.PERFORMANCE_ANALYSIS, {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting performance analysis:', error);
      throw error;
    }
  },

  /**
   * Get next recommended activities
   * @param {Object} params - Query parameters
   * @param {number} params.learning_path_id - Optional learning path filter
   * @param {number} params.count - Number of activities (1-10)
   * @returns {Promise} Recommended activities
   */
  getNextActivities: async (params = {}) => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ADAPTIVE.NEXT_ACTIVITIES, {
        params: {
          count: params.count || 5,
          ...params
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting next activities:', error);
      throw error;
    }
  },

  /**
   * Identify learning gaps
   * @returns {Promise} Learning gaps analysis
   */
  getLearningGaps: async () => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ADAPTIVE.LEARNING_GAPS);
      return response.data;
    } catch (error) {
      console.error('Error getting learning gaps:', error);
      throw error;
    }
  },

  /**
   * Get user learning profile
   * @returns {Promise} Learning profile data
   */
  getLearningProfile: async () => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ADAPTIVE.LEARNING_PROFILE);
      return response.data;
    } catch (error) {
      console.error('Error getting learning profile:', error);
      throw error;
    }
  },

  /**
   * Adjust difficulty dynamically based on performance
   * @param {Object} data - Performance data
   * @param {number} data.activity_id - Activity ID
   * @param {Object} data.user_performance - Performance metrics
   * @param {number} data.user_performance.accuracy - Accuracy (0-1)
   * @param {number} data.user_performance.time_spent_minutes - Time spent
   * @param {number} data.user_performance.attempts - Number of attempts
   * @returns {Promise} Difficulty adjustment result
   */
  adjustDifficulty: async (data) => {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.ADAPTIVE.ADJUST_DIFFICULTY, data);
      return response.data;
    } catch (error) {
      console.error('Error adjusting difficulty:', error);
      throw error;
    }
  },

  /**
   * Get learning pace analysis
   * @returns {Promise} Learning pace data
   */
  getLearningPace: async () => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ADAPTIVE.LEARNING_PACE);
      return response.data;
    } catch (error) {
      console.error('Error getting learning pace:', error);
      throw error;
    }
  }
};

// Helper functions

/**
 * Get confidence level color
 * @param {number} confidence - Confidence score (0-1)
 * @returns {string} MUI color name
 */
export const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return 'success';
  if (confidence >= 0.6) return 'info';
  if (confidence >= 0.4) return 'warning';
  return 'error';
};

/**
 * Get confidence level label
 * @param {number} confidence - Confidence score (0-1)
 * @returns {string} Label
 */
export const getConfidenceLabel = (confidence) => {
  if (confidence >= 0.8) return 'High Confidence';
  if (confidence >= 0.6) return 'Medium Confidence';
  if (confidence >= 0.4) return 'Low Confidence';
  return 'Very Low';
};

/**
 * Format performance level
 * @param {number} accuracy - Accuracy percentage
 * @returns {Object} Level info
 */
export const getPerformanceLevel = (accuracy) => {
  if (accuracy >= 90) {
    return {
      level: 'Excellent',
      color: 'success',
      icon: '🌟',
      description: 'Outstanding performance!'
    };
  } else if (accuracy >= 75) {
    return {
      level: 'Good',
      color: 'info',
      icon: '👍',
      description: 'Great job!'
    };
  } else if (accuracy >= 60) {
    return {
      level: 'Fair',
      color: 'warning',
      icon: '📚',
      description: 'Keep practicing!'
    };
  } else {
    return {
      level: 'Needs Improvement',
      color: 'error',
      icon: '💪',
      description: 'Focus on improvement'
    };
  }
};

/**
 * Get skill strength indicator
 * @param {number} score - Skill score (0-100)
 * @returns {Object} Strength info
 */
export const getSkillStrength = (score) => {
  if (score >= 80) {
    return {
      label: 'Strong',
      color: 'success',
      icon: '💪',
      recommendation: 'Consider advanced exercises'
    };
  } else if (score >= 60) {
    return {
      label: 'Developing',
      color: 'info',
      icon: '📈',
      recommendation: 'Continue regular practice'
    };
  } else if (score >= 40) {
    return {
      label: 'Emerging',
      color: 'warning',
      icon: '🌱',
      recommendation: 'Focus more on this skill'
    };
  } else {
    return {
      label: 'Needs Work',
      color: 'error',
      icon: '🎯',
      recommendation: 'Prioritize this area'
    };
  }
};

/**
 * Calculate learning velocity
 * @param {Object[]} activities - Activity history
 * @param {number} days - Time period
 * @returns {Object} Velocity metrics
 */
export const calculateLearningVelocity = (activities, days = 7) => {
  if (!activities || activities.length === 0) {
    return {
      velocity: 0,
      trend: 'stable',
      description: 'Not enough data'
    };
  }

  const activitiesPerDay = activities.length / days;
  
  let trend = 'stable';
  if (activitiesPerDay > 2) trend = 'accelerating';
  else if (activitiesPerDay < 0.5) trend = 'slowing';

  return {
    velocity: activitiesPerDay.toFixed(1),
    trend,
    description: `${activitiesPerDay.toFixed(1)} activities per day`,
    icon: trend === 'accelerating' ? '📈' : trend === 'slowing' ? '📉' : '➡️'
  };
};

/**
 * Get difficulty adjustment recommendation
 * @param {number} accuracy - Current accuracy
 * @param {number} timeSpent - Time spent in minutes
 * @returns {Object} Recommendation
 */
export const getDifficultyRecommendation = (accuracy, timeSpent) => {
  if (accuracy >= 90 && timeSpent < 5) {
    return {
      adjustment: 'increase',
      reason: 'High accuracy with quick completion',
      suggestion: 'Try harder challenges',
      color: 'success'
    };
  } else if (accuracy < 60) {
    return {
      adjustment: 'decrease',
      reason: 'Low accuracy indicates difficulty',
      suggestion: 'Try easier exercises first',
      color: 'warning'
    };
  } else {
    return {
      adjustment: 'maintain',
      reason: 'Current level is appropriate',
      suggestion: 'Continue at this pace',
      color: 'info'
    };
  }
};

/**
 * Format recommendation reason
 * @param {string[]} factors - Recommendation factors
 * @returns {string} Formatted reason
 */
export const formatRecommendationReason = (factors) => {
  if (!factors || factors.length === 0) {
    return 'Based on your learning profile';
  }

  const reasons = factors.map(factor => {
    const reasonMap = {
      'performance_history': 'past performance',
      'learning_gaps': 'identified gaps',
      'difficulty_progression': 'skill progression',
      'activity_preferences': 'your preferences',
      'time_availability': 'available time'
    };
    return reasonMap[factor] || factor;
  });

  return `Recommended based on ${reasons.join(', ')}`;
};

/**
 * Get learning style icon
 * @param {string} style - Learning style
 * @returns {string} Icon emoji
 */
export const getLearningStyleIcon = (style) => {
  const icons = {
    visual: '👁️',
    auditory: '👂',
    reading: '📖',
    kinesthetic: '✋',
    mixed: '🎯'
  };
  return icons[style?.toLowerCase()] || '📚';
};

/**
 * Calculate mastery percentage
 * @param {Object} skillData - Skill performance data
 * @returns {number} Mastery percentage
 */
export const calculateMasteryPercentage = (skillData) => {
  if (!skillData) return 0;

  const {
    accuracy = 0,
    consistency = 0,
    retention = 0,
    speed = 0
  } = skillData;

  // Weighted average
  const mastery = (
    accuracy * 0.4 +
    consistency * 0.3 +
    retention * 0.2 +
    speed * 0.1
  );

  return Math.round(mastery);
};

export default adaptiveService;
