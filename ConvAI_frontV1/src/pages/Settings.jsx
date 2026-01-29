import { useState } from "react";
import { useTheme as useMuiTheme } from "@mui/material";
import { useTheme } from "../context/ThemeContext";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Button,
  Alert,
} from "@mui/material";
import {
  Notifications,
  Language,
  Palette,
  VolumeUp,
  Security,
  DataUsage,
  Help,
  Info,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import AnimatedButton from "../components/common/AnimatedButton";
import LanguageSwitcher from "../components/common/LanguageSwitcher";

const Settings = () => {
  const muiTheme = useMuiTheme();
  const { mode, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const { t, i18n } = useTranslation();

  const [settings, setSettings] = useState({
    notifications: {
      emailNotifications: true,
      pushNotifications: true,
      achievementAlerts: true,
      weeklyReport: false,
      streakReminders: true,
    },
    preferences: {
      language: "en",
      targetLanguage: "te",
      difficulty: "intermediate",
      dailyGoal: 30,
    },
    audio: {
      soundEffects: true,
      voiceGuidance: true,
      volume: 70,
    },
    privacy: {
      profileVisibility: "public",
      showOnLeaderboard: true,
      shareProgress: true,
    },
  });

  const [saved, setSaved] = useState(false);

  const handleSwitchChange = (category, field) => (event) => {
    setSettings({
      ...settings,
      [category]: {
        ...settings[category],
        [field]: event.target.checked,
      },
    });
  };

  const handleSelectChange = (category, field) => (event) => {
    setSettings({
      ...settings,
      [category]: {
        ...settings[category],
        [field]: event.target.value,
      },
    });
  };

  const handleSliderChange = (category, field) => (event, newValue) => {
    setSettings({
      ...settings,
      [category]: {
        ...settings[category],
        [field]: newValue,
      },
    });
  };

  const handleSaveSettings = () => {
    // Save settings logic here
    console.log("Saving settings:", settings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleResetSettings = () => {
    // Reset to default settings
    setSettings({
      notifications: {
        emailNotifications: true,
        pushNotifications: true,
        achievementAlerts: true,
        weeklyReport: false,
        streakReminders: true,
      },
      preferences: {
        language: "en",
        targetLanguage: "te",
        difficulty: "intermediate",
        dailyGoal: 30,
      },
      audio: {
        soundEffects: true,
        voiceGuidance: true,
        volume: 70,
      },
      privacy: {
        profileVisibility: "public",
        showOnLeaderboard: true,
        shareProgress: true,
      },
    });
  };

  const settingsSections = [
    {
      title: "Appearance",
      icon: <Palette />,
      items: [
        {
          type: "switch",
          label: "Dark Mode",
          description: "Toggle between light and dark theme",
          value: mode === "dark",
          onChange: toggleTheme,
        },
      ],
    },
    {
      title: "Notifications",
      icon: <Notifications />,
      items: [
        {
          type: "switch",
          label: "Email Notifications",
          description: "Receive updates via email",
          value: settings.notifications.emailNotifications,
          onChange: handleSwitchChange("notifications", "emailNotifications"),
        },
        {
          type: "switch",
          label: "Push Notifications",
          description: "Get push notifications on your device",
          value: settings.notifications.pushNotifications,
          onChange: handleSwitchChange("notifications", "pushNotifications"),
        },
        {
          type: "switch",
          label: "Achievement Alerts",
          description: "Notify when you unlock achievements",
          value: settings.notifications.achievementAlerts,
          onChange: handleSwitchChange("notifications", "achievementAlerts"),
        },
        {
          type: "switch",
          label: "Weekly Progress Report",
          description: "Receive weekly learning summaries",
          value: settings.notifications.weeklyReport,
          onChange: handleSwitchChange("notifications", "weeklyReport"),
        },
        {
          type: "switch",
          label: "Streak Reminders",
          description: "Get reminded to maintain your streak",
          value: settings.notifications.streakReminders,
          onChange: handleSwitchChange("notifications", "streakReminders"),
        },
      ],
    },
    {
      title: "Learning Preferences",
      icon: <Language />,
      items: [
        {
          type: "select",
          label: "Interface Language",
          value: settings.preferences.language,
          onChange: handleSelectChange("preferences", "language"),
          options: [
            { value: "en", label: "English" },
            { value: "te", label: "Telugu" },
            { value: "hi", label: "Hindi" },
          ],
        },
        {
          type: "select",
          label: "Target Language",
          value: settings.preferences.targetLanguage,
          onChange: handleSelectChange("preferences", "targetLanguage"),
          options: [
            { value: "en", label: "English" },
            { value: "te", label: "Telugu" },
          ],
        },
        {
          type: "select",
          label: "Difficulty Level",
          value: settings.preferences.difficulty,
          onChange: handleSelectChange("preferences", "difficulty"),
          options: [
            { value: "beginner", label: "Beginner" },
            { value: "intermediate", label: "Intermediate" },
            { value: "advanced", label: "Advanced" },
          ],
        },
        {
          type: "slider",
          label: "Daily Learning Goal",
          description: `${settings.preferences.dailyGoal} minutes per day`,
          value: settings.preferences.dailyGoal,
          onChange: handleSliderChange("preferences", "dailyGoal"),
          min: 5,
          max: 120,
          step: 5,
        },
      ],
    },
    {
      title: "Audio & Sound",
      icon: <VolumeUp />,
      items: [
        {
          type: "switch",
          label: "Sound Effects",
          description: "Play sounds for interactions",
          value: settings.audio.soundEffects,
          onChange: handleSwitchChange("audio", "soundEffects"),
        },
        {
          type: "switch",
          label: "Voice Guidance",
          description: "Enable text-to-speech for words",
          value: settings.audio.voiceGuidance,
          onChange: handleSwitchChange("audio", "voiceGuidance"),
        },
        {
          type: "slider",
          label: "Volume",
          description: `${settings.audio.volume}%`,
          value: settings.audio.volume,
          onChange: handleSliderChange("audio", "volume"),
          min: 0,
          max: 100,
          step: 10,
        },
      ],
    },
    {
      title: "Privacy & Security",
      icon: <Security />,
      items: [
        {
          type: "select",
          label: "Profile Visibility",
          value: settings.privacy.profileVisibility,
          onChange: handleSelectChange("privacy", "profileVisibility"),
          options: [
            { value: "public", label: "Public" },
            { value: "friends", label: "Friends Only" },
            { value: "private", label: "Private" },
          ],
        },
        {
          type: "switch",
          label: "Show on Leaderboard",
          description: "Display your rank on public leaderboards",
          value: settings.privacy.showOnLeaderboard,
          onChange: handleSwitchChange("privacy", "showOnLeaderboard"),
        },
        {
          type: "switch",
          label: "Share Progress",
          description: "Allow sharing progress with friends",
          value: settings.privacy.shareProgress,
          onChange: handleSwitchChange("privacy", "shareProgress"),
        },
      ],
    },
  ];

  return (
    <PageTransition>
      <Box>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
            {t('settings.title')}
          </GradientText>
          <Typography variant="body1" color="text.secondary">
            {t('settings.language')}
          </Typography>
          
          {/* Prominent Language Switcher */}
          <Box sx={{ mt: 2, mb: 2, p: 2, bgcolor: 'background.paper', borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
              {t('settings.selectLanguage')}
            </Typography>
            <LanguageSwitcher variant="button" />
          </Box>
        </Box>

        {saved && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Alert severity="success" sx={{ mb: 3 }}>
              Settings saved successfully!
            </Alert>
          </motion.div>
        )}

        {/* Settings Sections */}
        {settingsSections.map((section, sectionIndex) => (
          <motion.div
            key={sectionIndex}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: sectionIndex * 0.1 }}
          >
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
                >
                  {section.icon}
                  <Typography variant="h6" fontWeight={600}>
                    {section.title}
                  </Typography>
                </Box>
                <Divider sx={{ mb: 3 }} />

                {section.items.map((item, itemIndex) => (
                  <Box key={itemIndex} sx={{ mb: 3 }}>
                    {item.type === "switch" && (
                      <Box>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={item.value}
                              onChange={item.onChange}
                            />
                          }
                          label={
                            <Box>
                              <Typography variant="body1" fontWeight={600}>
                                {item.label}
                              </Typography>
                              {item.description && (
                                <Typography
                                  variant="body2"
                                  color="text.secondary"
                                >
                                  {item.description}
                                </Typography>
                              )}
                            </Box>
                          }
                        />
                      </Box>
                    )}

                    {item.type === "select" && (
                      <FormControl fullWidth>
                        <InputLabel>{item.label}</InputLabel>
                        <Select
                          value={item.value}
                          onChange={item.onChange}
                          label={item.label}
                        >
                          {item.options.map((option) => (
                            <MenuItem key={option.value} value={option.value}>
                              {option.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    )}

                    {item.type === "slider" && (
                      <Box>
                        <Typography
                          variant="body1"
                          fontWeight={600}
                          gutterBottom
                        >
                          {item.label}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          gutterBottom
                        >
                          {item.description}
                        </Typography>
                        <Slider
                          value={item.value}
                          onChange={item.onChange}
                          min={item.min}
                          max={item.max}
                          step={item.step}
                          marks
                          valueLabelDisplay="auto"
                        />
                      </Box>
                    )}
                  </Box>
                ))}
              </CardContent>
            </Card>
          </motion.div>
        ))}

        {/* Account Actions */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
              <DataUsage />
              <Typography variant="h6" fontWeight={600}>
                Account Actions
              </Typography>
            </Box>
            <Divider sx={{ mb: 3 }} />

            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <Button variant="outlined" startIcon={<Help />} fullWidth>
                Help & Support
              </Button>
              <Button variant="outlined" startIcon={<Info />} fullWidth>
                About & Legal
              </Button>
              <Button
                variant="outlined"
                color="error"
                onClick={logout}
                fullWidth
              >
                Sign Out
              </Button>
            </Box>
          </CardContent>
        </Card>

        {/* Save/Reset Buttons */}
        <Box sx={{ display: "flex", gap: 2, justifyContent: "flex-end" }}>
          <Button variant="outlined" onClick={handleResetSettings}>
            Reset to Default
          </Button>
          <AnimatedButton
            variant="contained"
            size="large"
            onClick={handleSaveSettings}
          >
            Save Settings
          </AnimatedButton>
        </Box>
      </Box>
    </PageTransition>
  );
};

export default Settings;
