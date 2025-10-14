import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  CircularProgress,
  IconButton,
} from "@mui/material";
import {
  ExpandMore,
  PlayArrow,
  CheckCircle,
  Lock,
  ArrowBack,
  School,
  AccessTime,
  TrendingUp,
  Quiz,
  MenuBook,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import HoverCard from "../components/common/HoverCard";
import AnimatedButton from "../components/common/AnimatedButton";
import axiosInstance, { API_ENDPOINTS } from "../config/api";
import learningPathService from "../services/learningPathService";

const LearningPathDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pathData, setPathData] = useState(null);
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedChapter, setExpandedChapter] = useState(null);
  const [chapterProgress, setChapterProgress] = useState({});
  const [startingChapter, setStartingChapter] = useState(null);
  const [completingChapter, setCompletingChapter] = useState(null);

  useEffect(() => {
    fetchPathDetails();
  }, [id]);

  const fetchPathDetails = async () => {
    try {
      const [pathResponse, chaptersResponse] = await Promise.all([
        axiosInstance.get(API_ENDPOINTS.COURSES.PATH_DETAIL(id)),
        axiosInstance.get(API_ENDPOINTS.CHAPTERS.LIST(id)),
      ]);
      setPathData(pathResponse.data);
      setChapters(
        chaptersResponse.data.chapters || chaptersResponse.data || []
      );
    } catch (error) {
      console.error("Error fetching path details:", error);
      // Mock data for demo
      setPathData({
        id: parseInt(id),
        title: "Beginner English",
        description:
          "Start your English learning journey with foundational concepts and basic vocabulary.",
        level: "Beginner",
        duration: "8 weeks",
        totalChapters: 10,
        progress: 30,
        enrolled: true,
        icon: "🎯",
        objectives: [
          "Master basic grammar and sentence structures",
          "Build a vocabulary of 500+ common words",
          "Hold simple conversations",
          "Understand basic written English",
        ],
      });
      setChapters([
        {
          id: 1,
          title: "Introduction to English",
          description: "Get started with English basics and greetings",
          lessons: 5,
          duration: "45 min",
          completed: true,
          locked: false,
          activities: [
            {
              id: 1,
              title: "Basic Greetings",
              type: "Vocabulary",
              completed: true,
            },
            {
              id: 2,
              title: "Self Introduction",
              type: "Speaking",
              completed: true,
            },
            {
              id: 3,
              title: "Common Phrases",
              type: "Reading",
              completed: true,
            },
          ],
        },
        {
          id: 2,
          title: "Numbers and Colors",
          description: "Learn to count and describe colors in English",
          lessons: 6,
          duration: "60 min",
          completed: true,
          locked: false,
          activities: [
            {
              id: 4,
              title: "Numbers 1-100",
              type: "Vocabulary",
              completed: true,
            },
            { id: 5, title: "Color Names", type: "Quiz", completed: true },
          ],
        },
        {
          id: 3,
          title: "Family and Relationships",
          description: "Vocabulary and phrases about family members",
          lessons: 7,
          duration: "70 min",
          completed: false,
          locked: false,
          inProgress: true,
          activities: [
            {
              id: 6,
              title: "Family Members",
              type: "Vocabulary",
              completed: true,
            },
            {
              id: 7,
              title: "Describing Relationships",
              type: "Grammar",
              completed: false,
            },
            {
              id: 8,
              title: "Family Tree Activity",
              type: "Practice",
              completed: false,
            },
          ],
        },
        {
          id: 4,
          title: "Daily Routines",
          description: "Learn to talk about your daily activities",
          lessons: 8,
          duration: "80 min",
          completed: false,
          locked: true,
          activities: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleChapterExpand = (chapterId) => {
    setExpandedChapter(expandedChapter === chapterId ? null : chapterId);
  };

  const handleStartChapter = async (chapterId) => {
    try {
      setStartingChapter(chapterId);
      const response = await learningPathService.startChapter(chapterId);
      
      if (response.success) {
        // Update chapter status
        setChapters(prevChapters =>
          prevChapters.map(ch =>
            ch.id === chapterId ? { ...ch, inProgress: true } : ch
          )
        );
        // Reload progress
        await fetchPathDetails();
      }
    } catch (error) {
      console.error('Error starting chapter:', error);
    } finally {
      setStartingChapter(null);
    }
  };

  const handleCompleteChapter = async (chapterId) => {
    try {
      setCompletingChapter(chapterId);
      const response = await learningPathService.completeChapter(chapterId, {
        completion_time: 0, // Could track actual time
        score: null,
        notes: ''
      });
      
      if (response.success) {
        // Update chapter status
        setChapters(prevChapters =>
          prevChapters.map(ch =>
            ch.id === chapterId ? { ...ch, completed: true, inProgress: false } : ch
          )
        );
        // Reload to update overall progress
        await fetchPathDetails();
      }
    } catch (error) {
      console.error('Error completing chapter:', error);
    } finally {
      setCompletingChapter(null);
    }
  };

  const handleStartActivity = (activityId) => {
    navigate(`/activities/${activityId}`);
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case "Vocabulary":
        return <MenuBook />;
      case "Quiz":
        return <Quiz />;
      case "Grammar":
        return <School />;
      default:
        return <PlayArrow />;
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

  if (!pathData) {
    return (
      <PageTransition>
        <Box sx={{ textAlign: "center", py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            Learning path not found
          </Typography>
          <Button
            startIcon={<ArrowBack />}
            onClick={() => navigate("/learning-paths")}
            sx={{ mt: 2 }}
          >
            Back to Learning Paths
          </Button>
        </Box>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <Box>
        {/* Back Button */}
        <IconButton onClick={() => navigate("/learning-paths")} sx={{ mb: 2 }}>
          <ArrowBack />
        </IconButton>

        {/* Header */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={8}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}
              >
                <Box sx={{ fontSize: "4rem" }}>{pathData.icon}</Box>
                <Box>
                  <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
                    {pathData.title}
                  </GradientText>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Chip label={pathData.level} color="success" />
                    {pathData.enrolled && (
                      <Chip
                        label="Enrolled"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                  </Box>
                </Box>
              </Box>

              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                {pathData.description}
              </Typography>

              {/* Stats */}
              <Box sx={{ display: "flex", gap: 4, mb: 3 }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <School color="primary" />
                  <Typography variant="body2">
                    {pathData.totalChapters} Chapters
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <AccessTime color="primary" />
                  <Typography variant="body2">{pathData.duration}</Typography>
                </Box>
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <TrendingUp color="primary" />
                  <Typography variant="body2">
                    {pathData.progress}% Complete
                  </Typography>
                </Box>
              </Box>

              {/* Progress Bar */}
              {pathData.enrolled && (
                <Box sx={{ mb: 3 }}>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2" fontWeight={600}>
                      Overall Progress
                    </Typography>
                    <Typography
                      variant="body2"
                      color="primary.main"
                      fontWeight={700}
                    >
                      {pathData.progress}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={pathData.progress}
                    sx={{ height: 10, borderRadius: 5 }}
                  />
                </Box>
              )}
            </motion.div>
          </Grid>

          {/* Sidebar */}
          <Grid item xs={12} md={4}>
            <HoverCard>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Learning Objectives
                </Typography>
                <List dense>
                  {pathData.objectives?.map((objective, index) => (
                    <ListItem key={index} disablePadding>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckCircle color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={objective}
                        primaryTypographyProps={{ variant: "body2" }}
                      />
                    </ListItem>
                  ))}
                </List>
                {!pathData.enrolled && (
                  <AnimatedButton fullWidth variant="contained" sx={{ mt: 2 }}>
                    Enroll in Path
                  </AnimatedButton>
                )}
              </CardContent>
            </HoverCard>
          </Grid>
        </Grid>

        {/* Chapters */}
        <Box>
          <Typography variant="h5" fontWeight={700} gutterBottom sx={{ mb: 3 }}>
            Chapters
          </Typography>

          {chapters.map((chapter, index) => (
            <motion.div
              key={chapter.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Accordion
                expanded={expandedChapter === chapter.id}
                onChange={() => handleChapterExpand(chapter.id)}
                disabled={chapter.locked}
                sx={{ mb: 2, borderRadius: 2, "&:before": { display: "none" } }}
              >
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      width: "100%",
                      gap: 2,
                    }}
                  >
                    <Box
                      sx={{
                        minWidth: 40,
                        height: 40,
                        borderRadius: "50%",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        bgcolor: chapter.completed
                          ? "success.main"
                          : chapter.inProgress
                          ? "primary.main"
                          : chapter.locked
                          ? "action.disabledBackground"
                          : "grey.300",
                        color: "white",
                      }}
                    >
                      {chapter.locked ? (
                        <Lock fontSize="small" />
                      ) : chapter.completed ? (
                        <CheckCircle fontSize="small" />
                      ) : (
                        <Typography variant="body2" fontWeight={700}>
                          {index + 1}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" fontWeight={600}>
                        {chapter.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {chapter.lessons} Lessons • {chapter.duration}
                      </Typography>
                    </Box>
                    {chapter.inProgress && (
                      <Chip label="In Progress" size="small" color="primary" />
                    )}
                    {chapter.completed && (
                      <Chip label="Completed" size="small" color="success" />
                    )}
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
                  
                  {/* Chapter Progress Actions */}
                  <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
                    {!chapter.completed && !chapter.inProgress && (
                      <Button
                        variant="contained"
                        startIcon={<PlayArrow />}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStartChapter(chapter.id);
                        }}
                        disabled={startingChapter === chapter.id}
                        size="small"
                      >
                        {startingChapter === chapter.id ? 'Starting...' : 'Start Chapter'}
                      </Button>
                    )}
                    {chapter.inProgress && !chapter.completed && (
                      <Button
                        variant="contained"
                        color="success"
                        startIcon={<CheckCircle />}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCompleteChapter(chapter.id);
                        }}
                        disabled={completingChapter === chapter.id}
                        size="small"
                      >
                        {completingChapter === chapter.id ? 'Completing...' : 'Mark as Complete'}
                      </Button>
                    )}
                    {chapter.completed && (
                      <Chip 
                        icon={<CheckCircle />} 
                        label="Chapter Completed" 
                        color="success" 
                        size="small" 
                      />
                    )}
                  </Box>
                  
                  <Divider sx={{ mb: 2 }} />
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                    Activities
                  </Typography>
                  <List>
                    {chapter.activities?.map((activity) => (
                      <ListItem key={activity.id} disablePadding>
                        <ListItemButton
                          onClick={() => handleStartActivity(activity.id)}
                          sx={{ borderRadius: 1, mb: 0.5 }}
                        >
                          <ListItemIcon>
                            {getActivityIcon(activity.type)}
                          </ListItemIcon>
                          <ListItemText
                            primary={activity.title}
                            secondary={activity.type}
                            primaryTypographyProps={{ fontWeight: 500 }}
                          />
                          {activity.completed ? (
                            <CheckCircle color="success" />
                          ) : (
                            <PlayArrow color="primary" />
                          )}
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </motion.div>
          ))}
        </Box>
      </Box>
    </PageTransition>
  );
};

export default LearningPathDetail;
