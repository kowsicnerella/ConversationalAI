import { useState, useEffect } from "react";
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Avatar,
  CircularProgress,
  Alert,
} from "@mui/material";
import { EmojiEvents, TrendingUp, School, Star } from "@mui/icons-material";
import { motion } from "framer-motion";
import axiosInstance, { API_ENDPOINTS } from "../config/api";
import GradientText from "../components/common/GradientText";
import PageTransition from "../components/common/PageTransition";

const skillIcons = {
  vocabulary: "📚",
  grammar: "✏️",
  reading: "📖",
  writing: "✍️",
  listening: "👂",
  speaking: "🗣️",
};

const MasteryDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [progressData, setProgressData] = useState(null);

  useEffect(() => {
    fetchProgressSnapshot();
  }, []);

  const fetchProgressSnapshot = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(
        API_ENDPOINTS.ONBOARDING.PROGRESS_SNAPSHOT
      );
      setProgressData(response.data.progress_snapshot);
    } catch (err) {
      console.error("Error fetching progress:", err);
      setError("Failed to load progress data");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  const masteryData = progressData?.mastery || {};
  const skillBreakdown = masteryData.skill_breakdown || {};
  const overallMastery = masteryData.overall_percentage || 0;
  const stats = progressData?.statistics || {};
  const nextMilestone = masteryData.next_milestone;

  return (
    <PageTransition>
      <Box
        sx={{
          minHeight: "100vh",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          py: 4,
        }}
      >
        <Container maxWidth="lg">
          {/* Header */}
          <Box textAlign="center" mb={4}>
            <GradientText variant="h3" sx={{ mb: 2, fontWeight: 700 }}>
              Your English Mastery Journey
            </GradientText>
            <Typography variant="h5" color="white" sx={{ opacity: 0.9 }}>
              మీ ఇంగ్లీష్ ప్రావీణ్య ప్రయాణం
            </Typography>
          </Box>

          {/* Overall Mastery Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card
              sx={{
                mb: 4,
                borderRadius: 3,
                background: "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)",
              }}
            >
              <CardContent sx={{ textAlign: "center", py: 4 }}>
                <EmojiEvents sx={{ fontSize: 80, color: "white", mb: 2 }} />
                <Typography
                  variant="h2"
                  fontWeight={700}
                  color="white"
                  gutterBottom
                >
                  {overallMastery.toFixed(1)}%
                </Typography>
                <Typography variant="h5" color="white" sx={{ opacity: 0.9 }}>
                  Overall English Mastery
                </Typography>
                <Typography
                  variant="h6"
                  color="white"
                  sx={{ opacity: 0.8, mt: 1 }}
                >
                  మొత్తం ఇంగ్లీష్ ప్రావీణ్యత
                </Typography>

                {nextMilestone && (
                  <Box mt={3}>
                    <Chip
                      label={`Next: ${nextMilestone.title} (${nextMilestone.target}%)`}
                      sx={{
                        bgcolor: "rgba(255, 255, 255, 0.2)",
                        color: "white",
                        fontSize: "1rem",
                        py: 2,
                        px: 1,
                      }}
                    />
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Statistics Grid */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Card sx={{ borderRadius: 3, height: "100%" }}>
                  <CardContent sx={{ textAlign: "center" }}>
                    <School sx={{ fontSize: 40, color: "#667eea", mb: 1 }} />
                    <Typography variant="h4" fontWeight={700}>
                      {stats.completed_lessons || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Lessons Completed
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card sx={{ borderRadius: 3, height: "100%" }}>
                  <CardContent sx={{ textAlign: "center" }}>
                    <Box sx={{ fontSize: 40, mb: 1 }}>🔥</Box>
                    <Typography variant="h4" fontWeight={700}>
                      {stats.current_streak || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Day Streak
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <Card sx={{ borderRadius: 3, height: "100%" }}>
                  <CardContent sx={{ textAlign: "center" }}>
                    <Star sx={{ fontSize: 40, color: "#FFD700", mb: 1 }} />
                    <Typography variant="h4" fontWeight={700}>
                      {stats.total_points || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Points
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <Card sx={{ borderRadius: 3, height: "100%" }}>
                  <CardContent sx={{ textAlign: "center" }}>
                    <TrendingUp
                      sx={{ fontSize: 40, color: "#4CAF50", mb: 1 }}
                    />
                    <Typography variant="h4" fontWeight={700}>
                      {stats.proficiency_level?.toUpperCase() || "BEGINNER"}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Current Level
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>

          {/* Skill Breakdown */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card sx={{ mb: 4, borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h5" fontWeight={600} gutterBottom>
                  Skill Mastery Breakdown
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  నైపుణ్య ప్రావీణ్య విభజన
                </Typography>

                <Box mt={3}>
                  {Object.entries(skillBreakdown)
                    .filter(([skill]) => skill !== "overall")
                    .map(([skill, percentage], index) => (
                      <Box key={skill} mb={3}>
                        <Box
                          display="flex"
                          justifyContent="space-between"
                          alignItems="center"
                          mb={1}
                        >
                          <Box display="flex" alignItems="center">
                            <Avatar
                              sx={{
                                width: 32,
                                height: 32,
                                mr: 1,
                                bgcolor: "transparent",
                                fontSize: "1.2rem",
                              }}
                            >
                              {skillIcons[skill] || "📝"}
                            </Avatar>
                            <Typography
                              variant="body1"
                              fontWeight={600}
                              sx={{ textTransform: "capitalize" }}
                            >
                              {skill}
                            </Typography>
                          </Box>
                          <Typography variant="body1" fontWeight={600}>
                            {percentage?.toFixed(1) || 0}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={percentage || 0}
                          sx={{
                            height: 10,
                            borderRadius: 5,
                            bgcolor: "rgba(0, 0, 0, 0.1)",
                            "& .MuiLinearProgress-bar": {
                              background:
                                percentage >= 85
                                  ? "linear-gradient(90deg, #4CAF50, #8BC34A)"
                                  : percentage >= 60
                                  ? "linear-gradient(90deg, #2196F3, #03A9F4)"
                                  : "linear-gradient(90deg, #FF9800, #FFC107)",
                              borderRadius: 5,
                            },
                          }}
                        />
                      </Box>
                    ))}
                </Box>
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Achievements */}
          {progressData?.recent_achievements &&
            progressData.recent_achievements.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Card sx={{ borderRadius: 3 }}>
                  <CardContent>
                    <Typography variant="h5" fontWeight={600} gutterBottom>
                      Recent Achievements 🏆
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      gutterBottom
                      sx={{ mb: 3 }}
                    >
                      ఇటీవలి విజయాలు
                    </Typography>

                    <Grid container spacing={2}>
                      {progressData.recent_achievements.map(
                        (achievement, index) => (
                          <Grid item xs={12} sm={6} md={4} key={index}>
                            <Card
                              sx={{
                                background: "rgba(102, 126, 234, 0.1)",
                                borderRadius: 2,
                              }}
                            >
                              <CardContent sx={{ textAlign: "center" }}>
                                <Box sx={{ fontSize: 40, mb: 1 }}>
                                  {achievement.icon || "🎉"}
                                </Box>
                                <Typography variant="h6" fontWeight={600}>
                                  {achievement.title}
                                </Typography>
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                  sx={{ mt: 1 }}
                                >
                                  {achievement.telugu_title}
                                </Typography>
                                {achievement.points_awarded > 0 && (
                                  <Chip
                                    label={`+${achievement.points_awarded} pts`}
                                    size="small"
                                    color="primary"
                                    sx={{ mt: 1 }}
                                  />
                                )}
                              </CardContent>
                            </Card>
                          </Grid>
                        )
                      )}
                    </Grid>
                  </CardContent>
                </Card>
              </motion.div>
            )}
        </Container>
      </Box>
    </PageTransition>
  );
};

export default MasteryDashboard;
