import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import {
  Box,
  TextField,
  Typography,
  Alert,
  IconButton,
  InputAdornment,
  MenuItem,
  Chip,
  Stack,
  Paper,
  LinearProgress,
  Grid,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Language as LanguageIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";

const learningGoals = [
  "Conversation",
  "Business",
  "Travel",
  "Academic",
  "Grammar",
  "Pronunciation",
];

const NewRegister = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isTablet = useMediaQuery(theme.breakpoints.down("md"));

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    native_language: "Telugu",
    target_language: "English",
    learning_goals: [],
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length >= 6) strength += 25;
    if (password.length >= 10) strength += 25;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
    if (/\d/.test(password)) strength += 15;
    if (/[^a-zA-Z0-9]/.test(password)) strength += 10;
    return Math.min(strength, 100);
  };

  const getPasswordStrengthColor = (strength) => {
    if (strength < 30) return "#ef4444";
    if (strength < 60) return "#f59e0b";
    if (strength < 80) return "#eab308";
    return "#22c55e";
  };

  const getPasswordStrengthLabel = (strength) => {
    if (strength < 30) return "Weak";
    if (strength < 60) return "Fair";
    if (strength < 80) return "Good";
    return "Strong";
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
    setError("");

    if (name === "password") {
      setPasswordStrength(calculatePasswordStrength(value));
    }
  };

  const handleGoalToggle = (goal) => {
    const currentGoals = formData.learning_goals;
    const newGoals = currentGoals.includes(goal)
      ? currentGoals.filter((g) => g !== goal)
      : [...currentGoals, goal];

    setFormData({ ...formData, learning_goals: newGoals });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    const { confirmPassword, ...registerData } = formData;
    const result = await register(registerData);

    if (result.success) {
      navigate("/onboarding", {
        state: {
          assessment: result.assessment,
          fromRegistration: true,
        },
      });
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  const inputStyles = {
    "& .MuiOutlinedInput-root": {
      borderRadius: 2,
      backgroundColor: "#f8fafc",
      "& fieldset": { borderColor: "#e2e8f0" },
      "&:hover fieldset": { borderColor: "#cbd5e1" },
      "&.Mui-focused fieldset": {
        borderColor: "#0ea5e9",
        borderWidth: 2,
      },
      "&.Mui-focused": { backgroundColor: "white" },
    },
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        width: "100%",
        display: "flex",
        flexDirection: { xs: "column", lg: "row" },
        background: "#f8fafc",
      }}
    >
      {/* Left Side - Branding (Hidden on tablet and mobile) */}
      <Box
        sx={{
          display: { xs: "none", lg: "flex" },
          flex: "0 0 40%",
          background: "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: 6,
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Background Pattern */}
        <Box
          sx={{
            position: "absolute",
            inset: 0,
            opacity: 0.1,
            backgroundImage: `
              radial-gradient(circle at 25% 25%, white 2px, transparent 2px),
              radial-gradient(circle at 75% 75%, white 2px, transparent 2px)
            `,
            backgroundSize: "50px 50px",
          }}
        />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          style={{ textAlign: "center", zIndex: 1, maxWidth: 400 }}
        >
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: "20px",
              background: "rgba(255, 255, 255, 0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 24px",
              backdropFilter: "blur(10px)",
            }}
          >
            <LanguageIcon sx={{ fontSize: 40, color: "white" }} />
          </Box>
          <Typography
            variant="h3"
            sx={{
              color: "white",
              fontWeight: 800,
              mb: 2,
              fontSize: "2.25rem",
            }}
          >
            ConvAI Learn
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: "rgba(255, 255, 255, 0.9)",
              lineHeight: 1.6,
              fontWeight: 400,
            }}
          >
            Start your language learning journey with AI-powered personalized lessons
          </Typography>

          {/* Features List */}
          <Stack spacing={2} sx={{ mt: 6, textAlign: "left" }}>
            {[
              "Adaptive learning paths",
              "Real-time AI conversations",
              "Progress tracking",
              "Gamified achievements",
            ].map((feature, index) => (
              <motion.div
                key={feature}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: "white",
                      flexShrink: 0,
                    }}
                  />
                  <Typography sx={{ color: "rgba(255, 255, 255, 0.9)" }}>
                    {feature}
                  </Typography>
                </Box>
              </motion.div>
            ))}
          </Stack>
        </motion.div>
      </Box>

      {/* Right Side - Register Form */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-start",
          alignItems: "center",
          padding: { xs: 2, sm: 3, md: 4 },
          minHeight: "100vh",
          overflowY: "auto",
        }}
      >
        {/* Mobile/Tablet Header */}
        <Box
          sx={{
            display: { xs: "flex", lg: "none" },
            alignItems: "center",
            gap: 2,
            mb: 3,
            mt: 2,
          }}
        >
          <Box
            sx={{
              width: 44,
              height: 44,
              borderRadius: "12px",
              background: "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <LanguageIcon sx={{ fontSize: 24, color: "white" }} />
          </Box>
          <Typography variant="h6" sx={{ fontWeight: 700, color: "#1e293b" }}>
            ConvAI Learn
          </Typography>
        </Box>

        <Box 
          sx={{ 
            width: "100%", 
            maxWidth: { xs: "100%", sm: 500, md: 600 }, 
            px: { xs: 0, sm: 2 },
            pb: 4,
          }}
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Paper
              elevation={0}
              sx={{
                p: { xs: 2.5, sm: 3, md: 4 },
                borderRadius: 3,
                background: "white",
                boxShadow: "0 4px 24px rgba(0, 0, 0, 0.06)",
                border: "1px solid #e2e8f0",
              }}
            >
              <Box sx={{ mb: 3 }}>
                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    color: "#1e293b",
                    mb: 1,
                    fontSize: { xs: "1.375rem", sm: "1.5rem", md: "1.75rem" },
                  }}
                >
                  Create your account
                </Typography>
                <Typography sx={{ color: "#64748b", fontSize: { xs: "0.875rem", sm: "1rem" } }}>
                  Join thousands of learners mastering new languages
                </Typography>
              </Box>

              {error && (
                <Alert
                  severity="error"
                  sx={{
                    mb: 3,
                    borderRadius: 2,
                    border: "1px solid #fecaca",
                  }}
                >
                  {error}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <Stack spacing={2}>
                  {/* Username & Email Row */}
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography
                        variant="body2"
                        sx={{ mb: 0.75, fontWeight: 600, color: "#374151", fontSize: "0.875rem" }}
                      >
                        Username *
                      </Typography>
                      <TextField
                        fullWidth
                        placeholder="Choose a username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                        autoFocus={!isMobile}
                        size="small"
                        sx={inputStyles}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography
                        variant="body2"
                        sx={{ mb: 0.75, fontWeight: 600, color: "#374151", fontSize: "0.875rem" }}
                      >
                        Email *
                      </Typography>
                      <TextField
                        fullWidth
                        placeholder="your@email.com"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        size="small"
                        sx={inputStyles}
                      />
                    </Grid>
                  </Grid>

                  {/* Password Row */}
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography
                        variant="body2"
                        sx={{ mb: 0.75, fontWeight: 600, color: "#374151", fontSize: "0.875rem" }}
                      >
                        Password *
                      </Typography>
                      <TextField
                        fullWidth
                        placeholder="Create password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        onChange={handleChange}
                        required
                        size="small"
                        sx={inputStyles}
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                onClick={() => setShowPassword(!showPassword)}
                                edge="end"
                                size="small"
                              >
                                {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                      {formData.password && (
                        <Box sx={{ mt: 1 }}>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              mb: 0.5,
                            }}
                          >
                            <Typography variant="caption" sx={{ color: "#64748b" }}>
                              Strength
                            </Typography>
                            <Typography
                              variant="caption"
                              sx={{
                                color: getPasswordStrengthColor(passwordStrength),
                                fontWeight: 600,
                              }}
                            >
                              {getPasswordStrengthLabel(passwordStrength)}
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={passwordStrength}
                            sx={{
                              height: 4,
                              borderRadius: 2,
                              backgroundColor: "#e2e8f0",
                              "& .MuiLinearProgress-bar": {
                                backgroundColor: getPasswordStrengthColor(passwordStrength),
                                borderRadius: 2,
                              },
                            }}
                          />
                        </Box>
                      )}
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography
                        variant="body2"
                        sx={{ mb: 0.75, fontWeight: 600, color: "#374151", fontSize: "0.875rem" }}
                      >
                        Confirm Password *
                      </Typography>
                      <TextField
                        fullWidth
                        placeholder="Confirm password"
                        name="confirmPassword"
                        type={showPassword ? "text" : "password"}
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        required
                        size="small"
                        sx={inputStyles}
                      />
                    </Grid>
                  </Grid>

                  {/* Language Selection Row */}
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography
                        variant="body2"
                        sx={{ mb: 0.75, fontWeight: 600, color: "#374151", fontSize: "0.875rem" }}
                      >
                        Native Language
                      </Typography>
                      <TextField
                        fullWidth
                        select
                        name="native_language"
                        value={formData.native_language}
                        onChange={handleChange}
                        size="small"
                        sx={inputStyles}
                      >
                        <MenuItem value="Telugu">Telugu</MenuItem>
                        <MenuItem value="Hindi">Hindi</MenuItem>
                        <MenuItem value="Tamil">Tamil</MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography
                        variant="body2"
                        sx={{ mb: 0.75, fontWeight: 600, color: "#374151", fontSize: "0.875rem" }}
                      >
                        Target Language
                      </Typography>
                      <TextField
                        fullWidth
                        select
                        name="target_language"
                        value={formData.target_language}
                        onChange={handleChange}
                        size="small"
                        sx={inputStyles}
                      >
                        <MenuItem value="English">English</MenuItem>
                        <MenuItem value="Spanish">Spanish</MenuItem>
                        <MenuItem value="French">French</MenuItem>
                      </TextField>
                    </Grid>
                  </Grid>

                  {/* Learning Goals */}
                  <Box>
                    <Typography
                      variant="body2"
                      sx={{ mb: 1, fontWeight: 600, color: "#374151", fontSize: "0.875rem" }}
                    >
                      Learning Goals{" "}
                      <Typography component="span" sx={{ color: "#94a3b8", fontWeight: 400 }}>
                        (Optional)
                      </Typography>
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                      {learningGoals.map((goal) => (
                        <Chip
                          key={goal}
                          label={goal}
                          onClick={() => handleGoalToggle(goal)}
                          size={isMobile ? "small" : "medium"}
                          sx={{
                            backgroundColor: formData.learning_goals.includes(goal)
                              ? "#0ea5e9"
                              : "white",
                            color: formData.learning_goals.includes(goal)
                              ? "white"
                              : "#64748b",
                            border: "1.5px solid",
                            borderColor: formData.learning_goals.includes(goal)
                              ? "#0ea5e9"
                              : "#e2e8f0",
                            fontWeight: 500,
                            fontSize: { xs: "0.75rem", sm: "0.813rem" },
                            cursor: "pointer",
                            transition: "all 0.2s ease",
                            "&:hover": {
                              backgroundColor: formData.learning_goals.includes(goal)
                                ? "#0284c7"
                                : "#f1f5f9",
                              borderColor: formData.learning_goals.includes(goal)
                                ? "#0284c7"
                                : "#cbd5e1",
                            },
                          }}
                        />
                      ))}
                    </Box>
                  </Box>

                  {/* Submit Button */}
                  <Box
                    component="button"
                    type="submit"
                    disabled={loading}
                    sx={{
                      width: "100%",
                      padding: { xs: "12px 20px", sm: "14px 24px" },
                      border: "none",
                      borderRadius: "12px",
                      background: "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
                      color: "white",
                      fontSize: { xs: "0.938rem", sm: "1rem" },
                      fontWeight: 600,
                      cursor: loading ? "not-allowed" : "pointer",
                      opacity: loading ? 0.7 : 1,
                      boxShadow: "0 4px 12px rgba(14, 165, 233, 0.3)",
                      transition: "all 0.2s ease",
                      mt: 1,
                      "&:hover": {
                        boxShadow: loading ? "none" : "0 6px 20px rgba(14, 165, 233, 0.4)",
                        transform: loading ? "none" : "translateY(-1px)",
                      },
                      "&:active": {
                        transform: "translateY(0)",
                      },
                    }}
                  >
                    {loading ? "Creating Account..." : "Create Account"}
                  </Box>
                </Stack>
              </form>

              <Box sx={{ textAlign: "center", mt: 3, pt: 2.5, borderTop: "1px solid #e2e8f0" }}>
                <Typography sx={{ color: "#64748b", fontSize: { xs: "0.875rem", sm: "1rem" } }}>
                  Already have an account?{" "}
                  <Link
                    to="/login"
                    style={{
                      color: "#0ea5e9",
                      textDecoration: "none",
                      fontWeight: 600,
                    }}
                  >
                    Sign in
                  </Link>
                </Typography>
              </Box>
            </Paper>
          </motion.div>
        </Box>
      </Box>
    </Box>
  );
};

export default NewRegister;
