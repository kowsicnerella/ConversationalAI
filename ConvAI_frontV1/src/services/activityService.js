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
   * Complete activity with full tracking (NEW - Data Persistence)
   * @param {Object} params - Completion parameters
   * @param {number} params.activityId - Database ID of the activity
   * @param {string} params.learningNodeId - Learning node identifier
   * @param {number} params.performanceScore - Score (0-1)
   * @param {number} params.timeSpentSeconds - Time spent in seconds
   * @param {Object} params.userResponses - User's answers/responses
   */
  async completeActivityTracked({
    activityId,
    learningNodeId,
    performanceScore,
    timeSpentSeconds,
    userResponses = {}
  }) {
    try {
      const response = await axiosInstance.post('/api/learning-path/complete-activity', {
        activity_id: activityId,
        learning_node_id: learningNodeId,
        performance_score: performanceScore,
        time_spent_seconds: timeSpentSeconds,
        user_responses: userResponses
      });
      console.log('✅ Activity completed with tracking:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Error completing activity with tracking:', error);
      throw error;
    }
  },

  /**
   * Get incomplete activities for resume functionality
   */
  async getIncompleteActivities() {
    try {
      const response = await axiosInstance.get('/api/learning-path/activities/incomplete');
      return response.data;
    } catch (error) {
      console.error('Error fetching incomplete activities:', error);
      throw error;
    }
  },

  /**
   * Resume an incomplete activity
   */
  async resumeActivity(activityId) {
    try {
      const response = await axiosInstance.put(`/api/learning-path/activities/${activityId}/resume`);
      return response.data;
    } catch (error) {
      console.error('Error resuming activity:', error);
      throw error;
    }
  },

  /**
   * Get activities due for spaced repetition review
   */
  async getDueReviews() {
    try {
      const response = await axiosInstance.get('/api/learning-path/spaced-repetition/due');
      return response.data;
    } catch (error) {
      console.error('Error fetching due reviews:', error);
      throw error;
    }
  },

  /**
   * Get activity logs with filters
   */
  async getActivityLogs(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.masteryLevel) params.append('mastery_level', filters.masteryLevel);
      if (filters.needsReview !== undefined) params.append('needs_review', filters.needsReview);
      if (filters.limit) params.append('limit', filters.limit);
      if (filters.offset) params.append('offset', filters.offset);

      const response = await axiosInstance.get(`/api/learning-path/activity-logs?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching activity logs:', error);
      throw error;
    }
  },

  /**
   * Get user's activities with filters
   */
  async getUserActivitiesFiltered(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.activityType) params.append('activity_type', filters.activityType);
      if (filters.limit) params.append('limit', filters.limit);
      if (filters.offset) params.append('offset', filters.offset);
      if (filters.fromDate) params.append('from_date', filters.fromDate);
      if (filters.toDate) params.append('to_date', filters.toDate);

      const response = await axiosInstance.get(`/api/learning-path/activities?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user activities:', error);
      throw error;
    }
  },

  /**
   * Get detailed activity information with completion logs
   */
  async getActivityDetailWithLogs(activityId) {
    try {
      const response = await axiosInstance.get(`/api/learning-path/activities/${activityId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching activity detail:', error);
      throw error;
    }
  },

  /**
   * Get comprehensive activity history with statistics
   */
  async getActivityHistoryStats() {
    try {
      const response = await axiosInstance.get('/api/learning-path/activity-history');
      return response.data;
    } catch (error) {
      console.error('Error fetching activity history:', error);
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
