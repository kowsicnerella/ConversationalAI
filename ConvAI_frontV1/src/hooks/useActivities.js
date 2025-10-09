import { useState, useEffect, useCallback } from "react";
import { activityService } from "../services/activityService";

/**
 * Custom hook for managing activities
 * @param {Object} options - Hook options
 * @param {boolean} options.autoFetch - Whether to fetch activities on mount
 * @param {Object} options.filters - Initial filters
 * @returns {Object} Activities state and methods
 */
export const useActivities = (options = {}) => {
  const { autoFetch = true, filters: initialFilters = {} } = options;

  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);

  const fetchActivities = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await activityService.getActivities({
        ...filters,
        ...params,
      });
      setActivities(data.activities || data || []);
      return data;
    } catch (err) {
      setError(err.message || "Failed to fetch activities");
      console.error("Error fetching activities:", err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const refreshActivities = useCallback(() => {
    return fetchActivities();
  }, [fetchActivities]);

  const updateFilters = useCallback((newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({});
  }, []);

  useEffect(() => {
    if (autoFetch) {
      fetchActivities();
    }
  }, [autoFetch, fetchActivities]);

  return {
    activities,
    loading,
    error,
    filters,
    fetchActivities,
    refreshActivities,
    updateFilters,
    clearFilters,
  };
};

/**
 * Custom hook for managing a single activity
 * @param {string|number} activityId - Activity ID
 * @param {Object} options - Hook options
 * @returns {Object} Activity state and methods
 */
export const useActivity = (activityId, options = {}) => {
  const { autoFetch = true } = options;

  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const fetchActivity = useCallback(async () => {
    if (!activityId) return null;

    try {
      setLoading(true);
      setError(null);
      const data = await activityService.getActivityDetail(activityId);
      setActivity(data);
      return data;
    } catch (err) {
      setError(err.message || "Failed to fetch activity");
      console.error("Error fetching activity:", err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [activityId]);

  const submitActivity = useCallback(async (answers, timeSpent) => {
    if (!activityId) return null;

    try {
      setSubmitting(true);
      setError(null);
      const result = await activityService.submitActivity(activityId, {
        answers,
        timeSpent,
      });
      return result;
    } catch (err) {
      setError(err.message || "Failed to submit activity");
      console.error("Error submitting activity:", err);
      return null;
    } finally {
      setSubmitting(false);
    }
  }, [activityId]);

  const startActivity = useCallback(async () => {
    if (!activityId) return null;

    try {
      const result = await activityService.startActivity(activityId);
      return result;
    } catch (err) {
      console.error("Error starting activity:", err);
      return null;
    }
  }, [activityId]);

  const toggleBookmark = useCallback(async (bookmarked) => {
    if (!activityId) return null;

    try {
      const result = await activityService.toggleBookmark(
        activityId,
        bookmarked
      );
      setActivity((prev) => (prev ? { ...prev, bookmarked } : prev));
      return result;
    } catch (err) {
      console.error("Error toggling bookmark:", err);
      return null;
    }
  }, [activityId]);

  const refreshActivity = useCallback(() => {
    return fetchActivity();
  }, [fetchActivity]);

  useEffect(() => {
    if (autoFetch && activityId) {
      fetchActivity();
    }
  }, [autoFetch, activityId, fetchActivity]);

  return {
    activity,
    loading,
    error,
    submitting,
    fetchActivity,
    refreshActivity,
    submitActivity,
    startActivity,
    toggleBookmark,
  };
};

/**
 * Custom hook for generating activities
 * @returns {Object} Activity generation state and methods
 */
export const useActivityGenerator = () => {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [generatedActivity, setGeneratedActivity] = useState(null);

  const generateActivity = useCallback(async (params) => {
    try {
      setGenerating(true);
      setError(null);
      const data = await activityService.generateActivity(params);
      setGeneratedActivity(data);
      return data;
    } catch (err) {
      setError(err.message || "Failed to generate activity");
      console.error("Error generating activity:", err);
      return null;
    } finally {
      setGenerating(false);
    }
  }, []);

  const clearGenerated = useCallback(() => {
    setGeneratedActivity(null);
    setError(null);
  }, []);

  return {
    generating,
    error,
    generatedActivity,
    generateActivity,
    clearGenerated,
  };
};

/**
 * Custom hook for activity statistics
 * @param {string|number} activityId - Activity ID
 * @returns {Object} Statistics state and methods
 */
export const useActivityStatistics = (activityId) => {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStatistics = useCallback(async () => {
    if (!activityId) return null;

    try {
      setLoading(true);
      setError(null);
      const data = await activityService.getActivityStatistics(activityId);
      setStatistics(data);
      return data;
    } catch (err) {
      setError(err.message || "Failed to fetch statistics");
      console.error("Error fetching statistics:", err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [activityId]);

  useEffect(() => {
    if (activityId) {
      fetchStatistics();
    }
  }, [activityId, fetchStatistics]);

  return {
    statistics,
    loading,
    error,
    fetchStatistics,
  };
};

export default {
  useActivities,
  useActivity,
  useActivityGenerator,
  useActivityStatistics,
};
