import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * Activity Service - Updated with real backend API endpoints
 * Handles all activity-related API calls
 */

export const activityService = {
  /**
   * Get list of all activities
   */
  async getActivities(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.LIST, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching activities:", error);
      throw error;
    }
  },

  /**
   * Get activities by type
   */
  async getActivitiesByType(type, params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.BY_TYPE(type), { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching activities by type:", error);
      throw error;
    }
  },

  /**
   * Get user's activities
   */
  async getUserActivities() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.USER_ACTIVITIES);
      return response.data;
    } catch (error) {
      console.error("Error fetching user activities:", error);
      throw error;
    }
  },

  /**
   * Get activity details by ID
   */
  async getActivityDetail(activityId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.DETAIL(activityId));
      return response.data;
    } catch (error) {
      console.error("Error fetching activity detail:", error);
      throw error;
    }
  },

  /**
   * Generate quiz activity
   */
  async generateQuiz(params) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.GENERATE_QUIZ, params);
      return response.data;
    } catch (error) {
      console.error("Error generating quiz:", error);
      throw error;
    }
  },

  /**
   * Generate flashcards activity
   */
  async generateFlashcards(params) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.GENERATE_FLASHCARDS, params);
      return response.data;
    } catch (error) {
      console.error("Error generating flashcards:", error);
      throw error;
    }
  },

  /**
   * Generate reading activity
   */
  async generateReading(params) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.GENERATE_READING, params);
      return response.data;
    } catch (error) {
      console.error("Error generating reading:", error);
      throw error;
    }
  },

  /**
   * Submit activity answers
   */
  async submitActivity(activityId, data) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.SUBMIT(activityId), data);
      return response.data;
    } catch (error) {
      console.error("Error submitting activity:", error);
      throw error;
    }
  },

  /**
   * Start activity
   */
  async startActivity(activityId) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.COURSES.START_ACTIVITY_BY_ID(activityId));
      return response.data;
    } catch (error) {
      console.error("Error starting activity:", error);
      throw error;
    }
  },

  /**
   * Complete activity
   */
  async completeActivity(activityId, completionData) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.COURSES.COMPLETE_ACTIVITY(activityId), completionData);
      return response.data;
    } catch (error) {
      console.error("Error completing activity:", error);
      throw error;
    }
  },

  /**
   * Get user's activity progress summary
   */
  async getProgressSummary() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.PROGRESS_SUMMARY);
      return response.data;
    } catch (error) {
      console.error("Error fetching progress summary:", error);
      throw error;
    }
  },

  /**
   * Get next recommended activity
   */
  async getNextActivity() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.NEXT_ACTIVITY);
      return response.data;
    } catch (error) {
      console.error("Error fetching next activity:", error);
      throw error;
    }
  },

  /**
   * Get recommended activities
   */
  async getRecommendedActivities(limit = 5) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ADAPTIVE.RECOMMENDATIONS, { params: { limit } });
      return response.data;
    } catch (error) {
      console.error("Error fetching recommended activities:", error);
      throw error;
    }
  },

  /**
   * Get activity statistics
   */
  async getActivityStatistics(userId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.GAMIFICATION.STATS(userId));
      return response.data;
    } catch (error) {
      console.error("Error fetching activity statistics:", error);
      throw error;
    }
  },

  /**
   * Get activity history
   */
  async getActivityHistory(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ENHANCED_ACTIVITY.PERFORMANCE_HISTORY, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching activity history:", error);
      throw error;
    }
  },

  /**
   * Get learning path activities
   */
  async getLearningPathActivities(learningPathId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.LEARNING_PATH_ACTIVITIES(learningPathId));
      return response.data;
    } catch (error) {
      console.error("Error fetching learning path activities:", error);
      throw error;
    }
  },
};

export default activityService;
