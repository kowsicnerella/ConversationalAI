import axiosInstance, { API_ENDPOINTS } from "../config/api";

/**
 * Vocabulary Service
 * Handles all vocabulary-related API calls
 */

export const vocabularyService = {
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
      const response = await axiosInstance.get(API_ENDPOINTS.VOCABULARY.STATS);
      return response.data;
    } catch (error) {
      console.error("Error fetching vocabulary stats:", error);
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
