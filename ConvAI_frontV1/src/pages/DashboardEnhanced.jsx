import { useState, useEffect } from "react";
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
  Paper,
  IconButton,
  CircularProgress,
} from "@mui/material";
import {
  LocalFireDepartment,
  EmojiEvents,
  AutoStories,
  School,
  AccessTime,
  ArrowForward,
  TrendingUp,
  PlayArrow,
  Star,
  CheckCircle,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import StatCard from "../components/common/StatCard";
import HoverCard from "../components/common/HoverCard";
import PageTransition from "../components/common/PageTransition";
import { useAuth } from "../context/AuthContext";
import axiosInstance, { API_ENDPOINTS } from "../config/api";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError("");

      // Fetch comprehensive dashboard data
      const response = await axiosInstance.get(
        API_ENDPOINTS.PERSONALIZATION.DASHBOARD
      );

      if (response.data && response.data.dashboard) {
        setDashboardData(response.data.dashboard);
      }
    } catch (err) {
      console.error("Error fetching dashboard:", err);
      setError("Failed to load dashboard data");
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
        minHeight="100vh"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error" onClose={() => setError("")}>
          {error}
        </Alert>
      </Box>
    );
  }

  const data = dashboardData || {};

  return (
    <PageTransition>
      <Box sx={{ p: { xs: 2, md: 4 } }}>
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
                  Welcome back, {data.user_name || user?.username}!
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Ready to continue your learning journey? 🚀
                </Typography>
                <Box sx={{ display: "flex", gap: 1, mt: 1 }}>
                  <Chip
                    label={`${data.proficiency_level || "Beginner"} Level`}
                    size="small"
                    color="primary"
                  />
                  <Chip
                    label={`${data.learning_goal || "Conversational"}`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </Box>
            </Box>
          </motion.div>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Current Streak"
              value={`${data.current_streak || 0} days`}
              icon={<LocalFireDepartment />}
              color="#f59e0b"
              loading={loading}
              subtitle={
                data.longest_streak
                  ? `Best: ${data.longest_streak} days 🔥`
                  : "Keep it up!"
              }
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Points"
              value={data.total_points || 0}
              icon={<EmojiEvents />}
              color="#22c55e"
              loading={loading}
              subtitle={`Level ${data.level || 1} 🎯`}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Words Learned"
              value={data.words_learned || 0}
              icon={<AutoStories />}
              color="#0ea5e9"
              loading={loading}
              subtitle={`+${data.new_words_this_month || 0} this month 📚`}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Time Spent"
              value={`${data.total_study_time_hours || 0}h`}
              icon={<AccessTime />}
              color="#d946ef"
              loading={loading}
              subtitle={`${data.study_time_this_week || 0}h this week ⏰`}
            />
          </Grid>
        </Grid>

        {/* Daily Goal Progress */}
        <Card sx={{ mb: 4, background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", color: "white" }}>
          <CardContent>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
              <Typography variant="h6" fontWeight={700}>
                Today's Goal Progress
              </Typography>
              <Typography variant="h4" fontWeight={800}>
                {data.daily_progress_percentage || 0}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={data.daily_progress_percentage || 0}
              sx={{
                height: 12,
                borderRadius: 6,
                backgroundColor: "rgba(255,255,255,0.3)",
                "& .MuiLinearProgress-bar": {
                  backgroundColor: "white",
                },
              }}
            />
            <Box sx={{ display: "flex", justifyContent: "space-between", mt: 2 }}>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {data.today_time_spent || 0} / {data.daily_goal_minutes || 15} minutes
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {Math.max(0, (data.daily_goal_minutes || 15) - (data.today_time_spent || 0))} min remaining
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* Next Milestone */}
        {data.next_milestone && (
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <Typography variant="h1">{data.next_milestone.icon}</Typography>
                  <Box>
                    <Typography variant="h6" fontWeight={700}>
                      Next Milestone: {data.next_milestone.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {data.next_milestone.description}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ textAlign: "right" }}>
                  <Typography variant="h4" fontWeight={700} color="primary">
                    {data.next_milestone.points_needed}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    points needed
                  </Typography>
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={data.next_milestone.progress_percentage || 0}
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        )}

        {/* Recommended Activities */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" fontWeight={700} gutterBottom>
            Recommended for You
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Based on your level, goals, and interests
          </Typography>
          <Grid container spacing={3}>
            {data.recommended_activities && data.recommended_activities.length > 0 ? (
              data.recommended_activities.map((activity, index) => (
                <Grid item xs={12} sm={6} md={4} key={activity.id || index}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <HoverCard>
                      <CardContent>
                        <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 2 }}>
                          <Typography variant="h3">{activity.icon}</Typography>
                          <Chip label={activity.topic} size="small" color="primary" />
                        </Box>
                        <Typography variant="h6" fontWeight={700} gutterBottom>
                          {activity.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {activity.description}
                        </Typography>
                        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <Box sx={{ display: "flex", gap: 1 }}>
                            <Chip
                              label={`${activity.estimated_time} min`}
                              size="small"
                              icon={<AccessTime />}
                            />
                            <Chip
                              label={`+${activity.points} pts`}
                              size="small"
                              icon={<Star />}
                              color="success"
                            />
                          </Box>
                          <IconButton
                            color="primary"
                            onClick={() => navigate(`/activity/${activity.type}`)}
                          >
                            <PlayArrow />
                          </IconButton>
                        </Box>
                      </CardContent>
                    </HoverCard>
                  </motion.div>
                </Grid>
              ))
            ) : (
              <Grid item xs={12}>
                <Alert severity="info">
                  Complete your onboarding to get personalized recommendations!
                </Alert>
              </Grid>
            )}
          </Grid>
        </Box>

        {/* Analytics Section */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Weekly Activity Chart */}
          <Grid item xs={12} md={7}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={700} gutterBottom>
                  Weekly Activity
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Your learning time over the past 7 days
                </Typography>
                {data.weekly_activity && data.weekly_activity.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={data.weekly_activity}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis label={{ value: "Minutes", angle: -90, position: "insideLeft" }} />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="minutes"
                        stroke="#667eea"
                        strokeWidth={3}
                        dot={{ r: 5 }}
                        activeDot={{ r: 8 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <Alert severity="info">Start learning to see your activity!</Alert>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Skill Breakdown Chart */}
          <Grid item xs={12} md={5}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={700} gutterBottom>
                  Skill Breakdown
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Your proficiency in different areas
                </Typography>
                {data.skill_breakdown && data.skill_breakdown.length > 0 ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={data.skill_breakdown} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={[0, 100]} />
                      <YAxis dataKey="skill" type="category" width={100} />
                      <Tooltip />
                      <Bar dataKey="progress" fill="#22c55e" radius={[0, 8, 8, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <Alert severity="info">Take an assessment to see your skills!</Alert>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Daily Challenge */}
        {data.daily_challenge && (
          <Card sx={{ mb: 4, borderLeft: 4, borderColor: "warning.main" }}>
            <CardContent>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <Box>
                  <Typography variant="h6" fontWeight={700} gutterBottom>
                    🎯 Today's Challenge
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 1 }}>
                    {data.daily_challenge.challenge?.question}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {data.daily_challenge.challenge?.telugu_hint}
                  </Typography>
                </Box>
                {data.daily_challenge.completed ? (
                  <CheckCircle sx={{ fontSize: 48, color: "success.main" }} />
                ) : (
                  <Button
                    variant="contained"
                    endIcon={<ArrowForward />}
                    onClick={() => navigate("/challenge")}
                  >
                    Start Challenge
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Recent Vocabulary */}
        {data.recent_vocabulary && data.recent_vocabulary.length > 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                📚 Recently Learned Words
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                {data.recent_vocabulary.map((word, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Paper
                      sx={{
                        p: 2,
                        background: "linear-gradient(135deg, #f093fb 10%, #f5576c 100%)",
                        color: "white",
                      }}
                    >
                      <Typography variant="h6" fontWeight={700}>
                        {word.english}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>
                        {word.telugu}
                      </Typography>
                      {word.context && (
                        <Typography variant="caption" sx={{ opacity: 0.8, mt: 1, display: "block" }}>
                          "{word.context}"
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}
      </Box>
    </PageTransition>
  );
};

export default Dashboard;
