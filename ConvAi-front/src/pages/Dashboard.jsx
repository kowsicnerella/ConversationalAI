import { useState, useEffect } from "react";
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  LinearProgress,
  Chip,
  Button,
  Paper,
  useTheme,
  Skeleton,
} from "@mui/material";
import {
  EmojiEvents,
  Star,
  PlayArrow,
  LocalFireDepartment,
  Psychology,
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
import { useAuthStore } from "../store/index.js";
import { toast } from "react-hot-toast";
import {
  NeuralBackground,
  AnimatedCounter,
} from "../components/ui/AIComponents";
import { analyticsAPI, userAPI, gamificationAPI } from "../services/api";

// Real data fetched from analytics API

// Removed unused learningPaths variable

const Dashboard = () => {
  const theme = useTheme();
  const user = useAuthStore((state) => state.user);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod] = useState("week");
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);

        // Fetch data from multiple endpoints
        const [dashboardSummary, userProfile, userStats, gamificationStats] =
          await Promise.allSettled([
            analyticsAPI.getDashboardSummary(),
            userAPI.getProfile(),
            userAPI.getStatistics(),
            user?.id
              ? gamificationAPI.getGamificationStats(user.id)
              : Promise.resolve({ data: {} }),
          ]);

        // Process results
        const summary =
          dashboardSummary.status === "fulfilled"
            ? dashboardSummary.value.data.summary
            : {};
        const profile =
          userProfile.status === "fulfilled"
            ? userProfile.value.data.user
            : user;
        const statistics =
          userStats.status === "fulfilled"
            ? userStats.value.data.statistics
            : {};
        const gamification =
          gamificationStats.status === "fulfilled"
            ? gamificationStats.value.data
            : {};

        setDashboardData({
          profile: profile || {
            id: user?.id || 1,
            username: user?.username || "Student",
            email: user?.email || "student@example.com",
            streak: summary.current_streak || 0,
            totalPoints: statistics.total_points || 0,
            level: statistics.level_progress?.current_level || "Beginner",
            avatar: user?.username?.substring(0, 2).toUpperCase() || "ST",
            joinedDays: 45,
          },
          stats: {
            totalLessons: statistics.activities_completed || 0,
            completedLessons: statistics.activities_completed || 0,
            currentStreak: summary.current_streak || 0,
            totalPoints: statistics.total_points || 0,
            weeklyGoal: summary.weekly_minutes || 180,
            accuracy: Math.round(statistics.average_score || 0),
            studyTime: summary.weekly_minutes || 0,
          },
          progressData: summary.weekly_progress || [
            { name: "Mon", score: 0 },
            { name: "Tue", score: 0 },
            { name: "Wed", score: 0 },
            { name: "Thu", score: 0 },
            { name: "Fri", score: 0 },
            { name: "Sat", score: 0 },
            { name: "Sun", score: 0 },
          ],
          skillsData: statistics.skill_breakdown || [
            { name: "Speaking", value: 0, color: "#667eea" },
            { name: "Reading", value: 0, color: "#764ba2" },
            { name: "Writing", value: 0, color: "#f093fb" },
            { name: "Listening", value: 0, color: "#f5576c" },
          ],
          recentActivities: summary.recent_activities || [],
          badges: gamification.badges || [],
        });
      } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
        toast.error("Failed to load dashboard data");

        // Fallback to mock data
        setDashboardData({
          profile: {
            id: user?.id || 1,
            username: user?.username || "Student",
            email: user?.email || "student@example.com",
            streak: 0,
            totalPoints: 0,
            level: "Beginner",
            avatar: user?.username?.substring(0, 2).toUpperCase() || "ST",
            joinedDays: 1,
          },
          stats: {
            totalLessons: 0,
            completedLessons: 0,
            currentStreak: 0,
            totalPoints: 0,
            weeklyGoal: 180,
            accuracy: 0,
            studyTime: 0,
          },
          progressData: [
            { name: "Mon", score: 0 },
            { name: "Tue", score: 0 },
            { name: "Wed", score: 0 },
            { name: "Thu", score: 0 },
            { name: "Fri", score: 0 },
            { name: "Sat", score: 0 },
            { name: "Sun", score: 0 },
          ],
          skillsData: [
            { name: "Speaking", value: 0, color: "#667eea" },
            { name: "Reading", value: 0, color: "#764ba2" },
            { name: "Writing", value: 0, color: "#f093fb" },
            { name: "Listening", value: 0, color: "#f5576c" },
          ],
          recentActivities: [],
          badges: [],
        });
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchDashboardData();
    }
  }, [user, selectedPeriod]);

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
    hover: { y: -5, boxShadow: "0 8px 25px rgba(0,0,0,0.15)" },
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Grid container spacing={3}>
          {/* Loading skeletons */}
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="rectangular" height={200} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        background:
          theme.palette.mode === "dark"
            ? "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%)"
            : "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%)",
      }}
    >
      <NeuralBackground opacity={0.03} />

      <Container
        maxWidth="xl"
        sx={{
          py: { xs: 2, sm: 3, md: 4 },
          px: { xs: 2, sm: 3 },
          position: "relative",
          zIndex: 1,
        }}
      >
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Hero Section */}
          <motion.div variants={cardVariants}>
            <Box
              sx={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                borderRadius: 4,
                p: { xs: 3, sm: 4, md: 5 },
                mb: { xs: 3, sm: 4 },
                color: "white",
                position: "relative",
                overflow: "hidden",
                "&::before": {
                  content: '""',
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background:
                    'url("data:image/svg+xml,%3Csvg width="60" height="60" viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg"%3E%3Cg fill="none" fill-rule="evenodd"%3E%3Cg fill="%23ffffff" fill-opacity="0.1"%3E%3Ccircle cx="30" cy="30" r="2"/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
                  opacity: 0.5,
                },
              }}
            >
              <Box sx={{ position: "relative", zIndex: 1 }}>
                <Grid container spacing={3} alignItems="center">
                  <Grid item xs={12} md={8}>
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="h2"
                        sx={{
                          fontWeight: 800,
                          mb: 1,
                          fontSize: { xs: "2rem", sm: "2.5rem", md: "3rem" },
                          textShadow: "0 2px 4px rgba(0,0,0,0.1)",
                        }}
                      >
                        Welcome back,{" "}
                        {dashboardData?.profile?.username || "Alex"}! 👋
                      </Typography>
                      <Typography
                        variant="h5"
                        sx={{
                          opacity: 0.9,
                          fontWeight: 400,
                          mb: 3,
                          fontSize: { xs: "1.1rem", sm: "1.25rem" },
                        }}
                      >
                        You&apos;re making amazing progress! Let&apos;s continue
                        your language learning journey.
                      </Typography>
                      <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <LocalFireDepartment sx={{ color: "#FFB020" }} />
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {dashboardData?.stats?.currentStreak || 12} Day
                            Streak
                          </Typography>
                        </Box>
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <Star sx={{ color: "#FFD700" }} />
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {dashboardData?.stats?.totalPoints || 2850} Points
                          </Typography>
                        </Box>
                        <Box
                          sx={{ display: "flex", alignItems: "center", gap: 1 }}
                        >
                          <EmojiEvents sx={{ color: "#4CAF50" }} />
                          <Typography variant="h6" sx={{ fontWeight: 600 }}>
                            {dashboardData?.profile?.level || "Advanced"} Level
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ textAlign: "center" }}>
                      <motion.div
                        animate={{
                          rotate: [0, 5, -5, 0],
                          scale: [1, 1.05, 1],
                        }}
                        transition={{
                          duration: 6,
                          repeat: Infinity,
                          repeatType: "reverse",
                        }}
                      >
                        <Avatar
                          sx={{
                            width: { xs: 80, sm: 100, md: 120 },
                            height: { xs: 80, sm: 100, md: 120 },
                            margin: "0 auto",
                            background: "rgba(255,255,255,0.2)",
                            backdropFilter: "blur(10px)",
                            border: "3px solid rgba(255,255,255,0.3)",
                            fontSize: { xs: "2rem", sm: "2.5rem", md: "3rem" },
                            fontWeight: 800,
                          }}
                        >
                          {dashboardData?.profile?.avatar || "AJ"}
                        </Avatar>
                      </motion.div>
                    </Box>
                  </Grid>
                </Grid>
              </Box>
            </Box>
          </motion.div>

          {/* Modern Stats Overview */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="h4"
              sx={{
                mb: 3,
                fontWeight: 700,
                textAlign: "center",
                background: "linear-gradient(45deg, #667eea, #764ba2)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              Your Learning Analytics
            </Typography>
            <Grid container spacing={3}>
              {[
                {
                  title: "Study Streak",
                  value: dashboardData?.stats?.currentStreak || 12,
                  unit: "days",
                  icon: <LocalFireDepartment />,
                  gradient: "linear-gradient(135deg, #FF6B6B, #FF8E53)",
                  change: "+2 from last week",
                  isPositive: true,
                },
                {
                  title: "Total Points",
                  value: dashboardData?.stats?.totalPoints || 2850,
                  unit: "pts",
                  icon: <Star />,
                  gradient: "linear-gradient(135deg, #4ECDC4, #44A08D)",
                  change: "+180 this week",
                  isPositive: true,
                },
                {
                  title: "Accuracy Rate",
                  value: dashboardData?.stats?.accuracy || 94,
                  unit: "%",
                  icon: <TrendingUp />,
                  gradient: "linear-gradient(135deg, #A8EDEA, #667eea)",
                  change: "+3% improvement",
                  isPositive: true,
                },
                {
                  title: "Study Time",
                  value:
                    Math.round(
                      ((dashboardData?.stats?.studyTime || 156) / 60) * 10
                    ) / 10,
                  unit: "hrs",
                  icon: <Psychology />,
                  gradient: "linear-gradient(135deg, #D299C2, #667eea)",
                  change: "This week",
                  isPositive: true,
                },
              ].map((stat, index) => (
                <Grid item xs={12} sm={6} lg={3} key={index}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                    whileHover={{ y: -5, scale: 1.02 }}
                  >
                    <Card
                      sx={{
                        height: "100%",
                        background: stat.gradient,
                        color: "white",
                        borderRadius: 4,
                        overflow: "hidden",
                        position: "relative",
                        boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
                        "&::before": {
                          content: '""',
                          position: "absolute",
                          top: 0,
                          left: 0,
                          right: 0,
                          bottom: 0,
                          background: "rgba(255,255,255,0.1)",
                          backdropFilter: "blur(10px)",
                        },
                      }}
                    >
                      <CardContent
                        sx={{ p: 3, position: "relative", zIndex: 1 }}
                      >
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "space-between",
                            mb: 2,
                          }}
                        >
                          <Box
                            sx={{
                              p: 1.5,
                              borderRadius: "50%",
                              background: "rgba(255,255,255,0.2)",
                              backdropFilter: "blur(10px)",
                            }}
                          >
                            {stat.icon}
                          </Box>
                          <Typography
                            variant="body2"
                            sx={{
                              background: "rgba(255,255,255,0.2)",
                              px: 2,
                              py: 0.5,
                              borderRadius: 2,
                              fontSize: "0.75rem",
                              fontWeight: 600,
                            }}
                          >
                            {stat.change}
                          </Typography>
                        </Box>

                        <Box sx={{ mb: 1 }}>
                          <Typography
                            variant="h3"
                            sx={{
                              fontWeight: 800,
                              mb: 0.5,
                              fontSize: { xs: "2rem", sm: "2.5rem" },
                              textShadow: "0 2px 4px rgba(0,0,0,0.1)",
                            }}
                          >
                            <AnimatedCounter to={stat.value} duration={2} />
                            <Typography
                              component="span"
                              variant="h5"
                              sx={{ ml: 0.5, opacity: 0.8 }}
                            >
                              {stat.unit}
                            </Typography>
                          </Typography>
                          <Typography
                            variant="h6"
                            sx={{
                              fontWeight: 500,
                              opacity: 0.9,
                              fontSize: "1.1rem",
                            }}
                          >
                            {stat.title}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Box>

          {/* Learning Progress Section */}
          <Box sx={{ mb: 4 }}>
            <Typography
              variant="h4"
              sx={{
                mb: 3,
                fontWeight: 700,
                textAlign: "center",
              }}
            >
              Your Learning Journey
            </Typography>
            <Grid container spacing={3}>
              {/* Weekly Progress Chart */}
              <Grid item xs={12} lg={8}>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6 }}
                >
                  <Card
                    sx={{
                      borderRadius: 4,
                      background:
                        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      color: "white",
                      boxShadow: "0 10px 30px rgba(102, 126, 234, 0.3)",
                    }}
                  >
                    <CardContent sx={{ p: 4 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          mb: 3,
                        }}
                      >
                        <Typography variant="h5" sx={{ fontWeight: 700 }}>
                          Weekly Learning Progress
                        </Typography>
                        <Button
                          variant="outlined"
                          sx={{
                            borderColor: "rgba(255,255,255,0.3)",
                            color: "white",
                            "&:hover": {
                              borderColor: "rgba(255,255,255,0.5)",
                              background: "rgba(255,255,255,0.1)",
                            },
                          }}
                        >
                          View Details
                        </Button>
                      </Box>
                      <Box sx={{ height: 300, position: "relative" }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={dashboardData.progressData || []}>
                            <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="rgba(255,255,255,0.2)"
                            />
                            <XAxis
                              dataKey="name"
                              axisLine={false}
                              tickLine={false}
                              tick={{ fill: "white", fontSize: 12 }}
                            />
                            <YAxis
                              axisLine={false}
                              tickLine={false}
                              tick={{ fill: "white", fontSize: 12 }}
                            />
                            <Tooltip
                              contentStyle={{
                                background: "rgba(255,255,255,0.95)",
                                border: "none",
                                borderRadius: 8,
                                color: "#333",
                              }}
                            />
                            <Line
                              type="monotone"
                              dataKey="score"
                              stroke="#FFD700"
                              strokeWidth={4}
                              dot={{
                                fill: "#FFD700",
                                strokeWidth: 2,
                                r: 6,
                              }}
                              activeDot={{ r: 8, fill: "#FFD700" }}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </Box>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>

              {/* Quick Stats Sidebar */}
              <Grid item xs={12} lg={4}>
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      gap: 2,
                      height: "100%",
                    }}
                  >
                    {/* Quick Action Card */}
                    <Card
                      sx={{
                        background:
                          "linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%)",
                        color: "white",
                        borderRadius: 3,
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Typography
                          variant="h6"
                          sx={{ mb: 2, fontWeight: 700 }}
                        >
                          Ready for your next lesson?
                        </Typography>
                        <Button
                          variant="contained"
                          fullWidth
                          startIcon={<PlayArrow />}
                          sx={{
                            background: "rgba(255,255,255,0.2)",
                            color: "white",
                            "&:hover": { background: "rgba(255,255,255,0.3)" },
                          }}
                        >
                          Continue Learning
                        </Button>
                      </CardContent>
                    </Card>

                    {/* Skills Overview */}
                    <Card sx={{ flex: 1, borderRadius: 3 }}>
                      <CardContent sx={{ p: 3 }}>
                        <Typography
                          variant="h6"
                          sx={{ mb: 2, fontWeight: 700 }}
                        >
                          Skills Overview
                        </Typography>
                        {(dashboardData.skillsData || []).map(
                          (skill, index) => (
                            <Box key={index} sx={{ mb: 2 }}>
                              <Box
                                sx={{
                                  display: "flex",
                                  justifyContent: "space-between",
                                  mb: 0.5,
                                }}
                              >
                                <Typography
                                  variant="body2"
                                  sx={{ fontWeight: 600 }}
                                >
                                  {skill.name}
                                </Typography>
                                <Typography
                                  variant="body2"
                                  sx={{ fontWeight: 700, color: skill.color }}
                                >
                                  {skill.value}%
                                </Typography>
                              </Box>
                              <LinearProgress
                                variant="determinate"
                                value={skill.value}
                                sx={{
                                  height: 8,
                                  borderRadius: 4,
                                  backgroundColor: `${skill.color}20`,
                                  "& .MuiLinearProgress-bar": {
                                    backgroundColor: skill.color,
                                    borderRadius: 4,
                                  },
                                }}
                              />
                            </Box>
                          )
                        )}
                      </CardContent>
                    </Card>
                  </Box>
                </motion.div>
              </Grid>
            </Grid>
          </Box>

          {/* Recent Activity & Achievements */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card sx={{ borderRadius: 4 }}>
                <CardContent sx={{ p: 4 }}>
                  <Typography variant="h5" sx={{ mb: 3, fontWeight: 700 }}>
                    Recent Learning Activity
                  </Typography>
                  <Box
                    sx={{ display: "flex", flexDirection: "column", gap: 2 }}
                  >
                    {(dashboardData.recentActivities || []).map(
                      (activity, index) => (
                        <motion.div
                          key={activity.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              p: 2,
                              borderRadius: 3,
                              background:
                                theme.palette.mode === "dark"
                                  ? "rgba(255,255,255,0.05)"
                                  : "rgba(0,0,0,0.02)",
                              "&:hover": {
                                background:
                                  theme.palette.mode === "dark"
                                    ? "rgba(255,255,255,0.08)"
                                    : "rgba(0,0,0,0.04)",
                              },
                            }}
                          >
                            <Avatar
                              sx={{
                                background:
                                  "linear-gradient(135deg, #667eea, #764ba2)",
                                mr: 2,
                              }}
                            >
                              {activity.icon}
                            </Avatar>
                            <Box sx={{ flex: 1 }}>
                              <Typography
                                variant="subtitle1"
                                sx={{ fontWeight: 600 }}
                              >
                                {activity.title}
                              </Typography>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                {activity.time}
                              </Typography>
                            </Box>
                            {activity.score && (
                              <Chip
                                label={`${activity.score}%`}
                                color="success"
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </motion.div>
                      )
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ borderRadius: 4 }}>
                <CardContent sx={{ p: 4 }}>
                  <Typography variant="h5" sx={{ mb: 3, fontWeight: 700 }}>
                    Achievements
                  </Typography>
                  <Grid container spacing={2}>
                    {(dashboardData.badges || []).slice(0, 4).map((badge) => (
                      <Grid item xs={6} key={badge.id}>
                        <motion.div whileHover={{ scale: 1.05 }}>
                          <Paper
                            elevation={badge.earned ? 4 : 1}
                            sx={{
                              p: 2,
                              textAlign: "center",
                              borderRadius: 3,
                              background: badge.earned
                                ? "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)"
                                : theme.palette.grey[100],
                              color: badge.earned ? "white" : "text.secondary",
                              cursor: "pointer",
                            }}
                          >
                            <Typography variant="h4" sx={{ mb: 0.5 }}>
                              {badge.icon}
                            </Typography>
                            <Typography
                              variant="caption"
                              sx={{ fontWeight: 600 }}
                            >
                              {badge.name}
                            </Typography>
                          </Paper>
                        </motion.div>
                      </Grid>
                    ))}
                  </Grid>
                  <Button
                    fullWidth
                    variant="outlined"
                    sx={{ mt: 2 }}
                    startIcon={<EmojiEvents />}
                  >
                    View All Achievements
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </motion.div>
      </Container>
    </Box>
  );
};

export default Dashboard;
