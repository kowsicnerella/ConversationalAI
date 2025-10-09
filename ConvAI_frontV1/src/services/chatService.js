import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * Chat Service
 * Handles all chat and conversation-related API calls
 */

export const chatService = {
  /**
   * Get conversation history
   */
  async getConversations(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.CHAT.CONVERSATIONS, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching conversations:", error);
      throw error;
    }
  },

  /**
   * Get messages for a specific conversation
   */
  async getConversationMessages(conversationId, params = {}) {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.CHAT.MESSAGES(conversationId),
        { params }
      );
      return response.data;
    } catch (error) {
      console.error("Error fetching conversation messages:", error);
      throw error;
    }
  },

  /**
   * Send a message in a conversation
   */
  async sendMessage(conversationId, messageData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.CHAT.SEND_MESSAGE(conversationId),
        messageData
      );
      return response.data;
    } catch (error) {
      console.error("Error sending message:", error);
      throw error;
    }
  },

  /**
   * Start a quick chat session
   */
  async quickChat(messageData) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.CHAT.QUICK_CHAT, messageData);
      return response.data;
    } catch (error) {
      console.error("Error starting quick chat:", error);
      throw error;
    }
  },

  /**
   * Send a chat message (general)
   */
  async send(messageData) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.CHAT.SEND, messageData);
      return response.data;
    } catch (error) {
      console.error("Error sending chat message:", error);
      throw error;
    }
  },

  /**
   * Provide feedback for a conversation
   */
  async provideFeedback(conversationId, feedbackData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.CHAT.FEEDBACK(conversationId),
        feedbackData
      );
      return response.data;
    } catch (error) {
      console.error("Error providing conversation feedback:", error);
      throw error;
    }
  },

  /**
   * Post general feedback
   */
  async postFeedback(feedbackData) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.CHAT.POST_FEEDBACK, feedbackData);
      return response.data;
    } catch (error) {
      console.error("Error posting feedback:", error);
      throw error;
    }
  },

  /**
   * Get chat suggestions
   */
  async getSuggestions() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.CHAT.SUGGESTIONS);
      return response.data;
    } catch (error) {
      console.error("Error fetching chat suggestions:", error);
      throw error;
    }
  },

  /**
   * Get alternative chat suggestions
   */
  async getChatSuggestions(context = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.CHAT.CHAT_SUGGESTIONS, {
        params: context,
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching chat suggestions:", error);
      throw error;
    }
  },

  /**
   * Start practice assistant session
   */
  async startPracticeAssistant(practiceData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.CHAT.PRACTICE_ASSISTANT,
        practiceData
      );
      return response.data;
    } catch (error) {
      console.error("Error starting practice assistant:", error);
      throw error;
    }
  },

  /**
   * Chat with practice assistant
   */
  async practiceAssistantChat(sessionId, messageData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.CHAT.PRACTICE_CHAT(sessionId),
        messageData
      );
      return response.data;
    } catch (error) {
      console.error("Error chatting with practice assistant:", error);
      throw error;
    }
  },

  /**
   * Get AI conversation context
   */
  async getConversationContext(conversationId) {
    try {
      const response = await axiosInstance.get(`/chat/context/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching conversation context:", error);
      throw error;
    }
  },

  /**
   * Start a new learning session
   */
  async startLearningSession(sessionData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.PERSONALIZATION.START_SESSION,
        sessionData
      );
      return response.data;
    } catch (error) {
      console.error("Error starting learning session:", error);
      throw error;
    }
  },

  /**
   * End a learning session
   */
  async endLearningSession(sessionId, sessionData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.PERSONALIZATION.END_SESSION(sessionId),
        sessionData
      );
      return response.data;
    } catch (error) {
      console.error("Error ending learning session:", error);
      throw error;
    }
  },
};

export default chatService;
