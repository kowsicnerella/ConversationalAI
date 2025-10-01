import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Container,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Button,
  Chip,
  Avatar,
  useTheme,
  useMediaQuery,
  Skeleton,
  Stack,
  Divider,
} from "@mui/material";
import {
  PlayArrow,
  CheckCircle,
  School,
  Quiz,
  Language,
  MenuBook,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { coursesAPI } from "../services/api";
import { toast } from "react-hot-toast";

// Helper functions moved outside component to avoid re-creation
const getIconForPath = (category) => {
  switch (category) {
    case "vocabulary":
      return <Quiz />;
    case "grammar":
      return <MenuBook />;
    case "conversation":
      return <School />;
    default:
      return <Language />;
  }
};

const getColorForDifficulty = (difficulty, theme) => {
  switch (difficulty?.toLowerCase()) {
    case "beginner":
      return theme.palette.success.main;
    case "intermediate":
      return theme.palette.warning.main;
    case "advanced":
      return theme.palette.error.main;
    default:
      return theme.palette.primary.main;
  }
};

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

const LearningPathsPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const [learningPaths, setLearningPaths] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLearningPaths = async () => {
      try {
        setLoading(true);
        const response = await coursesAPI.getLearningPaths();
        const paths = response.data.learning_paths || [];

        // Map backend data to frontend format
        const mappedPaths = paths.map((path) => ({
          id: path.id,
          title: path.title,
          description: path.description,
          progress: path.completion_percentage || 0,
          totalLessons: path.activity_count || 0,
          completedLessons: Math.round(
            ((path.completion_percentage || 0) / 100) *
              (path.activity_count || 0)
          ),
          difficulty: path.difficulty_level || "Beginner",
          estimatedTime: path.estimated_hours
            ? `${path.estimated_hours} hours`
            : "4-6 weeks",
          icon: getIconForPath(path.category),
          color: getColorForDifficulty(path.difficulty_level, theme),
          isActive: path.is_enrolled || false,
        }));

        setLearningPaths(mappedPaths);
      } catch (error) {
        console.error("Failed to fetch learning paths:", error);
        toast.error("Failed to load learning paths");

        // Fallback to mock data
        setLearningPaths([
          {
            id: 1,
            title: "Telugu Fundamentals",
            description:
              "Master the basics of Telugu language with AI-guided lessons",
            progress: 0,
            totalLessons: 24,
            completedLessons: 0,
            difficulty: "Beginner",
            estimatedTime: "6-8 weeks",
            icon: <Language />,
            color: theme.palette.primary.main,
            isActive: false,
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchLearningPaths();
  }, [theme]);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3, md: 4 } }}>
        <Grid container spacing={{ xs: 2, sm: 3 }}>
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card
                className="hover-lift"
                sx={{
                  borderRadius: { xs: 2, sm: 3 },
                  overflow: "hidden",
                }}
              >
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                  <Stack spacing={2}>
                    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                      <Skeleton variant="circular" width={48} height={48} />
                      <Box sx={{ flex: 1 }}>
                        <Skeleton variant="text" width="80%" height={32} />
                        <Skeleton variant="text" width="60%" />
                      </Box>
                    </Box>
                    <Skeleton variant="text" height={20} />
                    <Skeleton variant="text" height={20} width="90%" />
                    <Skeleton
                      variant="rectangular"
                      height={8}
                      sx={{ borderRadius: 4 }}
                    />
                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Skeleton
                        variant="rectangular"
                        width={80}
                        height={24}
                        sx={{ borderRadius: 2 }}
                      />
                      <Skeleton
                        variant="rectangular"
                        width={100}
                        height={24}
                        sx={{ borderRadius: 2 }}
                      />
                    </Box>
                    <Skeleton
                      variant="rectangular"
                      height={40}
                      sx={{ borderRadius: 2 }}
                    />
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3 } }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Box
          className="fade-in"
          sx={{
            mb: { xs: 2, sm: 3 },
            textAlign: { xs: "center", sm: "left" },
          }}
        >
          <Typography
            variant={isMobile ? "h6" : "h5"}
            sx={{
              mb: 1,
              fontWeight: 700,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              letterSpacing: "-0.01em",
            }}
          >
            Learning Paths
          </Typography>
          <Typography
            variant={isMobile ? "body2" : "body1"}
            color="text.secondary"
            sx={{
              fontWeight: 400,
              maxWidth: { sm: "80%", md: "60%" },
              mx: { xs: "auto", sm: 0 },
            }}
          >
            Choose your learning journey and track your progress
          </Typography>
        </Box>

        <Grid
          container
          spacing={{ xs: 2, sm: 2.5, md: 3 }}
          sx={{ alignItems: "stretch" }}
        >
          {learningPaths.map((path, index) => (
            <Grid item xs={12} sm={6} md={4} key={path.id}>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.08 }}
                whileHover={{ y: -8, scale: 1.02 }}
                style={{ height: "100%" }}
              >
                <Card
                  className="hover-lift"
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    background: path.isActive
                      ? `linear-gradient(135deg, ${path.color}15, ${path.color}05)`
                      : theme.palette.mode === "dark"
                      ? "rgba(30, 41, 59, 0.6)"
                      : "rgba(255, 255, 255, 0.9)",
                    backdropFilter: "blur(20px)",
                    border: path.isActive
                      ? `2px solid ${path.color}60`
                      : `1px solid ${theme.palette.divider}`,
                    borderRadius: { xs: 2, sm: 3 },
                    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    overflow: "hidden",
                    position: "relative",
                    "&::before": path.isActive
                      ? {
                          content: '""',
                          position: "absolute",
                          top: 0,
                          left: 0,
                          right: 0,
                          height: "4px",
                          background: `linear-gradient(90deg, ${path.color}, ${theme.palette.secondary.main})`,
                        }
                      : {},
                    "&:hover": {
                      boxShadow: path.isActive
                        ? `0 20px 40px ${path.color}40`
                        : theme.shadows[10],
                      borderColor: path.color,
                    },
                  }}
                >
                  <CardContent
                    sx={{
                      p: { xs: 1.75, sm: 2 },
                      flex: 1,
                      display: "flex",
                      flexDirection: "column",
                      gap: { xs: 1.5, sm: 1.75 },
                      "&:last-child": { pb: { xs: 1.75, sm: 2 } },
                    }}
                  >
                    {/* Header Section */}
                    <Stack spacing={1.25}>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 1.25,
                        }}
                      >
                        <Avatar
                          className="hover-scale"
                          sx={{
                            background: `linear-gradient(135deg, ${path.color}30, ${path.color}15)`,
                            color: path.color,
                            width: { xs: 36, sm: 40 },
                            height: { xs: 36, sm: 40 },
                            boxShadow: `0 3px 10px ${path.color}30`,
                            border: `2px solid ${path.color}40`,
                            "& svg": { fontSize: "1.25rem" },
                          }}
                        >
                          {path.icon}
                        </Avatar>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Stack
                            direction="row"
                            alignItems="center"
                            spacing={0.75}
                            flexWrap="wrap"
                          >
                            <Typography
                              variant={isMobile ? "body1" : "subtitle1"}
                              sx={{
                                fontWeight: 600,
                                lineHeight: 1.3,
                                wordBreak: "break-word",
                                fontSize: { xs: "0.9375rem", sm: "1rem" },
                              }}
                            >
                              {path.title}
                            </Typography>
                            {path.isActive && (
                              <Chip
                                label="Active"
                                size="small"
                                color="primary"
                                sx={{
                                  fontWeight: 600,
                                  fontSize: "0.625rem",
                                  height: 18,
                                  "& .MuiChip-label": { px: 0.75 },
                                }}
                              />
                            )}
                          </Stack>
                        </Box>
                      </Box>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{
                          lineHeight: 1.5,
                          fontSize: { xs: "0.813rem", sm: "0.813rem" },
                          display: "-webkit-box",
                          WebkitLineClamp: 3,
                          WebkitBoxOrient: "vertical",
                          overflow: "hidden",
                        }}
                      >
                        {path.description}
                      </Typography>
                    </Stack>

                    <Divider sx={{ opacity: 0.5 }} />

                    {/* Progress Section */}
                    <Stack spacing={1.25}>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                      >
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{
                            fontSize: { xs: "0.75rem", sm: "0.8125rem" },
                            fontWeight: 500,
                          }}
                        >
                          {path.completedLessons}/{path.totalLessons} lessons
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 700,
                            color: path.color,
                            fontSize: { xs: "0.875rem", sm: "1rem" },
                          }}
                        >
                          {path.progress}%
                        </Typography>
                      </Stack>
                      <LinearProgress
                        variant="determinate"
                        value={path.progress}
                        sx={{
                          height: { xs: 6, sm: 8 },
                          borderRadius: 4,
                          backgroundColor:
                            theme.palette.mode === "dark"
                              ? "rgba(255,255,255,0.1)"
                              : `${path.color}15`,
                          boxShadow: `inset 0 1px 2px rgba(0,0,0,0.1)`,
                          "& .MuiLinearProgress-bar": {
                            background: `linear-gradient(90deg, ${path.color}, ${path.color}dd)`,
                            borderRadius: 4,
                            boxShadow: `0 2px 4px ${path.color}40`,
                          },
                        }}
                      />
                    </Stack>

                    {/* Tags Section */}
                    <Stack
                      direction="row"
                      spacing={1}
                      flexWrap="wrap"
                      useFlexGap
                    >
                      <Chip
                        label={path.difficulty}
                        size="small"
                        color={getDifficultyColor(path.difficulty)}
                        sx={{
                          fontSize: { xs: "0.7rem", sm: "0.75rem" },
                          fontWeight: 600,
                          height: { xs: 24, sm: 26 },
                        }}
                      />
                      <Chip
                        label={path.estimatedTime}
                        size="small"
                        variant="outlined"
                        sx={{
                          fontSize: { xs: "0.7rem", sm: "0.75rem" },
                          fontWeight: 500,
                          height: { xs: 24, sm: 26 },
                        }}
                      />
                    </Stack>

                    {/* Action Buttons */}
                    <Stack
                      direction={path.progress === 100 ? "row" : "column"}
                      spacing={1}
                      sx={{ mt: "auto" }}
                    >
                      <Button
                        variant={path.isActive ? "contained" : "outlined"}
                        startIcon={
                          path.progress > 0 ? <PlayArrow /> : <School />
                        }
                        fullWidth
                        size={isMobile ? "medium" : "large"}
                        className="hover-scale"
                        sx={{
                          borderRadius: { xs: 2, sm: 2.5 },
                          py: { xs: 1, sm: 1.25 },
                          fontWeight: 600,
                          fontSize: { xs: "0.875rem", sm: "0.9375rem" },
                          textTransform: "none",
                          ...(path.isActive && {
                            background: `linear-gradient(135deg, ${path.color}, ${theme.palette.secondary.main})`,
                            boxShadow: `0 4px 12px ${path.color}40`,
                            "&:hover": {
                              background: `linear-gradient(135deg, ${path.color}ee, ${theme.palette.secondary.main}ee)`,
                              transform: "translateY(-2px)",
                              boxShadow: `0 6px 20px ${path.color}50`,
                            },
                          }),
                        }}
                        disabled={!path.isActive && path.progress === 0}
                      >
                        {path.progress > 0
                          ? "Continue Learning"
                          : "Start Learning"}
                      </Button>
                      {path.progress === 100 && (
                        <Button
                          variant="outlined"
                          startIcon={<CheckCircle />}
                          color="success"
                          className="hover-scale"
                          sx={{
                            borderRadius: { xs: 2, sm: 2.5 },
                            py: { xs: 1, sm: 1.25 },
                            fontWeight: 600,
                            fontSize: { xs: "0.875rem", sm: "0.9375rem" },
                            textTransform: "none",
                            minWidth: { xs: "auto", sm: 120 },
                            borderWidth: 2,
                            "&:hover": {
                              borderWidth: 2,
                            },
                          }}
                        >
                          Review
                        </Button>
                      )}
                    </Stack>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      </motion.div>
    </Container>
  );
};

export default LearningPathsPage;
