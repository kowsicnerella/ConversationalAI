import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * Notifications Service
 * Handles all notification-related API calls
 */

export const notificationsService = {
  /**
   * Get all notifications for the user
   */
  async getNotifications(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.NOTIFICATIONS.LIST, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching notifications:", error);
      throw error;
    }
  },

  /**
   * Mark a notification as read
   */
  async markAsRead(notificationId) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.NOTIFICATIONS.MARK_READ(notificationId)
      );
      return response.data;
    } catch (error) {
      console.error("Error marking notification as read:", error);
      throw error;
    }
  },

  /**
   * Mark all notifications as read
   */
  async markAllAsRead() {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ);
      return response.data;
    } catch (error) {
      console.error("Error marking all notifications as read:", error);
      throw error;
    }
  },

  /**
   * Get notification preferences
   */
  async getPreferences() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.NOTIFICATIONS.PREFERENCES);
      return response.data;
    } catch (error) {
      console.error("Error fetching notification preferences:", error);
      throw error;
    }
  },

  /**
   * Update notification preferences
   */
  async updatePreferences(preferences) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.NOTIFICATIONS.PREFERENCES,
        preferences
      );
      return response.data;
    } catch (error) {
      console.error("Error updating notification preferences:", error);
      throw error;
    }
  },

  /**
   * Send a notification (admin/system)
   */
  async sendNotification(notificationData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.NOTIFICATIONS.SEND,
        notificationData
      );
      return response.data;
    } catch (error) {
      console.error("Error sending notification:", error);
      throw error;
    }
  },

  /**
   * Get unread notification count
   */
  async getUnreadCount() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.NOTIFICATIONS.LIST, {
        params: { unread_only: true },
      });
      // Count unread notifications from the response
      return {
        count: response.data.notifications?.filter((n) => !n.is_read).length || 0,
        notifications: response.data.notifications || [],
      };
    } catch (error) {
      console.error("Error fetching unread count:", error);
      throw error;
    }
  },

  /**
   * Create sample notifications (for testing)
   */
  async createSamples(userId) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.NOTIFICATIONS.CREATE_SAMPLES(userId)
      );
      return response.data;
    } catch (error) {
      console.error("Error creating sample notifications:", error);
      throw error;
    }
  },
};

export default notificationsService;
