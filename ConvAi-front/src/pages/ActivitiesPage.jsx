import {
  Box,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  useTheme,
  LinearProgress,
} from "@mui/material";
import {
  Quiz,
  Chat,
  MenuBook,
  Psychology,
  Translate,
  Mic,
  PlayArrow,
  CheckCircle,
  Star,
} from "@mui/icons-material";
import { motion } from "framer-motion";

const ActivitiesPage = () => {
  const theme = useTheme();

  const activities = [
    {
      id: 1,
      title: "AI Conversation Practice",
      description:
        "Practice speaking with our AI tutor in real-time conversations",
      type: "Speaking",
      difficulty: "Intermediate",
      duration: "15-20 min",
      completed: true,
      progress: 100,
      rating: 4.8,
      icon: <Chat />,
      color: theme.palette.primary.main,
      participants: 1250,
    },
    {
      id: 2,
      title: "Vocabulary Quiz",
      description: "Test your Telugu vocabulary with adaptive questions",
      type: "Vocabulary",
      difficulty: "Beginner",
      duration: "10-15 min",
      completed: false,
      progress: 65,
      rating: 4.6,
      icon: <Quiz />,
      color: theme.palette.secondary.main,
      participants: 980,
    },
    {
      id: 3,
      title: "Reading Comprehension",
      description: "Improve reading skills with interactive Telugu stories",
      type: "Reading",
      difficulty: "Intermediate",
      duration: "20-25 min",
      completed: false,
      progress: 30,
      rating: 4.7,
      icon: <MenuBook />,
      color: theme.palette.info.main,
      participants: 750,
    },
    {
      id: 4,
      title: "AI Writing Assistant",
      description: "Get help writing in Telugu with AI-powered suggestions",
      type: "Writing",
      difficulty: "Advanced",
      duration: "25-30 min",
      completed: false,
      progress: 0,
      rating: 4.5,
      icon: <Psychology />,
      color: theme.palette.success.main,
      participants: 650,
    },
    {
      id: 5,
      title: "Pronunciation Trainer",
      description: "Perfect your Telugu pronunciation with AI feedback",
      type: "Pronunciation",
      difficulty: "Beginner",
      duration: "10-15 min",
      completed: true,
      progress: 100,
      rating: 4.9,
      icon: <Mic />,
      color: theme.palette.warning.main,
      participants: 1100,
    },
    {
      id: 6,
      title: "Translation Challenge",
      description: "Translate sentences between Telugu and English",
      type: "Translation",
      difficulty: "Intermediate",
      duration: "15-20 min",
      completed: false,
      progress: 45,
      rating: 4.4,
      icon: <Translate />,
      color: theme.palette.error.main,
      participants: 820,
    },
  ];

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
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

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3 } }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box sx={{ mb: { xs: 3, sm: 4 }, textAlign: "center" }}>
          <Typography
            variant="h4"
            sx={{
              mb: 1,
              fontWeight: 700,
              background: "linear-gradient(45deg, #4f46e5, #06b6d4)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Learning Activities
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Choose from our AI-powered activities to enhance your language
            skills
          </Typography>
        </Box>

        <Grid
          container
          spacing={{ xs: 2, sm: 3 }}
          className="card-grid-container"
        >
          {activities.map((activity, index) => (
            <Grid
              item
              xs={12}
              sm={6}
              lg={4}
              key={activity.id}
              className="card-grid-item"
            >
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                whileHover={{ y: -4 }}
                className="card-flex-layout"
              >
                <Card
                  className="card-flex-layout"
                  sx={{
                    background: `linear-gradient(135deg, ${activity.color}08, ${activity.color}03)`,
                    border: `1px solid ${activity.color}20`,
                    borderRadius: 3,
                    transition: "all 0.3s ease",
                    "&:hover": {
                      boxShadow: theme.shadows[8],
                      borderColor: `${activity.color}40`,
                    },
                  }}
                >
                  <CardContent
                    className="card-content-flex"
                    sx={{ p: { xs: 2, sm: 3 } }}
                  >
                    <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                      <Avatar
                        sx={{
                          background: `${activity.color}20`,
                          color: activity.color,
                          mr: 2,
                          width: 48,
                          height: 48,
                        }}
                      >
                        {activity.icon}
                      </Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Typography
                          variant="h6"
                          sx={{ fontWeight: 600, mb: 0.5 }}
                        >
                          {activity.title}
                        </Typography>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 0.5,
                          }}
                        >
                          <Star
                            sx={{
                              fontSize: 16,
                              color: theme.palette.warning.main,
                            }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {activity.rating} ({activity.participants} learners)
                          </Typography>
                        </Box>
                      </Box>
                      {activity.completed && (
                        <CheckCircle
                          sx={{ color: theme.palette.success.main, ml: 1 }}
                        />
                      )}
                    </Box>

                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 2, lineHeight: 1.5 }}
                    >
                      {activity.description}
                    </Typography>

                    <Box
                      sx={{ display: "flex", gap: 1, mb: 2, flexWrap: "wrap" }}
                    >
                      <Chip
                        label={activity.type}
                        size="small"
                        variant="outlined"
                        sx={{
                          borderColor: activity.color,
                          color: activity.color,
                        }}
                      />
                      <Chip
                        label={activity.difficulty}
                        size="small"
                        color={getDifficultyColor(activity.difficulty)}
                        variant="outlined"
                      />
                      <Chip
                        label={activity.duration}
                        size="small"
                        variant="outlined"
                      />
                    </Box>

                    {activity.progress > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            mb: 0.5,
                          }}
                        >
                          <Typography variant="caption" color="text.secondary">
                            Progress
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{ fontWeight: 600 }}
                          >
                            {activity.progress}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={activity.progress}
                          sx={{
                            height: 6,
                            borderRadius: 3,
                            backgroundColor: `${activity.color}20`,
                            "& .MuiLinearProgress-bar": {
                              backgroundColor: activity.color,
                              borderRadius: 3,
                            },
                          }}
                        />
                      </Box>
                    )}
                  </CardContent>

                  <CardActions sx={{ p: { xs: 2, sm: 3 }, pt: 0 }}>
                    <Button
                      fullWidth
                      variant={activity.completed ? "outlined" : "contained"}
                      startIcon={
                        activity.completed ? <PlayArrow /> : <PlayArrow />
                      }
                      sx={{
                        borderRadius: 2,
                        py: 1,
                        ...(activity.completed
                          ? {
                              borderColor: activity.color,
                              color: activity.color,
                              "&:hover": {
                                backgroundColor: `${activity.color}10`,
                              },
                            }
                          : {
                              background: `linear-gradient(135deg, ${activity.color}, ${theme.palette.secondary.main})`,
                              "&:hover": {
                                background: `linear-gradient(135deg, ${activity.color}dd, ${theme.palette.secondary.main}dd)`,
                              },
                            }),
                      }}
                    >
                      {activity.completed
                        ? "Practice Again"
                        : activity.progress > 0
                        ? "Continue"
                        : "Start Activity"}
                    </Button>
                  </CardActions>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </motion.div>
    </Container>
  );
};

export default ActivitiesPage;
