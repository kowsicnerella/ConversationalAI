import { useState } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import {
  Box,
  Container,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Typography,
  Avatar,
  Paper,
  Divider,
  Chip,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import {
  Edit,
  Save,
  Cancel,
  Person,
  Email,
  Language,
  School,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../store/index.js";
import { toast } from "react-hot-toast";

const profileSchema = yup.object().shape({
  username: yup
    .string()
    .min(3, "Username must be at least 3 characters")
    .required("Username is required"),
  email: yup
    .string()
    .email("Invalid email format")
    .required("Email is required"),
  nativeLanguage: yup.string().required("Native language is required"),
  targetLanguage: yup.string().required("Target language is required"),
});

const Profile = () => {
  const user = useAuthStore((state) => state.user);
  const updateProfile = useAuthStore((state) => state.updateProfile);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setError,
  } = useForm({
    resolver: yupResolver(profileSchema),
    defaultValues: {
      username: user?.username || "",
      email: user?.email || "",
      nativeLanguage: user?.native_language || "Telugu",
      targetLanguage: user?.target_language || "English",
    },
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      await updateProfile({
        username: data.username,
        email: data.email,
        native_language: data.nativeLanguage,
        target_language: data.targetLanguage,
      });

      toast.success("Profile updated successfully!");
      setIsEditing(false);
    } catch (error) {
      const errorMessage = error.message || "Failed to update profile";
      setError("root", { message: errorMessage });
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    reset();
    setIsEditing(false);
  };

  const stats = [
    { label: "Total Points", value: user?.total_points || 0, icon: <School /> },
    {
      label: "Current Streak",
      value: `${user?.current_streak || 0} days`,
      icon: <Language />,
    },
    { label: "Level", value: user?.level || "Beginner", icon: <Person /> },
  ];

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Profile Header */}
        <Paper
          elevation={0}
          sx={{
            p: 4,
            mb: 4,
            background: "linear-gradient(135deg, #667eea15, #764ba215)",
            borderRadius: 3,
            border: "1px solid #667eea20",
          }}
        >
          <Grid container spacing={3} alignItems="center">
            <Grid item>
              <motion.div
                whileHover={{ scale: 1.1 }}
                transition={{ duration: 0.2 }}
              >
                <Avatar
                  sx={{
                    width: 120,
                    height: 120,
                    background: "linear-gradient(135deg, #667eea, #764ba2)",
                    fontSize: "3rem",
                    fontWeight: "bold",
                  }}
                >
                  {user?.username?.charAt(0) || "U"}
                </Avatar>
              </motion.div>
            </Grid>
            <Grid item xs>
              <Typography variant="h4" sx={{ fontWeight: "bold", mb: 1 }}>
                {user?.username || "User"}
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                {user?.email || "user@example.com"}
              </Typography>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                <Chip
                  icon={<Language />}
                  label={`${user?.native_language || "Telugu"} → ${
                    user?.target_language || "English"
                  }`}
                  variant="outlined"
                  color="primary"
                />
                <Chip
                  label={`Level: ${user?.level || "Beginner"}`}
                  variant="outlined"
                  color="success"
                />
              </Box>
            </Grid>
            <Grid item>
              <AnimatePresence mode="wait">
                {!isEditing ? (
                  <motion.div
                    key="edit-button"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                  >
                    <Button
                      variant="contained"
                      startIcon={<Edit />}
                      onClick={() => setIsEditing(true)}
                      component={motion.button}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      Edit Profile
                    </Button>
                  </motion.div>
                ) : (
                  <motion.div
                    key="action-buttons"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                  >
                    <Box sx={{ display: "flex", gap: 1 }}>
                      <Button
                        variant="contained"
                        startIcon={
                          isLoading ? <CircularProgress size={16} /> : <Save />
                        }
                        onClick={handleSubmit(onSubmit)}
                        disabled={isLoading}
                        component={motion.button}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        Save
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<Cancel />}
                        onClick={handleCancel}
                        disabled={isLoading}
                        component={motion.button}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        Cancel
                      </Button>
                    </Box>
                  </motion.div>
                )}
              </AnimatePresence>
            </Grid>
          </Grid>
        </Paper>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} md={4} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.6 }}
                whileHover={{ y: -5 }}
              >
                <Card
                  sx={{
                    height: "100%",
                    borderRadius: 3,
                    background: "linear-gradient(135deg, #667eea10, #764ba210)",
                    border: "1px solid #667eea30",
                  }}
                >
                  <CardContent sx={{ textAlign: "center", p: 3 }}>
                    <Box
                      sx={{
                        mb: 2,
                        color: "#667eea",
                        display: "flex",
                        justifyContent: "center",
                      }}
                    >
                      {stat.icon}
                    </Box>
                    <Typography variant="h4" sx={{ fontWeight: "bold", mb: 1 }}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {stat.label}
                    </Typography>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Profile Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
        >
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h6" sx={{ fontWeight: "bold", mb: 3 }}>
                Profile Information
              </Typography>

              <Box component="form" onSubmit={handleSubmit(onSubmit)}>
                {errors.root && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {errors.root.message}
                  </Alert>
                )}

                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      {...register("username")}
                      fullWidth
                      label="Username"
                      disabled={!isEditing}
                      error={!!errors.username}
                      helperText={errors.username?.message}
                      InputProps={{
                        startAdornment: (
                          <Person sx={{ mr: 1, color: "action.active" }} />
                        ),
                      }}
                      sx={{
                        "& .MuiOutlinedInput-root": {
                          borderRadius: 2,
                        },
                      }}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      {...register("email")}
                      fullWidth
                      label="Email"
                      type="email"
                      disabled={!isEditing}
                      error={!!errors.email}
                      helperText={errors.email?.message}
                      InputProps={{
                        startAdornment: (
                          <Email sx={{ mr: 1, color: "action.active" }} />
                        ),
                      }}
                      sx={{
                        "& .MuiOutlinedInput-root": {
                          borderRadius: 2,
                        },
                      }}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={!isEditing}>
                      <InputLabel>Native Language</InputLabel>
                      <Select
                        {...register("nativeLanguage")}
                        label="Native Language"
                        error={!!errors.nativeLanguage}
                        sx={{ borderRadius: 2 }}
                      >
                        <MenuItem value="Telugu">Telugu</MenuItem>
                        <MenuItem value="Hindi">Hindi</MenuItem>
                        <MenuItem value="Tamil">Tamil</MenuItem>
                        <MenuItem value="Kannada">Kannada</MenuItem>
                        <MenuItem value="Malayalam">Malayalam</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth disabled={!isEditing}>
                      <InputLabel>Target Language</InputLabel>
                      <Select
                        {...register("targetLanguage")}
                        label="Target Language"
                        error={!!errors.targetLanguage}
                        sx={{ borderRadius: 2 }}
                      >
                        <MenuItem value="English">English</MenuItem>
                        <MenuItem value="Hindi">Hindi</MenuItem>
                        <MenuItem value="Spanish">Spanish</MenuItem>
                        <MenuItem value="French">French</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 4 }} />

                <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                  Learning Preferences
                </Typography>

                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Additional learning preferences and settings will be
                      available here in future updates.
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </Container>
  );
};

export default Profile;
