import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Grid,
  CardContent,
  Typography,
  Chip,
  Button,
  TextField,
  InputAdornment,
  LinearProgress,
  IconButton,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  AlertTitle,
} from "@mui/material";
import {
  Search,
  School,
  CheckCircle,
  AccessTime,
  PlayArrow,
  Bookmark,
  BookmarkBorder,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import HoverCard from "../components/common/HoverCard";
import AnimatedButton from "../components/common/AnimatedButton";
import learningPathService from "../services/learningPathService";

const LearningPaths = () => {
  const navigate = useNavigate();
  const [learningPaths, setLearningPaths] = useState([]);
  const [myPaths, setMyPaths] = useState([]);
  const [enrolledPathIds, setEnrolledPathIds] = useState(new Set()); // Track enrolled path IDs
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState(0);
  const [bookmarked, setBookmarked] = useState(new Set());
  const [enrolling, setEnrolling] = useState(null);
  const [error, setError] = useState(null);

  const fetchLearningPaths = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Always fetch enrolled paths first to get the current enrollment status
      const enrolledResponse = await learningPathService.getMyLearningPaths();
      const enrolledPaths = enrolledResponse.learning_paths || enrolledResponse.data || [];
      const enrolledIds = new Set(enrolledPaths.map(p => p.id));
      setEnrolledPathIds(enrolledIds);
      setMyPaths(enrolledPaths);

      if (activeTab === 0) {
        // Fetch all available learning paths
        const response = await learningPathService.getLearningPaths();
        const allPaths = response.learning_paths || response.data || [];
        
        // Mark enrolled paths with is_enrolled flag based on enrolledIds
        const pathsWithEnrollmentStatus = allPaths.map(path => ({
          ...path,
          is_enrolled: enrolledIds.has(path.id) || path.is_enrolled || path.enrolled
        }));
        
        setLearningPaths(pathsWithEnrollmentStatus);
      }
    } catch (error) {
      console.error("Error fetching learning paths:", error);

      // Set user-friendly error message
      if (error.response?.status === 401 || error.response?.status === 422) {
        setError("Please log in to view learning paths.");
      } else if (error.message?.includes("Authentication required")) {
        setError("Please log in to access learning paths.");
      } else {
        setError("Failed to load learning paths. Please try again later.");
      }

      setLearningPaths([]);
      setMyPaths([]);
    } finally {
      setLoading(false);
    }
  }, [activeTab]);

  useEffect(() => {
    fetchLearningPaths();
  }, [fetchLearningPaths]);

  const handleEnroll = async (pathId) => {
    try {
      setEnrolling(pathId);
      // Enroll in the path
      await learningPathService.enrollInPath(pathId);
      
      // Immediately update the UI with the enrolled path
      const newEnrolledIds = new Set(enrolledPathIds);
      newEnrolledIds.add(pathId);
      setEnrolledPathIds(newEnrolledIds);
      
      // Update the learningPaths list to mark this path as enrolled
      setLearningPaths(prevPaths =>
        prevPaths.map(p =>
          p.id === pathId
            ? { ...p, is_enrolled: true, enrolled: true }
            : p
        )
      );
      
      // Refresh the learning paths to get latest data
      await fetchLearningPaths();
    } catch (error) {
      console.error("Error enrolling in learning path:", error);
    } finally {
      setEnrolling(null);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const toggleBookmark = (pathId) => {
    setBookmarked((prev) => {
      const newBookmarked = new Set(prev);
      if (newBookmarked.has(pathId)) {
        newBookmarked.delete(pathId);
      } else {
        newBookmarked.add(pathId);
      }
      return newBookmarked;
    });
  };

  // Get the appropriate list based on activeTab
  const currentPaths = activeTab === 1 ? myPaths : learningPaths;

  const filteredPaths = currentPaths.filter((path) => {
    const matchesSearch =
      (path.title || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      (path.description || "").toLowerCase().includes(searchTerm.toLowerCase());

    // Filter by level for tabs 2-4
    const matchesTab =
      activeTab === 0 || activeTab === 1
        ? true
        : activeTab === 2
        ? (path.level || path.difficulty_level) === "Beginner" ||
          (path.level || path.difficulty_level) === "beginner"
        : activeTab === 3
        ? (path.level || path.difficulty_level) === "Intermediate" ||
          (path.level || path.difficulty_level) === "intermediate"
        : (path.level || path.difficulty_level) === "Advanced" ||
          (path.level || path.difficulty_level) === "advanced";

    return matchesSearch && matchesTab;
  });

  const getLevelColor = (level) => {
    const normalizedLevel = (level || "").toLowerCase();
    switch (normalizedLevel) {
      case "beginner":
        return "success";
      case "intermediate":
        return "warning";
      case "advanced":
        return "error";
      default:
        return "default";
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: 400,
        }}
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <PageTransition>
      <Box>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
            Learning Paths
          </GradientText>
          <Typography variant="body1" color="text.secondary">
            Choose a structured path to master English step by step
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            <AlertTitle>Error</AlertTitle>
            {error}
          </Alert>
        )}

        {/* Search and Filters */}
        <Box sx={{ mb: 4 }}>
          <TextField
            fullWidth
            placeholder="Search learning paths..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />

          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="All Paths" />
            <Tab label="My Paths" />
            <Tab label="Beginner" />
            <Tab label="Intermediate" />
            <Tab label="Advanced" />
          </Tabs>
        </Box>

        {/* Learning Paths Grid */}
        <Grid container spacing={3}>
          {filteredPaths.map((path, index) => (
            <Grid item xs={12} md={6} key={path.id}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
              >
                <HoverCard>
                  <CardContent sx={{ p: 3 }}>
                    {/* Header */}
                    <Box
                      sx={{ display: "flex", alignItems: "flex-start", mb: 2 }}
                    >
                      {path.icon && (
                        <Box
                          sx={{
                            fontSize: "3rem",
                            mr: 2,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          {path.icon}
                        </Box>
                      )}
                      <Box sx={{ flex: 1 }}>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            mb: 1,
                          }}
                        >
                          <Typography variant="h6" fontWeight={700}>
                            {path.title}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={() => toggleBookmark(path.id)}
                            color={
                              bookmarked.has(path.id) ? "primary" : "default"
                            }
                          >
                            {bookmarked.has(path.id) ? (
                              <Bookmark />
                            ) : (
                              <BookmarkBorder />
                            )}
                          </IconButton>
                        </Box>
                        <Box sx={{ display: "flex", gap: 1, mb: 1 }}>
                          <Chip
                            label={
                              path.level || path.difficulty_level || "Beginner"
                            }
                            size="small"
                            color={getLevelColor(
                              path.level || path.difficulty_level
                            )}
                          />
                          {(path.is_enrolled || path.enrolled) && (
                            <Chip
                              label="Enrolled"
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          )}
                        </Box>
                      </Box>
                    </Box>

                    {/* Description */}
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 2 }}
                    >
                      {path.description}
                    </Typography>

                    {/* Stats */}
                    <Box sx={{ display: "flex", gap: 3, mb: 2 }}>
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
                      >
                        <School fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          {path.chapters ||
                            path.total_chapters ||
                            path.chapter_count ||
                            0}{" "}
                          Chapters
                        </Typography>
                      </Box>
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 0.5 }}
                      >
                        <AccessTime fontSize="small" color="action" />
                        <Typography variant="body2" color="text.secondary">
                          {path.duration ||
                            path.estimated_duration ||
                            "Self-paced"}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Progress */}
                    {(path.is_enrolled || path.enrolled) &&
                      (path.progress || path.completion_percentage) > 0 && (
                        <Box sx={{ mb: 2 }}>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              mb: 0.5,
                            }}
                          >
                            <Typography variant="body2" fontWeight={500}>
                              Progress
                            </Typography>
                            <Typography
                              variant="body2"
                              color="primary.main"
                              fontWeight={600}
                            >
                              {path.progress || path.completion_percentage}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={path.progress || path.completion_percentage}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                      )}

                    {/* Actions */}
                    <Box sx={{ display: "flex", gap: 1 }}>
                      {path.is_enrolled || path.enrolled ? (
                        <AnimatedButton
                          fullWidth
                          variant="contained"
                          startIcon={
                            (path.progress || path.completion_percentage || 0) >
                            0 ? (
                              <PlayArrow />
                            ) : (
                              <School />
                            )
                          }
                          onClick={() => navigate(`/learning-paths/${path.id}`)}
                        >
                          {(path.progress || path.completion_percentage || 0) >
                          0
                            ? "Continue Learning"
                            : "Start Learning"}
                        </AnimatedButton>
                      ) : (
                        <>
                          <AnimatedButton
                            fullWidth
                            variant="contained"
                            startIcon={<CheckCircle />}
                            onClick={() => handleEnroll(path.id)}
                            disabled={enrolling === path.id}
                          >
                            {enrolling === path.id
                              ? "Enrolling..."
                              : "Enroll Now"}
                          </AnimatedButton>
                          <Button
                            variant="outlined"
                            onClick={() =>
                              navigate(`/learning-paths/${path.id}`)
                            }
                          >
                            Details
                          </Button>
                        </>
                      )}
                    </Box>
                  </CardContent>
                </HoverCard>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {filteredPaths.length === 0 && (
          <Box sx={{ textAlign: "center", py: 8 }}>
            <School sx={{ fontSize: 80, color: "text.disabled", mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No learning paths found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Try adjusting your search or filters
            </Typography>
          </Box>
        )}
      </Box>
    </PageTransition>
  );
};

export default LearningPaths;
