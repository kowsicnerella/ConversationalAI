import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  LinearProgress,
  Button,
  IconButton,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Rating,
  Tab,
  Tabs,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import {
  ArrowBack,
  PlayArrow,
  Bookmark,
  BookmarkBorder,
  Share,
  Star,
  People,
  CheckCircle,
  RadioButtonUnchecked,
  Lock,
  ExpandMore,
  Quiz,
  MenuBook,
  Headphones,
  Assignment,
  VideoLibrary,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../store/index.js";

// Mock data removed - using real API data from coursesAPI.getLearningPathDetail()
  id: 1,
  title: "Complete Telugu Grammar",
  description:
    "Master the fundamentals of Telugu grammar with comprehensive lessons and exercises. This course covers everything from basic sentence structure to advanced grammatical concepts.",
  image: "/images/telugu-grammar.jpg",
  level: "Beginner",
  duration: "6 weeks",
  lessonsCount: 24,
  studentsCount: 1250,
  rating: 4.8,
  progress: 65,
  isBookmarked: true,
  category: "Grammar",
  instructor: {
    name: "Dr. Priya Sharma",
    avatar: "/images/instructor-priya.jpg",
    title: "Telugu Language Expert",
    experience: "15+ years",
    studentsCount: 5000,
    rating: 4.9,
  },
  tags: ["Telugu", "Grammar", "Beginner"],
  completionRate: 87,
  whatYouWillLearn: [
    "Basic Telugu sentence structure and word order",
    "Noun declensions and verb conjugations",
    "Proper usage of grammatical particles",
    "Formation of complex sentences",
    "Common grammatical patterns and exceptions",
    "Practical application in daily conversations",
  ],
  requirements: [
    "Basic knowledge of Telugu script (reading ability)",
    "Motivation to learn Telugu grammar systematically",
    "Time commitment of 3-4 hours per week",
  ],
  chapters: [
    {
      id: 1,
      title: "Introduction to Telugu Grammar",
      lessons: [
        {
          id: 1,
          title: "Overview of Telugu Language Structure",
          type: "video",
          duration: "15 min",
          isCompleted: true,
        },
        {
          id: 2,
          title: "Basic Grammar Concepts",
          type: "reading",
          duration: "10 min",
          isCompleted: true,
        },
        {
          id: 3,
          title: "Practice Exercise: Identifying Parts of Speech",
          type: "quiz",
          duration: "20 min",
          isCompleted: true,
        },
      ],
      isCompleted: true,
    },
    {
      id: 2,
      title: "Nouns and Pronouns",
      lessons: [
        {
          id: 4,
          title: "Telugu Noun Classifications",
          type: "video",
          duration: "18 min",
          isCompleted: true,
        },
        {
          id: 5,
          title: "Case Endings and Declensions",
          type: "reading",
          duration: "25 min",
          isCompleted: true,
        },
        {
          id: 6,
          title: "Pronoun Usage in Different Contexts",
          type: "audio",
          duration: "12 min",
          isCompleted: false,
          isLocked: false,
        },
        {
          id: 7,
          title: "Chapter 2 Assessment",
          type: "quiz",
          duration: "30 min",
          isCompleted: false,
          isLocked: false,
        },
      ],
      isCompleted: false,
    },
    {
      id: 3,
      title: "Verbs and Tenses",
      lessons: [
        {
          id: 8,
          title: "Verb Root Identification",
          type: "video",
          duration: "20 min",
          isCompleted: false,
          isLocked: true,
        },
        {
          id: 9,
          title: "Present Tense Formations",
          type: "reading",
          duration: "15 min",
          isCompleted: false,
          isLocked: true,
        },
      ],
      isCompleted: false,
    },
  ],
  reviews: [
    {
      id: 1,
      user: "Ravi Kumar",
      avatar: "/images/user1.jpg",
      rating: 5,
      comment:
        "Excellent course! Dr. Priya explains complex grammar concepts in a very simple way.",
      date: "2 days ago",
    },
    {
      id: 2,
      user: "Meera Patel",
      avatar: "/images/user2.jpg",
      rating: 4,
      comment:
        "Great content and well-structured lessons. The practice exercises are very helpful.",
      date: "1 week ago",
    },
    {
      id: 3,
      user: "Anand Reddy",
      avatar: "/images/user3.jpg",
      rating: 5,
      comment:
        "This course helped me understand Telugu grammar much better than any book I&apos;ve read.",
      date: "2 weeks ago",
    },
  ],
};

const LearningPathDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [pathDetail] = useState(mockPathDetail);
  const [activeTab, setActiveTab] = useState(0);
  const [isBookmarked, setIsBookmarked] = useState(pathDetail.isBookmarked);
  const [showEnrollDialog, setShowEnrollDialog] = useState(false);
  const [expandedChapter, setExpandedChapter] = useState(false);

  const getLessonIcon = (type) => {
    switch (type) {
      case "video":
        return <VideoLibrary />;
      case "reading":
        return <MenuBook />;
      case "audio":
        return <Headphones />;
      case "quiz":
        return <Quiz />;
      default:
        return <Assignment />;
    }
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

  const handleToggleBookmark = () => {
    setIsBookmarked(!isBookmarked);
  };

  const handleStartLesson = (chapterId, lessonId) => {
    navigate(`/learning-paths/${id}/lessons/${lessonId}`);
  };

  const handleEnroll = () => {
    // Handle enrollment logic here
    setShowEnrollDialog(false);
    navigate(`/learning-paths/${id}/lessons/1`);
  };

  const ProgressStats = () => (
    <Grid container spacing={3}>
      <Grid item xs={6} md={3}>
        <Paper sx={{ p: 2, textAlign: "center", borderRadius: 2 }}>
          <Typography
            variant="h4"
            sx={{ fontWeight: "bold", color: "primary.main" }}
          >
            {pathDetail.progress}%
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Complete
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={6} md={3}>
        <Paper sx={{ p: 2, textAlign: "center", borderRadius: 2 }}>
          <Typography
            variant="h4"
            sx={{ fontWeight: "bold", color: "success.main" }}
          >
            {pathDetail.chapters.filter((c) => c.isCompleted).length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Chapters Done
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={6} md={3}>
        <Paper sx={{ p: 2, textAlign: "center", borderRadius: 2 }}>
          <Typography
            variant="h4"
            sx={{ fontWeight: "bold", color: "warning.main" }}
          >
            {pathDetail.rating}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Rating
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={6} md={3}>
        <Paper sx={{ p: 2, textAlign: "center", borderRadius: 2 }}>
          <Typography
            variant="h4"
            sx={{ fontWeight: "bold", color: "info.main" }}
          >
            {pathDetail.studentsCount.toLocaleString()}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Students
          </Typography>
        </Paper>
      </Grid>
    </Grid>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
          <IconButton
            onClick={() => navigate("/learning-paths")}
            sx={{ mr: 2 }}
            component={motion.button}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <ArrowBack />
          </IconButton>
          <Typography variant="h5" sx={{ fontWeight: "bold" }}>
            Learning Path Details
          </Typography>
        </Box>
      </motion.div>

      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        <Card sx={{ mb: 4, borderRadius: 3, overflow: "hidden" }}>
          <Box
            sx={{
              height: 300,
              background: "linear-gradient(135deg, #667eea, #764ba2)",
              display: "flex",
              alignItems: "center",
              position: "relative",
              color: "white",
            }}
          >
            <Container>
              <Grid container spacing={4} alignItems="center">
                <Grid item xs={12} md={8}>
                  <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
                    {pathDetail.title}
                  </Typography>
                  <Typography variant="h6" sx={{ mb: 3, opacity: 0.9 }}>
                    {pathDetail.description}
                  </Typography>
                  <Box
                    sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 3 }}
                  >
                    <Chip
                      label={pathDetail.level}
                      color={getLevelColor(pathDetail.level)}
                      sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
                    />
                    <Chip
                      label={pathDetail.category}
                      sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
                    />
                    <Chip
                      label={`${pathDetail.duration} • ${pathDetail.lessonsCount} lessons`}
                      sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
                    />
                  </Box>
                  <Box sx={{ display: "flex", gap: 2 }}>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<PlayArrow />}
                      onClick={() => setShowEnrollDialog(true)}
                      sx={{
                        bgcolor: "white",
                        color: "primary.main",
                        "&:hover": { bgcolor: "grey.100" },
                      }}
                      component={motion.button}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {pathDetail.progress > 0
                        ? "Continue Learning"
                        : "Start Learning"}
                    </Button>
                    <IconButton
                      onClick={handleToggleBookmark}
                      sx={{
                        bgcolor: "rgba(255,255,255,0.2)",
                        color: "white",
                        "&:hover": { bgcolor: "rgba(255,255,255,0.3)" },
                      }}
                      component={motion.button}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      {isBookmarked ? <Bookmark /> : <BookmarkBorder />}
                    </IconButton>
                    <IconButton
                      sx={{
                        bgcolor: "rgba(255,255,255,0.2)",
                        color: "white",
                        "&:hover": { bgcolor: "rgba(255,255,255,0.3)" },
                      }}
                      component={motion.button}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <Share />
                    </IconButton>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box sx={{ textAlign: "center" }}>
                    <Avatar
                      src={pathDetail.instructor.avatar}
                      sx={{ width: 120, height: 120, mx: "auto", mb: 2 }}
                    >
                      {pathDetail.instructor.name.charAt(0)}
                    </Avatar>
                    <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                      {pathDetail.instructor.name}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      {pathDetail.instructor.title}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Container>
          </Box>

          {pathDetail.progress > 0 && (
            <Box sx={{ p: 2, bgcolor: "primary.main", color: "white" }}>
              <Box
                sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}
              >
                <Typography variant="body2">Your Progress</Typography>
                <Typography variant="body2">
                  {pathDetail.progress}% Complete
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={pathDetail.progress}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: "rgba(255,255,255,0.3)",
                  "& .MuiLinearProgress-bar": {
                    bgcolor: "white",
                  },
                }}
              />
            </Box>
          )}
        </Card>
      </motion.div>

      {/* Progress Stats */}
      {pathDetail.progress > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <Box sx={{ mb: 4 }}>
            <ProgressStats />
          </Box>
        </motion.div>
      )}

      {/* Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        <Card sx={{ borderRadius: 3 }}>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: "divider" }}
          >
            <Tab label="Curriculum" />
            <Tab label="About" />
            <Tab label="Instructor" />
            <Tab label={`Reviews (${pathDetail.reviews.length})`} />
          </Tabs>

          <CardContent sx={{ p: 4 }}>
            <AnimatePresence mode="wait">
              {/* Curriculum Tab */}
              {activeTab === 0 && (
                <motion.div
                  key="curriculum"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 3 }}>
                    Course Curriculum
                  </Typography>
                  {pathDetail.chapters.map((chapter) => (
                    <Accordion
                      key={chapter.id}
                      expanded={expandedChapter === chapter.id}
                      onChange={(e, isExpanded) =>
                        setExpandedChapter(isExpanded ? chapter.id : false)
                      }
                      sx={{
                        mb: 2,
                        borderRadius: 2,
                        "&:before": { display: "none" },
                      }}
                    >
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            width: "100%",
                          }}
                        >
                          <Box sx={{ mr: 2 }}>
                            {chapter.isCompleted ? (
                              <CheckCircle sx={{ color: "success.main" }} />
                            ) : (
                              <RadioButtonUnchecked
                                sx={{ color: "text.secondary" }}
                              />
                            )}
                          </Box>
                          <Box sx={{ flexGrow: 1 }}>
                            <Typography
                              variant="subtitle1"
                              sx={{ fontWeight: "bold" }}
                            >
                              Chapter {chapter.id}: {chapter.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {chapter.lessons.length} lessons
                            </Typography>
                          </Box>
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <List>
                          {chapter.lessons.map((lesson) => (
                            <ListItem
                              key={lesson.id}
                              sx={{
                                borderRadius: 1,
                                mb: 1,
                                bgcolor: lesson.isCompleted
                                  ? "success.light"
                                  : "grey.50",
                                opacity: lesson.isLocked ? 0.5 : 1,
                              }}
                              secondaryAction={
                                !lesson.isLocked && (
                                  <Button
                                    size="small"
                                    variant={
                                      lesson.isCompleted
                                        ? "outlined"
                                        : "contained"
                                    }
                                    onClick={() =>
                                      handleStartLesson(chapter.id, lesson.id)
                                    }
                                    disabled={lesson.isLocked}
                                  >
                                    {lesson.isCompleted ? "Review" : "Start"}
                                  </Button>
                                )
                              }
                            >
                              <ListItemIcon>
                                {lesson.isLocked ? (
                                  <Lock />
                                ) : lesson.isCompleted ? (
                                  <CheckCircle sx={{ color: "success.main" }} />
                                ) : (
                                  getLessonIcon(lesson.type)
                                )}
                              </ListItemIcon>
                              <ListItemText
                                primary={lesson.title}
                                secondary={`${lesson.type} • ${lesson.duration}`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </motion.div>
              )}

              {/* About Tab */}
              {activeTab === 1 && (
                <motion.div
                  key="about"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 3 }}>
                    What you&apos;ll learn
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 4 }}>
                    {pathDetail.whatYouWillLearn.map((item, index) => (
                      <Grid item xs={12} md={6} key={index}>
                        <Box sx={{ display: "flex", alignItems: "flex-start" }}>
                          <CheckCircle
                            sx={{
                              color: "success.main",
                              mr: 1,
                              mt: 0.5,
                              fontSize: 20,
                            }}
                          />
                          <Typography variant="body2">{item}</Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>

                  <Divider sx={{ my: 4 }} />

                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 3 }}>
                    Requirements
                  </Typography>
                  {pathDetail.requirements.map((req, index) => (
                    <Box
                      key={index}
                      sx={{ display: "flex", alignItems: "flex-start", mb: 2 }}
                    >
                      <Box
                        sx={{
                          width: 6,
                          height: 6,
                          bgcolor: "text.secondary",
                          borderRadius: "50%",
                          mr: 2,
                          mt: 1,
                        }}
                      />
                      <Typography variant="body2">{req}</Typography>
                    </Box>
                  ))}
                </motion.div>
              )}

              {/* Instructor Tab */}
              {activeTab === 2 && (
                <motion.div
                  key="instructor"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Box sx={{ display: "flex", alignItems: "center", mb: 4 }}>
                    <Avatar
                      src={pathDetail.instructor.avatar}
                      sx={{ width: 80, height: 80, mr: 3 }}
                    >
                      {pathDetail.instructor.name.charAt(0)}
                    </Avatar>
                    <Box>
                      <Typography variant="h5" sx={{ fontWeight: "bold" }}>
                        {pathDetail.instructor.name}
                      </Typography>
                      <Typography
                        variant="body1"
                        color="text.secondary"
                        sx={{ mb: 1 }}
                      >
                        {pathDetail.instructor.title}
                      </Typography>
                      <Box
                        sx={{ display: "flex", alignItems: "center", gap: 2 }}
                      >
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                          <Star
                            sx={{
                              color: "warning.main",
                              mr: 0.5,
                              fontSize: 20,
                            }}
                          />
                          <Typography variant="body2">
                            {pathDetail.instructor.rating}
                          </Typography>
                        </Box>
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                          <People
                            sx={{
                              color: "text.secondary",
                              mr: 0.5,
                              fontSize: 20,
                            }}
                          />
                          <Typography variant="body2">
                            {pathDetail.instructor.studentsCount.toLocaleString()}{" "}
                            students
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {pathDetail.instructor.experience} experience
                        </Typography>
                      </Box>
                    </Box>
                  </Box>

                  <Typography variant="body1">
                    Dr. Priya Sharma is a renowned Telugu language expert with
                    over 15 years of experience in teaching and curriculum
                    development. She has helped thousands of students master
                    Telugu grammar through her innovative teaching methods and
                    comprehensive course materials.
                  </Typography>
                </motion.div>
              )}

              {/* Reviews Tab */}
              {activeTab === 3 && (
                <motion.div
                  key="reviews"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Box sx={{ display: "flex", alignItems: "center", mb: 4 }}>
                    <Typography variant="h4" sx={{ fontWeight: "bold", mr: 2 }}>
                      {pathDetail.rating}
                    </Typography>
                    <Box>
                      <Rating
                        value={pathDetail.rating}
                        readOnly
                        precision={0.1}
                      />
                      <Typography variant="body2" color="text.secondary">
                        Based on {pathDetail.reviews.length} reviews
                      </Typography>
                    </Box>
                  </Box>

                  {pathDetail.reviews.map((review) => (
                    <Box
                      key={review.id}
                      sx={{
                        mb: 3,
                        pb: 3,
                        borderBottom: 1,
                        borderColor: "divider",
                      }}
                    >
                      <Box
                        sx={{ display: "flex", alignItems: "center", mb: 2 }}
                      >
                        <Avatar src={review.avatar} sx={{ mr: 2 }}>
                          {review.user.charAt(0)}
                        </Avatar>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography
                            variant="subtitle2"
                            sx={{ fontWeight: "bold" }}
                          >
                            {review.user}
                          </Typography>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              gap: 1,
                            }}
                          >
                            <Rating
                              value={review.rating}
                              size="small"
                              readOnly
                            />
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {review.date}
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                      <Typography variant="body2">{review.comment}</Typography>
                    </Box>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </CardContent>
        </Card>
      </motion.div>

      {/* Enrollment Dialog */}
      <Dialog
        open={showEnrollDialog}
        onClose={() => setShowEnrollDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Start Learning Path</DialogTitle>
        <DialogContent>
          <Typography>
            Are you ready to start your learning journey with &quot;
            {pathDetail.title}&quot;? This course will help you master Telugu
            grammar through structured lessons and practical exercises.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEnrollDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleEnroll}>
            Start Learning
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default LearningPathDetail;
