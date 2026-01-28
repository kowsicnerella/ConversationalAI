import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  Stack,
  CircularProgress,
  Container,
  useTheme,
  useMediaQuery,
  alpha,
} from "@mui/material";
import {
  Psychology,
  Timer,
  PlayArrow,
  CheckCircle,
  Star,
  Refresh,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import AnimatedButton from "../components/common/AnimatedButton";
import AIGeneratingLoader from "../components/common/AIGeneratingLoader";
import AIGeneratedBadge from "../components/common/AIGeneratedBadge";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const Activities = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

  // State
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [orchestratorMessage, setOrchestratorMessage] = useState("");
  const [currentNode, setCurrentNode] = useState(null);

  const fetchNextActivity = useCallback(async () => {
    try {
      setLoading(true);
      // Call AI-personalized learning path orchestrator
      const response = await axiosInstance.post(API_ENDPOINTS.LEARNING_PATH.NEXT_ACTIVITY);
      
      if (response.data.success) {
        const { activity, reasoning, node_info, message } = response.data.data;
        
        // Debug: Log full orchestrator response
        console.log("🔍 Orchestrator Response Debug:", {
          activity,
          node_info,
          message,
          reasoning
        });
        console.log("📊 Available fields in node_info:", Object.keys(node_info || {}));
        console.log("📊 Available fields in activity:", Object.keys(activity || {}));
        
        // Set the personalized activity
        if (activity) {
          // Try to find node_id from various possible sources
          const nodeId = node_info?.node_id 
            || node_info?.id 
            || node_info?.nodeId
            || activity?.node_id
            || activity?.nodeId
            || activity?.learning_node_id;
          
          // Transform backend activity format to frontend format
          const transformedActivity = {
            id: activity.id || `activity_${Date.now()}`,
            type: activity.activity_type || activity.type,
            title: activity.title,
            description: activity.instructions || activity.description,
            difficulty: node_info?.level_name?.toLowerCase() || 'beginner',
            estimatedTime: activity.estimated_time || 15,
            completed: false,
            progress: 0,
            // Add activity-specific data
            content: activity.content,
            questions: activity.questions,
            flashcards: activity.flashcards,
            prompt: activity.prompt,
            // Add metadata
            nodeId: nodeId,
            nodeName: node_info?.node_name,
            levelName: node_info?.level_name,
            tags: node_info?.focus_areas || [],
            // Store full node_info for debugging
            _node_info: node_info,
          };
          
          console.log("✅ Transformed Activity with nodeId:", { nodeId, transformedActivity });
          
          setActivities([transformedActivity]);
          setOrchestratorMessage(message || reasoning);
          setCurrentNode(node_info);
        } else {
          // No activity available
          setActivities([]);
          setOrchestratorMessage(message || "No activities available at this time.");
        }
      }
    } catch (error) {
      console.error("Error fetching next activity:", error);
      setOrchestratorMessage("Unable to load personalized activity. Please try again.");
      setActivities([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNextActivity();
  }, [fetchNextActivity]);

  // Display all activities (typically just one personalized activity)
  const filteredActivities = activities;

  const handleActivityClick = (activity) => {
    // Navigate to specific activity type with activity data
    const activityPath = `/activities/${activity.type}/${activity.id}`;
    
    // Store activity data in sessionStorage for the activity page to use
    sessionStorage.setItem('currentActivity', JSON.stringify(activity));
    
    // Navigate based on activity type
    switch (activity.type) {
      case "flashcard":
      case "flashcards":
        navigate(`/activities/flashcards/${activity.id}`, { state: { activity } });
        break;
      case "quiz":
        navigate(`/activities/quiz/${activity.id}`, { state: { activity } });
        break;
      case "reading":
        navigate(`/activities/reading/${activity.id}`, { state: { activity } });
        break;
      case "writing":
        navigate(`/activities/writing/${activity.id}`, { state: { activity } });
        break;
      case "listening":
        navigate(`/activities/listening/${activity.id}`, { state: { activity } });
        break;
      case "speaking":
        navigate(`/activities/speaking/${activity.id}`, { state: { activity } });
        break;
      default:
        navigate(activityPath, { state: { activity } });
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

  // Get color for activity - use activity.color if available, otherwise generate from theme
  const getActivityColor = (activity) => {
    if (activity?.color) return activity.color;
    
    // Generate color based on activity type
    switch (activity?.type) {
      case "flashcard":
        return theme.palette.info.main;
      case "quiz":
        return theme.palette.success.main;
      case "reading":
        return theme.palette.warning.main;
      default:
        return theme.palette.primary.main;
    }
  };

  const ActivityCard = ({ activity }) => {
    const IconComponent = activity.icon || Psychology;
    const activityColor = getActivityColor(activity);

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
                    activityColor,
                    0.1
                  )} 0%, ${alpha(theme.palette.background.paper, 0.9)} 100%)`
                : theme.palette.background.paper,
            backdropFilter: "blur(10px)",
            border: `1px solid ${alpha(activityColor, 0.2)}`,
            "&:hover": {
              boxShadow: `0 12px 40px ${alpha(activityColor, 0.3)}`,
              border: `1px solid ${alpha(activityColor, 0.5)}`,
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
                  activityColor
                } 0%, ${alpha(activityColor, 0.5)} 100%)`,
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
                    activityColor,
                    0.2
                  )}, ${alpha(activityColor, 0.1)})`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <IconComponent sx={{ color: activityColor, fontSize: 28 }} />
              </Box>
              <Chip
                label={getActivityTypeLabel(activity.type)}
                size="small"
                sx={{
                  fontWeight: 600,
                  background: alpha(activityColor, 0.1),
                  color: activityColor,
                }}
              />
            </Stack>

            {/* Title with AI badge */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  color: theme.palette.text.primary,
                  flex: 1,
                }}
              >
                {activity.title}
              </Typography>
              <AIGeneratedBadge size="small" />
            </Box>

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
                  ? `linear-gradient(135deg, ${activityColor}, ${alpha(
                      activityColor,
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

  // PropTypes validation for ActivityCard
  ActivityCard.propTypes = {
    activity: PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      type: PropTypes.string,
      title: PropTypes.string,
      description: PropTypes.string,
      difficulty: PropTypes.string,
      estimatedTime: PropTypes.number,
      completed: PropTypes.bool,
      progress: PropTypes.number,
      score: PropTypes.number,
      wordsCount: PropTypes.number,
      questionsCount: PropTypes.number,
      tags: PropTypes.arrayOf(PropTypes.string),
      icon: PropTypes.elementType,
      color: PropTypes.string,
    }).isRequired,
  };

  if (loading) {
    return (
      <PageTransition>
        <Container maxWidth="xl">
          <Box mb={4}>
            <GradientText
              variant={isMobile ? "h4" : "h3"}
              sx={{ mb: 2, fontWeight: 700 }}
            >
              AI-Personalized Learning
            </GradientText>
          </Box>
          <AIGeneratingLoader 
            message="AI is selecting your next optimal activity..."
            subMessage="Analyzing your progress and learning patterns"
          />
        </Container>
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
            AI-Personalized Learning
          </GradientText>
          <Typography variant="body1" color="text.secondary">
            Your next activity is intelligently selected based on your progress and goals
          </Typography>
        </Box>

        {/* Orchestrator Message Banner */}
        {orchestratorMessage && (
          <Box
            mb={3}
            sx={{
              p: 3,
              borderRadius: 3,
              background: `linear-gradient(135deg, ${alpha(
                theme.palette.primary.main,
                0.1
              )}, ${alpha(theme.palette.secondary.main, 0.1)})`,
              border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
              display: "flex",
              alignItems: "center",
              gap: 2,
            }}
          >
            <Psychology
              sx={{
                fontSize: 40,
                color: theme.palette.primary.main,
              }}
            />
            <Box>
              <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 700, mb: 0.5 }}>
                AI Learning Assistant
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {orchestratorMessage}
              </Typography>
            </Box>
          </Box>
        )}

        {/* Learning Path Info */}
        {currentNode && (
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
            <Stack direction="row" spacing={2} alignItems="center">
              <Chip
                label={currentNode.level_name || "Learning"}
                color="primary"
                sx={{ fontWeight: 600 }}
              />
              <Typography variant="body2" color="text.secondary">
                {currentNode.node_name || "Current Focus"}
              </Typography>
              {currentNode.focus_areas && currentNode.focus_areas.length > 0 && (
                <>
                  <Typography variant="body2" color="text.secondary">•</Typography>
                  <Stack direction="row" spacing={0.5} flexWrap="wrap">
                    {currentNode.focus_areas.map((area, index) => (
                      <Chip
                        key={index}
                        label={area}
                        size="small"
                        variant="outlined"
                        sx={{ fontSize: "0.75rem" }}
                      />
                    ))}
                  </Stack>
                </>
              )}
            </Stack>
          </Box>
        )}

        {/* Personalized Activity Display */}
        {filteredActivities.length > 0 ? (
          <Grid container spacing={3} justifyContent="center">
            {filteredActivities.map((activity) => (
              <Grid
                item
                xs={12}
                sm={10}
                md={8}
                lg={6}
                key={activity.id}
              >
                <ActivityCard activity={activity} />
              </Grid>
            ))}
          </Grid>
        ) : (
          /* Empty state */
          <Box
            textAlign="center"
            py={8}
            sx={{
              background: alpha(theme.palette.background.paper, 0.5),
              borderRadius: 3,
              border: `1px dashed ${theme.palette.divider}`,
            }}
          >
            <Psychology sx={{ fontSize: 80, color: theme.palette.divider, mb: 2 }} />
            <Typography variant="h6" color="text.secondary" mb={1}>
              No activity available
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              The AI couldn&apos;t generate an activity at this time. Please try again.
            </Typography>
            <AnimatedButton
              variant="contained"
              startIcon={<Refresh />}
              onClick={fetchNextActivity}
            >
              Get Next Activity
            </AnimatedButton>
          </Box>
        )}
        
        {/* Refresh Activity Button */}
        {filteredActivities.length > 0 && (
          <Box textAlign="center" mt={4}>
            <AnimatedButton
              variant="outlined"
              startIcon={<Refresh />}
              onClick={fetchNextActivity}
              disabled={loading}
            >
              Get Different Activity
            </AnimatedButton>
          </Box>
        )}
      </Container>
    </PageTransition>
  );
};

export default Activities;
