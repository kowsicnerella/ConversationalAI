/**
 * Activity Utilities
 * Helper functions for activity-related operations
 */

import {
  Style,
  Quiz,
  MenuBook,
  Psychology,
  Headphones,
  Chat,
  Mic,
  VideoLibrary,
} from "@mui/icons-material";

/**
 * Get icon component for activity type
 * @param {string} type - Activity type
 * @returns {Component} MUI Icon component
 */
export const getActivityIcon = (type) => {
  const iconMap = {
    flashcard: Style,
    quiz: Quiz,
    reading: MenuBook,
    listening: Headphones,
    speaking: Mic,
    conversation: Chat,
    video: VideoLibrary,
    default: Psychology,
  };

  return iconMap[type?.toLowerCase()] || iconMap.default;
};

/**
 * Get display label for activity type
 * @param {string} type - Activity type
 * @returns {string} Display label
 */
export const getActivityTypeLabel = (type) => {
  const labelMap = {
    flashcard: "Flashcards",
    quiz: "Quiz",
    reading: "Reading",
    listening: "Listening",
    speaking: "Speaking",
    conversation: "Conversation",
    video: "Video",
  };

  return labelMap[type?.toLowerCase()] || type;
};

/**
 * Get MUI color for difficulty level
 * @param {string} difficulty - Difficulty level
 * @returns {string} MUI color name
 */
export const getDifficultyColor = (difficulty) => {
  const colorMap = {
    beginner: "success",
    intermediate: "warning",
    advanced: "error",
    expert: "error",
  };

  return colorMap[difficulty?.toLowerCase()] || "default";
};

/**
 * Get hex color for difficulty level
 * @param {string} difficulty - Difficulty level
 * @param {Object} theme - MUI theme object
 * @returns {string} Hex color
 */
export const getDifficultyHexColor = (difficulty, theme) => {
  const colorMap = {
    beginner: theme.palette.success.main,
    intermediate: theme.palette.warning.main,
    advanced: theme.palette.error.main,
    expert: theme.palette.error.dark,
  };

  return colorMap[difficulty?.toLowerCase()] || theme.palette.grey[500];
};

/**
 * Format activity duration
 * @param {number} minutes - Duration in minutes
 * @returns {string} Formatted duration
 */
export const formatDuration = (minutes) => {
  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  if (remainingMinutes === 0) {
    return `${hours}h`;
  }

  return `${hours}h ${remainingMinutes}m`;
};

/**
 * Calculate activity score percentage
 * @param {number} correct - Number of correct answers
 * @param {number} total - Total number of questions
 * @returns {number} Score percentage
 */
export const calculateScore = (correct, total) => {
  if (total === 0) return 0;
  return Math.round((correct / total) * 100);
};

/**
 * Get performance message based on score
 * @param {number} score - Score percentage
 * @returns {Object} Performance message and color
 */
export const getPerformanceMessage = (score) => {
  if (score >= 95) {
    return {
      message: "Perfect! 🎉",
      emoji: "🎉",
      color: "success",
      grade: "A+",
    };
  } else if (score >= 90) {
    return {
      message: "Excellent! ⭐",
      emoji: "⭐",
      color: "success",
      grade: "A",
    };
  } else if (score >= 80) {
    return {
      message: "Great Job! 🌟",
      emoji: "🌟",
      color: "success",
      grade: "B",
    };
  } else if (score >= 70) {
    return {
      message: "Good Work! 👍",
      emoji: "👍",
      color: "info",
      grade: "C",
    };
  } else if (score >= 60) {
    return {
      message: "Keep Practicing! 💪",
      emoji: "💪",
      color: "warning",
      grade: "D",
    };
  } else {
    return {
      message: "Try Again! 📚",
      emoji: "📚",
      color: "error",
      grade: "F",
    };
  }
};

/**
 * Format activity statistics
 * @param {Object} stats - Raw statistics object
 * @returns {Object} Formatted statistics
 */
export const formatActivityStats = (stats) => {
  return {
    averageScore: stats.average_score || stats.averageScore || 0,
    completionRate: stats.completion_rate || stats.completionRate || 0,
    totalAttempts: stats.total_attempts || stats.totalAttempts || 0,
    averageTimeSpent: stats.average_time_spent || stats.averageTimeSpent || 0,
    lastAttempt: stats.last_attempt || stats.lastAttempt || null,
  };
};

/**
 * Check if activity is completed
 * @param {Object} activity - Activity object
 * @returns {boolean} Whether activity is completed
 */
export const isActivityCompleted = (activity) => {
  return activity?.completed === true || activity?.status === "completed";
};

/**
 * Check if activity is in progress
 * @param {Object} activity - Activity object
 * @returns {boolean} Whether activity is in progress
 */
export const isActivityInProgress = (activity) => {
  return (
    activity?.progress > 0 &&
    activity?.progress < 100 &&
    !isActivityCompleted(activity)
  );
};

/**
 * Get activity status label
 * @param {Object} activity - Activity object
 * @returns {string} Status label
 */
export const getActivityStatus = (activity) => {
  if (isActivityCompleted(activity)) {
    return "Completed";
  } else if (isActivityInProgress(activity)) {
    return "In Progress";
  } else {
    return "Not Started";
  }
};

/**
 * Sort activities by various criteria
 * @param {Array} activities - Array of activities
 * @param {string} sortBy - Sort criteria
 * @returns {Array} Sorted activities
 */
export const sortActivities = (activities, sortBy) => {
  const sorted = [...activities];

  switch (sortBy) {
    case "title":
      return sorted.sort((a, b) => a.title.localeCompare(b.title));
    case "difficulty": {
      const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 };
      return sorted.sort(
        (a, b) =>
          difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty]
      );
    }
    case "duration":
      return sorted.sort((a, b) => a.estimatedTime - b.estimatedTime);
    case "progress":
      return sorted.sort((a, b) => (b.progress || 0) - (a.progress || 0));
    case "newest":
      return sorted.sort(
        (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
      );
    case "popular":
      return sorted.sort(
        (a, b) => (b.totalAttempts || 0) - (a.totalAttempts || 0)
      );
    default:
      return sorted;
  }
};

/**
 * Filter activities by multiple criteria
 * @param {Array} activities - Array of activities
 * @param {Object} filters - Filter criteria
 * @returns {Array} Filtered activities
 */
export const filterActivities = (activities, filters) => {
  return activities.filter((activity) => {
    // Search filter
    if (filters.search) {
      const searchLower = filters.search.toLowerCase();
      const matchesSearch =
        activity.title?.toLowerCase().includes(searchLower) ||
        activity.description?.toLowerCase().includes(searchLower) ||
        activity.tags?.some((tag) => tag.toLowerCase().includes(searchLower));

      if (!matchesSearch) return false;
    }

    // Type filter
    if (filters.type && filters.type !== "all") {
      if (activity.type !== filters.type) return false;
    }

    // Difficulty filter
    if (filters.difficulty && filters.difficulty !== "all") {
      if (activity.difficulty !== filters.difficulty) return false;
    }

    // Status filter
    if (filters.status) {
      const status = getActivityStatus(activity);
      if (status.toLowerCase() !== filters.status.toLowerCase()) return false;
    }

    // Duration filter
    if (filters.maxDuration) {
      if (activity.estimatedTime > filters.maxDuration) return false;
    }

    return true;
  });
};

/**
 * Get activity progress color
 * @param {number} progress - Progress percentage
 * @param {Object} theme - MUI theme object
 * @returns {string} Color
 */
export const getProgressColor = (progress, theme) => {
  if (progress === 100) return theme.palette.success.main;
  if (progress >= 50) return theme.palette.info.main;
  if (progress > 0) return theme.palette.warning.main;
  return theme.palette.grey[300];
};

/**
 * Generate activity route based on type
 * @param {string} type - Activity type
 * @param {string|number} id - Activity ID
 * @returns {string} Route path
 */
export const getActivityRoute = (type, id) => {
  const routeMap = {
    flashcard: `/activities/flashcards/${id}`,
    quiz: `/activities/quiz/${id}`,
    reading: `/activities/reading/${id}`,
  };

  return routeMap[type?.toLowerCase()] || `/activities/${id}`;
};

/**
 * Calculate estimated completion time based on current progress
 * @param {number} estimatedTime - Total estimated time in minutes
 * @param {number} progress - Current progress percentage
 * @returns {number} Remaining time in minutes
 */
export const calculateRemainingTime = (estimatedTime, progress) => {
  if (progress >= 100) return 0;
  const remaining = estimatedTime * ((100 - progress) / 100);
  return Math.ceil(remaining);
};

/**
 * Check if user can start activity (prerequisites check)
 * @param {Object} activity - Activity object
 * @param {Object} userProgress - User's progress data
 * @returns {Object} { canStart: boolean, reason: string }
 */
export const canStartActivity = (activity, userProgress) => {
  // Check if activity has prerequisites
  if (!activity.prerequisites || activity.prerequisites.length === 0) {
    return { canStart: true };
  }

  // Check each prerequisite
  for (const prereq of activity.prerequisites) {
    const prereqCompleted = userProgress?.completedActivities?.includes(
      prereq.id
    );
    if (!prereqCompleted) {
      return {
        canStart: false,
        reason: `Please complete "${prereq.title}" first`,
      };
    }
  }

  return { canStart: true };
};

export default {
  getActivityIcon,
  getActivityTypeLabel,
  getDifficultyColor,
  getDifficultyHexColor,
  formatDuration,
  calculateScore,
  getPerformanceMessage,
  formatActivityStats,
  isActivityCompleted,
  isActivityInProgress,
  getActivityStatus,
  sortActivities,
  filterActivities,
  getProgressColor,
  getActivityRoute,
  calculateRemainingTime,
  canStartActivity,
};
