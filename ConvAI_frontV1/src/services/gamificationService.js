import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * Gamification Service
 * Handles all gamification-related API calls (badges, achievements, leaderboard, etc.)
 */

export const gamificationService = {
  /**
   * Get user's badges
   */
  async getUserBadges(userId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.GAMIFICATION.BADGES(userId));
      return response.data;
    } catch (error) {
      console.error("Error fetching user badges:", error);
      throw error;
    }
  },

  /**
   * Get available badges
   */
  async getAvailableBadges() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.GAMIFICATION.AVAILABLE_BADGES);
      return response.data;
    } catch (error) {
      console.error("Error fetching available badges:", error);
      throw error;
    }
  },

  /**
   * Check achievements for user
   */
  async checkAchievements(userId) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.GAMIFICATION.CHECK_ACHIEVEMENTS(userId)
      );
      return response.data;
    } catch (error) {
      console.error("Error checking achievements:", error);
      throw error;
    }
  },

  /**
   * Update user streak
   */
  async updateStreak(userId) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.GAMIFICATION.UPDATE_STREAK(userId));
      return response.data;
    } catch (error) {
      console.error("Error updating streak:", error);
      throw error;
    }
  },

  /**
   * Get leaderboard
   */
  async getLeaderboard(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.GAMIFICATION.LEADERBOARD, {
        params,
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
      throw error;
    }
  },

  /**
   * Get daily challenge for user
   */
  async getDailyChallenge(userId) {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.GAMIFICATION.DAILY_CHALLENGE(userId)
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching daily challenge:", error);
      throw error;
    }
  },

  /**
   * Get all achievements
   */
  async getAchievements() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.GAMIFICATION.ACHIEVEMENTS);
      return response.data;
    } catch (error) {
      console.error("Error fetching achievements:", error);
      throw error;
    }
  },

  /**
   * Get gamification stats for user
   */
  async getStats(userId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.GAMIFICATION.STATS(userId));
      return response.data;
    } catch (error) {
      console.error("Error fetching gamification stats:", error);
      throw error;
    }
  },

  /**
   * Get gamification profile
   */
  async getProfile() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.GAMIFICATION.PROFILE);
      return response.data;
    } catch (error) {
      console.error("Error fetching gamification profile:", error);
      throw error;
    }
  },

  /**
   * Get reward details
   */
  async getReward(rewardId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.GAMIFICATION.REWARD(rewardId));
      return response.data;
    } catch (error) {
      console.error("Error fetching reward:", error);
      throw error;
    }
  },
};

export default gamificationService;
