import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Chip,
  Tabs,
  Tab,
  Grid,
  CircularProgress,
} from "@mui/material";
import {
  EmojiEvents,
  LocalFireDepartment,
  Star,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import HoverCard from "../components/common/HoverCard";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const Leaderboard = () => {
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  const fetchLeaderboard = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.GAMIFICATION.LEADERBOARD,
        {
          params: {
            timeframe:
              activeTab === 0
                ? "weekly"
                : activeTab === 1
                ? "monthly"
                : "all-time",
          },
        }
      );
      // Ensure we always set an array
      const leaderboardData = response.data.leaderboard || response.data.data || [];
      const arrayData = Array.isArray(leaderboardData) ? leaderboardData : [];
      setLeaderboard(arrayData);
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
      // Mock data for demo
      setLeaderboard([
        {
          id: 1,
          username: "SuperLearner",
          points: 5420,
          level: 15,
          streak: 45,
          avatar: null,
          rank: 1,
        },
        {
          id: 2,
          username: "EnglishPro",
          points: 4890,
          level: 14,
          streak: 32,
          avatar: null,
          rank: 2,
        },
        {
          id: 3,
          username: "QuizMaster",
          points: 4650,
          level: 13,
          streak: 28,
          avatar: null,
          rank: 3,
        },
        {
          id: 4,
          username: user?.username || "You",
          points: 3210,
          level: 10,
          streak: 15,
          avatar: null,
          rank: 4,
          isCurrentUser: true,
        },
        ...Array.from({ length: 6 }, (_, i) => ({
          id: i + 5,
          username: `User${i + 5}`,
          points: 3000 - i * 200,
          level: 9 - i,
          streak: 10 - i,
          avatar: null,
          rank: i + 5,
        })),
      ]);
    } finally {
      setLoading(false);
    }
  }, [activeTab, user?.username]);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const getRankColor = (rank) => {
    switch (rank) {
      case 1:
        return "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)";
      case 2:
        return "linear-gradient(135deg, #C0C0C0 0%, #808080 100%)";
      case 3:
        return "linear-gradient(135deg, #CD7F32 0%, #8B4513 100%)";
      default:
        return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
    }
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return "🥇";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    return rank;
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

  // Ensure leaderboard is an array
  const leaderboardArray = Array.isArray(leaderboard) ? leaderboard : [];
  const currentUser = leaderboardArray.find((u) => u.isCurrentUser);
  const topThree = leaderboardArray.slice(0, 3);
  const restOfLeaderboard = leaderboardArray.slice(3);

  return (
    <PageTransition>
      <Box>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
            Leaderboard
          </GradientText>
          <Typography variant="body1" color="text.secondary">
            Compete with learners around the world
          </Typography>
        </Box>

        {/* Time Period Tabs */}
        <Box sx={{ mb: 4 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
          >
            <Tab label="This Week" />
            <Tab label="This Month" />
            <Tab label="All Time" />
          </Tabs>
        </Box>

        {/* Your Stats */}
        {currentUser && (
          <Card
            sx={{
              mb: 4,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
            }}
          >
            <CardContent>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Your Ranking
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h4" fontWeight={700}>
                      #{currentUser.rank}
                    </Typography>
                    <Typography variant="body2">Rank</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h4" fontWeight={700}>
                      {currentUser.points}
                    </Typography>
                    <Typography variant="body2">Points</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h4" fontWeight={700}>
                      {currentUser.level}
                    </Typography>
                    <Typography variant="body2">Level</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h4" fontWeight={700}>
                      {currentUser.streak}
                    </Typography>
                    <Typography variant="body2">Day Streak</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Top 3 Podium */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={700} gutterBottom>
            Top Performers
          </Typography>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {/* 2nd Place */}
            {topThree[1] && (
              <Grid item xs={12} sm={4} order={{ xs: 2, sm: 1 }}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                >
                  <Card sx={{ textAlign: "center", pt: 4 }}>
                    <CardContent>
                      <Box
                        sx={{
                          width: 80,
                          height: 80,
                          borderRadius: "50%",
                          background: getRankColor(2),
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          margin: "0 auto 16px",
                          fontSize: "2rem",
                        }}
                      >
                        {getRankIcon(2)}
                      </Box>
                      <Avatar
                        sx={{
                          width: 60,
                          height: 60,
                          margin: "0 auto 12px",
                          bgcolor: "primary.main",
                        }}
                      >
                        {topThree[1].username.charAt(0).toUpperCase()}
                      </Avatar>
                      <Typography variant="h6" fontWeight={700} gutterBottom>
                        {topThree[1].username}
                      </Typography>
                      <Chip
                        label={`Level ${topThree[1].level}`}
                        size="small"
                        color="primary"
                        sx={{ mb: 1 }}
                      />
                      <Typography
                        variant="h5"
                        color="primary.main"
                        fontWeight={700}
                      >
                        {topThree[1].points}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        points
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            )}

            {/* 1st Place */}
            {topThree[0] && (
              <Grid item xs={12} sm={4} order={{ xs: 1, sm: 2 }}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.1 }}
                >
                  <Card
                    sx={{
                      textAlign: "center",
                      pt: 2,
                      position: "relative",
                      "&::before": {
                        content: '""',
                        position: "absolute",
                        top: 0,
                        left: 0,
                        right: 0,
                        height: 4,
                        background: getRankColor(1),
                      },
                    }}
                  >
                    <CardContent>
                      <EmojiEvents
                        sx={{ fontSize: 40, color: "#FFD700", mb: 1 }}
                      />
                      <Box
                        sx={{
                          width: 100,
                          height: 100,
                          borderRadius: "50%",
                          background: getRankColor(1),
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          margin: "0 auto 16px",
                          fontSize: "2.5rem",
                          boxShadow: "0 8px 24px rgba(255, 215, 0, 0.3)",
                        }}
                      >
                        {getRankIcon(1)}
                      </Box>
                      <Avatar
                        sx={{
                          width: 80,
                          height: 80,
                          margin: "0 auto 12px",
                          bgcolor: "primary.main",
                        }}
                      >
                        {topThree[0].username.charAt(0).toUpperCase()}
                      </Avatar>
                      <Typography variant="h5" fontWeight={700} gutterBottom>
                        {topThree[0].username}
                      </Typography>
                      <Chip
                        label={`Level ${topThree[0].level}`}
                        size="small"
                        color="primary"
                        sx={{ mb: 1 }}
                      />
                      <Typography
                        variant="h4"
                        color="primary.main"
                        fontWeight={700}
                      >
                        {topThree[0].points}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        points
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            )}

            {/* 3rd Place */}
            {topThree[2] && (
              <Grid item xs={12} sm={4} order={{ xs: 3, sm: 3 }}>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.3 }}
                >
                  <Card sx={{ textAlign: "center", pt: 4 }}>
                    <CardContent>
                      <Box
                        sx={{
                          width: 80,
                          height: 80,
                          borderRadius: "50%",
                          background: getRankColor(3),
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          margin: "0 auto 16px",
                          fontSize: "2rem",
                        }}
                      >
                        {getRankIcon(3)}
                      </Box>
                      <Avatar
                        sx={{
                          width: 60,
                          height: 60,
                          margin: "0 auto 12px",
                          bgcolor: "primary.main",
                        }}
                      >
                        {topThree[2].username.charAt(0).toUpperCase()}
                      </Avatar>
                      <Typography variant="h6" fontWeight={700} gutterBottom>
                        {topThree[2].username}
                      </Typography>
                      <Chip
                        label={`Level ${topThree[2].level}`}
                        size="small"
                        color="primary"
                        sx={{ mb: 1 }}
                      />
                      <Typography
                        variant="h5"
                        color="primary.main"
                        fontWeight={700}
                      >
                        {topThree[2].points}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        points
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            )}
          </Grid>
        </Box>

        {/* Rest of Leaderboard */}
        <Box>
          <Typography variant="h6" fontWeight={700} gutterBottom>
            Rankings
          </Typography>
          {restOfLeaderboard.map((user, index) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              <HoverCard sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                    <Typography
                      variant="h6"
                      fontWeight={700}
                      sx={{
                        minWidth: 40,
                        color: user.isCurrentUser
                          ? "primary.main"
                          : "text.primary",
                      }}
                    >
                      #{user.rank}
                    </Typography>
                    <Avatar
                      sx={{
                        bgcolor: user.isCurrentUser
                          ? "primary.main"
                          : "grey.400",
                      }}
                    >
                      {user.avatar || user.username.charAt(0).toUpperCase()}
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" fontWeight={600}>
                        {user.username}
                        {user.isCurrentUser && (
                          <Chip
                            label="You"
                            size="small"
                            color="primary"
                            sx={{ ml: 1 }}
                          />
                        )}
                      </Typography>
                      <Box
                        sx={{
                          display: "flex",
                          gap: 2,
                          alignItems: "center",
                          mt: 0.5,
                        }}
                      >
                        <Chip
                          icon={<Star />}
                          label={`Level ${user.level}`}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          icon={<LocalFireDepartment />}
                          label={`${user.streak} days`}
                          size="small"
                          variant="outlined"
                          color="warning"
                        />
                      </Box>
                    </Box>
                    <Box sx={{ textAlign: "right" }}>
                      <Typography
                        variant="h5"
                        fontWeight={700}
                        color="primary.main"
                      >
                        {user.points}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        points
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </HoverCard>
            </motion.div>
          ))}
        </Box>
      </Box>
    </PageTransition>
  );
};

export default Leaderboard;
