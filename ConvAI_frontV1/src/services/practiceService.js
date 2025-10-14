import axiosInstance, { API_ENDPOINTS } from '../config/api';

/**
 * Practice Service
 * Handles all practice session-related API calls
 */

const practiceService = {
  /**
   * Generate practice questions without a session
   * @param {Object} params - Question generation parameters
   * @param {string} params.topic - Topic to practice
   * @param {string} params.difficulty - 'beginner', 'intermediate', or 'advanced'
   * @param {number} params.num_questions - Number of questions (max 20)
   * @param {string[]} params.question_types - Types of questions
   * @param {string} params.language_focus - 'vocabulary', 'grammar', 'pronunciation', 'mixed'
   * @returns {Promise} Generated questions
   */
  generateQuestions: async (params) => {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.PRACTICE.GENERATE_QUESTIONS, {
        topic: params.topic || 'general',
        difficulty: params.difficulty || 'beginner',
        num_questions: params.num_questions || 5,
        question_types: params.question_types || ['multiple_choice'],
        language_focus: params.language_focus || 'vocabulary'
      });
      return response.data;
    } catch (error) {
      console.error('Error generating questions:', error);
      throw error;
    }
  },

  /**
   * Submit an answer for evaluation (without session)
   * @param {Object} answerData - Answer submission data
   * @param {string} answerData.question_id - Question ID
   * @param {string} answerData.question_type - Type of question
   * @param {string} answerData.user_answer - User's answer
   * @param {string} answerData.correct_answer - Correct answer
   * @param {string} answerData.question_text - Question text
   * @param {string[]} answerData.options - Answer options (for multiple choice)
   * @param {number} answerData.response_time - Time spent in seconds
   * @param {string} answerData.difficulty_level - Question difficulty
   * @returns {Promise} Evaluation result with feedback
   */
  submitAnswer: async (answerData) => {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.PRACTICE.SUBMIT_ANSWER, answerData);
      return response.data;
    } catch (error) {
      console.error('Error submitting answer:', error);
      throw error;
    }
  },

  /**
   * Start a practice session for a specific chapter
   * @param {number} chapterId - Chapter ID
   * @returns {Promise} Session details
   */
  startSession: async (chapterId) => {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.PRACTICE.START_SESSION, {
        chapter_id: chapterId
      });
      return response.data;
    } catch (error) {
      console.error('Error starting practice session:', error);
      throw error;
    }
  },

  /**
   * Generate questions for an existing session
   * @param {number} sessionId - Session ID
   * @param {Object} params - Question parameters
   * @param {number} params.num_questions - Number of questions
   * @param {string[]} params.question_types - Question types
   * @returns {Promise} Generated questions for session
   */
  generateSessionQuestions: async (sessionId, params) => {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.PRACTICE.SESSION_GENERATE_QUESTIONS(sessionId),
        {
          num_questions: params.num_questions || 5,
          question_types: params.question_types || ['multiple_choice']
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error generating session questions:', error);
      throw error;
    }
  },

  /**
   * Submit answer for a session question
   * @param {number} sessionId - Session ID
   * @param {Object} answerData - Answer data
   * @param {string} answerData.question_id - Question ID
   * @param {string} answerData.user_answer - User's answer
   * @param {number} answerData.time_spent_seconds - Time spent
   * @returns {Promise} Answer evaluation result
   */
  submitSessionAnswer: async (sessionId, answerData) => {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.PRACTICE.SESSION_SUBMIT_ANSWER(sessionId),
        answerData
      );
      return response.data;
    } catch (error) {
      console.error('Error submitting session answer:', error);
      throw error;
    }
  },

  /**
   * Complete a practice session
   * @param {number} sessionId - Session ID
   * @returns {Promise} Session completion result
   */
  completeSession: async (sessionId) => {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.PRACTICE.COMPLETE_SESSION(sessionId));
      return response.data;
    } catch (error) {
      console.error('Error completing session:', error);
      throw error;
    }
  },

  /**
   * Get session results
   * @param {number} sessionId - Session ID
   * @returns {Promise} Detailed session results
   */
  getSessionResults: async (sessionId) => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.PRACTICE.SESSION_RESULTS(sessionId));
      return response.data;
    } catch (error) {
      console.error('Error getting session results:', error);
      throw error;
    }
  },

  /**
   * Get practice history
   * @param {Object} filters - Optional filters
   * @param {string} filters.date_from - Start date (ISO format)
   * @param {string} filters.date_to - End date (ISO format)
   * @param {number} filters.limit - Number of results
   * @returns {Promise} Practice history
   */
  getHistory: async (filters = {}) => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.PRACTICE.HISTORY, {
        params: filters
      });
      return response.data;
    } catch (error) {
      console.error('Error getting practice history:', error);
      throw error;
    }
  }
};

// Helper functions

/**
 * Calculate session statistics
 * @param {Object[]} questions - Array of questions with user responses
 * @returns {Object} Statistics
 */
export const calculateSessionStats = (questions) => {
  if (!questions || questions.length === 0) {
    return {
      total: 0,
      answered: 0,
      correct: 0,
      incorrect: 0,
      accuracy: 0,
      score: 0
    };
  }

  const answered = questions.filter(q => q.user_answer !== undefined && q.user_answer !== null);
  const correct = answered.filter(q => q.is_correct === true);

  return {
    total: questions.length,
    answered: answered.length,
    correct: correct.length,
    incorrect: answered.length - correct.length,
    accuracy: answered.length > 0 ? (correct.length / answered.length) * 100 : 0,
    score: correct.reduce((sum, q) => sum + (q.score || 10), 0)
  };
};

/**
 * Format time in seconds to readable string
 * @param {number} seconds - Time in seconds
 * @returns {string} Formatted time
 */
export const formatTime = (seconds) => {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}m ${secs}s`;
};

/**
 * Get performance level based on accuracy
 * @param {number} accuracy - Accuracy percentage
 * @returns {Object} Performance level info
 */
export const getPerformanceLevel = (accuracy) => {
  if (accuracy >= 90) {
    return {
      level: 'Excellent',
      color: 'success',
      icon: '🌟',
      message: 'Outstanding performance!',
      telugu: 'అద్భుతమైన పనితీరు!'
    };
  } else if (accuracy >= 75) {
    return {
      level: 'Good',
      color: 'info',
      icon: '👍',
      message: 'Great job!',
      telugu: 'మంచి పని!'
    };
  } else if (accuracy >= 60) {
    return {
      level: 'Fair',
      color: 'warning',
      icon: '📚',
      message: 'Keep practicing!',
      telugu: 'అభ్యసించడం కొనసాగించండి!'
    };
  } else {
    return {
      level: 'Needs Improvement',
      color: 'error',
      icon: '💪',
      message: 'Don\'t give up!',
      telugu: 'వదులుకోకండి!'
    };
  }
};

/**
 * Get difficulty level display info
 * @param {string} difficulty - Difficulty level
 * @returns {Object} Display info
 */
export const getDifficultyInfo = (difficulty) => {
  const levels = {
    beginner: {
      label: 'Beginner',
      color: 'success',
      icon: '🌱',
      description: 'Start your learning journey'
    },
    intermediate: {
      label: 'Intermediate',
      color: 'warning',
      icon: '📖',
      description: 'Build on your knowledge'
    },
    advanced: {
      label: 'Advanced',
      color: 'error',
      icon: '🎓',
      description: 'Master complex concepts'
    }
  };

  return levels[difficulty?.toLowerCase()] || levels.beginner;
};

/**
 * Get question type display name
 * @param {string} type - Question type
 * @returns {string} Display name
 */
export const getQuestionTypeLabel = (type) => {
  const labels = {
    multiple_choice: 'Multiple Choice',
    fill_blank: 'Fill in the Blank',
    translation: 'Translation',
    true_false: 'True/False',
    matching: 'Matching'
  };

  return labels[type] || type;
};

export default practiceService;
