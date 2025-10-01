import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Grid,
  Chip,
  LinearProgress,
  Button,
  IconButton,
  InputAdornment,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Avatar,
  AvatarGroup,
} from "@mui/material";
import {
  Search,
  FilterList,
  Add,
  Star,
  StarBorder,
  People,
  Schedule,
  PlayArrow,
  BookmarkBorder,
  Bookmark,
  TrendingUp,
  Language,
  Close,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../store/index.js";
import { coursesAPI, userAPI } from "../services/api";
import { toast } from "react-hot-toast";

// Mock data removed - using real API data from coursesAPI.getLearningPaths()

const LearningPaths = () => {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  const [learningPaths, setLearningPaths] = useState([]);
  const [filteredPaths, setFilteredPaths] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("All");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [sortBy, setSortBy] = useState("popular");
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  // Load learning paths from API
  useEffect(() => {
    loadLearningPaths();
  }, []);

  useEffect(() => {
    filterAndSortPaths();
  }, [searchQuery, selectedLevel, selectedCategory, sortBy, learningPaths]);

  const loadLearningPaths = async () => {
    try {
      setLoading(true);
      const response = await coursesAPI.getLearningPaths();

      // Transform API data to match UI expectations
      const transformedPaths = response.data.learning_paths.map((path) => ({
        id: path.id,
        title: path.title,
        description: path.description,
        image: `/images/path-${path.id}.jpg`, // Placeholder
        level: path.difficulty_level || "Beginner",
        duration: `${path.estimated_duration || 4} weeks`,
        lessonsCount: path.activities_count || 0,
        studentsCount: path.enrolled_count || 0,
        rating: 4.5, // Default rating
        progress: 0, // Will be loaded separately if user is enrolled
        isBookmarked: false, // Will be enhanced later
        category: path.category || "General",
        instructor: "AI Tutor",
        tags: [path.difficulty_level, path.category].filter(Boolean),
        completionRate: 85, // Default completion rate
      }));

      setLearningPaths(transformedPaths);

      // Load user's enrollment progress if logged in
      if (user) {
        loadUserProgress(transformedPaths);
      }
    } catch (error) {
      console.error("Failed to load learning paths:", error);
      toast.error("Failed to load learning paths");
    } finally {
      setLoading(false);
    }
  };

  const loadUserProgress = async (paths) => {
    try {
      const response = await userAPI.getLearningPaths(user.id);
      const userPaths = response.data.learning_paths || [];

      // Update progress for enrolled paths
      const updatedPaths = paths.map((path) => {
        const userPath = userPaths.find(
          (up) => up.learning_path_id === path.id
        );
        if (userPath) {
          return {
            ...path,
            progress: userPath.progress_percentage || 0,
            isEnrolled: true,
          };
        }
        return path;
      });

      setLearningPaths(updatedPaths);
    } catch (error) {
      console.error("Failed to load user progress:", error);
    }
  };

  const handleEnroll = async (pathId) => {
    if (!user) {
      toast.error("Please login to enroll in learning paths");
      navigate("/login");
      return;
    }

    try {
      setEnrolling(pathId);
      await coursesAPI.enroll(pathId);
      toast.success("Successfully enrolled in learning path!");

      // Refresh learning paths to show updated progress
      loadLearningPaths();
    } catch (error) {
      console.error("Failed to enroll:", error);
      toast.error("Failed to enroll in learning path");
    } finally {
      setEnrolling(null);
    }
  };

  const filterAndSortPaths = () => {
    let filtered = [...learningPaths];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (path) =>
          path.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          path.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          path.tags.some((tag) =>
            tag.toLowerCase().includes(searchQuery.toLowerCase())
          )
      );
    }

    // Apply level filter
    if (selectedLevel !== "All") {
      filtered = filtered.filter((path) => path.level === selectedLevel);
    }

    // Apply category filter
    if (selectedCategory !== "All") {
      filtered = filtered.filter((path) => path.category === selectedCategory);
    }

    // Apply sorting
    switch (sortBy) {
      case "popular":
        filtered.sort((a, b) => b.studentsCount - a.studentsCount);
        break;
      case "rating":
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      case "newest":
        filtered.sort((a, b) => b.id - a.id);
        break;
      case "progress":
        filtered.sort((a, b) => b.progress - a.progress);
        break;
      default:
        break;
    }

    setFilteredPaths(filtered);
  };

  const toggleBookmark = (pathId) => {
    setLearningPaths((prevPaths) =>
      prevPaths.map((path) =>
        path.id === pathId
          ? { ...path, isBookmarked: !path.isBookmarked }
          : path
      )
    );
  };

  const handleStartPath = (pathId) => {
    navigate(`/learning-paths/${pathId}`);
  };

  const handleCreatePath = () => {
    navigate("/learning-paths/create");
  };

  const getLevelColor = (level) => {
    switch (level) {
      case "Beginner":
        return "success";
      case "Intermediate":
        return "warning";
      case "Advanced":
        return "error";
      default:
        return "primary";
    }
  };

  const PathCard = ({ path, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.6 }}
      whileHover={{ y: -8 }}
    >
      <Card
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          borderRadius: 3,
          overflow: "hidden",
          transition: "all 0.3s ease",
          border: "1px solid",
          borderColor: "divider",
          "&:hover": {
            boxShadow: (theme) => theme.shadows[8],
            borderColor: "primary.main",
          },
        }}
      >
        <Box sx={{ position: "relative" }}>
          <CardMedia
            component="div"
            sx={{
              height: 200,
              background: `linear-gradient(135deg, ${
                path.category === "Grammar"
                  ? "#667eea, #764ba2"
                  : path.category === "Speaking"
                  ? "#f093fb, #f5576c"
                  : path.category === "Professional"
                  ? "#4facfe, #00f2fe"
                  : path.category === "Literature"
                  ? "#43e97b, #38f9d7"
                  : path.category === "Writing"
                  ? "#fa709a, #fee140"
                  : "#667eea, #764ba2"
              })`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "white",
              fontSize: "4rem",
              fontWeight: "bold",
            }}
          >
            {path.title.charAt(0)}
          </CardMedia>

          <IconButton
            sx={{
              position: "absolute",
              top: 8,
              right: 8,
              bgcolor: "rgba(255, 255, 255, 0.9)",
              "&:hover": { bgcolor: "rgba(255, 255, 255, 1)" },
            }}
            onClick={() => toggleBookmark(path.id)}
          >
            {path.isBookmarked ? (
              <Bookmark sx={{ color: "primary.main" }} />
            ) : (
              <BookmarkBorder />
            )}
          </IconButton>

          {path.progress > 0 && (
            <Box
              sx={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                bgcolor: "rgba(0, 0, 0, 0.7)",
                color: "white",
                p: 1,
              }}
            >
              <Typography variant="caption" display="block" gutterBottom>
                Progress: {path.progress}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={path.progress}
                sx={{
                  height: 4,
                  borderRadius: 2,
                  bgcolor: "rgba(255, 255, 255, 0.3)",
                  "& .MuiLinearProgress-bar": {
                    bgcolor: "primary.main",
                  },
                }}
              />
            </Box>
          )}
        </Box>

        <CardContent sx={{ flexGrow: 1, p: 3 }}>
          <Box sx={{ mb: 2 }}>
            <Typography
              variant="h6"
              component="h3"
              sx={{ fontWeight: "bold", mb: 1 }}
            >
              {path.title}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {path.description}
            </Typography>
          </Box>

          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
            <Chip
              label={path.level}
              size="small"
              color={getLevelColor(path.level)}
              variant="outlined"
            />
            <Chip label={path.category} size="small" variant="outlined" />
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Star sx={{ color: "warning.main", fontSize: 16 }} />
              <Typography variant="body2">{path.rating}</Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <People sx={{ fontSize: 16, color: "text.secondary" }} />
              <Typography variant="body2" color="text.secondary">
                {path.studentsCount.toLocaleString()}
              </Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Schedule sx={{ fontSize: 16, color: "text.secondary" }} />
              <Typography variant="body2" color="text.secondary">
                {path.duration}
              </Typography>
            </Box>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            By {path.instructor} • {path.lessonsCount} lessons
          </Typography>

          <Box sx={{ display: "flex", gap: 1 }}>
            <Button
              variant="contained"
              startIcon={<PlayArrow />}
              onClick={() => handleStartPath(path.id)}
              sx={{ flexGrow: 1 }}
              component={motion.button}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {path.progress > 0 ? "Continue" : "Start Learning"}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: "bold", mb: 1 }}>
            Learning Paths
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Discover structured learning journeys to master Telugu and English
          </Typography>
        </Box>
      </motion.div>

      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        <Card sx={{ mb: 4, borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  placeholder="Search learning paths..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Search />
                      </InputAdornment>
                    ),
                  }}
                  sx={{ "& .MuiOutlinedInput-root": { borderRadius: 2 } }}
                />
              </Grid>

              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Level</InputLabel>
                  <Select
                    value={selectedLevel}
                    label="Level"
                    onChange={(e) => setSelectedLevel(e.target.value)}
                    sx={{ borderRadius: 2 }}
                  >
                    <MenuItem value="All">All Levels</MenuItem>
                    <MenuItem value="Beginner">Beginner</MenuItem>
                    <MenuItem value="Intermediate">Intermediate</MenuItem>
                    <MenuItem value="Advanced">Advanced</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={selectedCategory}
                    label="Category"
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    sx={{ borderRadius: 2 }}
                  >
                    <MenuItem value="All">All Categories</MenuItem>
                    <MenuItem value="Grammar">Grammar</MenuItem>
                    <MenuItem value="Speaking">Speaking</MenuItem>
                    <MenuItem value="Professional">Professional</MenuItem>
                    <MenuItem value="Literature">Literature</MenuItem>
                    <MenuItem value="Writing">Writing</MenuItem>
                    <MenuItem value="Practical">Practical</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Sort By</InputLabel>
                  <Select
                    value={sortBy}
                    label="Sort By"
                    onChange={(e) => setSortBy(e.target.value)}
                    sx={{ borderRadius: 2 }}
                  >
                    <MenuItem value="popular">Most Popular</MenuItem>
                    <MenuItem value="rating">Highest Rated</MenuItem>
                    <MenuItem value="newest">Newest</MenuItem>
                    <MenuItem value="progress">My Progress</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={2}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<FilterList />}
                  onClick={() => setShowFilters(!showFilters)}
                  sx={{ height: "56px", borderRadius: 2 }}
                >
                  Filters
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </motion.div>

      {/* Results Summary */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
      >
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Showing {filteredPaths.length} of {learningPaths.length} learning
          paths
        </Typography>
      </motion.div>

      {/* Learning Paths Grid */}
      <Grid container spacing={3}>
        {filteredPaths.map((path, index) => (
          <Grid item xs={12} sm={6} lg={4} key={path.id}>
            <PathCard path={path} index={index} />
          </Grid>
        ))}
      </Grid>

      {/* Empty State */}
      {filteredPaths.length === 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <Box
            sx={{
              textAlign: "center",
              py: 8,
              background: "linear-gradient(135deg, #667eea10, #764ba210)",
              borderRadius: 3,
              border: "1px solid #667eea20",
            }}
          >
            <Language sx={{ fontSize: 64, color: "text.secondary", mb: 2 }} />
            <Typography variant="h6" sx={{ mb: 1 }}>
              No learning paths found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Try adjusting your search or filter criteria
            </Typography>
            <Button
              variant="contained"
              onClick={() => {
                setSearchQuery("");
                setSelectedLevel("All");
                setSelectedCategory("All");
              }}
            >
              Clear Filters
            </Button>
          </Box>
        </motion.div>
      )}

      {/* Floating Action Button */}
      <Fab
        color="primary"
        sx={{
          position: "fixed",
          bottom: 24,
          right: 24,
          background: "linear-gradient(135deg, #667eea, #764ba2)",
        }}
        onClick={handleCreatePath}
        component={motion.button}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        <Add />
      </Fab>
    </Container>
  );
};

export default LearningPaths;
