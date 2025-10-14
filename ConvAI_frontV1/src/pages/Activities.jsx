import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  TextField,
  InputAdornment,
  ToggleButtonGroup,
  ToggleButton,
  Chip,
  Stack,
  IconButton,
  Tooltip,
  CircularProgress,
  Container,
  useTheme,
  useMediaQuery,
  alpha,
} from "@mui/material";
import {
  Search,
  FilterList,
  ViewModule,
  ViewList,
  Style,
  Quiz,
  MenuBook,
  Psychology,
  Timer,
  TrendingUp,
  PlayArrow,
  CheckCircle,
  Star,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import AnimatedButton from "../components/common/AnimatedButton";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const Activities = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isTablet = useMediaQuery(theme.breakpoints.down("md"));

  // State
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterDifficulty, setFilterDifficulty] = useState("all");
  const [viewMode, setViewMode] = useState("grid");

  useEffect(() => {
    fetchActivities();
  }, []);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      // Try to fetch from API
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.LIST);
      // Backend returns {success: true, data: {activities: [...], pagination: {...}}}
      setActivities(response.data.data?.activities || response.data.activities || []);
    } catch (error) {
      console.error("Error fetching activities:", error);
      // Use mock data
      setActivities(getMockActivities());
    } finally {
      setLoading(false);
    }
  };

  const getMockActivities = () => [
    {
      id: 1,
      type: "flashcard",
      title: "Daily Vocabulary Practice",
      description:
        "Practice common English words with Telugu translations using interactive flashcards",
      difficulty: "beginner",
      estimatedTime: 15,
      wordsCount: 20,
      completed: false,
      progress: 0,
      icon: Style,
      color: theme.palette.primary.main,
      tags: ["vocabulary", "daily"],
    },
    {
      id: 2,
      type: "quiz",
      title: "Grammar Quiz: Present Tense",
      description:
        "Test your understanding of present tense verbs and sentence structure",
      difficulty: "intermediate",
      estimatedTime: 10,
      questionsCount: 15,
      completed: false,
      progress: 60,
      icon: Quiz,
      color: theme.palette.secondary.main,
      tags: ["grammar", "quiz"],
    },
    {
      id: 3,
      type: "reading",
      title: "Reading Comprehension: Technology",
      description:
        "Read an article about modern technology and answer comprehension questions",
      difficulty: "intermediate",
      estimatedTime: 20,
      questionsCount: 8,
      completed: true,
      progress: 100,
      score: 87,
      icon: MenuBook,
      color: theme.palette.success.main,
      tags: ["reading", "technology"],
    },
    {
      id: 4,
      type: "flashcard",
      title: "Business English Phrases",
      description:
        "Learn professional vocabulary and common business expressions",
      difficulty: "advanced",
      estimatedTime: 25,
      wordsCount: 30,
      completed: false,
      progress: 40,
      icon: Style,
      color: theme.palette.primary.main,
      tags: ["business", "professional"],
    },
    {
      id: 5,
      type: "quiz",
      title: "Vocabulary Quiz: Common Idioms",
      description: "Test your knowledge of popular English idioms and phrases",
      difficulty: "advanced",
      estimatedTime: 12,
      questionsCount: 20,
      completed: false,
      progress: 0,
      icon: Quiz,
      color: theme.palette.secondary.main,
      tags: ["idioms", "vocabulary"],
    },
    {
      id: 6,
      type: "reading",
      title: "Short Story: The Journey",
      description:
        "Read a short story and answer questions about plot and characters",
      difficulty: "beginner",
      estimatedTime: 15,
      questionsCount: 10,
      completed: false,
      progress: 0,
      icon: MenuBook,
      color: theme.palette.success.main,
      tags: ["story", "beginner"],
    },
    {
      id: 7,
      type: "flashcard",
      title: "Travel & Tourism Vocabulary",
      description:
        "Essential words and phrases for traveling and exploring new places",
      difficulty: "intermediate",
      estimatedTime: 18,
      wordsCount: 25,
      completed: false,
      progress: 0,
      icon: Style,
      color: theme.palette.primary.main,
      tags: ["travel", "vocabulary"],
    },
    {
      id: 8,
      type: "quiz",
      title: "Pronunciation Practice Quiz",
      description:
        "Identify correct pronunciation and stress patterns in English words",
      difficulty: "beginner",
      estimatedTime: 8,
      questionsCount: 12,
      completed: true,
      progress: 100,
      score: 92,
      icon: Quiz,
      color: theme.palette.secondary.main,
      tags: ["pronunciation", "speaking"],
    },
  ];

  // Filter activities
  const filteredActivities = activities.filter((activity) => {
    const matchesSearch =
      activity.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      activity.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      activity.tags?.some((tag) =>
        tag.toLowerCase().includes(searchTerm.toLowerCase())
      );

    const matchesType = filterType === "all" || activity.type === filterType;
    const matchesDifficulty =
      filterDifficulty === "all" || activity.difficulty === filterDifficulty;

    return matchesSearch && matchesType && matchesDifficulty;
  });

  const handleActivityClick = (activity) => {
    // Navigate to specific activity type
    if (activity.type === "flashcard") {
      navigate(`/activities/flashcards/${activity.id}`);
    } else if (activity.type === "quiz") {
      navigate(`/activities/quiz/${activity.id}`);
    } else if (activity.type === "reading") {
      navigate(`/activities/reading/${activity.id}`);
    } else {
      navigate(`/activities/${activity.id}`);
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

  const ActivityCard = ({ activity }) => {
    const IconComponent = activity.icon || Psychology;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -8 }}
        transition={{ duration: 0.3 }}
      >
        <Card
          sx={{
            height: "100%",
            display: "flex",
            flexDirection: "column",
            position: "relative",
            overflow: "visible",
            cursor: "pointer",
            transition: "all 0.3s ease",
            background:
              theme.palette.mode === "dark"
                ? `linear-gradient(135deg, ${alpha(
                    activity.color,
                    0.1
                  )} 0%, ${alpha(theme.palette.background.paper, 0.9)} 100%)`
                : theme.palette.background.paper,
            backdropFilter: "blur(10px)",
            border: `1px solid ${alpha(activity.color, 0.2)}`,
            "&:hover": {
              boxShadow: `0 12px 40px ${alpha(activity.color, 0.3)}`,
              border: `1px solid ${alpha(activity.color, 0.5)}`,
            },
          }}
          onClick={() => handleActivityClick(activity)}
        >
          {/* Progress indicator */}
          {activity.progress > 0 && (
            <Box
              sx={{
                position: "absolute",
                top: 0,
                left: 0,
                right: 0,
                height: 4,
                background: `linear-gradient(90deg, ${
                  activity.color
                } 0%, ${alpha(activity.color, 0.5)} 100%)`,
                width: `${activity.progress}%`,
                transition: "width 0.3s ease",
              }}
            />
          )}

          {/* Completed badge */}
          {activity.completed && (
            <Chip
              icon={<CheckCircle />}
              label={`Score: ${activity.score}%`}
              color="success"
              size="small"
              sx={{
                position: "absolute",
                top: 12,
                right: 12,
                zIndex: 1,
                fontWeight: 600,
              }}
            />
          )}

          <CardContent sx={{ flexGrow: 1, pt: activity.completed ? 5 : 2 }}>
            {/* Icon & Type */}
            <Stack direction="row" spacing={2} alignItems="center" mb={2}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  background: `linear-gradient(135deg, ${alpha(
                    activity.color,
                    0.2
                  )}, ${alpha(activity.color, 0.1)})`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <IconComponent sx={{ color: activity.color, fontSize: 28 }} />
              </Box>
              <Chip
                label={getActivityTypeLabel(activity.type)}
                size="small"
                sx={{
                  fontWeight: 600,
                  background: alpha(activity.color, 0.1),
                  color: activity.color,
                }}
              />
            </Stack>

            {/* Title */}
            <Typography
              variant="h6"
              sx={{
                fontWeight: 700,
                mb: 1,
                color: theme.palette.text.primary,
              }}
            >
              {activity.title}
            </Typography>

            {/* Description */}
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                mb: 2,
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
                minHeight: 40,
              }}
            >
              {activity.description}
            </Typography>

            {/* Stats */}
            <Stack direction="row" spacing={2} mb={2} flexWrap="wrap" gap={1}>
              <Chip
                icon={<Timer />}
                label={`${activity.estimatedTime} min`}
                size="small"
                variant="outlined"
              />
              <Chip
                label={activity.difficulty}
                size="small"
                color={getDifficultyColor(activity.difficulty)}
              />
              {activity.wordsCount && (
                <Chip
                  label={`${activity.wordsCount} words`}
                  size="small"
                  variant="outlined"
                />
              )}
              {activity.questionsCount && (
                <Chip
                  label={`${activity.questionsCount} questions`}
                  size="small"
                  variant="outlined"
                />
              )}
            </Stack>

            {/* Tags */}
            {activity.tags && (
              <Stack direction="row" spacing={0.5} flexWrap="wrap" gap={0.5}>
                {activity.tags.map((tag, index) => (
                  <Chip
                    key={index}
                    label={tag}
                    size="small"
                    variant="outlined"
                    sx={{ fontSize: "0.7rem", height: 20 }}
                  />
                ))}
              </Stack>
            )}
          </CardContent>

          <CardActions sx={{ p: 2, pt: 0 }}>
            <AnimatedButton
              fullWidth
              variant={activity.completed ? "outlined" : "contained"}
              startIcon={activity.completed ? <Star /> : <PlayArrow />}
              sx={{
                background: !activity.completed
                  ? `linear-gradient(135deg, ${activity.color}, ${alpha(
                      activity.color,
                      0.7
                    )})`
                  : "transparent",
                color: !activity.completed
                  ? "#fff"
                  : theme.palette.text.primary,
              }}
            >
              {activity.completed
                ? "Practice Again"
                : activity.progress > 0
                ? "Continue"
                : "Start Activity"}
            </AnimatedButton>
          </CardActions>
        </Card>
      </motion.div>
    );
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

  return (
    <PageTransition>
      <Container maxWidth="xl">
        {/* Header */}
        <Box mb={4}>
          <GradientText
            variant={isMobile ? "h4" : "h3"}
            sx={{ mb: 2, fontWeight: 700 }}
          >
            Learning Activities
          </GradientText>
          <Typography variant="body1" color="text.secondary">
            Choose from various activities to enhance your English learning
            journey
          </Typography>
        </Box>

        {/* Filters & Search */}
        <Box
          mb={4}
          sx={{
            p: 3,
            borderRadius: 3,
            background:
              theme.palette.mode === "dark"
                ? alpha(theme.palette.background.paper, 0.6)
                : theme.palette.background.paper,
            backdropFilter: "blur(10px)",
            border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
          }}
        >
          <Stack spacing={3}>
            {/* Search */}
            <TextField
              fullWidth
              placeholder="Search activities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 2,
                },
              }}
            />

            {/* Filters */}
            <Stack
              direction={isMobile ? "column" : "row"}
              spacing={2}
              alignItems={isMobile ? "stretch" : "center"}
              justifyContent="space-between"
            >
              {/* Type filter */}
              <Box>
                <Typography variant="caption" color="text.secondary" mb={1}>
                  Activity Type
                </Typography>
                <ToggleButtonGroup
                  value={filterType}
                  exclusive
                  onChange={(e, value) => value && setFilterType(value)}
                  size="small"
                  sx={{ flexWrap: "wrap" }}
                >
                  <ToggleButton value="all">All</ToggleButton>
                  <ToggleButton value="flashcard">
                    <Style sx={{ mr: 0.5, fontSize: 18 }} /> Flashcards
                  </ToggleButton>
                  <ToggleButton value="quiz">
                    <Quiz sx={{ mr: 0.5, fontSize: 18 }} /> Quiz
                  </ToggleButton>
                  <ToggleButton value="reading">
                    <MenuBook sx={{ mr: 0.5, fontSize: 18 }} /> Reading
                  </ToggleButton>
                </ToggleButtonGroup>
              </Box>

              {/* Difficulty filter */}
              <Box>
                <Typography variant="caption" color="text.secondary" mb={1}>
                  Difficulty
                </Typography>
                <ToggleButtonGroup
                  value={filterDifficulty}
                  exclusive
                  onChange={(e, value) => value && setFilterDifficulty(value)}
                  size="small"
                >
                  <ToggleButton value="all">All</ToggleButton>
                  <ToggleButton value="beginner">Beginner</ToggleButton>
                  <ToggleButton value="intermediate">Intermediate</ToggleButton>
                  <ToggleButton value="advanced">Advanced</ToggleButton>
                </ToggleButtonGroup>
              </Box>

              {/* View mode toggle */}
              {!isMobile && (
                <ToggleButtonGroup
                  value={viewMode}
                  exclusive
                  onChange={(e, value) => value && setViewMode(value)}
                  size="small"
                >
                  <ToggleButton value="grid">
                    <ViewModule />
                  </ToggleButton>
                  <ToggleButton value="list">
                    <ViewList />
                  </ToggleButton>
                </ToggleButtonGroup>
              )}
            </Stack>
          </Stack>
        </Box>

        {/* Results count */}
        <Typography variant="body2" color="text.secondary" mb={2}>
          Showing {filteredActivities.length} of {activities.length} activities
        </Typography>

        {/* Activities Grid */}
        <Grid container spacing={3}>
          {filteredActivities.map((activity) => (
            <Grid
              item
              xs={12}
              sm={viewMode === "list" ? 12 : 6}
              md={viewMode === "list" ? 12 : 4}
              lg={viewMode === "list" ? 12 : 3}
              key={activity.id}
            >
              <ActivityCard activity={activity} />
            </Grid>
          ))}
        </Grid>

        {/* Empty state */}
        {filteredActivities.length === 0 && (
          <Box
            textAlign="center"
            py={8}
            sx={{
              background: alpha(theme.palette.background.paper, 0.5),
              borderRadius: 3,
              border: `1px dashed ${theme.palette.divider}`,
            }}
          >
            <Psychology sx={{ fontSize: 80, color: theme.palette.divider }} />
            <Typography variant="h6" color="text.secondary" mt={2}>
              No activities found
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Try adjusting your filters or search terms
            </Typography>
          </Box>
        )}
      </Container>
    </PageTransition>
  );
};

export default Activities;
