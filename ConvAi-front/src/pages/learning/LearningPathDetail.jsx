import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  Grid,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Paper,
  Fab,
} from "@mui/material";
import {
  ArrowBack,
  ExpandMore,
  PlayArrow,
  CheckCircle,
  Lock,
  Schedule,
  Person,
  Star,
  Share,
  Bookmark,
  BookmarkBorder,
  PlayCircleFilled,
  Quiz,
  Assignment,
  Chat,
  VolumeUp,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../../store/index.js";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";

// Mock data - replace with API calls
const mockLearningPath = {
  id: 1,
  title: "Telugu to English Conversation Basics",
  description:
    "Master the fundamentals of English conversation with Telugu explanations and cultural context.",
  instructor: "Dr. Priya Sharma",
  instructorAvatar: "/avatars/instructor.jpg",
  difficulty: "Beginner",
  duration: "4 weeks",
  totalLessons: 24,
  completedLessons: 12,
  rating: 4.8,
  totalStudents: 1250,
  isBookmarked: false,
  price: "Free",
  tags: ["Conversation", "Beginner", "Telugu", "English"],
  chapters: [
    {
      id: 1,
      title: "Introduction & Greetings",
      description: "Learn basic greetings and introductions in English",
      lessons: [
        {
          id: 1,
          title: "Hello & Basic Greetings",
          type: "video",
          duration: "10 min",
          completed: true,
        },
        {
          id: 2,
          title: "Introducing Yourself",
          type: "interactive",
          duration: "15 min",
          completed: true,
        },
        {
          id: 3,
          title: "Practice Conversations",
          type: "practice",
          duration: "20 min",
          completed: false,
        },
      ],
    },
    {
      id: 2,
      title: "Daily Conversations",
      description: "Common everyday English conversations",
      lessons: [
        {
          id: 4,
          title: "At the Market",
          type: "video",
          duration: "12 min",
          completed: false,
        },
        {
          id: 5,
          title: "Asking for Directions",
          type: "interactive",
          duration: "18 min",
          completed: false,
        },
        {
          id: 6,
          title: "Restaurant Conversations",
          type: "practice",
          duration: "25 min",
          completed: false,
        },
      ],
    },
    {
      id: 3,
      title: "Advanced Topics",
      description: "More complex conversation topics",
      lessons: [
        {
          id: 7,
          title: "Job Interviews",
          type: "video",
          duration: "20 min",
          completed: false,
          locked: true,
        },
        {
          id: 8,
          title: "Business Meetings",
          type: "interactive",
          duration: "30 min",
          completed: false,
          locked: true,
        },
      ],
    },
  ],
};

const LessonIcon = ({ type }) => {
  switch (type) {
    case "video":
      return <PlayCircleFilled sx={{ color: "#f44336" }} />;
    case "interactive":
      return <Quiz sx={{ color: "#2196f3" }} />;
    case "practice":
      return <Chat sx={{ color: "#4caf50" }} />;
    default:
      return <Assignment sx={{ color: "#ff9800" }} />;
  }
};

LessonIcon.propTypes = {
  type: PropTypes.string.isRequired,
};

const LearningPathDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [learningPath, setLearningPath] = useState(null);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [expandedChapter, setExpandedChapter] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    const fetchLearningPath = async () => {
      setLoading(true);
      try {
        // Replace with actual API call
        setTimeout(() => {
          setLearningPath(mockLearningPath);
          setIsBookmarked(mockLearningPath.isBookmarked);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error("Failed to load learning path:", error);
        toast.error("Failed to load learning path");
        setLoading(false);
      }
    };

    fetchLearningPath();
  }, [id]);

  const handleBookmark = () => {
    setIsBookmarked(!isBookmarked);
    toast.success(
      isBookmarked ? "Removed from bookmarks" : "Added to bookmarks"
    );
  };

  const handleStartLesson = (lesson) => {
    if (lesson.locked) {
      toast.error("Complete previous lessons to unlock this content");
      return;
    }
    // Navigate to lesson
    navigate(`/lesson/${lesson.id}`);
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: learningPath.title,
        text: learningPath.description,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      toast.success("Link copied to clipboard!");
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "50vh",
          }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <PlayCircleFilled sx={{ fontSize: 60, color: "primary.main" }} />
          </motion.div>
        </Box>
      </Container>
    );
  }

  if (!learningPath) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h6" color="error">
          Learning path not found
        </Typography>
      </Container>
    );
  }

  const progressPercentage =
    (learningPath.completedLessons / learningPath.totalLessons) * 100;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/learning-paths")}
            sx={{ mb: 2 }}
          >
            Back to Learning Paths
          </Button>

          <Paper
            elevation={3}
            sx={{
              p: 4,
              borderRadius: 3,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              position: "relative",
              overflow: "hidden",
            }}
          >
            <Grid container spacing={4} alignItems="center">
              <Grid item xs={12} md={8}>
                <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
                  {learningPath.title}
                </Typography>
                <Typography variant="h6" sx={{ mb: 3, opacity: 0.9 }}>
                  {learningPath.description}
                </Typography>

                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 3 }}>
                  {learningPath.tags.map((tag, index) => (
                    <Chip
                      key={index}
                      label={tag}
                      sx={{
                        background: "rgba(255, 255, 255, 0.2)",
                        color: "white",
                        backdropFilter: "blur(10px)",
                      }}
                    />
                  ))}
                </Box>

                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 3,
                    flexWrap: "wrap",
                  }}
                >
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Avatar src={learningPath.instructorAvatar}>
                      <Person />
                    </Avatar>
                    <Typography variant="body2">
                      {learningPath.instructor}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                    <Star sx={{ color: "#ffd700" }} />
                    <Typography variant="body2">
                      {learningPath.rating} ({learningPath.totalStudents}{" "}
                      students)
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
                    <Schedule />
                    <Typography variant="body2">
                      {learningPath.duration}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12} md={4}>
                <Card
                  sx={{
                    background: "rgba(255, 255, 255, 0.1)",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(255, 255, 255, 0.2)",
                    color: "white",
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Your Progress
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant="body2">
                          {learningPath.completedLessons} of{" "}
                          {learningPath.totalLessons} lessons
                        </Typography>
                        <Typography variant="body2">
                          {Math.round(progressPercentage)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={progressPercentage}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: "rgba(255, 255, 255, 0.2)",
                          "& .MuiLinearProgress-bar": {
                            backgroundColor: "#4caf50",
                          },
                        }}
                      />
                    </Box>
                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Button
                        variant="contained"
                        fullWidth
                        startIcon={<PlayArrow />}
                        sx={{
                          background: "rgba(255, 255, 255, 0.9)",
                          color: "primary.main",
                          "&:hover": {
                            background: "white",
                          },
                        }}
                      >
                        Continue Learning
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Action Buttons */}
            <Box
              sx={{
                position: "absolute",
                top: 16,
                right: 16,
                display: "flex",
                gap: 1,
              }}
            >
              <IconButton onClick={handleBookmark} sx={{ color: "white" }}>
                {isBookmarked ? <Bookmark /> : <BookmarkBorder />}
              </IconButton>
              <IconButton onClick={handleShare} sx={{ color: "white" }}>
                <Share />
              </IconButton>
            </Box>
          </Paper>
        </Box>

        {/* Course Content */}
        <Grid container spacing={4}>
          <Grid item xs={12} md={8}>
            <Typography variant="h5" sx={{ fontWeight: "bold", mb: 3 }}>
              Course Content
            </Typography>

            <AnimatePresence>
              {learningPath.chapters.map((chapter, chapterIndex) => (
                <motion.div
                  key={chapter.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: chapterIndex * 0.1 }}
                >
                  <Accordion
                    expanded={expandedChapter === chapterIndex}
                    onChange={() =>
                      setExpandedChapter(
                        expandedChapter === chapterIndex ? -1 : chapterIndex
                      )
                    }
                    sx={{
                      mb: 2,
                      borderRadius: 2,
                      "&:before": { display: "none" },
                      boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                    }}
                  >
                    <AccordionSummary
                      expandIcon={<ExpandMore />}
                      sx={{
                        borderRadius: 2,
                        "&.Mui-expanded": {
                          borderBottomLeftRadius: 0,
                          borderBottomRightRadius: 0,
                        },
                      }}
                    >
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 2,
                          width: "100%",
                        }}
                      >
                        <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                          Chapter {chapterIndex + 1}: {chapter.title}
                        </Typography>
                        <Chip
                          label={`${chapter.lessons.length} lessons`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 2 }}
                      >
                        {chapter.description}
                      </Typography>
                      <List>
                        {chapter.lessons.map((lesson, lessonIndex) => (
                          <motion.div
                            key={lesson.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: lessonIndex * 0.05 }}
                          >
                            <ListItem disablePadding>
                              <ListItemButton
                                onClick={() => handleStartLesson(lesson)}
                                disabled={lesson.locked}
                                sx={{
                                  borderRadius: 2,
                                  mb: 1,
                                  "&:hover": {
                                    backgroundColor: "primary.light",
                                    "& .MuiListItemText-primary": {
                                      color: "white",
                                    },
                                  },
                                }}
                              >
                                <ListItemIcon>
                                  {lesson.locked ? (
                                    <Lock sx={{ color: "text.disabled" }} />
                                  ) : lesson.completed ? (
                                    <CheckCircle
                                      sx={{ color: "success.main" }}
                                    />
                                  ) : (
                                    <LessonIcon type={lesson.type} />
                                  )}
                                </ListItemIcon>
                                <ListItemText
                                  primary={lesson.title}
                                  secondary={lesson.duration}
                                  sx={{
                                    opacity: lesson.locked ? 0.5 : 1,
                                  }}
                                />
                                {lesson.completed && (
                                  <Chip
                                    label="Completed"
                                    size="small"
                                    color="success"
                                    variant="outlined"
                                  />
                                )}
                              </ListItemButton>
                            </ListItem>
                          </motion.div>
                        ))}
                      </List>
                    </AccordionDetails>
                  </Accordion>
                </motion.div>
              ))}
            </AnimatePresence>
          </Grid>

          <Grid item xs={12} md={4}>
            {/* Course Stats */}
            <Card sx={{ mb: 3, borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Course Statistics
                </Typography>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                  <Box
                    sx={{ display: "flex", justifyContent: "space-between" }}
                  >
                    <Typography variant="body2">Total Lessons:</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {learningPath.totalLessons}
                    </Typography>
                  </Box>
                  <Box
                    sx={{ display: "flex", justifyContent: "space-between" }}
                  >
                    <Typography variant="body2">Completed:</Typography>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color="success.main"
                    >
                      {learningPath.completedLessons}
                    </Typography>
                  </Box>
                  <Box
                    sx={{ display: "flex", justifyContent: "space-between" }}
                  >
                    <Typography variant="body2">Remaining:</Typography>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color="warning.main"
                    >
                      {learningPath.totalLessons -
                        learningPath.completedLessons}
                    </Typography>
                  </Box>
                  <Divider />
                  <Box
                    sx={{ display: "flex", justifyContent: "space-between" }}
                  >
                    <Typography variant="body2">Difficulty:</Typography>
                    <Chip
                      label={learningPath.difficulty}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                  <Button variant="outlined" startIcon={<VolumeUp />} fullWidth>
                    Practice Pronunciation
                  </Button>
                  <Button variant="outlined" startIcon={<Quiz />} fullWidth>
                    Take Quiz
                  </Button>
                  <Button variant="outlined" startIcon={<Chat />} fullWidth>
                    Chat with AI Tutor
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Floating Action Button */}
        <Fab
          color="primary"
          sx={{
            position: "fixed",
            bottom: 24,
            right: 24,
            background: "linear-gradient(135deg, #667eea, #764ba2)",
          }}
          onClick={() => {
            // Find next incomplete lesson
            const nextLesson = learningPath.chapters
              .flatMap((chapter) => chapter.lessons)
              .find((lesson) => !lesson.completed && !lesson.locked);

            if (nextLesson) {
              handleStartLesson(nextLesson);
            } else {
              toast.info("All available lessons completed!");
            }
          }}
        >
          <PlayArrow />
        </Fab>
      </motion.div>
    </Container>
  );
};

export default LearningPathDetail;
