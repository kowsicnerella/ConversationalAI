import { useState, useEffect, useCallback } from "react";
import {
  Box,
  Grid,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Avatar,
  Chip,
  Button,
  Alert,
} from "@mui/material";
import {
  LocalFireDepartment,
  EmojiEvents,
  AutoStories,
  School,
  AccessTime,
  ArrowForward,
  TrendingUp,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import StatCard from "../components/common/StatCard";
import HoverCard from "../components/common/HoverCard";
import PageTransition from "../components/common/PageTransition";
import { useAuth } from "../context/AuthContext";
import analyticsService from "../services/analyticsService";
import learningPathService from "../services/learningPathService";
import gamificationService from "../services/gamificationService";
import axiosInstance, { API_ENDPOINTS } from "../config/api";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [learningPaths, setLearningPaths] = useState([]);
  const [weeklyProgress, setWeeklyProgress] = useState([]);
  const [skillProgress, setSkillProgress] = useState([]);
  const [progressSnapshot, setProgressSnapshot] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setLoading(true);

      // Fetch multiple data sources in parallel
      const [analyticsData, pathsData, _statsData, snapshotData] =
        await Promise.all([
          analyticsService.getDashboardSummary().catch((err) => {
            console.error("Error fetching analytics:", err);
            return { data: null };
          }),
          learningPathService.getMyLearningPaths().catch((err) => {
            console.error("Error fetching learning paths:", err);
            return { learning_paths: [] };
          }),
          gamificationService.getStats(user?.id).catch((err) => {
            console.error("Error fetching gamification stats:", err);
            return { data: null };
          }),
          axiosInstance
            .get(API_ENDPOINTS.ONBOARDING.PROGRESS_SNAPSHOT)
            .catch((err) => {
              console.error("Error fetching progress snapshot:", err);
              return { data: { progress_snapshot: null } };
            }),
        ]);

      // Set dashboard data from analytics
      if (analyticsData?.data) {
        setDashboardData(analyticsData.data);

        // Extract weekly progress if available
        if (analyticsData.data.weekly_activity) {
          setWeeklyProgress(analyticsData.data.weekly_activity);
        }

        // Extract skill progress if available
        if (analyticsData.data.skill_breakdown) {
          setSkillProgress(analyticsData.data.skill_breakdown);
        }
      }

      // Set learning paths data
      if (pathsData?.learning_paths) {
        setLearningPaths(pathsData.learning_paths);
      }

      // Set progress snapshot
      if (snapshotData?.data?.progress_snapshot) {
        setProgressSnapshot(snapshotData.data.progress_snapshot);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Default fallback data if API doesn't return data
  const defaultWeeklyProgress = [
    { day: "Mon", minutes: 0 },
    { day: "Tue", minutes: 0 },
    { day: "Wed", minutes: 0 },
    { day: "Thu", minutes: 0 },
    { day: "Fri", minutes: 0 },
    { day: "Sat", minutes: 0 },
    { day: "Sun", minutes: 0 },
  ];

  const defaultSkillProgress = [
    { skill: "Vocabulary", progress: 0 },
    { skill: "Grammar", progress: 0 },
    { skill: "Speaking", progress: 0 },
    { skill: "Listening", progress: 0 },
  ];

  return (
    <PageTransition>
      <Box>
        {/* Welcome Section */}
        <Box sx={{ mb: 4 }}>
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
              <Avatar
                sx={{
                  width: 64,
                  height: 64,
                  bgcolor: "primary.main",
                  fontSize: "1.5rem",
                }}
              >
                {user?.username?.charAt(0).toUpperCase()}
              </Avatar>
              <Box>
                <Typography variant="h4" fontWeight={700}>
                  Welcome back, {user?.username}!
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Ready to continue your learning journey?
                </Typography>
              </Box>
            </Box>
          </motion.div>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Learning Streak"
              value={
                dashboardData?.current_streak
                  ? `${dashboardData.current_streak} days`
                  : "0 days"
              }
              icon={<LocalFireDepartment />}
              color="#f59e0b"
              loading={loading}
              subtitle={
                dashboardData?.longest_streak
                  ? `Best: ${dashboardData.longest_streak} days`
                  : "Keep it up!"
              }
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Points"
              value={dashboardData?.total_points || "0"}
              icon={<EmojiEvents />}
              color="#22c55e"
              loading={loading}
              subtitle={
                dashboardData?.level
                  ? `Level ${dashboardData.level}`
                  : "Level 1"
              }
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Words Learned"
              value={dashboardData?.words_learned || "0"}
              icon={<AutoStories />}
              color="#0ea5e9"
              loading={loading}
              subtitle={
                dashboardData?.new_words_this_month
                  ? `${dashboardData.new_words_this_month} this month`
                  : "Keep learning"
              }
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Time Spent"
              value={
                dashboardData?.total_study_time_hours
                  ? `${dashboardData.total_study_time_hours}h`
                  : "0h"
              }
              icon={<AccessTime />}
              color="#d946ef"
              loading={loading}
              subtitle={
                dashboardData?.study_time_this_week
                  ? `${dashboardData.study_time_this_week}h this week`
                  : "This week"
              }
            />
          </Grid>
        </Grid>

        {/* Learning Journey Progress Section */}
        {progressSnapshot && (
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* Overall Mastery Card */}
            <Grid item xs={12} md={4}>
              <Card
                sx={{
                  background:
                    "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "white",
                  height: "100%",
                }}
              >
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <TrendingUp sx={{ fontSize: 40, mr: 2 }} />
                    <Typography variant="h5" fontWeight={700}>
                      Overall Mastery
                    </Typography>
                  </Box>
                  <Typography variant="h2" fontWeight={800} sx={{ mb: 2 }}>
                    {Math.round(
                      progressSnapshot.mastery?.overall_percentage || 0
                    )}
                    %
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={progressSnapshot.mastery?.overall_percentage || 0}
                    sx={{
                      height: 10,
                      borderRadius: 5,
                      backgroundColor: "rgba(255,255,255,0.3)",
                      "& .MuiLinearProgress-bar": {
                        backgroundColor: "white",
                      },
                    }}
                  />
                  <Typography variant="body2" sx={{ mt: 2, opacity: 0.9 }}>
                    {progressSnapshot.statistics?.completed_lessons || 0}{" "}
                    lessons completed
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Current Lesson Card */}
            {progressSnapshot.current_lesson && (
              <Grid item xs={12} md={8}>
                <Card
                  sx={{
                    background:
                      "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
                    color: "white",
                    height: "100%",
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Continue Your Learning Journey
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        mt: 2,
                      }}
                    >
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h5" fontWeight={700} gutterBottom>
                          {progressSnapshot.current_lesson.title}
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{ opacity: 0.9, mb: 2 }}
                        >
                          {progressSnapshot.current_lesson.description}
                        </Typography>
                        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                          <Chip
                            label={`Difficulty: ${progressSnapshot.current_lesson.difficulty_level}`}
                            size="small"
                            sx={{
                              backgroundColor: "rgba(255,255,255,0.2)",
                              color: "white",
                            }}
                          />
                          {progressSnapshot.current_lesson.estimated_time && (
                            <Chip
                              label={`${progressSnapshot.current_lesson.estimated_time} min`}
                              size="small"
                              sx={{
                                backgroundColor: "rgba(255,255,255,0.2)",
                                color: "white",
                              }}
                            />
                          )}
                        </Box>
                      </Box>
                      <Button
                        variant="contained"
                        size="large"
                        endIcon={<ArrowForward />}
                        onClick={() =>
                          navigate(
                            `/lesson/${progressSnapshot.current_lesson.id}`
                          )
                        }
                        sx={{
                          backgroundColor: "white",
                          color: "#f5576c",
                          "&:hover": {
                            backgroundColor: "rgba(255,255,255,0.9)",
                          },
                          ml: 2,
                        }}
                      >
                        Continue
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Next Lesson Preview */}
            {!progressSnapshot.current_lesson &&
              progressSnapshot.next_lesson && (
                <Grid item xs={12} md={8}>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Ready for your next challenge!
                  </Alert>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        Up Next: {progressSnapshot.next_lesson.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        paragraph
                      >
                        {progressSnapshot.next_lesson.description}
                      </Typography>
                      <Button
                        variant="contained"
                        endIcon={<ArrowForward />}
                        onClick={() =>
                          navigate(`/lesson/${progressSnapshot.next_lesson.id}`)
                        }
                      >
                        Start Lesson
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              )}

            {/* Recent Achievements from Progress Snapshot */}
            {progressSnapshot.recent_achievements &&
              progressSnapshot.recent_achievements.length > 0 && (
                <Grid item xs={12}>
                  <HoverCard>
                    <CardContent>
                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        🏆 Recent Achievements
                      </Typography>
                      <Grid container spacing={2} sx={{ mt: 1 }}>
                        {progressSnapshot.recent_achievements
                          .slice(0, 4)
                          .map((achievement, index) => (
                            <Grid item xs={12} sm={6} md={3} key={index}>
                              <Card
                                sx={{
                                  textAlign: "center",
                                  p: 2,
                                  background:
                                    "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
                                }}
                              >
                                <Typography variant="h3">
                                  {achievement.icon || "🎯"}
                                </Typography>
                                <Typography
                                  variant="subtitle1"
                                  fontWeight={600}
                                  sx={{ mt: 1 }}
                                >
                                  {achievement.title}
                                </Typography>
                                <Typography
                                  variant="caption"
                                  color="text.secondary"
                                >
                                  {achievement.description}
                                </Typography>
                                <Chip
                                  label={`+${achievement.points_awarded} pts`}
                                  size="small"
                                  color="warning"
                                  sx={{ mt: 1 }}
                                />
                              </Card>
                            </Grid>
                          ))}
                      </Grid>
                    </CardContent>
                  </HoverCard>
                </Grid>
              )}
          </Grid>
        )}

        <Grid container spacing={3} sx={{ mt: 1 }}>
          {/* Weekly Progress Chart */}
          <Grid item xs={12} md={8}>
            <HoverCard>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Weekly Activity
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={
                      weeklyProgress.length > 0
                        ? weeklyProgress
                        : defaultWeeklyProgress
                    }
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="day" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="minutes"
                      stroke="#0ea5e9"
                      strokeWidth={3}
                      dot={{ fill: "#0ea5e9", r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </HoverCard>
          </Grid>

          {/* Current Learning Path */}
          <Grid item xs={12} md={4}>
            <HoverCard>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Current Learning Path
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {learningPaths.length > 0 ? (
                    <>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          gap: 2,
                          mb: 2,
                        }}
                      >
                        <School color="primary" />
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="body1" fontWeight={600}>
                            {learningPaths[0]?.title || "No Learning Path"}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {learningPaths[0]?.current_chapter
                              ? `Chapter ${learningPaths[0].current_chapter} of ${learningPaths[0].total_chapters}`
                              : "Start learning"}
                          </Typography>
                        </Box>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={learningPaths[0]?.completion_percentage || 0}
                        sx={{ height: 8, borderRadius: 4, mb: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {learningPaths[0]?.completion_percentage || 0}% Complete
                      </Typography>
                    </>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      No active learning path. Start one from the Learning Paths
                      page!
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </HoverCard>
          </Grid>

          {/* Skill Progress */}
          <Grid item xs={12} md={6}>
            <HoverCard>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Skill Progress
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {(skillProgress.length > 0
                    ? skillProgress
                    : defaultSkillProgress
                  ).map((skill, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant="body2" fontWeight={500}>
                          {skill.skill || skill.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {skill.progress || skill.percentage || 0}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={skill.progress || skill.percentage || 0}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </HoverCard>
          </Grid>

          {/* Recent Achievements */}
          <Grid item xs={12} md={6}>
            <HoverCard>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Recent Achievements
                </Typography>
                <Box
                  sx={{
                    mt: 2,
                    display: "flex",
                    flexDirection: "column",
                    gap: 2,
                  }}
                >
                  {[
                    {
                      title: "Week Warrior",
                      description: "7-day learning streak",
                      color: "warning",
                    },
                    {
                      title: "Vocabulary Master",
                      description: "Learned 100 words",
                      color: "primary",
                    },
                    {
                      title: "Quiz Champion",
                      description: "Perfect score on 5 quizzes",
                      color: "success",
                    },
                  ].map((achievement, index) => (
                    <Box
                      key={index}
                      sx={{ display: "flex", alignItems: "center", gap: 2 }}
                    >
                      <EmojiEvents color={achievement.color} />
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {achievement.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {achievement.description}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </HoverCard>
          </Grid>

          {/* Recommended Activities */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Recommended for You
                </Typography>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  {[
                    {
                      title: "Daily Vocabulary Practice",
                      type: "Flashcards",
                      time: "10 min",
                    },
                    {
                      title: "Grammar Quiz: Present Tense",
                      type: "Quiz",
                      time: "15 min",
                    },
                    {
                      title: "Conversation Practice",
                      type: "AI Chat",
                      time: "20 min",
                    },
                    {
                      title: "Reading Comprehension",
                      type: "Reading",
                      time: "12 min",
                    },
                  ].map((activity, index) => (
                    <Grid item xs={12} sm={6} md={3} key={index}>
                      <motion.div whileHover={{ y: -4 }}>
                        <Card
                          sx={{
                            cursor: "pointer",
                            border: 1,
                            borderColor: "divider",
                            "&:hover": { borderColor: "primary.main" },
                          }}
                        >
                          <CardContent>
                            <Typography
                              variant="body2"
                              fontWeight={600}
                              gutterBottom
                            >
                              {activity.title}
                            </Typography>
                            <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
                              <Chip
                                label={activity.type}
                                size="small"
                                color="primary"
                              />
                              <Chip
                                label={activity.time}
                                size="small"
                                variant="outlined"
                              />
                            </Box>
                          </CardContent>
                        </Card>
                      </motion.div>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </PageTransition>
  );
};

export default Dashboard;
