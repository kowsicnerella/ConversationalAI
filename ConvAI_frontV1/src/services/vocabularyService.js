import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * Vocabulary Service - Phase 5 Implementation
 * Handles all vocabulary-related API calls with SM-2 Spaced Repetition
 */

export const vocabularyService = {
  // ==================== Core Vocabulary Management ====================
  
  /**
   * Get vocabulary words list
   */
  async getVocabularyWords(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.WORDS, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching vocabulary words:", error);
      throw error;
    }
  },
  
  /**
   * Get user's vocabulary with filters
   */
  async getMyVocabulary(filters = {}) {
    try {
      const response = await axiosInstance.get('/vocabulary/my-vocabulary', { params: filters });
      return response.data;
    } catch (error) {
      console.error("Error fetching my vocabulary:", error);
      throw error;
    }
  },

  /**
   * Get vocabulary word detail
   */
  async getWordDetail(wordId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.WORD_DETAIL(wordId));
      return response.data;
    } catch (error) {
      console.error("Error fetching word detail:", error);
      throw error;
    }
  },
  
  // ==================== Vocabulary Introduction ====================
  
  /**
   * Introduce a new vocabulary word with AI-generated content
   */
  async introduceWord(wordData) {
    try {
      const response = await axiosInstance.post('/vocabulary/introduce', wordData);
      return response.data;
    } catch (error) {
      console.error("Error introducing word:", error);
      throw error;
    }
  },
  
  /**
   * Introduce vocabulary from text passage
   */
  async introduceFromText(textData) {
    try {
      const response = await axiosInstance.post('/vocabulary/introduce-from-text', textData);
      return response.data;
    } catch (error) {
      console.error("Error introducing vocabulary from text:", error);
      throw error;
    }
  },
  
  // ==================== SM-2 Spaced Repetition ====================
  
  /**
   * Get words due for review (spaced repetition)
   */
  async getWordsDue(limit = 20) {
    try {
      const response = await axiosInstance.get('/vocabulary/words-due', { 
        params: { limit } 
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching words due:", error);
      throw error;
    }
  },
  
  /**
   * Submit vocabulary review with quality rating (SM-2)
   */
  async submitReview(reviewData) {
    try {
      const response = await axiosInstance.post('/vocabulary/review', reviewData);
      return response.data;
    } catch (error) {
      console.error("Error submitting review:", error);
      throw error;
    }
  },
  
  /**
   * Submit batch reviews
   */
  async submitBatchReview(reviewsData) {
    try {
      const response = await axiosInstance.post('/vocabulary/batch-review', reviewsData);
      return response.data;
    } catch (error) {
      console.error("Error submitting batch review:", error);
      throw error;
    }
  },
  
  // ==================== Practice Sessions ====================
  
  /**
   * Start a vocabulary practice session
   */
  async startPracticeSession(sessionData) {
    try {
      const response = await axiosInstance.post('/vocabulary/practice-session/start', sessionData);
      return response.data;
    } catch (error) {
      console.error("Error starting practice session:", error);
      throw error;
    }
  },
  
  /**
   * Get practice session details
   */
  async getPracticeSession(sessionId) {
    try {
      const response = await axiosInstance.get(`/vocabulary/practice-session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching practice session:", error);
      throw error;
    }
  },
  
  /**
   * Complete practice session
   */
  async completePracticeSession(sessionId, resultsData) {
    try {
      const response = await axiosInstance.post(`/vocabulary/practice-session/${sessionId}/complete`, resultsData);
      return response.data;
    } catch (error) {
      console.error("Error completing practice session:", error);
      throw error;
    }
  },
  
  /**
   * Get practice history
   */
  async getPracticeHistory(params = {}) {
    try {
      const response = await axiosInstance.get('/vocabulary/practice-history', { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching practice history:", error);
      throw error;
    }
  },
  
  // ==================== Practice Activities ====================
  
  /**
   * Generate practice activity for a word
   */
  async generatePracticeActivity(wordId, activityType) {
    try {
      const response = await axiosInstance.post('/vocabulary/generate-practice-activity', {
        word_id: wordId,
        activity_type: activityType
      });
      return response.data;
    } catch (error) {
      console.error("Error generating practice activity:", error);
      throw error;
    }
  },
  
  // ==================== Mastery & Progress ====================
  
  /**
   * Get vocabulary mastery assessment
   */
  async getVocabularyMastery() {
    try {
      const response = await axiosInstance.get('/vocabulary/mastery');
      return response.data;
    } catch (error) {
      console.error("Error fetching vocabulary mastery:", error);
      throw error;
    }
  },

  /**
   * Add a new vocabulary word
   */
  async addWord(wordData) {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.VOCABULARY.WORDS, wordData);
      return response.data;
    } catch (error) {
      console.error("Error adding vocabulary word:", error);
      throw error;
    }
  },

  /**
   * Update a vocabulary word
   */
  async updateWord(wordId, wordData) {
    try {
      const response = await axiosInstance.put(
        API_ENDPOINTS.VOCABULARY.UPDATE_WORD(wordId),
        wordData
      );
      return response.data;
    } catch (error) {
      console.error("Error updating vocabulary word:", error);
      throw error;
    }
  },

  /**
   * Delete a vocabulary word
   */
  async deleteWord(wordId) {
    try {
      const response = await axiosInstance.delete(API_ENDPOINTS.VOCABULARY.DELETE_WORD(wordId));
      return response.data;
    } catch (error) {
      console.error("Error deleting vocabulary word:", error);
      throw error;
    }
  },

  /**
   * Get examples for a word
   */
  async getWordExamples(wordId) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.EXAMPLES(wordId));
      return response.data;
    } catch (error) {
      console.error("Error fetching word examples:", error);
      throw error;
    }
  },

  /**
   * Submit practice result for a word
   */
  async submitPracticeResult(wordId, resultData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.VOCABULARY.PRACTICE_RESULT(wordId),
        resultData
      );
      return response.data;
    } catch (error) {
      console.error("Error submitting practice result:", error);
      throw error;
    }
  },
  
  /**
   * Get vocabulary statistics
   */
  async getVocabularyStats() {
    try {
      const response = await axiosInstance.get('/vocabulary/statistics');
      return response.data;
    } catch (error) {
      console.error("Error fetching vocabulary stats:", error);
      throw error;
    }
  },
  
  /**
   * Get activity reinforcement stats
   */
  async getReinforcementStats(days = 30) {
    try {
      const response = await axiosInstance.get('/vocabulary/reinforcement-stats', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching reinforcement stats:", error);
      throw error;
    }
  },
  
  // ==================== Word Networks & Relationships ====================
  
  /**
   * Get word network (semantic relationships)
   */
  async getWordNetwork(wordId, depth = 2) {
    try {
      const response = await axiosInstance.get(`/vocabulary/word-network/${wordId}`, {
        params: { depth }
      });
      return response.data;
    } catch (error) {
      console.error("Error fetching word network:", error);
      throw error;
    }
  },
  
  // ==================== User Actions ====================
  
  /**
   * Toggle favorite status
   */
  async toggleFavorite(wordId) {
    try {
      const response = await axiosInstance.post('/vocabulary/toggle-favorite', {
        word_id: wordId
      });
      return response.data;
    } catch (error) {
      console.error("Error toggling favorite:", error);
      throw error;
    }
  },
  
  /**
   * Add note to vocabulary word
   */
  async addNote(wordId, note) {
    try {
      const response = await axiosInstance.post('/vocabulary/add-note', {
        word_id: wordId,
        note: note
      });
      return response.data;
    } catch (error) {
      console.error("Error adding note:", error);
      throw error;
    }
  },

  /**
   * Search vocabulary words
   */
  async searchWords(query) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.SEARCH, {
        params: { q: query },
      });
      return response.data;
    } catch (error) {
      console.error("Error searching vocabulary words:", error);
      throw error;
    }
  },

  /**
   * Get words for practice
   */
  async getPracticeWords(params = {}) {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.PRACTICE, { params });
      return response.data;
    } catch (error) {
      console.error("Error fetching practice words:", error);
      throw error;
    }
  },

  /**
   * Get spaced repetition words
   */
  async getSpacedRepetitionWords() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.SPACED_REPETITION);
      return response.data;
    } catch (error) {
      console.error("Error fetching spaced repetition words:", error);
      throw error;
    }
  },

  /**
   * Track vocabulary usage in personalization
   */
  async trackVocabularyUsage(wordData) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.PERSONALIZATION.TRACK_VOCABULARY,
        wordData
      );
      return response.data;
    } catch (error) {
      console.error("Error tracking vocabulary usage:", error);
      throw error;
    }
  },

  /**
   * Get personalized vocabulary
   */
  async getPersonalizedVocabulary() {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.PERSONALIZATION.VOCABULARY);
      return response.data;
    } catch (error) {
      console.error("Error fetching personalized vocabulary:", error);
      throw error;
    }
  },

  /**
   * Practice a specific vocabulary word
   */
  async practiceWord(wordId) {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.PERSONALIZATION.PRACTICE_VOCABULARY(wordId)
      );
      return response.data;
    } catch (error) {
      console.error("Error practicing vocabulary word:", error);
      throw error;
    }
  },
};

export default vocabularyService;
