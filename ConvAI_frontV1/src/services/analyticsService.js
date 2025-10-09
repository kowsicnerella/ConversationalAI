import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * Analytics Service
 * Handles all analytics and reporting API calls
 */

export const analyticsService = {
  /**
   * Get dashboard summary analytics
   */
  async getDashboardSummary() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.DASHBOARD);
      return response.data;
    } catch (error) {
      console.error("Error fetching dashboard summary:", error);
      throw error;
    }
  },

  /**
   * Get learning trends over time
   */
  async getLearningTrends(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.PERFORMANCE_TRENDS, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching learning trends:", error);
      throw error;
    }
  },

  /**
   * Get performance analysis
   */
  async getPerformanceAnalysis(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.PERFORMANCE, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching performance analysis:", error);
      throw error;
    }
  },

  /**
   * Get vocabulary analytics
   */
  async getVocabularyAnalytics() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.VOCABULARY_ANALYTICS);
      return response.data;
    } catch (error) {
      console.error("Error fetching vocabulary analytics:", error);
      throw error;
    }
  },

  /**
   * Get activity performance analysis
   */
  async getActivityPerformance(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.ACTIVITY_PERFORMANCE, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching activity performance:", error);
      throw error;
    }
  },

  /**
   * Get learning pattern recognition
   */
  async getLearningPatterns() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.LEARNING_PATTERNS);
      return response.data;
    } catch (error) {
      console.error("Error fetching learning patterns:", error);
      throw error;
    }
  },

  /**
   * Get engagement analytics
   */
  async getEngagementAnalytics(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.TIME_SPENT, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching engagement analytics:", error);
      throw error;
    }
  },

  /**
   * Get predictive analytics
   */
  async getPredictiveAnalytics() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.PREDICTIVE);
      return response.data;
    } catch (error) {
      console.error("Error fetching predictive analytics:", error);
      throw error;
    }
  },

  /**
   * Export comprehensive progress report
   */
  async exportProgressReport(format = 'json') {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.COMPREHENSIVE_REPORT, {
        params: { format },
      });
      return response.data;
    } catch (error) {
      console.error("Error exporting progress report:", error);
      throw error;
    }
  },

  /**
   * Get user statistics
   */
  async getUserStatistics() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.STATISTICS);
      return response.data;
    } catch (error) {
      console.error("Error fetching user statistics:", error);
      throw error;
    }
  },

  /**
   * Get skill breakdown
   */
  async getSkillBreakdown() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ANALYTICS.SKILL_BREAKDOWN);
      return response.data;
    } catch (error) {
      console.error("Error fetching skill breakdown:", error);
      throw error;
    }
  },

  /**
   * Get enhanced performance trends
   */
  async getEnhancedPerformanceTrends(params = {}) {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.ENHANCED_ANALYTICS.PERFORMANCE_TRENDS,
        { params }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching enhanced performance trends:", error);
      throw error;
    }
  },

  /**
   * Get learning streaks
   */
  async getLearningStreaks() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ENHANCED_ANALYTICS.LEARNING_STREAKS);
      return response.data;
    } catch (error) {
      console.error("Error fetching learning streaks:", error);
      throw error;
    }
  },

  /**
   * Get difficulty progression
   */
  async getDifficultyProgression() {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.ENHANCED_ANALYTICS.DIFFICULTY_PROGRESSION
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching difficulty progression:", error);
      throw error;
    }
  },

  /**
   * Get learning timeline
   */
  async getLearningTimeline(params = {}) {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.ENHANCED_ANALYTICS.LEARNING_TIMELINE,
        { params }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching learning timeline:", error);
      throw error;
    }
  },

  /**
   * Get comprehensive analytics report
   */
  async getComprehensiveReport() {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.ENHANCED_ANALYTICS.COMPREHENSIVE_REPORT
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching comprehensive report:", error);
      throw error;
    }
  },
};

export default analyticsService;
