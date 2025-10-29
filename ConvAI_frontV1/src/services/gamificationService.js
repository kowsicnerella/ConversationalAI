import axiosInstance from "../config/api";

/**
 * Gamification Service - Phase 9 Enhanced
 * Handles all gamification-related API calls:
 * - Daily Challenges (AI-powered, personalized)
 * - Achievements (52 achievements across 6 categories)
 * - Leaderboards (9 categories, 4 time periods)
 * - Learning Streaks (with freeze & recovery)
 * - Progress Milestones (automatic tracking)
 * - Social Features (connections, sharing, feed)
 */

// Phase 9 Enhanced Gamification routes (registered at /api/gamification-v2)
const GAMIFICATION_BASE = '/gamification-v2';

export const gamificationService = {
  // ============================================================================
  // DAILY CHALLENGES
  // ============================================================================

  /**
   * Get today's daily challenges (AI-generated)
   */
  async getDailyChallenges() {
    try {
      const response = await axiosInstance.get(`${GAMIFICATION_BASE}/challenges/today`);
      return response.data;
    } catch (error) {
      console.error("Error fetching daily challenges:", error);
      throw error;
    }
  },

  /**
   * Get challenge history for past 30 days
   */
  async getChallengeHistory() {
    try {
      const response = await axiosInstance.get(`${GAMIFICATION_BASE}/challenges/history`);
      return response.data;
    } catch (error) {
      console.error("Error fetching challenge history:", error);
      throw error;
    }
  },

  /**
   * Manually complete a challenge
   */
  async completeChallenge(challengeId) {
    try {
      const response = await axiosInstance.post(`${GAMIFICATION_BASE}/challenges/${challengeId}/complete`);
      return response.data;
    } catch (error) {
      console.error("Error completing challenge:", error);
      throw error;
    }
  },

  // ============================================================================
  // ACHIEVEMENTS
  // ============================================================================

  /**
   * Get all achievements with user's progress
   * @param {string} category - Optional: filter by category
   */
  async getAchievements(category = null) {
    try {
      const url = category 
        ? `${GAMIFICATION_BASE}/achievements?category=${category}`
        : `${GAMIFICATION_BASE}/achievements`;
      const response = await axiosInstance.get(url);
      return response.data;
    } catch (error) {
      console.error("Error fetching achievements:", error);
      throw error;
    }
  },

  /**
   * Toggle achievement showcase status
   */
  async toggleAchievementShowcase(achievementId) {
    try {
      const response = await axiosInstance.post(`${GAMIFICATION_BASE}/achievements/${achievementId}/showcase`);
      return response.data;
    } catch (error) {
      console.error("Error toggling achievement showcase:", error);
      throw error;
    }
  },

  // ============================================================================
  // LEADERBOARDS
  // ============================================================================

  /**
   * Get leaderboard rankings
   * @param {string} category - Category: overall, vocabulary, grammar, reading, writing, listening, speaking, study_time, activity_count, streak
   * @param {string} timePeriod - Time period: daily, weekly, monthly, all_time
   * @param {number} limit - Number of entries (default: 100)
   */
  async getLeaderboard(category = 'overall', timePeriod = 'weekly', limit = 100) {
    try {
      const response = await axiosInstance.get(
        `${GAMIFICATION_BASE}/leaderboard?category=${category}&time_period=${timePeriod}&limit=${limit}`
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
      throw error;
    }
  },

  /**
   * Get available leaderboard categories
   */
  async getLeaderboardCategories() {
    try {
      const response = await axiosInstance.get(`${GAMIFICATION_BASE}/leaderboard/categories`);
      return response.data;
    } catch (error) {
      console.error("Error fetching leaderboard categories:", error);
      throw error;
    }
  },

  // ============================================================================
  // LEARNING STREAKS
  // ============================================================================

  /**
   * Get user's streak information
   */
  async getStreak() {
    try {
      const response = await axiosInstance.get(`${GAMIFICATION_BASE}/streak`);
      return response.data;
    } catch (error) {
      console.error("Error fetching streak:", error);
      throw error;
    }
  },

  /**
   * Use a streak freeze to protect today's streak
   */
  async useStreakFreeze() {
    try {
      const response = await axiosInstance.post(`${GAMIFICATION_BASE}/streak/freeze`);
      return response.data;
    } catch (error) {
      console.error("Error using streak freeze:", error);
      throw error;
    }
  },

  /**
   * Update streak (called after completing an activity)
   */
  async updateStreak() {
    try {
      const response = await axiosInstance.post(`${GAMIFICATION_BASE}/streak/update`);
      return response.data;
    } catch (error) {
      console.error("Error updating streak:", error);
      throw error;
    }
  },

  // ============================================================================
  // PROGRESS MILESTONES
  // ============================================================================

  /**
   * Get user's progress milestones
   * @param {string} milestoneType - Optional: filter by type
   * @param {number} limit - Number of milestones (default: 20)
   */
  async getMilestones(milestoneType = null, limit = 20) {
    try {
      let url = `${GAMIFICATION_BASE}/milestones?limit=${limit}`;
      if (milestoneType) {
        url += `&milestone_type=${milestoneType}`;
      }
      const response = await axiosInstance.get(url);
      return response.data;
    } catch (error) {
      console.error("Error fetching milestones:", error);
      throw error;
    }
  },

  /**
   * Mark a milestone as celebrated
   */
  async celebrateMilestone(milestoneId) {
    try {
      const response = await axiosInstance.post(`${GAMIFICATION_BASE}/milestones/${milestoneId}/celebrate`);
      return response.data;
    } catch (error) {
      console.error("Error celebrating milestone:", error);
      throw error;
    }
  },

  // ============================================================================
  // SOCIAL FEATURES
  // ============================================================================

  /**
   * Get user's social connections
   * @param {string} status - Optional: filter by status (pending, accepted, blocked)
   * @param {string} connectionType - Optional: filter by type (friend, study_partner, practice_partner)
   */
  async getConnections(status = null, connectionType = null) {
    try {
      let url = `${GAMIFICATION_BASE}/social/connections`;
      const params = [];
      if (status) params.push(`status=${status}`);
      if (connectionType) params.push(`connection_type=${connectionType}`);
      if (params.length > 0) url += `?${params.join('&')}`;
      
      const response = await axiosInstance.get(url);
      return response.data;
    } catch (error) {
      console.error("Error fetching connections:", error);
      throw error;
    }
  },

  /**
   * Send a connection request
   * @param {number} targetUserId - Target user ID
   * @param {string} connectionType - Connection type (friend, study_partner, practice_partner)
   */
  async sendConnectionRequest(targetUserId, connectionType = 'friend') {
    try {
      const response = await axiosInstance.post(
        `${GAMIFICATION_BASE}/social/connect/${targetUserId}`,
        { connection_type: connectionType }
      );
      return response.data;
    } catch (error) {
      console.error("Error sending connection request:", error);
      throw error;
    }
  },

  /**
   * Share an achievement to social feed
   * @param {number} achievementId - Achievement ID
   * @param {string} caption - Optional caption
   * @param {string} visibility - Visibility (public, friends, private)
   */
  async shareAchievement(achievementId, caption = '', visibility = 'friends') {
    try {
      const response = await axiosInstance.post(
        `${GAMIFICATION_BASE}/social/share-achievement`,
        {
          achievement_id: achievementId,
          caption: caption,
          visibility: visibility
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error sharing achievement:", error);
      throw error;
    }
  },

  /**
   * Get social feed with shared achievements
   * @param {number} limit - Number of posts (default: 20)
   */
  async getSocialFeed(limit = 20) {
    try {
      const response = await axiosInstance.get(`${GAMIFICATION_BASE}/social/feed?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching social feed:", error);
      throw error;
    }
  },

  // ============================================================================
  // GAMIFICATION SUMMARY
  // ============================================================================

  /**
   * Get comprehensive gamification summary
   * Includes: streak, challenges, achievements, leaderboard, milestones, social
   */
  async getGamificationSummary() {
    try {
      const response = await axiosInstance.get(`${GAMIFICATION_BASE}/summary`);
      return response.data;
    } catch (error) {
      console.error("Error fetching gamification summary:", error);
      throw error;
    }
  },

  // ============================================================================
  // HEALTH CHECK
  // ============================================================================

  /**
   * Check gamification service health
   */
  async healthCheck() {
    try {
      const response = await axiosInstance.get(`${GAMIFICATION_BASE}/health`);
      return response.data;
    } catch (error) {
      console.error("Health check failed:", error);
      return { status: 'unhealthy' };
    }
  },

  // ============================================================================
  // LEGACY METHODS (Backward Compatibility)
  // ============================================================================

  /**
   * @deprecated Use getAchievements() instead
   */
  async getUserBadges(userId) {
    console.warn("getUserBadges is deprecated. Use getAchievements() instead.");
    return this.getAchievements();
  },

  /**
   * @deprecated Use getGamificationSummary() instead
   */
  async getProfile() {
    console.warn("getProfile is deprecated. Use getGamificationSummary() instead.");
    return this.getGamificationSummary();
  },

  /**
   * @deprecated Use getGamificationSummary() instead
   */
  async getStats(userId) {
    console.warn("getStats is deprecated. Use getGamificationSummary() instead.");
    return this.getGamificationSummary();
  },
};

export default gamificationService;
