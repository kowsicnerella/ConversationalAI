import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  CardMedia,
  Button,
  Chip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  IconButton,
  LinearProgress,
  Avatar,
  Fab,
  Skeleton,
} from "@mui/material";
import {
  Search,
  FilterList,
  School,
  PlayArrow,
  Bookmark,
  BookmarkBorder,
  Person,
  Schedule,
  Star,
  Add,
  TrendingUp,
  EmojiEvents,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../../store/index.js";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";
import { coursesAPI } from "../../services/api";

const difficultyColors = {
  Beginner: "#4caf50",
  Intermediate: "#ff9800",
  Advanced: "#f44336",
};

// Mock data removed - using real API data from coursesAPI.getLearningPaths()

const LearningPaths = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [learningPaths, setLearningPaths] = useState([]);
  const [filteredPaths, setFilteredPaths] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [difficultyFilter, setDifficultyFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    // Simulate API call
    const fetchLearningPaths = async () => {
      setLoading(true);
      try {
        // Use real API call
        const response = await coursesAPI.getLearningPaths();
        if (response.success && response.data) {
          setLearningPaths(response.data);
          setFilteredPaths(response.data);
        } else {
          setLearningPaths([]);
          setFilteredPaths([]);
          toast.error("Failed to load learning paths");
        }
        setLoading(false);
      } catch (error) {
        console.error("Failed to load learning paths:", error);
        toast.error("Failed to load learning paths");
        setLoading(false);
      }
    };

    fetchLearningPaths();
  }, []);

  useEffect(() => {
    let filtered = learningPaths;

    // Search filter
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

    // Difficulty filter
    if (difficultyFilter !== "all") {
      filtered = filtered.filter(
        (path) => path.difficulty === difficultyFilter
      );
    }

    // Status filter
    if (statusFilter !== "all") {
      if (statusFilter === "enrolled") {
        filtered = filtered.filter((path) => path.isEnrolled);
      } else if (statusFilter === "bookmarked") {
        filtered = filtered.filter((path) => path.isBookmarked);
      } else if (statusFilter === "available") {
        filtered = filtered.filter((path) => !path.isEnrolled);
      }
    }

    setFilteredPaths(filtered);
  }, [learningPaths, searchQuery, difficultyFilter, statusFilter]);

  const handleBookmark = (pathId) => {
    const updatedPaths = learningPaths.map((path) => {
      if (path.id === pathId) {
        const newBookmarkStatus = !path.isBookmarked;
        toast.success(
          newBookmarkStatus ? "Added to bookmarks" : "Removed from bookmarks"
        );
        return { ...path, isBookmarked: newBookmarkStatus };
      }
      return path;
    });
    setLearningPaths(updatedPaths);
  };

  const handleEnroll = async (pathId) => {
    try {
      // API call to enroll
      const updatedPaths = learningPaths.map((path) => {
        if (path.id === pathId) {
          toast.success("Successfully enrolled!");
          return { ...path, isEnrolled: true, progress: 0 };
        }
        return path;
      });
      setLearningPaths(updatedPaths);
    } catch (error) {
      console.error("Failed to enroll:", error);
      toast.error("Failed to enroll in course");
    }
  };

  const LearningPathCard = ({ path }) => (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -5 }}
    >
      <Card
        sx={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          borderRadius: 3,
          overflow: "hidden",
          transition: "all 0.3s ease-in-out",
          "&:hover": {
            boxShadow: "0 12px 40px rgba(0,0,0,0.15)",
          },
        }}
      >
        <Box sx={{ position: "relative" }}>
          <CardMedia
            component="img"
            height="200"
            image={path.image}
            alt={path.title}
            sx={{
              transition: "transform 0.3s ease-in-out",
              "&:hover": { transform: "scale(1.05)" },
            }}
          />
          <Box
            sx={{
              position: "absolute",
              top: 16,
              right: 16,
              display: "flex",
              gap: 1,
            }}
          >
            <Chip
              label={path.difficulty}
              size="small"
              sx={{
                backgroundColor: difficultyColors[path.difficulty],
                color: "white",
                fontWeight: "bold",
              }}
            />
            <IconButton
              onClick={() => handleBookmark(path.id)}
              sx={{
                backgroundColor: "rgba(255,255,255,0.9)",
                "&:hover": { backgroundColor: "rgba(255,255,255,1)" },
              }}
              size="small"
            >
              {path.isBookmarked ? (
                <Bookmark color="primary" />
              ) : (
                <BookmarkBorder />
              )}
            </IconButton>
          </Box>

          {path.isEnrolled && (
            <Box
              sx={{
                position: "absolute",
                bottom: 0,
                left: 0,
                right: 0,
                backgroundColor: "rgba(0,0,0,0.8)",
                color: "white",
                p: 1,
              }}
            >
              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
              >
                <Typography variant="caption">
                  Progress: {path.completedLessons}/{path.lessonsCount} lessons
                </Typography>
                <Typography variant="caption">{path.progress}%</Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={path.progress}
                sx={{ borderRadius: 1 }}
              />
            </Box>
          )}
        </Box>

        <CardContent sx={{ flexGrow: 1, p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: "bold", mb: 1 }}>
            {path.title}
          </Typography>

          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              mb: 2,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {path.description}
          </Typography>

          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
            <Avatar
              src={path.instructorAvatar}
              sx={{ width: 24, height: 24 }}
            />
            <Typography variant="caption" color="text.secondary">
              {path.instructor}
            </Typography>
          </Box>

          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mb: 2 }}>
            {path.tags.slice(0, 3).map((tag) => (
              <Chip key={tag} label={tag} size="small" variant="outlined" />
            ))}
          </Box>

          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Star sx={{ color: "#ffc107", fontSize: 16 }} />
              <Typography variant="caption">{path.rating}</Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Person sx={{ fontSize: 16, color: "text.secondary" }} />
              <Typography variant="caption" color="text.secondary">
                {path.enrolledStudents.toLocaleString()}
              </Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Schedule sx={{ fontSize: 16, color: "text.secondary" }} />
              <Typography variant="caption" color="text.secondary">
                {path.duration}
              </Typography>
            </Box>
          </Box>
        </CardContent>

        <CardActions sx={{ p: 3, pt: 0 }}>
          <Button
            fullWidth
            variant={path.isEnrolled ? "contained" : "outlined"}
            startIcon={path.isEnrolled ? <PlayArrow /> : <School />}
            onClick={() => {
              if (path.isEnrolled) {
                navigate(`/learning-paths/${path.id}`);
              } else {
                handleEnroll(path.id);
              }
            }}
            sx={{ borderRadius: 2 }}
          >
            {path.isEnrolled ? "Continue Learning" : "Enroll Now"}
          </Button>
        </CardActions>
      </Card>
    </motion.div>
  );

  LearningPathCard.propTypes = {
    path: PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      difficulty: PropTypes.string.isRequired,
      duration: PropTypes.string.isRequired,
      enrolledStudents: PropTypes.number.isRequired,
      rating: PropTypes.number.isRequired,
      progress: PropTypes.number.isRequired,
      isEnrolled: PropTypes.bool.isRequired,
      isBookmarked: PropTypes.bool.isRequired,
      instructor: PropTypes.string.isRequired,
      instructorAvatar: PropTypes.string.isRequired,
      image: PropTypes.string.isRequired,
      tags: PropTypes.arrayOf(PropTypes.string).isRequired,
      chaptersCount: PropTypes.number.isRequired,
      lessonsCount: PropTypes.number.isRequired,
      completedLessons: PropTypes.number.isRequired,
    }).isRequired,
  };

  const LoadingCard = () => (
    <Card sx={{ height: "100%", borderRadius: 3 }}>
      <Skeleton variant="rectangular" height={200} />
      <CardContent>
        <Skeleton variant="text" height={32} sx={{ mb: 1 }} />
        <Skeleton variant="text" height={20} sx={{ mb: 2 }} />
        <Skeleton variant="text" height={20} sx={{ mb: 2 }} />
        <Box sx={{ display: "flex", gap: 1, mb: 2 }}>
          <Skeleton variant="rounded" width={60} height={24} />
          <Skeleton variant="rounded" width={80} height={24} />
        </Box>
        <Skeleton variant="rectangular" height={36} />
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Paper
          elevation={3}
          sx={{
            p: 4,
            mb: 4,
            borderRadius: 3,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            textAlign: "center",
          }}
        >
          <School sx={{ fontSize: 60, mb: 2 }} />
          <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
            Learning Paths
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9 }}>
            Discover structured learning journeys tailored to your goals
          </Typography>
        </Paper>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <motion.div whileHover={{ scale: 1.02 }}>
              <Paper sx={{ p: 3, textAlign: "center", borderRadius: 3 }}>
                <TrendingUp sx={{ fontSize: 40, color: "#4caf50", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: "bold", color: "#4caf50" }}
                >
                  {learningPaths.filter((p) => p.isEnrolled).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Enrolled Courses
                </Typography>
              </Paper>
            </motion.div>
          </Grid>
          <Grid item xs={12} md={3}>
            <motion.div whileHover={{ scale: 1.02 }}>
              <Paper sx={{ p: 3, textAlign: "center", borderRadius: 3 }}>
                <Bookmark sx={{ fontSize: 40, color: "#2196f3", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: "bold", color: "#2196f3" }}
                >
                  {learningPaths.filter((p) => p.isBookmarked).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Bookmarked
                </Typography>
              </Paper>
            </motion.div>
          </Grid>
          <Grid item xs={12} md={3}>
            <motion.div whileHover={{ scale: 1.02 }}>
              <Paper sx={{ p: 3, textAlign: "center", borderRadius: 3 }}>
                <EmojiEvents sx={{ fontSize: 40, color: "#ff9800", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: "bold", color: "#ff9800" }}
                >
                  {learningPaths
                    .filter((p) => p.isEnrolled)
                    .reduce((acc, p) => acc + p.completedLessons, 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Lessons Completed
                </Typography>
              </Paper>
            </motion.div>
          </Grid>
          <Grid item xs={12} md={3}>
            <motion.div whileHover={{ scale: 1.02 }}>
              <Paper sx={{ p: 3, textAlign: "center", borderRadius: 3 }}>
                <School sx={{ fontSize: 40, color: "#9c27b0", mb: 1 }} />
                <Typography
                  variant="h4"
                  sx={{ fontWeight: "bold", color: "#9c27b0" }}
                >
                  {learningPaths.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Available Paths
                </Typography>
              </Paper>
            </motion.div>
          </Grid>
        </Grid>

        {/* Filters */}
        <Paper sx={{ p: 3, mb: 4, borderRadius: 3 }}>
          <Grid container spacing={3} alignItems="center">
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
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Difficulty</InputLabel>
                <Select
                  value={difficultyFilter}
                  onChange={(e) => setDifficultyFilter(e.target.value)}
                  label="Difficulty"
                  sx={{ borderRadius: 2 }}
                >
                  <MenuItem value="all">All Levels</MenuItem>
                  <MenuItem value="Beginner">Beginner</MenuItem>
                  <MenuItem value="Intermediate">Intermediate</MenuItem>
                  <MenuItem value="Advanced">Advanced</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  label="Status"
                  sx={{ borderRadius: 2 }}
                >
                  <MenuItem value="all">All Courses</MenuItem>
                  <MenuItem value="enrolled">Enrolled</MenuItem>
                  <MenuItem value="bookmarked">Bookmarked</MenuItem>
                  <MenuItem value="available">Available</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<FilterList />}
                size="large"
                sx={{ borderRadius: 2, height: 56 }}
              >
                Filter
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Learning Paths Grid */}
        <AnimatePresence>
          <Grid container spacing={3}>
            {loading
              ? Array.from({ length: 8 }).map((_, index) => (
                  <Grid item xs={12} sm={6} lg={4} xl={3} key={index}>
                    <LoadingCard />
                  </Grid>
                ))
              : filteredPaths.map((path) => (
                  <Grid item xs={12} sm={6} lg={4} xl={3} key={path.id}>
                    <LearningPathCard path={path} />
                  </Grid>
                ))}
          </Grid>
        </AnimatePresence>

        {!loading && filteredPaths.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Paper
              sx={{
                p: 8,
                textAlign: "center",
                borderRadius: 3,
                background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
              }}
            >
              <School sx={{ fontSize: 80, color: "text.secondary", mb: 2 }} />
              <Typography variant="h5" sx={{ fontWeight: "bold", mb: 2 }}>
                No Learning Paths Found
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Try adjusting your search criteria or explore our available
                courses
              </Typography>
              <Button
                variant="contained"
                onClick={() => {
                  setSearchQuery("");
                  setDifficultyFilter("all");
                  setStatusFilter("all");
                }}
                sx={{ borderRadius: 2 }}
              >
                Reset Filters
              </Button>
            </Paper>
          </motion.div>
        )}

        {/* Floating Action Button */}
        {user?.role === "instructor" && (
          <Fab
            color="primary"
            sx={{
              position: "fixed",
              bottom: 24,
              right: 24,
              background: "linear-gradient(135deg, #667eea, #764ba2)",
            }}
            onClick={() => navigate("/learning-paths/create")}
          >
            <Add />
          </Fab>
        )}
      </motion.div>
    </Container>
  );
};

export default LearningPaths;
