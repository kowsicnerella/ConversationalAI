/**
 * Goals Service
 * API calls for goal management, progress tracking, and certificates
 */

import axiosInstance, { API_ENDPOINTS } from '../config/api';

export const goalsService = {
  /**
   * Get all available goal templates
   * @returns {Promise} List of available goal types
   */
  getAvailableGoals: () => {
    return axiosInstance.get(API_ENDPOINTS.GOALS.AVAILABLE);
  },

  /**
   * Create a new goal for the user
   * @param {Object} goalData - Goal creation data
   * @param {number} goalData.goal_type_id - Template goal type ID (for template goals)
   * @param {boolean} goalData.is_custom - Whether this is a custom goal
   * @param {string} goalData.title - Goal title (required for custom goals)
   * @param {string} goalData.description - Goal description
   * @param {Object} goalData.criteria - Goal criteria (required for custom goals)
   * @param {string} goalData.target_date - Target completion date (YYYY-MM-DD)
   * @param {Array} goalData.milestones - Custom milestones
   * @returns {Promise} Created goal object
   */
  createGoal: (goalData) => {
    return axiosInstance.post(API_ENDPOINTS.GOALS.CREATE, goalData);
  },

  /**
   * Get user's goals with optional status filter
   * @param {string} status - Filter by status: 'active', 'completed', 'paused', 'abandoned'
   * @returns {Promise} List of user's goals
   */
  getMyGoals: (status = null) => {
    const params = status ? { status } : {};
    return axiosInstance.get(API_ENDPOINTS.GOALS.MY_GOALS, { params });
  },

  /**
   * Get detailed goal information with milestones
   * @param {number} goalId - Goal ID
   * @returns {Promise} Detailed goal object
   */
  getGoalDetail: (goalId) => {
    return axiosInstance.get(API_ENDPOINTS.GOALS.DETAIL(goalId));
  },

  /**
   * Update goal progress (usually called automatically by system)
   * @param {number} goalId - Goal ID
   * @param {Object} progressData - Progress update data
   * @returns {Promise} Updated goal
   */
  updateGoalProgress: (goalId, progressData) => {
    return axiosInstance.post(API_ENDPOINTS.GOALS.UPDATE_PROGRESS(goalId), progressData);
  },

  /**
   * Manually complete a goal
   * @param {number} goalId - Goal ID
   * @returns {Promise} Completion result with certificate and rewards
   */
  completeGoal: (goalId) => {
    return axiosInstance.post(API_ENDPOINTS.GOALS.COMPLETE(goalId));
  },

  /**
   * Abandon a goal
   * @param {number} goalId - Goal ID
   * @returns {Promise} Abandonment confirmation
   */
  abandonGoal: (goalId) => {
    return axiosInstance.post(API_ENDPOINTS.GOALS.ABANDON(goalId));
  },

  /**
   * Create a new milestone for a goal
   * @param {number} goalId - Goal ID
   * @param {Object} milestoneData - Milestone data
   * @param {string} milestoneData.title - Milestone title
   * @param {string} milestoneData.description - Milestone description
   * @param {Object} milestoneData.criteria - Completion criteria
   * @param {number} milestoneData.order - Display order
   * @returns {Promise} Created milestone
   */
  createMilestone: (goalId, milestoneData) => {
    return axiosInstance.post(API_ENDPOINTS.GOALS.CREATE_MILESTONE(goalId), milestoneData);
  },

  /**
   * Complete a milestone
   * @param {number} milestoneId - Milestone ID
   * @returns {Promise} Completion result
   */
  completeMilestone: (milestoneId) => {
    return axiosInstance.post(API_ENDPOINTS.GOALS.COMPLETE_MILESTONE(milestoneId));
  },

  /**
   * Get goal progress history/timeline
   * @param {number} goalId - Goal ID
   * @returns {Promise} Progress history array
   */
  getProgressHistory: (goalId) => {
    return axiosInstance.get(API_ENDPOINTS.GOALS.PROGRESS_HISTORY(goalId));
  },

  /**
   * Get list of user's certificates
   * @returns {Promise} List of earned certificates
   */
  getCertificates: () => {
    return axiosInstance.get(API_ENDPOINTS.GOALS.CERTIFICATES);
  },

  /**
   * Get detailed certificate information
   * @param {number} certificateId - Certificate ID
   * @returns {Promise} Certificate detail
   */
  getCertificateDetail: (certificateId) => {
    return axiosInstance.get(API_ENDPOINTS.GOALS.CERTIFICATE_DETAIL(certificateId));
  },

  /**
   * Download certificate as PDF
   * @param {number} certificateId - Certificate ID
   * @returns {Promise} PDF blob
   */
  downloadCertificate: async (certificateId) => {
    const response = await axiosInstance.get(
      API_ENDPOINTS.GOALS.CERTIFICATE_DOWNLOAD(certificateId),
      { responseType: 'blob' }
    );
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `certificate_${certificateId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    return response;
  },

  /**
   * Helper: Calculate goal progress percentage
   * @param {Object} goal - Goal object with milestones
   * @returns {number} Progress percentage (0-100)
   */
  calculateProgress: (goal) => {
    if (!goal.milestones || goal.milestones.length === 0) {
      return goal.current_value && goal.target_value 
        ? Math.min((goal.current_value / goal.target_value) * 100, 100)
        : 0;
    }
    
    const completedMilestones = goal.milestones.filter(m => m.is_completed).length;
    return Math.round((completedMilestones / goal.milestones.length) * 100);
  },

  /**
   * Helper: Check if goal is overdue
   * @param {Object} goal - Goal object
   * @returns {boolean} True if goal is overdue
   */
  isOverdue: (goal) => {
    if (!goal.target_date || goal.status === 'completed') return false;
    return new Date(goal.target_date) < new Date();
  },

  /**
   * Helper: Get days remaining until target date
   * @param {Object} goal - Goal object
   * @returns {number} Days remaining (negative if overdue)
   */
  getDaysRemaining: (goal) => {
    if (!goal.target_date) return null;
    const today = new Date();
    const target = new Date(goal.target_date);
    const diffTime = target - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  },

  /**
   * Helper: Format goal status for display
   * @param {string} status - Goal status
   * @returns {Object} Status with label, color, and icon
   */
  formatStatus: (status) => {
    const statusMap = {
      'active': {
        label: 'Active',
        color: 'primary',
        icon: '🎯',
        description: 'In Progress'
      },
      'completed': {
        label: 'Completed',
        color: 'success',
        icon: '✅',
        description: 'Successfully Achieved'
      },
      'paused': {
        label: 'Paused',
        color: 'warning',
        icon: '⏸️',
        description: 'Temporarily Paused'
      },
      'abandoned': {
        label: 'Abandoned',
        color: 'error',
        icon: '❌',
        description: 'Given Up'
      }
    };
    return statusMap[status] || statusMap['active'];
  },
};

export default goalsService;
