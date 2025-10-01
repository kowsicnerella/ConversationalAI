import { useState, useEffect } from "react";
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  Tab,
  Tabs,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Chip,
  LinearProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  Badge,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  useMediaQuery,
  Stack,
  alpha,
} from "@mui/material";
import {
  EmojiEvents,
  Star,
  LocalFireDepartment,
  School,
  TrendingUp,
  Timeline,
  Group,
  Person,
  WorkspacePremium,
  AutoAwesome,
  Celebration,
  Share,
} from "@mui/icons-material";
import { gamificationAPI } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../store/index.js";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";

const TabPanel = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`leaderboard-tabpanel-${index}`}
    aria-labelledby={`leaderboard-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
  </div>
);

TabPanel.propTypes = {
  children: PropTypes.node,
  value: PropTypes.number.isRequired,
  index: PropTypes.number.isRequired,
};

const LeaderboardPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState(0);
  const [selectedPeriod, setSelectedPeriod] = useState("weekly");
  const [achievementDialogOpen, setAchievementDialogOpen] = useState(false);
  const [selectedAchievement, setSelectedAchievement] = useState(null);
  const [loading, setLoading] = useState(false);
  const [realLeaderboardData, setRealLeaderboardData] = useState(null);
  const [userBadges, setUserBadges] = useState([]);
  const [availableBadges, setAvailableBadges] = useState([]);

  // Load leaderboard and gamification data
  useEffect(() => {
    const loadGameData = async () => {
      setLoading(true);
      try {
        const [leaderboardResponse, badgesResponse, availableBadgesResponse] =
          await Promise.all([
            gamificationAPI.getLeaderboard(),
            gamificationAPI.getUserBadges(user?.id || 1),
            gamificationAPI.getAvailableBadges(),
          ]);

        if (leaderboardResponse.data.success) {
          setRealLeaderboardData(leaderboardResponse.data.leaderboard);
        }

        if (badgesResponse.data.success) {
          setUserBadges(badgesResponse.data.badges || []);
        }

        if (availableBadgesResponse.data.success) {
          setAvailableBadges(
            availableBadgesResponse.data.available_badges || []
          );
        }
      } catch (error) {
        console.error("Error loading gamification data:", error);
        toast.error("Failed to load leaderboard data");
      } finally {
        setLoading(false);
      }
    };

    loadGameData();
  }, [selectedPeriod, user?.id]);

  // Mock leaderboard data
  const [leaderboardData] = useState({
    weekly: [
      {
        id: 1,
        name: "Alex Johnson",
        avatar: "AJ",
        points: 2847,
        streak: 12,
        level: "Advanced",
        badge: "🔥",
        change: "+2",
      },
      {
        id: 2,
        name: "Priya Sharma",
        avatar: "PS",
        points: 2634,
        streak: 18,
        level: "Advanced",
        badge: "⭐",
        change: "0",
      },
      {
        id: 3,
        name: "Raj Kumar",
        avatar: "RK",
        points: 2521,
        streak: 9,
        level: "Intermediate",
        badge: "🚀",
        change: "+1",
      },
      {
        id: 4,
        name: "Sarah Chen",
        avatar: "SC",
        points: 2398,
        streak: 15,
        level: "Intermediate",
        badge: "💎",
        change: "-1",
      },
      {
        id: 5,
        name: "John Doe",
        avatar: "JD",
        points: 2156,
        streak: 7,
        level: "Beginner",
        badge: "🌟",
        change: "+3",
      },
      {
        id: 6,
        name: "Maria Garcia",
        avatar: "MG",
        points: 1987,
        streak: 11,
        level: "Intermediate",
        badge: "🎯",
        change: "-2",
      },
      {
        id: 7,
        name: "David Kim",
        avatar: "DK",
        points: 1834,
        streak: 6,
        level: "Beginner",
        badge: "🏆",
        change: "+1",
      },
      {
        id: 8,
        name: "Lisa Wang",
        avatar: "LW",
        points: 1756,
        streak: 14,
        level: "Intermediate",
        badge: "💫",
        change: "0",
      },
    ],
    monthly: [
      {
        id: 1,
        name: "Priya Sharma",
        avatar: "PS",
        points: 12847,
        streak: 28,
        level: "Advanced",
        badge: "👑",
        change: "+1",
      },
      {
        id: 2,
        name: "Alex Johnson",
        avatar: "AJ",
        points: 11634,
        streak: 25,
        level: "Advanced",
        badge: "🔥",
        change: "-1",
      },
      {
        id: 3,
        name: "Sarah Chen",
        avatar: "SC",
        points: 10521,
        streak: 22,
        level: "Advanced",
        badge: "💎",
        change: "0",
      },
      {
        id: 4,
        name: "Raj Kumar",
        avatar: "RK",
        points: 9398,
        streak: 19,
        level: "Intermediate",
        badge: "🚀",
        change: "+2",
      },
      {
        id: 5,
        name: "Maria Garcia",
        avatar: "MG",
        points: 8756,
        streak: 17,
        level: "Intermediate",
        badge: "🎯",
        change: "+1",
      },
    ],
    allTime: [
      {
        id: 1,
        name: "Sarah Chen",
        avatar: "SC",
        points: 45847,
        streak: 89,
        level: "Expert",
        badge: "🏆",
        change: "0",
      },
      {
        id: 2,
        name: "Priya Sharma",
        avatar: "PS",
        points: 42634,
        streak: 67,
        level: "Advanced",
        badge: "👑",
        change: "+1",
      },
      {
        id: 3,
        name: "Alex Johnson",
        avatar: "AJ",
        points: 38521,
        streak: 54,
        level: "Advanced",
        badge: "🔥",
        change: "-1",
      },
    ],
  });

  // Mock achievements data
  const [achievements] = useState([
    {
      id: 1,
      name: "First Steps",
      description: "Complete your first lesson",
      icon: "🎯",
      category: "Beginner",
      points: 50,
      rarity: "Common",
      earned: true,
      earnedDate: "2024-01-01",
      progress: 100,
      total: 1,
    },
    {
      id: 2,
      name: "Week Warrior",
      description: "Study for 7 consecutive days",
      icon: "🔥",
      category: "Streak",
      points: 200,
      rarity: "Uncommon",
      earned: true,
      earnedDate: "2024-01-08",
      progress: 100,
      total: 7,
    },
    {
      id: 3,
      name: "Vocabulary Master",
      description: "Learn 100 new words",
      icon: "📚",
      category: "Learning",
      points: 300,
      rarity: "Rare",
      earned: true,
      earnedDate: "2024-01-15",
      progress: 100,
      total: 100,
    },
    {
      id: 4,
      name: "Perfect Score",
      description: "Get 100% on any quiz",
      icon: "⭐",
      category: "Performance",
      points: 150,
      rarity: "Uncommon",
      earned: true,
      earnedDate: "2024-01-12",
      progress: 100,
      total: 1,
    },
    {
      id: 5,
      name: "Social Butterfly",
      description: "Share your progress 5 times",
      icon: "🤝",
      category: "Social",
      points: 250,
      rarity: "Rare",
      earned: false,
      progress: 60,
      total: 5,
    },
    {
      id: 6,
      name: "Night Owl",
      description: "Study after 10 PM for 5 days",
      icon: "🦉",
      category: "Dedication",
      points: 400,
      rarity: "Epic",
      earned: false,
      progress: 20,
      total: 5,
    },
    {
      id: 7,
      name: "Telugu Master",
      description: "Complete all Telugu courses",
      icon: "👑",
      category: "Mastery",
      points: 1000,
      rarity: "Legendary",
      earned: false,
      progress: 25,
      total: 10,
    },
    {
      id: 8,
      name: "Speed Demon",
      description: "Complete 50 lessons in one day",
      icon: "⚡",
      category: "Challenge",
      points: 500,
      rarity: "Epic",
      earned: false,
      progress: 0,
      total: 50,
    },
  ]);

  // Mock user stats
  const [userStats] = useState({
    currentRank: 15,
    totalPoints: 1456,
    weeklyRank: 8,
    monthlyRank: 12,
    streak: 7,
    level: "Intermediate",
    nextLevelPoints: 2000,
    achievementsEarned: 4,
    totalAchievements: 8,
  });

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handlePeriodChange = (event) => {
    setSelectedPeriod(event.target.value);
  };

  const handleAchievementClick = (achievement) => {
    setSelectedAchievement(achievement);
    setAchievementDialogOpen(true);
  };

  const getRankColor = (rank) => {
    if (rank === 1) return theme.palette.warning.main; // Gold
    if (rank === 2) return theme.palette.grey[400]; // Silver
    if (rank === 3) return "#CD7F32"; // Bronze
    return theme.palette.text.secondary;
  };

  const getRankIcon = (rank) => {
    if (rank === 1)
      return <EmojiEvents sx={{ color: theme.palette.warning.main }} />;
    if (rank === 2)
      return <WorkspacePremium sx={{ color: theme.palette.grey[400] }} />;
    if (rank === 3) return <EmojiEvents sx={{ color: "#CD7F32" }} />;
    return <Person />;
  };

  const getRarityColor = (rarity) => {
    switch (rarity) {
      case "Common":
        return theme.palette.grey[500];
      case "Uncommon":
        return theme.palette.success.main;
      case "Rare":
        return theme.palette.info.main;
      case "Epic":
        return theme.palette.secondary.main;
      case "Legendary":
        return theme.palette.warning.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const shareProgress = () => {
    const text = `🎉 I'm ranked #${userStats.currentRank} with ${userStats.totalPoints} points on the Telugu Learning Platform! Join me in learning Telugu! 🇮🇳`;

    if (navigator.share) {
      navigator.share({
        title: "My Telugu Learning Progress",
        text: text,
        url: window.location.origin,
      });
    } else {
      navigator.clipboard.writeText(text);
      toast.success("Progress copied to clipboard!");
    }
  };

  // Use real data if available, otherwise fallback to mock data
  const currentLeaderboardData =
    realLeaderboardData || leaderboardData[selectedPeriod];

  if (loading) {
    return (
      <Container
        maxWidth="lg"
        sx={{
          py: 3,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: "60vh",
        }}
      >
        <CircularProgress size={60} />
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: { xs: 2, sm: 3, md: 4 }, px: { xs: 2, sm: 3 } }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Header */}
        <Stack
          direction={{ xs: "column", sm: "row" }}
          justifyContent="space-between"
          alignItems={{ xs: "flex-start", sm: "center" }}
          spacing={{ xs: 2, sm: 0 }}
          sx={{ mb: 3 }}
        >
          <Typography variant={isMobile ? "h5" : "h4"} fontWeight="bold">
            🏆 Leaderboard & Achievements
          </Typography>
          <Button
            variant="outlined"
            size={isMobile ? "small" : "medium"}
            startIcon={!isMobile && <Share />}
            onClick={shareProgress}
            fullWidth={isMobile}
          >
            Share Progress
          </Button>
        </Stack>

        {/* User Stats Overview */}
        <Card
          sx={{
            mb: { xs: 2, sm: 3 },
            background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
          }}
        >
          <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
            <Grid container spacing={{ xs: 2, sm: 3 }} alignItems="center">
              <Grid item xs={12} sm="auto" sx={{ textAlign: { xs: "center", sm: "left" } }}>
                <Avatar
                  sx={{
                    width: { xs: 64, sm: 80 },
                    height: { xs: 64, sm: 80 },
                    bgcolor: "rgba(255,255,255,0.2)",
                    fontSize: { xs: "1.5rem", sm: "2rem" },
                    mx: { xs: "auto", sm: 0 },
                  }}
                >
                  {user?.firstName?.[0] || "U"}
                  {user?.lastName?.[0] || "U"}
                </Avatar>
              </Grid>

              <Grid item xs={12} sm>
                <Typography
                  variant={isMobile ? "h6" : "h5"}
                  sx={{ color: "white", fontWeight: "bold", textAlign: { xs: "center", sm: "left" } }}
                >
                  Your Progress
                </Typography>
                <Stack
                  direction="row"
                  spacing={1}
                  flexWrap="wrap"
                  justifyContent={{ xs: "center", sm: "flex-start" }}
                  sx={{ mt: 1, gap: 1 }}
                >
                  <Chip
                    icon={<EmojiEvents sx={{ fontSize: { xs: 16, sm: 20 } }} />}
                    label={`Rank #${userStats.currentRank}`}
                    size={isMobile ? "small" : "medium"}
                    sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
                  />
                  <Chip
                    icon={<Star sx={{ fontSize: { xs: 16, sm: 20 } }} />}
                    label={`${userStats.totalPoints} Points`}
                    size={isMobile ? "small" : "medium"}
                    sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
                  />
                  <Chip
                    icon={<LocalFireDepartment sx={{ fontSize: { xs: 16, sm: 20 } }} />}
                    label={`${userStats.streak} Day Streak`}
                    size={isMobile ? "small" : "medium"}
                    sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
                  />
                  <Chip
                    icon={<School sx={{ fontSize: { xs: 16, sm: 20 } }} />}
                    label={userStats.level}
                    size={isMobile ? "small" : "medium"}
                    sx={{ bgcolor: "rgba(255,255,255,0.2)", color: "white" }}
                  />
                </Stack>

                <Box sx={{ mt: 2 }}>
                  <Typography variant={isMobile ? "caption" : "body2"} sx={{ color: "white", mb: 1 }}>
                    Progress to next level: {userStats.totalPoints}/
                    {userStats.nextLevelPoints}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={
                      (userStats.totalPoints / userStats.nextLevelPoints) * 100
                    }
                    sx={{
                      height: { xs: 6, sm: 8 },
                      borderRadius: 4,
                      bgcolor: "rgba(255,255,255,0.2)",
                      "& .MuiLinearProgress-bar": {
                        bgcolor: "white",
                      },
                    }}
                  />
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Paper sx={{ mb: { xs: 2, sm: 3 } }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant={isMobile ? "scrollable" : "fullWidth"}
            scrollButtons="auto"
          >
            <Tab 
              icon={<Timeline />} 
              label="Leaderboard" 
              iconPosition={isMobile ? "start" : "top"}
              sx={{ fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
            />
            <Tab 
              icon={<EmojiEvents />} 
              label="Achievements" 
              iconPosition={isMobile ? "start" : "top"}
              sx={{ fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
            />
            <Tab 
              icon={<TrendingUp />} 
              label="Statistics" 
              iconPosition={isMobile ? "start" : "top"}
              sx={{ fontSize: { xs: "0.8rem", sm: "0.875rem" } }}
            />
          </Tabs>
        </Paper>

        {/* Tab Panels */}
        <TabPanel value={activeTab} index={0}>
          {/* Leaderboard */}
          <Card>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Stack
                direction={{ xs: "column", sm: "row" }}
                justifyContent="space-between"
                alignItems={{ xs: "stretch", sm: "center" }}
                spacing={{ xs: 2, sm: 0 }}
                sx={{ mb: 3 }}
              >
                <Typography variant={isMobile ? "subtitle1" : "h6"}>Rankings</Typography>
                <FormControl size="small" sx={{ minWidth: { xs: "100%", sm: 120 } }}>
                  <InputLabel>Period</InputLabel>
                  <Select
                    value={selectedPeriod}
                    onChange={handlePeriodChange}
                    label="Period"
                  >
                    <MenuItem value="weekly">Weekly</MenuItem>
                    <MenuItem value="monthly">Monthly</MenuItem>
                    <MenuItem value="allTime">All Time</MenuItem>
                  </Select>
                </FormControl>
              </Stack>

              <TableContainer>
                <Table size={isMobile ? "small" : "medium"}>
                  <TableHead>
                    <TableRow>
                      <TableCell>Rank</TableCell>
                      <TableCell>User</TableCell>
                      {!isMobile && <TableCell align="center">Level</TableCell>}
                      {!isMobile && <TableCell align="center">Streak</TableCell>}
                      <TableCell align="right">Points</TableCell>
                      {!isMobile && <TableCell align="center">Change</TableCell>}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    <AnimatePresence>
                      {currentLeaderboardData.map((user, index) => (
                        <motion.tr
                          key={user.id}
                          component={TableRow}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: 20 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          sx={{
                            bgcolor:
                              user.name === "John Doe"
                                ? theme.palette.action.selected
                                : "transparent",
                            "&:hover": {
                              bgcolor: theme.palette.action.hover,
                            },
                          }}
                        >
                          <TableCell>
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                              }}
                            >
                              {getRankIcon(index + 1)}
                              <Typography
                                variant="h6"
                                sx={{
                                  color: getRankColor(index + 1),
                                  fontWeight: index < 3 ? "bold" : "normal",
                                }}
                              >
                                #{index + 1}
                              </Typography>
                            </Box>
                          </TableCell>

                          <TableCell>
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 2,
                              }}
                            >
                              <Badge
                                badgeContent={user.badge}
                                anchorOrigin={{
                                  vertical: "bottom",
                                  horizontal: "right",
                                }}
                              >
                                <Avatar
                                  sx={{ bgcolor: theme.palette.primary.main }}
                                >
                                  {user.avatar}
                                </Avatar>
                              </Badge>
                              <Typography variant="body1" fontWeight="medium">
                                {user.name}
                              </Typography>
                            </Box>
                          </TableCell>

                          <TableCell align="center">
                            <Chip
                              label={user.level}
                              size="small"
                              color={
                                user.level === "Expert"
                                  ? "error"
                                  : user.level === "Advanced"
                                  ? "warning"
                                  : user.level === "Intermediate"
                                  ? "info"
                                  : "default"
                              }
                            />
                          </TableCell>

                          <TableCell align="center">
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                gap: 0.5,
                              }}
                            >
                              <LocalFireDepartment
                                sx={{
                                  color: theme.palette.error.main,
                                  fontSize: 18,
                                }}
                              />
                              <Typography variant="body2">
                                {user.streak}
                              </Typography>
                            </Box>
                          </TableCell>

                          <TableCell align="right">
                            <Typography variant="h6" fontWeight="bold">
                              {user.points.toLocaleString()}
                            </Typography>
                          </TableCell>

                          <TableCell align="center">
                            <Chip
                              label={user.change}
                              size="small"
                              color={
                                user.change.startsWith("+")
                                  ? "success"
                                  : user.change.startsWith("-")
                                  ? "error"
                                  : "default"
                              }
                              variant="outlined"
                            />
                          </TableCell>
                        </motion.tr>
                      ))}
                    </AnimatePresence>
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {/* Achievements */}
          <Grid container spacing={3}>
            {achievements.map((achievement) => (
              <Grid item xs={12} sm={6} md={4} key={achievement.id}>
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Card
                    sx={{
                      cursor: "pointer",
                      opacity: achievement.earned ? 1 : 0.7,
                      border: achievement.earned ? 2 : 1,
                      borderColor: achievement.earned
                        ? getRarityColor(achievement.rarity)
                        : theme.palette.divider,
                      position: "relative",
                      overflow: "visible",
                    }}
                    onClick={() => handleAchievementClick(achievement)}
                  >
                    {achievement.earned && (
                      <Box
                        sx={{
                          position: "absolute",
                          top: -8,
                          right: -8,
                          zIndex: 1,
                        }}
                      >
                        <Avatar
                          sx={{
                            width: 32,
                            height: 32,
                            bgcolor: theme.palette.success.main,
                            fontSize: "1rem",
                          }}
                        >
                          ✓
                        </Avatar>
                      </Box>
                    )}

                    <CardContent sx={{ textAlign: "center" }}>
                      <Typography variant="h2" sx={{ mb: 1 }}>
                        {achievement.icon}
                      </Typography>

                      <Typography variant="h6" gutterBottom>
                        {achievement.name}
                      </Typography>

                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 2 }}
                      >
                        {achievement.description}
                      </Typography>

                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "center",
                          gap: 1,
                          mb: 2,
                        }}
                      >
                        <Chip
                          label={achievement.category}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                        <Chip
                          label={achievement.rarity}
                          size="small"
                          sx={{
                            bgcolor: getRarityColor(achievement.rarity),
                            color: "white",
                          }}
                        />
                      </Box>

                      <Typography
                        variant="body2"
                        fontWeight="bold"
                        sx={{ mb: 1 }}
                      >
                        {achievement.points} Points
                      </Typography>

                      {!achievement.earned && (
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Progress: {achievement.progress}%
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={achievement.progress}
                            sx={{ mt: 1, height: 4, borderRadius: 2 }}
                          />
                        </Box>
                      )}

                      {achievement.earned && (
                        <Typography
                          variant="caption"
                          color="success.main"
                          fontWeight="bold"
                        >
                          Earned on{" "}
                          {new Date(
                            achievement.earnedDate
                          ).toLocaleDateString()}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {/* Statistics */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Ranking History
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                          <Timeline />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary="Current Rank"
                        secondary={`#${userStats.currentRank} overall`}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: theme.palette.secondary.main }}>
                          <TrendingUp />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary="Weekly Rank"
                        secondary={`#${userStats.weeklyRank} this week`}
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: theme.palette.success.main }}>
                          <Group />
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary="Monthly Rank"
                        secondary={`#${userStats.monthlyRank} this month`}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Achievement Progress
                  </Typography>

                  <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" gutterBottom>
                      Achievements Earned: {userStats.achievementsEarned}/
                      {userStats.totalAchievements}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={
                        (userStats.achievementsEarned /
                          userStats.totalAchievements) *
                        100
                      }
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  <Box sx={{ textAlign: "center" }}>
                    <Typography variant="h3" color="primary" gutterBottom>
                      {userStats.achievementsEarned}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Achievements Unlocked
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </motion.div>

      {/* Achievement Detail Dialog */}
      <Dialog
        open={achievementDialogOpen}
        onClose={() => setAchievementDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        {selectedAchievement && (
          <>
            <DialogTitle sx={{ textAlign: "center", pb: 1 }}>
              <Typography variant="h3" sx={{ mb: 1 }}>
                {selectedAchievement.icon}
              </Typography>
              <Typography variant="h5" gutterBottom>
                {selectedAchievement.name}
              </Typography>
              <Chip
                label={selectedAchievement.rarity}
                sx={{
                  bgcolor: getRarityColor(selectedAchievement.rarity),
                  color: "white",
                  fontWeight: "bold",
                }}
              />
            </DialogTitle>

            <DialogContent>
              <Typography
                variant="body1"
                gutterBottom
                sx={{ textAlign: "center" }}
              >
                {selectedAchievement.description}
              </Typography>

              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  gap: 2,
                  my: 2,
                }}
              >
                <Chip
                  icon={<Star />}
                  label={`${selectedAchievement.points} Points`}
                  color="primary"
                />
                <Chip
                  icon={<AutoAwesome />}
                  label={selectedAchievement.category}
                  variant="outlined"
                />
              </Box>

              {selectedAchievement.earned ? (
                <Box sx={{ textAlign: "center", mt: 2 }}>
                  <Celebration
                    sx={{
                      fontSize: 48,
                      color: theme.palette.success.main,
                      mb: 1,
                    }}
                  />
                  <Typography variant="h6" color="success.main" gutterBottom>
                    Achievement Unlocked!
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Earned on{" "}
                    {new Date(
                      selectedAchievement.earnedDate
                    ).toLocaleDateString()}
                  </Typography>
                </Box>
              ) : (
                <Box>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    gutterBottom
                  >
                    Progress: {selectedAchievement.progress}% (
                    {Math.floor(
                      (selectedAchievement.progress *
                        selectedAchievement.total) /
                        100
                    )}
                    /{selectedAchievement.total})
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={selectedAchievement.progress}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              )}
            </DialogContent>

            <DialogActions>
              <Button onClick={() => setAchievementDialogOpen(false)}>
                Close
              </Button>
              {selectedAchievement.earned && (
                <Button variant="contained" startIcon={<Share />}>
                  Share Achievement
                </Button>
              )}
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default LeaderboardPage;
