import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stack,
  Chip,
  Grid,
  LinearProgress,
  Container,
  useTheme,
  useMediaQuery,
  alpha,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
} from "@mui/material";
import {
  ArrowBack,
  Style,
  Quiz,
  MenuBook,
  Timer,
  TrendingUp,
  PlayArrow,
  CheckCircle,
  Star,
  Psychology,
  School,
  EmojiEvents,
  Person,
  CalendarToday,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import AnimatedButton from "../components/common/AnimatedButton";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const ActivityDetail = () => {
  const { id } = useParams();  // Route uses :id not :activityId
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchActivityDetail();
    }
  }, [id]);

  const fetchActivityDetail = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(
        API_ENDPOINTS.ACTIVITIES.DETAIL(id)
      );
      // Backend returns {message: ..., activity: {...}}
      setActivity(response.data.activity || response.data);
    } catch (error) {
      console.error("Error fetching activity detail:", error);
      // Use mock data
      setActivity(getMockActivity());
    } finally {
      setLoading(false);
    }
  };

  const getMockActivity = () => ({
    id: id,
    type: "flashcard",
    title: "Daily Vocabulary Practice",
    description:
      "Master essential English vocabulary with interactive flashcards. This activity includes common words used in everyday conversations, their pronunciation, usage examples, and Telugu translations.",
    difficulty: "beginner",
    estimatedTime: 15,
    wordsCount: 20,
    completed: false,
    progress: 0,
    color: theme.palette.primary.main,
    tags: ["vocabulary", "daily", "beginner"],
    learningObjectives: [
      "Learn 20 new English vocabulary words",
      "Understand correct pronunciation",
      "Practice usage in context",
      "Build confidence in daily conversations",
    ],
    prerequisites: ["Basic Telugu literacy", "Interest in learning English"],
    recommendedFor: [
      "Beginners starting their English journey",
      "Anyone looking to expand vocabulary",
      "Daily practice enthusiasts",
    ],
    statistics: {
      averageScore: 85,
      completionRate: 92,
      totalAttempts: 1250,
      averageTimeSpent: 14,
    },
  });

  const handleStartActivity = () => {
    if (activity.type === "flashcard") {
      navigate(`/activities/flashcards/${id}`);
    } else if (activity.type === "quiz") {
      navigate(`/activities/quiz/${id}`);
    } else if (activity.type === "reading") {
      navigate(`/activities/reading/${id}`);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
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

  const getActivityIcon = (type) => {
    switch (type) {
      case "flashcard":
        return Style;
      case "quiz":
        return Quiz;
      case "reading":
        return MenuBook;
      default:
        return Psychology;
    }
  };

  const getActivityTypeLabel = (type) => {
    switch (type) {
      case "flashcard":
        return "Flashcards";
      case "quiz":
        return "Quiz";
      case "reading":
        return "Reading";
      default:
        return type;
    }
  };

  if (loading) {
    return (
      <PageTransition>
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="60vh"
        >
          <CircularProgress size={60} />
        </Box>
      </PageTransition>
    );
  }

  if (!activity) {
    return (
      <PageTransition>
        <Container maxWidth="lg">
          <Box textAlign="center" py={8}>
            <Typography variant="h5" color="text.secondary">
              Activity not found
            </Typography>
            <AnimatedButton
              startIcon={<ArrowBack />}
              onClick={() => navigate("/activities")}
              sx={{ mt: 3 }}
            >
              Back to Activities
            </AnimatedButton>
          </Box>
        </Container>
      </PageTransition>
    );
  }

  const IconComponent = getActivityIcon(activity.type);

  return (
    <PageTransition>
      <Container maxWidth="lg">
        {/* Back button */}
        <AnimatedButton
          startIcon={<ArrowBack />}
          onClick={() => navigate("/activities")}
          sx={{ mb: 3 }}
          variant="outlined"
        >
          Back to Activities
        </AnimatedButton>

        <Grid container spacing={3}>
          {/* Main content */}
          <Grid item xs={12} md={8}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card
                sx={{
                  background:
                    theme.palette.mode === "dark"
                      ? `linear-gradient(135deg, ${alpha(
                          activity.color,
                          0.1
                        )} 0%, ${alpha(
                          theme.palette.background.paper,
                          0.9
                        )} 100%)`
                      : theme.palette.background.paper,
                  backdropFilter: "blur(10px)",
                  border: `1px solid ${alpha(activity.color, 0.2)}`,
                }}
              >
                {/* Progress bar */}
                {activity.progress > 0 && (
                  <Box sx={{ p: 3, pb: 0 }}>
                    <Stack
                      direction="row"
                      justifyContent="space-between"
                      alignItems="center"
                      mb={1}
                    >
                      <Typography variant="body2" color="text.secondary">
                        Your Progress
                      </Typography>
                      <Typography variant="body2" fontWeight={600}>
                        {activity.progress}%
                      </Typography>
                    </Stack>
                    <LinearProgress
                      variant="determinate"
                      value={activity.progress}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        background: alpha(activity.color, 0.1),
                        "& .MuiLinearProgress-bar": {
                          background: `linear-gradient(90deg, ${
                            activity.color
                          }, ${alpha(activity.color, 0.7)})`,
                        },
                      }}
                    />
                  </Box>
                )}

                <CardContent sx={{ p: 4 }}>
                  {/* Icon & badges */}
                  <Stack
                    direction="row"
                    spacing={2}
                    alignItems="center"
                    mb={3}
                    flexWrap="wrap"
                    gap={1}
                  >
                    <Box
                      sx={{
                        p: 2,
                        borderRadius: 3,
                        background: `linear-gradient(135deg, ${alpha(
                          activity.color,
                          0.2
                        )}, ${alpha(activity.color, 0.1)})`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <IconComponent
                        sx={{ color: activity.color, fontSize: 40 }}
                      />
                    </Box>
                    <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                      <Chip
                        label={getActivityTypeLabel(activity.type)}
                        sx={{
                          fontWeight: 600,
                          background: alpha(activity.color, 0.1),
                          color: activity.color,
                        }}
                      />
                      <Chip
                        label={activity.difficulty}
                        color={getDifficultyColor(activity.difficulty)}
                      />
                      {activity.completed && (
                        <Chip
                          icon={<CheckCircle />}
                          label="Completed"
                          color="success"
                        />
                      )}
                    </Stack>
                  </Stack>

                  {/* Title */}
                  <GradientText
                    variant={isMobile ? "h5" : "h4"}
                    sx={{ mb: 2, fontWeight: 700 }}
                  >
                    {activity.title}
                  </GradientText>

                  {/* Description */}
                  <Typography
                    variant="body1"
                    color="text.secondary"
                    sx={{ mb: 3, lineHeight: 1.8 }}
                  >
                    {activity.description}
                  </Typography>

                  <Divider sx={{ my: 3 }} />

                  {/* Learning Objectives */}
                  {activity.learningObjectives && (
                    <Box mb={3}>
                      <Typography
                        variant="h6"
                        fontWeight={700}
                        mb={2}
                        display="flex"
                        alignItems="center"
                        gap={1}
                      >
                        <School color="primary" />
                        Learning Objectives
                      </Typography>
                      <List dense>
                        {activity.learningObjectives.map((objective, index) => (
                          <ListItem key={index} sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <CheckCircle
                                fontSize="small"
                                sx={{ color: activity.color }}
                              />
                            </ListItemIcon>
                            <ListItemText primary={objective} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Prerequisites */}
                  {activity.prerequisites && (
                    <Box mb={3}>
                      <Typography
                        variant="h6"
                        fontWeight={700}
                        mb={2}
                        display="flex"
                        alignItems="center"
                        gap={1}
                      >
                        <Psychology color="primary" />
                        Prerequisites
                      </Typography>
                      <Stack spacing={1}>
                        {activity.prerequisites.map((prereq, index) => (
                          <Chip
                            key={index}
                            label={prereq}
                            variant="outlined"
                            size="small"
                          />
                        ))}
                      </Stack>
                    </Box>
                  )}

                  {/* Recommended For */}
                  {activity.recommendedFor && (
                    <Box mb={3}>
                      <Typography
                        variant="h6"
                        fontWeight={700}
                        mb={2}
                        display="flex"
                        alignItems="center"
                        gap={1}
                      >
                        <Person color="primary" />
                        Recommended For
                      </Typography>
                      <List dense>
                        {activity.recommendedFor.map((item, index) => (
                          <ListItem key={index} sx={{ py: 0.5 }}>
                            <ListItemIcon sx={{ minWidth: 32 }}>
                              <Star
                                fontSize="small"
                                sx={{ color: theme.palette.warning.main }}
                              />
                            </ListItemIcon>
                            <ListItemText primary={item} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}

                  {/* Tags */}
                  {activity.tags && (
                    <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                      {activity.tags.map((tag, index) => (
                        <Chip
                          key={index}
                          label={`#${tag}`}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Stack>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} md={4}>
            <Stack spacing={3}>
              {/* Quick Info Card */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={700} mb={2}>
                      Quick Info
                    </Typography>
                    <Stack spacing={2}>
                      <Stack direction="row" alignItems="center" spacing={2}>
                        <Timer color="action" />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Estimated Time
                          </Typography>
                          <Typography variant="body1" fontWeight={600}>
                            {activity.estimatedTime} minutes
                          </Typography>
                        </Box>
                      </Stack>
                      {activity.wordsCount && (
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Style color="action" />
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Total Words
                            </Typography>
                            <Typography variant="body1" fontWeight={600}>
                              {activity.wordsCount} words
                            </Typography>
                          </Box>
                        </Stack>
                      )}
                      {activity.questionsCount && (
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Quiz color="action" />
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Questions
                            </Typography>
                            <Typography variant="body1" fontWeight={600}>
                              {activity.questionsCount} questions
                            </Typography>
                          </Box>
                        </Stack>
                      )}
                      <Stack direction="row" alignItems="center" spacing={2}>
                        <TrendingUp color="action" />
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Difficulty
                          </Typography>
                          <Chip
                            label={activity.difficulty}
                            size="small"
                            color={getDifficultyColor(activity.difficulty)}
                          />
                        </Box>
                      </Stack>
                    </Stack>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Statistics Card */}
              {activity.statistics && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <Card>
                    <CardContent>
                      <Typography
                        variant="h6"
                        fontWeight={700}
                        mb={2}
                        display="flex"
                        alignItems="center"
                        gap={1}
                      >
                        <EmojiEvents color="warning" />
                        Community Stats
                      </Typography>
                      <Stack spacing={2}>
                        <Box>
                          <Stack
                            direction="row"
                            justifyContent="space-between"
                            mb={0.5}
                          >
                            <Typography variant="body2" color="text.secondary">
                              Average Score
                            </Typography>
                            <Typography variant="body2" fontWeight={600}>
                              {activity.statistics.averageScore}%
                            </Typography>
                          </Stack>
                          <LinearProgress
                            variant="determinate"
                            value={activity.statistics.averageScore}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                        <Box>
                          <Stack
                            direction="row"
                            justifyContent="space-between"
                            mb={0.5}
                          >
                            <Typography variant="body2" color="text.secondary">
                              Completion Rate
                            </Typography>
                            <Typography variant="body2" fontWeight={600}>
                              {activity.statistics.completionRate}%
                            </Typography>
                          </Stack>
                          <LinearProgress
                            variant="determinate"
                            value={activity.statistics.completionRate}
                            color="success"
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <Person color="action" />
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Total Attempts
                            </Typography>
                            <Typography variant="body1" fontWeight={600}>
                              {activity.statistics.totalAttempts.toLocaleString()}
                            </Typography>
                          </Box>
                        </Stack>
                        <Stack direction="row" alignItems="center" spacing={2}>
                          <CalendarToday color="action" />
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Avg. Time Spent
                            </Typography>
                            <Typography variant="body1" fontWeight={600}>
                              {activity.statistics.averageTimeSpent} min
                            </Typography>
                          </Box>
                        </Stack>
                      </Stack>
                    </CardContent>
                  </Card>
                </motion.div>
              )}

              {/* Start Activity Button */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <AnimatedButton
                  fullWidth
                  size="large"
                  variant="contained"
                  startIcon={activity.completed ? <Star /> : <PlayArrow />}
                  onClick={handleStartActivity}
                  sx={{
                    py: 2,
                    background: `linear-gradient(135deg, ${
                      activity.color
                    }, ${alpha(activity.color, 0.7)})`,
                    fontSize: "1.1rem",
                    fontWeight: 700,
                  }}
                >
                  {activity.completed
                    ? "Practice Again"
                    : activity.progress > 0
                    ? "Continue Activity"
                    : "Start Activity"}
                </AnimatedButton>
              </motion.div>
            </Stack>
          </Grid>
        </Grid>
      </Container>
    </PageTransition>
  );
};

export default ActivityDetail;
