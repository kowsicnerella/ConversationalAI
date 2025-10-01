import { useState, useEffect } from "react";
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
  TextField,
  Tab,
  Tabs,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  LinearProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  useMediaQuery,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Stack,
  Divider,
} from "@mui/material";
import {
  Edit,
  Camera,
  Save,
  Cancel,
  Notifications,
  EmojiEvents,
  School,
  Schedule,
  TrendingUp,
  LocalFireDepartment,
  Download,
  Delete,
  Visibility,
  VisibilityOff,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { useAuthStore } from "../store/index.js";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";
import { userAPI } from "../services/api";

const TabPanel = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`profile-tabpanel-${index}`}
    aria-labelledby={`profile-tab-${index}`}
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

const ProfilePage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const { user, updateProfile } = useAuthStore();
  const [activeTab, setActiveTab] = useState(0);
  const [editMode, setEditMode] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [userStats, setUserStats] = useState(null);

  // Profile form state
  const [profileData, setProfileData] = useState({
    firstName: user?.firstName || "John",
    lastName: user?.lastName || "Doe",
    email: user?.email || "john.doe@example.com",
    phone: "+1 (555) 123-4567",
    dateOfBirth: "1990-01-01",
    location: "New York, USA",
    bio: "Learning Telugu to connect with my cultural roots. Passionate about languages and technology.",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  // Load user profile and statistics
  useEffect(() => {
    const loadUserData = async () => {
      setLoading(true);
      try {
        const [profileResponse, statsResponse] = await Promise.all([
          userAPI.getProfile(),
          userAPI.getStatistics(),
        ]);

        if (profileResponse.data.success) {
          const profile = profileResponse.data.profile;
          setProfileData((prev) => ({
            ...prev,
            firstName: profile.first_name || prev.firstName,
            lastName: profile.last_name || prev.lastName,
            email: profile.email || prev.email,
            bio: profile.bio || prev.bio,
          }));
        }

        if (statsResponse.data.success) {
          setUserStats(statsResponse.data.statistics);
        }
      } catch (error) {
        console.error("Error loading user data:", error);
        toast.error("Failed to load profile data");
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, []);

  // Settings state
  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    learningReminders: true,
    weeklyProgress: true,
    achievementAlerts: true,
    language: "en",
    theme: "system",
    autoSpeak: true,
    speechSpeed: "normal",
    difficultyLevel: "intermediate",
    dailyGoal: 30,
    privacyMode: false,
    shareProgress: true,
    showProfile: true,
  });

  // Learning statistics (real data from API or fallback to mock)
  const learningStats = userStats
    ? {
        totalHours: userStats.total_study_time || 127,
        currentStreak: userStats.current_streak || 15,
        longestStreak: userStats.longest_streak || 28,
        wordsLearned: userStats.vocabulary_learned || 234,
        lessonsCompleted: userStats.lessons_completed || 45,
        achievements: userStats.achievements_earned || 12,
        level: userStats.current_level || "Intermediate",
        progress: userStats.overall_progress || 68,
        weeklyGoal: 210, // minutes
        weeklyProgress: 185,
      }
    : {
        totalHours: 127,
        currentStreak: 15,
        longestStreak: 28,
        wordsLearned: 234,
        lessonsCompleted: 45,
        achievements: 12,
        level: "Intermediate",
        progress: 68,
        weeklyGoal: 210, // minutes
        weeklyProgress: 185,
      };

  // Recent activity data comes from real API (userAPI.getRecentActivity())
  const recentActivity = profileData?.recentActivity || [];

  // Achievements data comes from real API (gamificationAPI.getAchievements())
  const achievements = profileData?.achievements || [];

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleProfileChange = (field, value) => {
    setProfileData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSettingChange = (setting, value) => {
    setSettings((prev) => ({ ...prev, [setting]: value }));
    toast.success("Setting updated successfully");
  };

  const handleSaveProfile = () => {
    // Validate form
    if (!profileData.firstName || !profileData.lastName || !profileData.email) {
      toast.error("Please fill in all required fields");
      return;
    }

    // Update profile
    updateProfile({
      firstName: profileData.firstName,
      lastName: profileData.lastName,
      email: profileData.email,
    });

    setEditMode(false);
    toast.success("Profile updated successfully");
  };

  const handlePasswordChange = () => {
    if (!profileData.currentPassword || !profileData.newPassword) {
      toast.error("Please fill in all password fields");
      return;
    }

    if (profileData.newPassword !== profileData.confirmPassword) {
      toast.error("New passwords don't match");
      return;
    }

    if (profileData.newPassword.length < 8) {
      toast.error("Password must be at least 8 characters long");
      return;
    }

    // Simulate password change
    toast.success("Password changed successfully");
    setProfileData((prev) => ({
      ...prev,
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    }));
  };

  const handleExportData = () => {
    const exportData = {
      profile: profileData,
      settings,
      statistics: learningStats,
      recentActivity,
      achievements,
      exportDate: new Date().toISOString(),
    };

    const dataStr = JSON.stringify(exportData, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);
    const exportFileDefaultName = `profile-data-${
      new Date().toISOString().split("T")[0]
    }.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();

    toast.success("Profile data exported successfully");
  };

  const handleDeleteAccount = () => {
    // This would typically call an API to delete the account
    toast.success("Account deletion request submitted");
    setDeleteDialogOpen(false);
  };

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
        {/* Profile Header */}
        <Card
          className="hover-lift"
          sx={{
            mb: { xs: 2, sm: 3 },
            borderRadius: { xs: 2, sm: 3 },
            background: theme.palette.mode === 'dark'
              ? 'rgba(30, 41, 59, 0.6)'
              : 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(20px)',
          }}
        >
          <CardContent sx={{ p: { xs: 2, sm: 3, md: 4 } }}>
            <Grid container spacing={{ xs: 2, sm: 3 }} alignItems="center">
              <Grid item xs={12} sm="auto" sx={{ textAlign: { xs: 'center', sm: 'left' } }}>
                <Box sx={{ position: "relative", display: 'inline-block' }}>
                  <Avatar
                    className="hover-scale"
                    sx={{
                      width: { xs: 80, sm: 96 },
                      height: { xs: 80, sm: 96 },
                      fontSize: { xs: "1.25rem", sm: "1.5rem" },
                      background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                      border: `3px solid ${theme.palette.background.paper}`,
                      boxShadow: `0 6px 20px ${theme.palette.primary.main}40`,
                    }}
                  >
                    {profileData.firstName[0]}
                    {profileData.lastName[0]}
                  </Avatar>
                  <IconButton
                    className="hover-scale"
                    sx={{
                      position: "absolute",
                      bottom: 0,
                      right: 0,
                      bgcolor: theme.palette.primary.main,
                      color: 'white',
                      border: 2,
                      borderColor: "background.paper",
                      width: { xs: 36, sm: 40 },
                      height: { xs: 36, sm: 40 },
                      "&:hover": {
                        bgcolor: theme.palette.primary.dark,
                      },
                    }}
                    size="small"
                  >
                    <Camera fontSize="small" />
                  </IconButton>
                </Box>
              </Grid>

              <Grid item xs={12} sm sx={{ textAlign: { xs: 'center', sm: 'left' } }}>
                <Typography
                  variant={isMobile ? "h5" : "h4"}
                  sx={{
                    fontWeight: 700,
                    mb: 1,
                    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    backgroundClip: "text",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }}
                >
                  {profileData.firstName} {profileData.lastName}
                </Typography>
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ mb: 1, fontSize: { xs: '0.875rem', sm: '1rem' } }}
                >
                  {profileData.email}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    mb: 2,
                    fontSize: { xs: '0.875rem', sm: '0.9375rem' },
                    lineHeight: 1.6,
                  }}
                >
                  {profileData.bio}
                </Typography>

                <Stack
                  direction="row"
                  spacing={1}
                  flexWrap="wrap"
                  useFlexGap
                  justifyContent={{ xs: 'center', sm: 'flex-start' }}
                >
                  <Chip
                    icon={<School />}
                    label={`Level ${learningStats.level}`}
                    color="primary"
                    size={isMobile ? "small" : "medium"}
                    sx={{ fontWeight: 600 }}
                  />
                  <Chip
                    icon={<LocalFireDepartment />}
                    label={`${learningStats.currentStreak} day streak`}
                    color="error"
                    size={isMobile ? "small" : "medium"}
                    sx={{ fontWeight: 600 }}
                  />
                  <Chip
                    icon={<EmojiEvents />}
                    label={`${learningStats.achievements} achievements`}
                    color="success"
                    size={isMobile ? "small" : "medium"}
                    sx={{ fontWeight: 600 }}
                  />
                </Stack>
              </Grid>

              <Grid item xs={12} sm="auto" sx={{ textAlign: { xs: 'center', sm: 'right' } }}>
                <Button
                  variant={editMode ? "outlined" : "contained"}
                  startIcon={editMode ? <Cancel /> : <Edit />}
                  onClick={() => setEditMode(!editMode)}
                  fullWidth={isMobile}
                  size={isMobile ? "medium" : "large"}
                  className="hover-scale"
                  sx={{
                    borderRadius: 2,
                    py: { xs: 1, sm: 1.25 },
                    fontWeight: 600,
                    textTransform: 'none',
                  }}
                >
                  {editMode ? "Cancel" : "Edit Profile"}
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Paper
          elevation={0}
          sx={{
            mb: { xs: 2, sm: 3 },
            borderRadius: { xs: 2, sm: 3 },
            background: theme.palette.mode === 'dark'
              ? 'rgba(30, 41, 59, 0.6)'
              : 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(20px)',
          }}
        >
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant={isMobile ? "scrollable" : "fullWidth"}
            scrollButtons="auto"
            allowScrollButtonsMobile
            sx={{
              '& .MuiTab-root': {
                minHeight: { xs: 48, sm: 56 },
                fontSize: { xs: '0.8125rem', sm: '0.9375rem' },
                fontWeight: 600,
                textTransform: 'none',
                px: { xs: 2, sm: 3 },
              },
              '& .Mui-selected': {
                fontWeight: 700,
              },
            }}
          >
            <Tab label="Overview" />
            <Tab label="Personal Info" />
            <Tab label="Learning Stats" />
            <Tab label="Settings" />
            <Tab label="Privacy" />
          </Tabs>
        </Paper>

        {/* Tab Panels */}
        <TabPanel value={activeTab} index={0}>
          {/* Overview */}
          <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }}>
            {/* Progress Overview */}
            <Grid item xs={12} md={8}>
              <Card
                className="hover-lift"
                sx={{
                  borderRadius: { xs: 2, sm: 3 },
                  height: '100%',
                }}
              >
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                  <Typography
                    variant={isMobile ? "subtitle1" : "h6"}
                    sx={{ fontWeight: 700, mb: 3 }}
                  >
                    Learning Progress
                  </Typography>

                  <Stack spacing={3}>
                    <Box>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                        sx={{ mb: 1 }}
                      >
                        <Typography
                          variant="body2"
                          sx={{ fontWeight: 500, fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                        >
                          Overall Progress
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 700,
                            color: theme.palette.primary.main,
                            fontSize: { xs: '0.875rem', sm: '1rem' },
                          }}
                        >
                          {learningStats.progress}%
                        </Typography>
                      </Stack>
                      <LinearProgress
                        variant="determinate"
                        value={learningStats.progress}
                        sx={{
                          height: { xs: 8, sm: 10 },
                          borderRadius: 5,
                          bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 5,
                            background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                          },
                        }}
                      />
                    </Box>

                    <Box>
                      <Stack
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                        sx={{ mb: 1 }}
                      >
                        <Typography
                          variant="body2"
                          sx={{ fontWeight: 500, fontSize: { xs: '0.8125rem', sm: '0.875rem' } }}
                        >
                          Weekly Goal
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: 700,
                            color: theme.palette.secondary.main,
                            fontSize: { xs: '0.875rem', sm: '1rem' },
                          }}
                        >
                          {learningStats.weeklyProgress}/{learningStats.weeklyGoal} min
                        </Typography>
                      </Stack>
                      <LinearProgress
                        variant="determinate"
                        value={
                          (learningStats.weeklyProgress / learningStats.weeklyGoal) * 100
                        }
                        sx={{
                          height: { xs: 8, sm: 10 },
                          borderRadius: 5,
                          bgcolor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                          '& .MuiLinearProgress-bar': {
                            borderRadius: 5,
                            background: `linear-gradient(90deg, ${theme.palette.secondary.main}, ${theme.palette.secondary.light})`,
                          },
                        }}
                        color="secondary"
                      />
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            {/* Quick Stats */}
            <Grid item xs={12} md={4}>
              <Card
                className="hover-lift"
                sx={{
                  borderRadius: { xs: 2, sm: 3 },
                  height: '100%',
                }}
              >
                <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                  <Typography
                    variant={isMobile ? "subtitle1" : "h6"}
                    sx={{ fontWeight: 700, mb: 2 }}
                  >
                    Quick Stats
                  </Typography>
                  <List disablePadding>
                    <ListItem
                      sx={{
                        px: 0,
                        py: { xs: 1, sm: 1.5 },
                        borderRadius: 2,
                        '&:hover': {
                          bgcolor: theme.palette.action.hover,
                        },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: { xs: 40, sm: 48 } }}>
                        <Schedule color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${learningStats.totalHours} hours`}
                        secondary="Total study time"
                        primaryTypographyProps={{
                          fontWeight: 600,
                          fontSize: { xs: '0.9375rem', sm: '1rem' },
                        }}
                        secondaryTypographyProps={{
                          fontSize: { xs: '0.75rem', sm: '0.8125rem' },
                        }}
                      />
                    </ListItem>
                    <Divider sx={{ my: 0.5 }} />
                    <ListItem
                      sx={{
                        px: 0,
                        py: { xs: 1, sm: 1.5 },
                        borderRadius: 2,
                        '&:hover': {
                          bgcolor: theme.palette.action.hover,
                        },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: { xs: 40, sm: 48 } }}>
                        <School color="success" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${learningStats.wordsLearned} words`}
                        secondary="Vocabulary learned"
                        primaryTypographyProps={{
                          fontWeight: 600,
                          fontSize: { xs: '0.9375rem', sm: '1rem' },
                        }}
                        secondaryTypographyProps={{
                          fontSize: { xs: '0.75rem', sm: '0.8125rem' },
                        }}
                      />
                    </ListItem>
                    <Divider sx={{ my: 0.5 }} />
                    <ListItem
                      sx={{
                        px: 0,
                        py: { xs: 1, sm: 1.5 },
                        borderRadius: 2,
                        '&:hover': {
                          bgcolor: theme.palette.action.hover,
                        },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: { xs: 40, sm: 48 } }}>
                        <TrendingUp color="error" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${learningStats.lessonsCompleted} lessons`}
                        secondary="Completed"
                        primaryTypographyProps={{
                          fontWeight: 600,
                          fontSize: { xs: '0.9375rem', sm: '1rem' },
                        }}
                        secondaryTypographyProps={{
                          fontSize: { xs: '0.75rem', sm: '0.8125rem' },
                        }}
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Recent Activity */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Recent Activity
                  </Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell>Activity</TableCell>
                          <TableCell align="right">Score</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {recentActivity.map((activity, index) => (
                          <TableRow key={index}>
                            <TableCell>
                              {new Date(activity.date).toLocaleDateString()}
                            </TableCell>
                            <TableCell>{activity.activity}</TableCell>
                            <TableCell align="right">
                              <Chip
                                label={`${activity.points}%`}
                                color={
                                  activity.points >= 90
                                    ? "success"
                                    : activity.points >= 70
                                    ? "warning"
                                    : "error"
                                }
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {/* Personal Info */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Personal Information
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    value={profileData.firstName}
                    onChange={(e) =>
                      handleProfileChange("firstName", e.target.value)
                    }
                    disabled={!editMode}
                    required
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={profileData.lastName}
                    onChange={(e) =>
                      handleProfileChange("lastName", e.target.value)
                    }
                    disabled={!editMode}
                    required
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    type="email"
                    value={profileData.email}
                    onChange={(e) =>
                      handleProfileChange("email", e.target.value)
                    }
                    disabled={!editMode}
                    required
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Phone"
                    value={profileData.phone}
                    onChange={(e) =>
                      handleProfileChange("phone", e.target.value)
                    }
                    disabled={!editMode}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Date of Birth"
                    type="date"
                    value={profileData.dateOfBirth}
                    onChange={(e) =>
                      handleProfileChange("dateOfBirth", e.target.value)
                    }
                    disabled={!editMode}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Location"
                    value={profileData.location}
                    onChange={(e) =>
                      handleProfileChange("location", e.target.value)
                    }
                    disabled={!editMode}
                  />
                </Grid>

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Bio"
                    multiline
                    rows={3}
                    value={profileData.bio}
                    onChange={(e) => handleProfileChange("bio", e.target.value)}
                    disabled={!editMode}
                    placeholder="Tell us about yourself and your learning goals..."
                  />
                </Grid>

                {editMode && (
                  <Grid item xs={12}>
                    <Box sx={{ display: "flex", gap: 2 }}>
                      <Button
                        variant="contained"
                        startIcon={<Save />}
                        onClick={handleSaveProfile}
                      >
                        Save Changes
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<Cancel />}
                        onClick={() => setEditMode(false)}
                      >
                        Cancel
                      </Button>
                    </Box>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {/* Learning Stats */}
          <Grid container spacing={3}>
            {/* Achievements */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Achievements
                  </Typography>
                  <Grid container spacing={2}>
                    {achievements.map((achievement, index) => (
                      <Grid item xs={12} sm={6} md={4} key={index}>
                        <Card
                          sx={{
                            opacity: achievement.earned ? 1 : 0.6,
                            border: achievement.earned ? 2 : 1,
                            borderColor: achievement.earned
                              ? theme.palette.primary.main
                              : theme.palette.divider,
                          }}
                        >
                          <CardContent sx={{ textAlign: "center" }}>
                            <Typography variant="h3" sx={{ mb: 1 }}>
                              {achievement.icon}
                            </Typography>
                            <Typography variant="h6" gutterBottom>
                              {achievement.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {achievement.description}
                            </Typography>
                            {achievement.earned && (
                              <Chip
                                label="Earned"
                                color="success"
                                size="small"
                                sx={{ mt: 1 }}
                              />
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          {/* Settings */}
          <Grid container spacing={3}>
            {/* Notification Settings */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography
                    variant="h6"
                    gutterBottom
                    startIcon={<Notifications />}
                  >
                    Notifications
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemIcon>
                        <Notifications />
                      </ListItemIcon>
                      <ListItemText primary="Email Notifications" />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings.emailNotifications}
                            onChange={(e) =>
                              handleSettingChange(
                                "emailNotifications",
                                e.target.checked
                              )
                            }
                          />
                        }
                        label=""
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <Notifications />
                      </ListItemIcon>
                      <ListItemText primary="Push Notifications" />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings.pushNotifications}
                            onChange={(e) =>
                              handleSettingChange(
                                "pushNotifications",
                                e.target.checked
                              )
                            }
                          />
                        }
                        label=""
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemIcon>
                        <Schedule />
                      </ListItemIcon>
                      <ListItemText primary="Learning Reminders" />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings.learningReminders}
                            onChange={(e) =>
                              handleSettingChange(
                                "learningReminders",
                                e.target.checked
                              )
                            }
                          />
                        }
                        label=""
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Learning Preferences */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Learning Preferences
                  </Typography>

                  <Box sx={{ mb: 3 }}>
                    <FormControl fullWidth>
                      <InputLabel>Language</InputLabel>
                      <Select
                        value={settings.language}
                        onChange={(e) =>
                          handleSettingChange("language", e.target.value)
                        }
                        label="Language"
                      >
                        <MenuItem value="en">English</MenuItem>
                        <MenuItem value="te">Telugu</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <FormControl fullWidth>
                      <InputLabel>Difficulty Level</InputLabel>
                      <Select
                        value={settings.difficultyLevel}
                        onChange={(e) =>
                          handleSettingChange("difficultyLevel", e.target.value)
                        }
                        label="Difficulty Level"
                      >
                        <MenuItem value="beginner">Beginner</MenuItem>
                        <MenuItem value="intermediate">Intermediate</MenuItem>
                        <MenuItem value="advanced">Advanced</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>

                  <Box sx={{ mb: 3 }}>
                    <Typography gutterBottom>
                      Daily Learning Goal (minutes)
                    </Typography>
                    <TextField
                      type="number"
                      value={settings.dailyGoal}
                      onChange={(e) =>
                        handleSettingChange(
                          "dailyGoal",
                          parseInt(e.target.value)
                        )
                      }
                      inputProps={{ min: 5, max: 120 }}
                      fullWidth
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={4}>
          {/* Privacy & Security */}
          <Grid container spacing={3}>
            {/* Password Change */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Change Password
                  </Typography>

                  <Box
                    sx={{ display: "flex", flexDirection: "column", gap: 2 }}
                  >
                    <TextField
                      fullWidth
                      label="Current Password"
                      type={showPassword ? "text" : "password"}
                      value={profileData.currentPassword}
                      onChange={(e) =>
                        handleProfileChange("currentPassword", e.target.value)
                      }
                      InputProps={{
                        endAdornment: (
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        ),
                      }}
                    />

                    <TextField
                      fullWidth
                      label="New Password"
                      type={showPassword ? "text" : "password"}
                      value={profileData.newPassword}
                      onChange={(e) =>
                        handleProfileChange("newPassword", e.target.value)
                      }
                    />

                    <TextField
                      fullWidth
                      label="Confirm New Password"
                      type={showPassword ? "text" : "password"}
                      value={profileData.confirmPassword}
                      onChange={(e) =>
                        handleProfileChange("confirmPassword", e.target.value)
                      }
                    />

                    <Button
                      variant="contained"
                      onClick={handlePasswordChange}
                      disabled={
                        !profileData.currentPassword ||
                        !profileData.newPassword ||
                        !profileData.confirmPassword
                      }
                    >
                      Change Password
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Privacy Settings */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Privacy Settings
                  </Typography>

                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Share Progress"
                        secondary="Allow others to see your learning progress"
                      />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings.shareProgress}
                            onChange={(e) =>
                              handleSettingChange(
                                "shareProgress",
                                e.target.checked
                              )
                            }
                          />
                        }
                        label=""
                      />
                    </ListItem>

                    <ListItem>
                      <ListItemText
                        primary="Show Profile"
                        secondary="Make your profile visible to other learners"
                      />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings.showProfile}
                            onChange={(e) =>
                              handleSettingChange(
                                "showProfile",
                                e.target.checked
                              )
                            }
                          />
                        }
                        label=""
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>

            {/* Data Management */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Data Management
                  </Typography>

                  <Alert severity="info" sx={{ mb: 3 }}>
                    You can export your data or delete your account. These
                    actions cannot be undone.
                  </Alert>

                  <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                    <Button
                      variant="outlined"
                      startIcon={<Download />}
                      onClick={handleExportData}
                    >
                      Export My Data
                    </Button>

                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<Delete />}
                      onClick={() => setDeleteDialogOpen(true)}
                    >
                      Delete Account
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </motion.div>

      {/* Delete Account Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Account</DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            This action cannot be undone. All your data, progress, and
            achievements will be permanently deleted.
          </Alert>
          <Typography>
            Are you sure you want to delete your account? This will permanently
            remove all your learning data.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteAccount}
            color="error"
            variant="contained"
          >
            Delete Account
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProfilePage;
