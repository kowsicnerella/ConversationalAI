import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Typography,
  Alert,
  IconButton,
  InputAdornment,
  MenuItem,
  Chip,
  LinearProgress,
  Divider,
  Tooltip,
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import { motion } from "framer-motion";
import AnimatedButton from "../../components/common/AnimatedButton";
import GradientText from "../../components/common/GradientText";
import FloatingParticles from "../../components/common/FloatingParticles";

const learningGoals = [
  "Conversation",
  "Business",
  "Travel",
  "Academic",
  "Grammar",
  "Pronunciation",
];

const Register = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

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
  const [focusedField, setFocusedField] = useState(null);

  // Password strength calculation helper functions
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

    // eslint-disable-next-line no-unused-vars
    const { confirmPassword, ...registerData } = formData;
    const result = await register(registerData);

    if (result.success) {
      // Redirect to onboarding with assessment data from registration
      navigate("/onboarding", {
        state: {
          assessment: result.assessment, // Pass assessment from registration response
          fromRegistration: true
        }
      });
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <Box sx={{ position: "relative", width: "100%", maxWidth: 500 }}>
      <FloatingParticles />

      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{
          duration: 0.6,
          type: "spring",
          stiffness: 100,
        }}
      >
        <Card
          component={motion.div}
          whileHover={{
            boxShadow: "0 25px 70px rgba(0, 0, 0, 0.35)",
            y: -5,
          }}
          sx={{
            backdropFilter: "blur(20px)",
            background: "rgba(255, 255, 255, 0.98)",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.3)",
            border: "1px solid rgba(255, 255, 255, 0.2)",
            position: "relative",
            zIndex: 1,
            borderRadius: 3,
            maxHeight: "90vh",
            overflowY: "auto",
            transition: "all 0.3s ease",
            "&::-webkit-scrollbar": {
              width: "8px",
            },
            "&::-webkit-scrollbar-track": {
              background: "rgba(0, 0, 0, 0.05)",
              borderRadius: "4px",
            },
            "&::-webkit-scrollbar-thumb": {
              background: "rgba(14, 165, 233, 0.5)",
              borderRadius: "4px",
              "&:hover": {
                background: "rgba(14, 165, 233, 0.7)",
              },
            },
          }}
        >
          <CardContent sx={{ p: 4 }}>
            {/* Header */}
            <Box sx={{ textAlign: "center", mb: 3 }}>
              <GradientText variant="h4" sx={{ mb: 1, fontWeight: 800 }}>
                Join ConvAI Learn
              </GradientText>
              <Typography
                variant="body2"
                sx={{ color: "text.secondary", opacity: 0.8 }}
              >
                Start your language learning journey today
              </Typography>
            </Box>

            {/* Error Alert */}
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit}>
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <TextField
                  fullWidth
                  label="Username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  onFocus={() => setFocusedField("username")}
                  onBlur={() => setFocusedField(null)}
                  required
                  sx={{
                    mb: 2,
                    "& .MuiOutlinedInput-root": {
                      transition: "all 0.3s ease",
                      "&:hover": {
                        transform: "translateY(-2px)",
                      },
                      "&.Mui-focused": {
                        transform: "translateY(-2px)",
                        boxShadow: "0 4px 12px rgba(14, 165, 233, 0.2)",
                      },
                    },
                  }}
                  autoFocus
                  InputLabelProps={{
                    style: {
                      color:
                        focusedField === "username"
                          ? "#0ea5e9"
                          : "rgba(0, 0, 0, 0.7)",
                      fontWeight: 500,
                      transition: "color 0.3s ease",
                    },
                  }}
                  InputProps={{
                    style: { color: "rgba(0, 0, 0, 0.87)" },
                  }}
                />
              </motion.div>

              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
              >
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  onFocus={() => setFocusedField("email")}
                  onBlur={() => setFocusedField(null)}
                  required
                  sx={{
                    mb: 2,
                    "& .MuiOutlinedInput-root": {
                      transition: "all 0.3s ease",
                      "&:hover": {
                        transform: "translateY(-2px)",
                      },
                      "&.Mui-focused": {
                        transform: "translateY(-2px)",
                        boxShadow: "0 4px 12px rgba(14, 165, 233, 0.2)",
                      },
                    },
                  }}
                  InputLabelProps={{
                    style: {
                      color:
                        focusedField === "email"
                          ? "#0ea5e9"
                          : "rgba(0, 0, 0, 0.7)",
                      fontWeight: 500,
                      transition: "color 0.3s ease",
                    },
                  }}
                  InputProps={{
                    style: { color: "rgba(0, 0, 0, 0.87)" },
                  }}
                />
              </motion.div>

              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={handleChange}
                  onFocus={() => setFocusedField("password")}
                  onBlur={() => setFocusedField(null)}
                  required
                  sx={{
                    mb: 1,
                    "& .MuiOutlinedInput-root": {
                      transition: "all 0.3s ease",
                      "&:hover": {
                        transform: "translateY(-2px)",
                      },
                      "&.Mui-focused": {
                        transform: "translateY(-2px)",
                        boxShadow: "0 4px 12px rgba(14, 165, 233, 0.2)",
                      },
                    },
                  }}
                  InputLabelProps={{
                    style: {
                      color:
                        focusedField === "password"
                          ? "#0ea5e9"
                          : "rgba(0, 0, 0, 0.7)",
                      fontWeight: 500,
                      transition: "color 0.3s ease",
                    },
                  }}
                  InputProps={{
                    style: { color: "rgba(0, 0, 0, 0.87)" },
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                          sx={{
                            transition: "transform 0.2s ease",
                            "&:hover": {
                              transform: "scale(1.1)",
                            },
                          }}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
                {formData.password && (
                  <Box sx={{ mb: 2 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        mb: 0.5,
                      }}
                    >
                      <Typography
                        variant="caption"
                        sx={{ color: "text.secondary" }}
                      >
                        Password Strength:
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
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: "rgba(0, 0, 0, 0.1)",
                        "& .MuiLinearProgress-bar": {
                          backgroundColor:
                            getPasswordStrengthColor(passwordStrength),
                          borderRadius: 3,
                          transition: "all 0.3s ease",
                        },
                      }}
                    />
                  </Box>
                )}
              </motion.div>

              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <TextField
                  fullWidth
                  label="Confirm Password"
                  name="confirmPassword"
                  type={showPassword ? "text" : "password"}
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  onFocus={() => setFocusedField("confirmPassword")}
                  onBlur={() => setFocusedField(null)}
                  required
                  sx={{
                    mb: 2,
                    "& .MuiOutlinedInput-root": {
                      transition: "all 0.3s ease",
                      "&:hover": {
                        transform: "translateY(-2px)",
                      },
                      "&.Mui-focused": {
                        transform: "translateY(-2px)",
                        boxShadow: "0 4px 12px rgba(14, 165, 233, 0.2)",
                      },
                    },
                  }}
                  InputLabelProps={{
                    style: {
                      color:
                        focusedField === "confirmPassword"
                          ? "#0ea5e9"
                          : "rgba(0, 0, 0, 0.7)",
                      fontWeight: 500,
                      transition: "color 0.3s ease",
                    },
                  }}
                  InputProps={{
                    style: { color: "rgba(0, 0, 0, 0.87)" },
                  }}
                />
              </motion.div>

              <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
                <TextField
                  fullWidth
                  select
                  label="Native Language"
                  name="native_language"
                  value={formData.native_language}
                  onChange={handleChange}
                  InputLabelProps={{
                    style: { color: "rgba(0, 0, 0, 0.7)", fontWeight: 500 },
                  }}
                  InputProps={{
                    style: { color: "rgba(0, 0, 0, 0.87)" },
                  }}
                >
                  <MenuItem value="Telugu">Telugu</MenuItem>
                  <MenuItem value="Hindi">Hindi</MenuItem>
                  <MenuItem value="Tamil">Tamil</MenuItem>
                </TextField>

                <TextField
                  fullWidth
                  select
                  label="Target Language"
                  name="target_language"
                  value={formData.target_language}
                  onChange={handleChange}
                  InputLabelProps={{
                    style: { color: "rgba(0, 0, 0, 0.7)", fontWeight: 500 },
                  }}
                  InputProps={{
                    style: { color: "rgba(0, 0, 0, 0.87)" },
                  }}
                >
                  <MenuItem value="English">English</MenuItem>
                  <MenuItem value="Spanish">Spanish</MenuItem>
                  <MenuItem value="French">French</MenuItem>
                </TextField>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography
                  variant="body2"
                  sx={{
                    mb: 1,
                    color: "text.primary",
                    fontWeight: 600,
                  }}
                >
                  Learning Goals (Select any)
                </Typography>
                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                  {learningGoals.map((goal) => (
                    <Chip
                      key={goal}
                      label={goal}
                      onClick={() => handleGoalToggle(goal)}
                      color={
                        formData.learning_goals.includes(goal)
                          ? "primary"
                          : "default"
                      }
                      variant={
                        formData.learning_goals.includes(goal)
                          ? "filled"
                          : "outlined"
                      }
                    />
                  ))}
                </Box>
              </Box>

              <motion.div
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.7 }}
                style={{ marginBottom: "16px" }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <AnimatedButton
                  type="submit"
                  fullWidth
                  size="large"
                  disabled={loading}
                  sx={{
                    mb: 3,
                    py: 1.5,
                    fontSize: "1.1rem",
                    fontWeight: 600,
                    boxShadow: loading
                      ? "none"
                      : "0 4px 14px rgba(14, 165, 233, 0.4)",
                    "&:hover": {
                      boxShadow: "0 6px 20px rgba(14, 165, 233, 0.5)",
                    },
                  }}
                >
                  {loading ? (
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{
                          duration: 1,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                        style={{ display: "flex" }}
                      >
                        ⏳
                      </motion.div>
                      Creating Account...
                    </Box>
                  ) : (
                    "Sign Up"
                  )}
                </AnimatedButton>
              </motion.div>

              <Divider sx={{ mb: 3 }}>
                <Typography
                  variant="body2"
                  sx={{ color: "text.secondary", px: 2 }}
                >
                  Already a member?
                </Typography>
              </Divider>

              <AnimatedButton
                type="submit"
                fullWidth
                size="large"
                disabled={loading}
                sx={{ mb: 2 }}
              >
                {loading ? "Creating Account..." : "Sign Up"}
              </AnimatedButton>

              <Typography
                variant="body2"
                textAlign="center"
                sx={{ color: "text.primary", opacity: 0.9 }}
              >
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
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
};

export default Register;
