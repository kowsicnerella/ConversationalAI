import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * User Service
 * Handles all user-related API calls (profile, settings, etc.)
 */

export const userService = {
  /**
   * Get user profile
   */
  async getProfile() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.PROFILE);
      return response.data;
    } catch (error) {
      console.error("Error fetching user profile:", error);
      throw error;
    }
  },

  /**
   * Update user profile
   */
  async updateProfile(profileData) {
    try {
      const response = await axiosInstance.put(API_ENDPOINTS.USER.UPDATE_PROFILE, profileData);
      return response.data;
    } catch (error) {
      console.error("Error updating user profile:", error);
      throw error;
    }
  },

  /**
   * Get user settings
   */
  async getSettings() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.SETTINGS);
      return response.data;
    } catch (error) {
      console.error("Error fetching user settings:", error);
      throw error;
    }
  },

  /**
   * Update user settings
   */
  async updateSettings(settings) {
    try {
      const response = await axiosInstance.put(API_ENDPOINTS.USER.SETTINGS, settings);
      return response.data;
    } catch (error) {
      console.error("Error updating user settings:", error);
      throw error;
    }
  },

  /**
   * Change user password
   */
  async changePassword(passwordData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.USER.CHANGE_PASSWORD,
        passwordData
      );
      return response.data;
    } catch (error) {
      console.error("Error changing password:", error);
      throw error;
    }
  },

  /**
   * Get user statistics
   */
  async getStatistics() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.STATISTICS);
      return response.data;
    } catch (error) {
      console.error("Error fetching user statistics:", error);
      throw error;
    }
  },

  /**
   * Delete user account
   */
  async deleteAccount() {
    try {
      const response = await axiosInstance.delete(API_ENDPOINTS.USER.DELETE_ACCOUNT);
      return response.data;
    } catch (error) {
      console.error("Error deleting account:", error);
      throw error;
    }
  },

  /**
   * Get user activity history
   */
  async getHistory(userId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.HISTORY(userId));
      return response.data;
    } catch (error) {
      console.error("Error fetching user history:", error);
      throw error;
    }
  },

  /**
   * Get user's learning paths
   */
  async getLearningPaths(userId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.LEARNING_PATHS(userId));
      return response.data;
    } catch (error) {
      console.error("Error fetching user learning paths:", error);
      throw error;
    }
  },

  /**
   * Create a learning path for user
   */
  async createLearningPath(pathData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.USER.CREATE_LEARNING_PATH,
        pathData
      );
      return response.data;
    } catch (error) {
      console.error("Error creating learning path:", error);
      throw error;
    }
  },

  /**
   * Record activity completion
   */
  async recordActivityCompletion(completionData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.USER.ACTIVITY_COMPLETION,
        completionData
      );
      return response.data;
    } catch (error) {
      console.error("Error recording activity completion:", error);
      throw error;
    }
  },

  /**
   * Get user dashboard data
   */
  async getDashboard(userId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.DASHBOARD(userId));
      return response.data;
    } catch (error) {
      console.error("Error fetching user dashboard:", error);
      throw error;
    }
  },
};

export default userService;
