import React, { createContext, useState, useCallback, useEffect } from "react";
import axiosInstance from "../config/api";

export const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [learningContext, setLearningContext] = useState(null);
  const [memories, setMemories] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load all chat data
  const loadConversations = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get("/chat-v2/conversations");
      if (response.data.success) {
        setConversations(response.data.conversations);
        if (response.data.conversations.length > 0) {
          setCurrentConversation(response.data.conversations[0]);
        }
      }
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load specific conversation
  const loadConversation = useCallback(async (conversationId) => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(
        `/chat-v2/conversations/${conversationId}`
      );
      if (response.data.success) {
        setCurrentConversation(response.data.conversation);
        setMessages(response.data.messages || []);
      }
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Create new conversation
  const createConversation = useCallback(
    async (title, topic = "General") => {
      try {
        setLoading(true);
        const response = await axiosInstance.post("/chat-v2/conversations", {
          title,
          topic,
        });
        if (response.data.success) {
          const newConv = response.data.conversation;
          setConversations([newConv, ...conversations]);
          setCurrentConversation(newConv);
          setMessages([]);
          setError(null);
          return newConv;
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [conversations]
  );

  // Send message
  const sendMessage = useCallback(
    async (message, useWebSearch = false, topic = "general") => {
      if (!currentConversation) return null;

      try {
        setLoading(true);
        const response = await axiosInstance.post(
          `/chat-v2/conversations/${currentConversation.id}/messages`,
          {
            message,
            use_web_search: useWebSearch,
            topic,
          }
        );

        if (response.data.success) {
          setMessages((prev) => [
            ...prev,
            response.data.user_message,
            response.data.ai_response,
          ]);
          setCurrentConversation(response.data.conversation);
          setError(null);
          return response.data.ai_response;
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [currentConversation]
  );

  // Load learning context
  const loadLearningContext = useCallback(async () => {
    try {
      const response = await axiosInstance.get("/chat-v2/user-learning-context");
      if (response.data.success) {
        setLearningContext(response.data.context);
      }
    } catch (err) {
      console.error("Error loading learning context:", err);
    }
  }, []);

  // Load memories
  const loadMemories = useCallback(async () => {
    try {
      const response = await axiosInstance.get("/chat-v2/user-memories");
      if (response.data.success) {
        setMemories(response.data.memories);
      }
    } catch (err) {
      console.error("Error loading memories:", err);
    }
  }, []);

  // Load statistics
  const loadStatistics = useCallback(async () => {
    try {
      const response = await axiosInstance.get("/chat-v2/learning-statistics");
      if (response.data.success) {
        setStatistics(response.data.statistics);
      }
    } catch (err) {
      console.error("Error loading statistics:", err);
    }
  }, []);

  // Search conversations
  const searchConversations = useCallback(async (query) => {
    try {
      const response = await axiosInstance.post("/chat-v2/search-conversations", {
        query,
      });
      if (response.data.success) {
        setConversations(response.data.conversations);
      }
    } catch (err) {
      setError(err.message);
    }
  }, []);

  // Web search
  const webSearch = useCallback(async (query) => {
    try {
      const response = await axiosInstance.post("/chat-v2/web-search", {
        query,
      });
      if (response.data.success) {
        return response.data.results;
      }
    } catch (err) {
      console.error("Web search error:", err);
      return [];
    }
  }, []);

  // Search memories
  const searchMemories = useCallback(async (query) => {
    try {
      const response = await axiosInstance.post("/chat-v2/search-memories", {
        query,
      });
      if (response.data.success) {
        return response.data.results;
      }
    } catch (err) {
      console.error("Memory search error:", err);
      return [];
    }
  }, []);

  // Delete conversation
  const deleteConversation = useCallback(async (conversationId) => {
    try {
      const response = await axiosInstance.delete(
        `/chat-v2/conversations/${conversationId}`
      );
      if (response.data.success) {
        setConversations(conversations.filter((c) => c.id !== conversationId));
        if (currentConversation?.id === conversationId) {
          setCurrentConversation(null);
          setMessages([]);
        }
      }
    } catch (err) {
      setError(err.message);
    }
  }, [conversations, currentConversation]);

  // Export conversation
  const exportConversation = useCallback(
    async (format = "json") => {
      if (!currentConversation) return null;

      try {
        const response = await axiosInstance.get(
          `/chat-v2/conversations/${currentConversation.id}/export`,
          { params: { format } }
        );
        return response.data.data;
      } catch (err) {
        setError(err.message);
        return null;
      }
    },
    [currentConversation]
  );

  // Semantic search
  const semanticSearch = useCallback(async (query) => {
    try {
      const response = await axiosInstance.post("/chat-v2/semantic-search", {
        query,
      });
      if (response.data.success) {
        return response.data.results;
      }
    } catch (err) {
      console.error("Semantic search error:", err);
      return [];
    }
  }, []);

  // Initialize chat data - only when user is authenticated
  const initializeChatData = useCallback(async () => {
    // Check if user is authenticated before making API calls
    const token = localStorage.getItem("access_token");
    if (!token) {
      console.log("ChatContext: Skipping initialization - user not authenticated");
      return;
    }
    
    if (isInitialized) {
      console.log("ChatContext: Already initialized");
      return;
    }
    
    console.log("ChatContext: Initializing chat data...");
    setIsInitialized(true);
    
    try {
      await Promise.all([
        loadConversations(),
        loadLearningContext(),
        loadMemories(),
        loadStatistics()
      ]);
    } catch (err) {
      console.error("Error initializing chat data:", err);
      // Reset initialization flag on error so it can retry
      setIsInitialized(false);
    }
  }, [isInitialized, loadConversations, loadLearningContext, loadMemories, loadStatistics]);

  // Don't auto-initialize on mount - wait for explicit call from authenticated pages
  // This prevents 401 errors on the landing page

  const value = {
    // State
    conversations,
    currentConversation,
    messages,
    learningContext,
    memories,
    statistics,
    loading,
    error,
    isInitialized,

    // Methods
    initializeChatData,
    loadConversations,
    loadConversation,
    createConversation,
    sendMessage,
    loadLearningContext,
    loadMemories,
    loadStatistics,
    searchConversations,
    webSearch,
    searchMemories,
    deleteConversation,
    exportConversation,
    semanticSearch,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const context = React.useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within ChatProvider");
  }
  return context;
};
