import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * Learning Path Service
 * Handles all learning path-related API calls
 */

export const learningPathService = {
  /**
   * Get all available learning paths
   */
  async getLearningPaths(params = {}) {
    try {
      // Check if user is authenticated
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('No access token found. User may not be logged in.');
        throw new Error('Authentication required. Please log in.');
      }

      const response = await axiosInstance.get(API_ENDPOINTS.COURSES.LEARNING_PATHS, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching learning paths:", error);
      console.error("Error response:", error.response?.data);
      console.error("Error status:", error.response?.status);
      throw error;
    }
  },

  /**
   * Get learning path detail by ID
   */
  async getLearningPathDetail(pathId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.COURSES.PATH_DETAIL(pathId));
      return response.data;
    } catch (error) {
      console.error("Error fetching learning path detail:", error);
      throw error;
    }
  },

  /**
   * Get user's enrolled learning paths
   */
  async getMyLearningPaths() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.COURSES.MY_PATHS);
      return response.data;
    } catch (error) {
      console.error("Error fetching enrolled learning paths:", error);
      throw error;
    }
  },

  /**
   * Enroll in a learning path
   */
  async enrollInPath(pathId) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.COURSES.ENROLL_PATH(pathId));
      return response.data;
    } catch (error) {
      console.error("Error enrolling in learning path:", error);
      throw error;
    }
  },

  /**
   * Get learning path progress
   */
  async getPathProgress(pathId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.COURSES.PROGRESS(pathId));
      return response.data;
    } catch (error) {
      console.error("Error fetching path progress:", error);
      throw error;
    }
  },

  /**
   * Get activities for a learning path
   */
  async getPathActivities(pathId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.LEARNING_PATH_ACTIVITIES(pathId));
      return response.data;
    } catch (error) {
      console.error("Error fetching path activities:", error);
      throw error;
    }
  },

  /**
   * Get chapters for a learning path
   */
  async getPathChapters(pathId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.CHAPTERS.LIST(pathId));
      return response.data;
    } catch (error) {
      console.error("Error fetching path chapters:", error);
      throw error;
    }
  },

  /**
   * Get personalized learning path recommendations
   */
  async getPersonalizedRecommendations(assessmentData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.LEARNING_PATHS.PERSONALIZED_RECOMMENDATION,
        assessmentData
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching personalized recommendations:", error);
      throw error;
    }
  },

  /**
   * Create custom learning path
   */
  async createCustomPath(pathData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.LEARNING_PATHS.CREATE_CUSTOM,
        pathData
      );
      return response.data;
    } catch (error) {
      console.error("Error creating custom learning path:", error);
      throw error;
    }
  },

  /**
   * Get progress analysis for a learning path
   */
  async getProgressAnalysis(pathId) {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.LEARNING_PATHS.PROGRESS_ANALYSIS(pathId)
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching progress analysis:", error);
      throw error;
    }
  },

  /**
   * Start a chapter
   */
  async startChapter(chapterId) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.CHAPTERS.START(chapterId));
      return response.data;
    } catch (error) {
      console.error("Error starting chapter:", error);
      throw error;
    }
  },

  /**
   * Complete a chapter
   */
  async completeChapter(chapterId, completionData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.CHAPTERS.COMPLETE(chapterId),
        completionData
      );
      return response.data;
    } catch (error) {
      console.error("Error completing chapter:", error);
      throw error;
    }
  },

  /**
   * Get chapter detail
   */
  async getChapterDetail(chapterId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.CHAPTERS.DETAIL(chapterId));
      return response.data;
    } catch (error) {
      console.error("Error fetching chapter detail:", error);
      throw error;
    }
  },

  /**
   * Get chapter progress
   */
  async getChapterProgress(chapterId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.CHAPTERS.PROGRESS(chapterId));
      return response.data;
    } catch (error) {
      console.error("Error fetching chapter progress:", error);
      throw error;
    }
  },
};

export default learningPathService;
