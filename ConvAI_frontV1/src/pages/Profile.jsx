import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
  Grid,
  Chip,
  Divider,
  LinearProgress,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from "@mui/material";
import {
  Edit,
  EmojiEvents,
  LocalFireDepartment,
  Star,
  TrendingUp,
  School,
  Verified,
  PhotoCamera,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import HoverCard from "../components/common/HoverCard";
import AnimatedButton from "../components/common/AnimatedButton";

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editedUser, setEditedUser] = useState({
    username: user?.username || "",
    email: user?.email || "",
    bio: user?.bio || "",
  });

  const stats = [
    {
      label: "Total Points",
      value: "12,450",
      icon: <EmojiEvents />,
      color: "#FFD700",
    },
    {
      label: "Current Streak",
      value: "15 days",
      icon: <LocalFireDepartment />,
      color: "#FF6B6B",
    },
    { label: "Level", value: "10", icon: <Star />, color: "#667eea" },
    { label: "Rank", value: "#4", icon: <TrendingUp />, color: "#43e97b" },
  ];

  const achievements = [
    {
      id: 1,
      name: "7 Day Streak",
      icon: "🔥",
      earned: true,
      date: "2025-09-15",
    },
    { id: 2, name: "First Quiz", icon: "📝", earned: true, date: "2025-08-20" },
    {
      id: 3,
      name: "100 Flashcards",
      icon: "🎴",
      earned: true,
      date: "2025-09-01",
    },
    {
      id: 4,
      name: "Chat Master",
      icon: "💬",
      earned: true,
      date: "2025-09-10",
    },
    {
      id: 5,
      name: "Vocabulary Pro",
      icon: "📚",
      earned: true,
      date: "2025-09-20",
    },
    { id: 6, name: "Perfect Score", icon: "⭐", earned: false, date: null },
    { id: 7, name: "30 Day Streak", icon: "🏆", earned: false, date: null },
    { id: 8, name: "Reading Champion", icon: "📖", earned: false, date: null },
  ];

  const skillProgress = [
    { skill: "Reading", level: 8, progress: 75, xp: 1200 },
    { skill: "Writing", level: 6, progress: 45, xp: 850 },
    { skill: "Listening", level: 7, progress: 60, xp: 980 },
    { skill: "Speaking", level: 5, progress: 30, xp: 620 },
    { skill: "Grammar", level: 9, progress: 85, xp: 1450 },
    { skill: "Vocabulary", level: 10, progress: 95, xp: 1680 },
  ];

  const recentActivity = [
    {
      type: "Quiz",
      title: "English Vocabulary Quiz",
      points: 150,
      date: "2 hours ago",
    },
    {
      type: "Flashcards",
      title: "Common Phrases",
      points: 80,
      date: "5 hours ago",
    },
    {
      type: "Reading",
      title: "Technology Article",
      points: 200,
      date: "1 day ago",
    },
    { type: "Chat", title: "AI Conversation", points: 50, date: "1 day ago" },
  ];

  const handleEditOpen = () => {
    setEditDialogOpen(true);
  };

  const handleEditClose = () => {
    setEditDialogOpen(false);
    setEditedUser({
      username: user?.username || "",
      email: user?.email || "",
      bio: user?.bio || "",
    });
  };

  const handleSaveProfile = () => {
    updateUser(editedUser);
    setEditDialogOpen(false);
  };

  const handleInputChange = (field) => (event) => {
    setEditedUser({ ...editedUser, [field]: event.target.value });
  };

  return (
    <PageTransition>
      <Box>
        {/* Header Section */}
        <Card sx={{ mb: 4, position: "relative", overflow: "visible" }}>
          <Box
            sx={{
              height: 150,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            }}
          />
          <CardContent sx={{ pt: 0 }}>
            <Box
              sx={{
                display: "flex",
                flexDirection: { xs: "column", md: "row" },
                gap: 3,
                alignItems: { md: "flex-end" },
              }}
            >
              <Box sx={{ position: "relative", mt: -8 }}>
                <Avatar
                  sx={{
                    width: 150,
                    height: 150,
                    border: 4,
                    borderColor: "background.paper",
                    fontSize: "3rem",
                    bgcolor: "primary.main",
                  }}
                >
                  {user?.username?.charAt(0).toUpperCase()}
                </Avatar>
                <IconButton
                  sx={{
                    position: "absolute",
                    bottom: 0,
                    right: 0,
                    bgcolor: "primary.main",
                    color: "white",
                    "&:hover": { bgcolor: "primary.dark" },
                  }}
                >
                  <PhotoCamera />
                </IconButton>
              </Box>
              <Box sx={{ flex: 1 }}>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
                >
                  <Typography variant="h4" fontWeight={700}>
                    {user?.username || "User"}
                  </Typography>
                  <Verified color="primary" />
                </Box>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  {user?.email || "user@example.com"}
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  {user?.bio ||
                    "Passionate language learner exploring the world of English!"}
                </Typography>
                <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                  <Chip
                    icon={<School />}
                    label="Intermediate Learner"
                    color="primary"
                  />
                  <Chip label="Joined August 2025" size="small" />
                </Box>
              </Box>
              <Button
                variant="outlined"
                startIcon={<Edit />}
                onClick={handleEditOpen}
              >
                Edit Profile
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={6} md={3} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <HoverCard>
                  <CardContent sx={{ textAlign: "center" }}>
                    <Box sx={{ color: stat.color, mb: 1 }}>{stat.icon}</Box>
                    <Typography
                      variant="h4"
                      fontWeight={700}
                      color="primary.main"
                    >
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.label}
                    </Typography>
                  </CardContent>
                </HoverCard>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        <Grid container spacing={3}>
          {/* Skills Progress */}
          <Grid item xs={12} lg={8}>
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Skill Progress
                </Typography>
                <Divider sx={{ mb: 3 }} />
                {skillProgress.map((skill, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Box sx={{ mb: 3 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant="body1" fontWeight={600}>
                          {skill.skill}
                        </Typography>
                        <Box sx={{ display: "flex", gap: 2 }}>
                          <Chip
                            label={`Level ${skill.level}`}
                            size="small"
                            color="primary"
                          />
                          <Typography variant="body2" color="text.secondary">
                            {skill.xp} XP
                          </Typography>
                        </Box>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={skill.progress}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  </motion.div>
                ))}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Recent Activity
                </Typography>
                <Divider sx={{ mb: 2 }} />
                {recentActivity.map((activity, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        py: 2,
                        borderBottom: index < recentActivity.length - 1 ? 1 : 0,
                        borderColor: "divider",
                      }}
                    >
                      <Box>
                        <Typography variant="body1" fontWeight={600}>
                          {activity.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {activity.type} • {activity.date}
                        </Typography>
                      </Box>
                      <Chip
                        label={`+${activity.points} XP`}
                        color="success"
                        size="small"
                      />
                    </Box>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Achievements */}
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Achievements
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {achievements.filter((a) => a.earned).length} /{" "}
                  {achievements.length} unlocked
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Grid container spacing={2}>
                  {achievements.map((achievement, index) => (
                    <Grid item xs={6} key={achievement.id}>
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <Card
                          sx={{
                            textAlign: "center",
                            p: 2,
                            cursor: "pointer",
                            opacity: achievement.earned ? 1 : 0.3,
                            transition: "all 0.3s",
                            "&:hover": {
                              transform: "scale(1.05)",
                              boxShadow: 3,
                            },
                          }}
                        >
                          <Typography variant="h3" sx={{ mb: 1 }}>
                            {achievement.icon}
                          </Typography>
                          <Typography
                            variant="body2"
                            fontWeight={600}
                            sx={{ fontSize: "0.75rem" }}
                          >
                            {achievement.name}
                          </Typography>
                          {achievement.earned && achievement.date && (
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ fontSize: "0.65rem" }}
                            >
                              {achievement.date}
                            </Typography>
                          )}
                        </Card>
                      </motion.div>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Edit Profile Dialog */}
        <Dialog
          open={editDialogOpen}
          onClose={handleEditClose}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            <GradientText variant="h5" fontWeight={700}>
              Edit Profile
            </GradientText>
          </DialogTitle>
          <DialogContent>
            <Box
              sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 2 }}
            >
              <TextField
                label="Username"
                value={editedUser.username}
                onChange={handleInputChange("username")}
                fullWidth
              />
              <TextField
                label="Email"
                type="email"
                value={editedUser.email}
                onChange={handleInputChange("email")}
                fullWidth
              />
              <TextField
                label="Bio"
                value={editedUser.bio}
                onChange={handleInputChange("bio")}
                multiline
                rows={4}
                fullWidth
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleEditClose}>Cancel</Button>
            <AnimatedButton variant="contained" onClick={handleSaveProfile}>
              Save Changes
            </AnimatedButton>
          </DialogActions>
        </Dialog>
      </Box>
    </PageTransition>
  );
};

export default Profile;
