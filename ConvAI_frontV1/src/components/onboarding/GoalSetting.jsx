import { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Slider,
  FormGroup,
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress,
} from "@mui/material";
import {
  School,
  Business,
  Flight,
  Chat,
  Timer,
  Topic,
  Notifications,
  CheckCircle,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import axiosInstance, { API_ENDPOINTS } from "../../config/api";

const LEARNING_GOALS = [
  {
    id: "conversational_fluency",
    title: "Conversational Fluency",
    titleTelugu: "సంభాషణ నైపుణ్యం",
    description: "Master everyday conversations",
    icon: <Chat sx={{ fontSize: 40 }} />,
    color: "#3b82f6",
  },
  {
    id: "business_english",
    title: "Business English",
    titleTelugu: "వ్యాపార ఇంగ్లీష్",
    description: "Professional communication skills",
    icon: <Business sx={{ fontSize: 40 }} />,
    color: "#8b5cf6",
  },
  {
    id: "travel_english",
    title: "Travel English",
    titleTelugu: "ప్రయాణ ఇంగ్లీష్",
    description: "Communicate while traveling",
    icon: <Flight sx={{ fontSize: 40 }} />,
    color: "#10b981",
  },
  {
    id: "academic_english",
    title: "Academic English",
    titleTelugu: "విద్యా ఇంగ్లీష్",
    description: "For studies and exams",
    icon: <School sx={{ fontSize: 40 }} />,
    color: "#f59e0b",
  },
];

const TOPICS = [
  { id: "food", label: "Food & Dining", telugu: "ఆహారం" },
  { id: "travel", label: "Travel", telugu: "ప్రయాణం" },
  { id: "work", label: "Work & Career", telugu: "ఉద్యోగం" },
  { id: "daily_life", label: "Daily Life", telugu: "రోజువారీ జీవితం" },
  { id: "shopping", label: "Shopping", telugu: "షాపింగ్" },
  { id: "health", label: "Health & Fitness", telugu: "ఆరోగ్యం" },
  { id: "technology", label: "Technology", telugu: "టెక్నాలజీ" },
  { id: "entertainment", label: "Entertainment", telugu: "వినోదం" },
  { id: "family", label: "Family & Friends", telugu: "కుటుంబం" },
  { id: "education", label: "Education", telugu: "విద్య" },
];

const TIME_MARKS = [
  { value: 5, label: "5 min" },
  { value: 15, label: "15 min" },
  { value: 30, label: "30 min" },
  { value: 45, label: "45 min" },
  { value: 60, label: "1 hr" },
];

const GoalSetting = ({ onComplete, proficiencyLevel }) => {
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [dailyTime, setDailyTime] = useState(15);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [notifications, setNotifications] = useState({
    daily_reminders: true,
    streak_alerts: true,
    achievement_notifications: true,
    weekly_report: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleGoalSelect = (goalId) => {
    setSelectedGoal(goalId);
  };

  const handleTopicToggle = (topicId) => {
    setSelectedTopics((prev) =>
      prev.includes(topicId)
        ? prev.filter((t) => t !== topicId)
        : [...prev, topicId]
    );
  };

  const handleNotificationToggle = (key) => {
    setNotifications((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const handleSubmit = async () => {
    // Validation
    if (!selectedGoal) {
      setError("Please select a learning goal");
      return;
    }

    if (selectedTopics.length === 0) {
      setError("Please select at least one topic of interest");
      return;
    }

    try {
      setLoading(true);
      setError("");

      // Step 1: Set daily time goal
      await axiosInstance.post(API_ENDPOINTS.PERSONALIZATION.GOALS, {
        daily_time_goal: dailyTime,
        learning_focus: selectedGoal,
      });

      // Step 2: Set preferences
      await axiosInstance.post(API_ENDPOINTS.PERSONALIZATION.PREFERENCES, {
        preferred_topics: selectedTopics,
        learning_goal_type: selectedGoal,
        notification_settings: notifications,
      });

      setSuccess(true);

      // Wait a moment to show success message
      setTimeout(() => {
        onComplete && onComplete();
      }, 1500);
    } catch (err) {
      console.error("Error saving goals and preferences:", err);
      setError(
        err.response?.data?.error ||
          "Failed to save preferences. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Card
          sx={{
            textAlign: "center",
            py: 6,
            background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            color: "white",
          }}
        >
          <CardContent>
            <CheckCircle sx={{ fontSize: 80, mb: 2 }} />
            <Typography variant="h4" fontWeight={700} gutterBottom>
              All Set! 🎉
            </Typography>
            <Typography variant="h6">
              అన్నీ సిద్ధంగా ఉన్నాయి!
            </Typography>
            <Typography variant="body1" sx={{ mt: 2, opacity: 0.9 }}>
              Your personalized learning journey begins now!
            </Typography>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom textAlign="center">
        🎯 Set Your Learning Goals
      </Typography>
      <Typography
        variant="body1"
        color="text.secondary"
        textAlign="center"
        mb={4}
      >
        మీ అభ్యాస లక్ష్యాలను సెట్ చేయండి
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* Step 1: Select Learning Goal */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
            <Typography variant="h6" fontWeight={600}>
              1️⃣ Whats your main learning goal?
            </Typography>
          </Box>
          <Grid container spacing={2}>
            {LEARNING_GOALS.map((goal) => (
              <Grid item xs={12} sm={6} md={3} key={goal.id}>
                <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                  <Card
                    onClick={() => handleGoalSelect(goal.id)}
                    sx={{
                      cursor: "pointer",
                      border: 2,
                      borderColor:
                        selectedGoal === goal.id ? goal.color : "transparent",
                      backgroundColor:
                        selectedGoal === goal.id
                          ? `${goal.color}10`
                          : "background.paper",
                      transition: "all 0.3s",
                      "&:hover": {
                        borderColor: goal.color,
                        backgroundColor: `${goal.color}05`,
                      },
                    }}
                  >
                    <CardContent sx={{ textAlign: "center", py: 3 }}>
                      <Box sx={{ color: goal.color, mb: 1 }}>{goal.icon}</Box>
                      <Typography variant="h6" fontWeight={600} gutterBottom>
                        {goal.title}
                      </Typography>
                      <Typography
                        variant="caption"
                        color="text.secondary"
                        display="block"
                        mb={1}
                      >
                        {goal.titleTelugu}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {goal.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Step 2: Daily Time Commitment */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
            <Timer sx={{ mr: 1 }} />
            <Typography variant="h6" fontWeight={600}>
              2️⃣ How much time can you dedicate daily?
            </Typography>
          </Box>
          <Box sx={{ px: 2 }}>
            <Typography variant="h4" fontWeight={700} color="primary" mb={2}>
              {dailyTime} minutes
            </Typography>
            <Slider
              value={dailyTime}
              onChange={(e, value) => setDailyTime(value)}
              min={5}
              max={60}
              step={5}
              marks={TIME_MARKS}
              valueLabelDisplay="auto"
              sx={{
                "& .MuiSlider-thumb": {
                  width: 24,
                  height: 24,
                },
              }}
            />
            <Typography variant="body2" color="text.secondary" mt={2}>
              💡 Consistent practice is more important than duration. Even 5-10
              minutes daily can make a big difference!
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Step 3: Topic Preferences */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
            <Topic sx={{ mr: 1 }} />
            <Typography variant="h6" fontWeight={600}>
              3️⃣ Which topics interest you? (Select 3-5)
            </Typography>
          </Box>
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
            {TOPICS.map((topic) => (
              <Chip
                key={topic.id}
                label={
                  <Box>
                    <Typography variant="body2" fontWeight={600}>
                      {topic.label}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {topic.telugu}
                    </Typography>
                  </Box>
                }
                onClick={() => handleTopicToggle(topic.id)}
                color={selectedTopics.includes(topic.id) ? "primary" : "default"}
                variant={selectedTopics.includes(topic.id) ? "filled" : "outlined"}
                sx={{
                  height: "auto",
                  py: 1.5,
                  px: 2,
                  "& .MuiChip-label": {
                    display: "block",
                  },
                }}
              />
            ))}
          </Box>
          <Typography variant="caption" color="text.secondary" display="block" mt={2}>
            Selected: {selectedTopics.length} topic(s)
          </Typography>
        </CardContent>
      </Card>

      {/* Step 4: Notification Settings */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
            <Notifications sx={{ mr: 1 }} />
            <Typography variant="h6" fontWeight={600}>
              4️⃣ Notification Preferences
            </Typography>
          </Box>
          <FormGroup>
            <FormControlLabel
              control={
                <Switch
                  checked={notifications.daily_reminders}
                  onChange={() => handleNotificationToggle("daily_reminders")}
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Daily Reminders</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Get reminded to practice every day
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              control={
                <Switch
                  checked={notifications.streak_alerts}
                  onChange={() => handleNotificationToggle("streak_alerts")}
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Streak Alerts</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Notify when youre about to lose your streak
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              control={
                <Switch
                  checked={notifications.achievement_notifications}
                  onChange={() =>
                    handleNotificationToggle("achievement_notifications")
                  }
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Achievement Notifications</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Get notified when you earn badges or level up
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              control={
                <Switch
                  checked={notifications.weekly_report}
                  onChange={() => handleNotificationToggle("weekly_report")}
                />
              }
              label={
                <Box>
                  <Typography variant="body1">Weekly Progress Report</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Receive weekly summary of your learning progress
                  </Typography>
                </Box>
              }
            />
          </FormGroup>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <Box sx={{ textAlign: "center", mt: 4 }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleSubmit}
          disabled={loading || !selectedGoal || selectedTopics.length === 0}
          sx={{
            px: 6,
            py: 2,
            fontSize: "1.1rem",
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "&:hover": {
              background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
            },
          }}
        >
          {loading ? (
            <>
              <CircularProgress size={24} sx={{ mr: 2 }} color="inherit" />
              Saving...
            </>
          ) : (
            "Continue to Dashboard →"
          )}
        </Button>
        <Typography variant="body2" color="text.secondary" mt={2}>
          You can change these settings anytime from your profile
        </Typography>
      </Box>
    </Box>
  );
};

export default GoalSetting;
