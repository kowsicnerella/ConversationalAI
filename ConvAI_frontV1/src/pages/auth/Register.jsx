import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useTranslation } from "react-i18next";
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
  Container,
  Grid,
} from "@mui/material";
import { 
  Visibility, 
  VisibilityOff, 
  PersonOutline, 
  EmailOutlined, 
  LockOutlined,
  LanguageOutlined,
  CheckCircleOutline,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import AnimatedButton from "../../components/common/AnimatedButton";
import FloatingParticles from "../../components/common/FloatingParticles";
import LanguageSwitcher from "../../components/common/LanguageSwitcher";

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
  const { t } = useTranslation();

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
    if (strength < 30) return t('auth.register.strength.weak');
    if (strength < 60) return t('auth.register.strength.fair');
    if (strength < 80) return t('auth.register.strength.good');
    return t('auth.register.strength.strong');
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
    <Container maxWidth="md">
      <Box sx={{ position: "relative", width: "100%", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", py: 4 }}>
        <FloatingParticles />
        
        {/* Language Switcher - Top Right */}
        <Box sx={{ position: "absolute", top: 16, right: 16, zIndex: 10 }}>
          <LanguageSwitcher />
        </Box>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{ width: "100%", maxWidth: 700 }}
        >
          <Card
            elevation={0}
            sx={{
              background: "#ffffff",
              boxShadow: "0 8px 40px rgba(0, 0, 0, 0.12)",
              border: "1px solid rgba(0, 0, 0, 0.08)",
              borderRadius: 4,
              overflow: "hidden",
            }}
          >
            {/* Brand Header */}
            <Box
              sx={{
                background: "linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)",
                py: 4,
                px: 4,
                textAlign: "center",
              }}
            >
              <Box
                sx={{
                  width: 64,
                  height: 64,
                  borderRadius: "50%",
                  background: "rgba(255, 255, 255, 0.2)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 16px",
                  backdropFilter: "blur(10px)",
                }}
              >
                <CheckCircleOutline sx={{ fontSize: 32, color: "white" }} />
              </Box>
              <Typography
                variant="h4"
                sx={{ color: "white", fontWeight: 700, mb: 0.5 }}
              >
                {t('auth.register.title')}
              </Typography>
              <Typography
                variant="body2"
                sx={{ color: "rgba(255, 255, 255, 0.9)" }}
              >
                {t('auth.register.subtitle')}
              </Typography>
            </Box>

            <CardContent sx={{ p: 4 }}>

              {/* Error Alert */}
              {error && (
                <Alert 
                  severity="error" 
                  sx={{ 
                    mb: 3,
                    borderRadius: 2,
                    "& .MuiAlert-message": {
                      width: "100%",
                    },
                  }}
                >
                  {error}
                </Alert>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit}>
                <Grid container spacing={2.5}>
                  {/* Username */}
                  <Grid item xs={12} sm={6}>
                    <Typography
                      variant="body2"
                      sx={{
                        mb: 1,
                        fontWeight: 600,
                        color: "text.primary",
                        fontSize: "0.875rem",
                      }}
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
                      autoFocus
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <PersonOutline sx={{ color: "text.secondary" }} />
                          </InputAdornment>
                        ),
                        sx: {
                          backgroundColor: "#f8fafc",
                          borderRadius: 2,
                          "&:hover": {
                            backgroundColor: "#f1f5f9",
                          },
                          "&.Mui-focused": {
                            backgroundColor: "white",
                            "& .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#0ea5e9",
                              borderWidth: 2,
                            },
                          },
                        },
                      }}
                      sx={{
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#e2e8f0",
                        },
                        "&:hover .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#cbd5e1",
                        },
                      }}
                    />
                  </Grid>

                  {/* Email */}
                  <Grid item xs={12} sm={6}>
                    <Typography
                      variant="body2"
                      sx={{
                        mb: 1,
                        fontWeight: 600,
                        color: "text.primary",
                        fontSize: "0.875rem",
                      }}
                    >
                      Email Address *
                    </Typography>
                    <TextField
                      fullWidth
                      placeholder="your.email@example.com"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <EmailOutlined sx={{ color: "text.secondary" }} />
                          </InputAdornment>
                        ),
                        sx: {
                          backgroundColor: "#f8fafc",
                          borderRadius: 2,
                          "&:hover": {
                            backgroundColor: "#f1f5f9",
                          },
                          "&.Mui-focused": {
                            backgroundColor: "white",
                            "& .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#0ea5e9",
                              borderWidth: 2,
                            },
                          },
                        },
                      }}
                      sx={{
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#e2e8f0",
                        },
                        "&:hover .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#cbd5e1",
                        },
                      }}
                    />
                  </Grid>

                  {/* Password */}
                  <Grid item xs={12} sm={6}>
                    <Typography
                      variant="body2"
                      sx={{
                        mb: 1,
                        fontWeight: 600,
                        color: "text.primary",
                        fontSize: "0.875rem",
                      }}
                    >
                      Password *
                    </Typography>
                    <TextField
                      fullWidth
                      placeholder="Create a strong password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleChange}
                      required
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockOutlined sx={{ color: "text.secondary" }} />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                              size="small"
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                        sx: {
                          backgroundColor: "#f8fafc",
                          borderRadius: 2,
                          "&:hover": {
                            backgroundColor: "#f1f5f9",
                          },
                          "&.Mui-focused": {
                            backgroundColor: "white",
                            "& .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#0ea5e9",
                              borderWidth: 2,
                            },
                          },
                        },
                      }}
                      sx={{
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#e2e8f0",
                        },
                        "&:hover .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#cbd5e1",
                        },
                      }}
                    />
                    {formData.password && (
                      <Box sx={{ mt: 1.5 }}>
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
                            sx={{ color: "text.secondary", fontSize: "0.75rem" }}
                          >
                            Strength:
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              color: getPasswordStrengthColor(passwordStrength),
                              fontWeight: 600,
                              fontSize: "0.75rem",
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
                              backgroundColor:
                                getPasswordStrengthColor(passwordStrength),
                              borderRadius: 2,
                            },
                          }}
                        />
                      </Box>
                    )}
                  </Grid>

                  {/* Confirm Password */}
                  <Grid item xs={12} sm={6}>
                    <Typography
                      variant="body2"
                      sx={{
                        mb: 1,
                        fontWeight: 600,
                        color: "text.primary",
                        fontSize: "0.875rem",
                      }}
                    >
                      Confirm Password *
                    </Typography>
                    <TextField
                      fullWidth
                      placeholder="Re-enter your password"
                      name="confirmPassword"
                      type={showPassword ? "text" : "password"}
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LockOutlined sx={{ color: "text.secondary" }} />
                          </InputAdornment>
                        ),
                        sx: {
                          backgroundColor: "#f8fafc",
                          borderRadius: 2,
                          "&:hover": {
                            backgroundColor: "#f1f5f9",
                          },
                          "&.Mui-focused": {
                            backgroundColor: "white",
                            "& .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#0ea5e9",
                              borderWidth: 2,
                            },
                          },
                        },
                      }}
                      sx={{
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#e2e8f0",
                        },
                        "&:hover .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#cbd5e1",
                        },
                      }}
                    />
                  </Grid>

                  {/* Native Language */}
                  <Grid item xs={12} sm={6}>
                    <Typography
                      variant="body2"
                      sx={{
                        mb: 1,
                        fontWeight: 600,
                        color: "text.primary",
                        fontSize: "0.875rem",
                      }}
                    >
                      Native Language
                    </Typography>
                    <TextField
                      fullWidth
                      select
                      name="native_language"
                      value={formData.native_language}
                      onChange={handleChange}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LanguageOutlined sx={{ color: "text.secondary" }} />
                          </InputAdornment>
                        ),
                        sx: {
                          backgroundColor: "#f8fafc",
                          borderRadius: 2,
                          "&:hover": {
                            backgroundColor: "#f1f5f9",
                          },
                          "&.Mui-focused": {
                            backgroundColor: "white",
                            "& .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#0ea5e9",
                              borderWidth: 2,
                            },
                          },
                        },
                      }}
                      sx={{
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#e2e8f0",
                        },
                        "&:hover .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#cbd5e1",
                        },
                      }}
                    >
                      <MenuItem value="Telugu">Telugu</MenuItem>
                      <MenuItem value="Hindi">Hindi</MenuItem>
                      <MenuItem value="Tamil">Tamil</MenuItem>
                    </TextField>
                  </Grid>

                  {/* Target Language */}
                  <Grid item xs={12} sm={6}>
                    <Typography
                      variant="body2"
                      sx={{
                        mb: 1,
                        fontWeight: 600,
                        color: "text.primary",
                        fontSize: "0.875rem",
                      }}
                    >
                      Target Language
                    </Typography>
                    <TextField
                      fullWidth
                      select
                      name="target_language"
                      value={formData.target_language}
                      onChange={handleChange}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <LanguageOutlined sx={{ color: "text.secondary" }} />
                          </InputAdornment>
                        ),
                        sx: {
                          backgroundColor: "#f8fafc",
                          borderRadius: 2,
                          "&:hover": {
                            backgroundColor: "#f1f5f9",
                          },
                          "&.Mui-focused": {
                            backgroundColor: "white",
                            "& .MuiOutlinedInput-notchedOutline": {
                              borderColor: "#0ea5e9",
                              borderWidth: 2,
                            },
                          },
                        },
                      }}
                      sx={{
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#e2e8f0",
                        },
                        "&:hover .MuiOutlinedInput-notchedOutline": {
                          borderColor: "#cbd5e1",
                        },
                      }}
                    >
                      <MenuItem value="English">English</MenuItem>
                      <MenuItem value="Spanish">Spanish</MenuItem>
                      <MenuItem value="French">French</MenuItem>
                    </TextField>
                  </Grid>

                  {/* Learning Goals */}
                  <Grid item xs={12}>
                    <Typography
                      variant="body2"
                      sx={{
                        mb: 1.5,
                        fontWeight: 600,
                        color: "text.primary",
                        fontSize: "0.875rem",
                      }}
                    >
                      Learning Goals
                      <Typography
                        component="span"
                        sx={{ color: "text.secondary", fontWeight: 400, ml: 1, fontSize: "0.813rem" }}
                      >
                        (Optional - Select any that apply)
                      </Typography>
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1.5 }}>
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
                          sx={{
                            fontWeight: 500,
                            fontSize: "0.875rem",
                            px: 1.5,
                            py: 2.5,
                            borderRadius: 2,
                            transition: "all 0.2s ease",
                            cursor: "pointer",
                            "&:hover": {
                              transform: "translateY(-2px)",
                              boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
                            },
                            ...(formData.learning_goals.includes(goal) && {
                              backgroundColor: "#0ea5e9",
                              color: "white",
                              "&:hover": {
                                backgroundColor: "#0284c7",
                              },
                            }),
                          }}
                        />
                      ))}
                    </Box>
                  </Grid>
                </Grid>

                <AnimatedButton
                  type="submit"
                  fullWidth
                  size="large"
                  disabled={loading}
                  sx={{
                    mt: 4,
                    mb: 3,
                    py: 1.75,
                    fontSize: "1rem",
                    fontWeight: 600,
                    textTransform: "none",
                    borderRadius: 2,
                    background: "linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)",
                    boxShadow: "0 4px 12px rgba(14, 165, 233, 0.3)",
                    "&:hover": {
                      background: "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
                      boxShadow: "0 6px 16px rgba(14, 165, 233, 0.4)",
                    },
                    "&:disabled": {
                      background: "#cbd5e1",
                      color: "#64748b",
                    },
                  }}
                >
                  {loading ? "Creating Your Account..." : "Create Account"}
                </AnimatedButton>

                <Divider sx={{ mb: 3, borderColor: "#e2e8f0" }}>
                  <Typography
                    variant="body2"
                    sx={{ color: "text.secondary", px: 2, fontSize: "0.813rem" }}
                  >
                    Already have an account?
                  </Typography>
                </Divider>

                <Box sx={{ textAlign: "center" }}>
                  <Link
                    to="/login"
                    style={{
                      display: "inline-block",
                      width: "100%",
                      padding: "12px",
                      color: "#0ea5e9",
                      textDecoration: "none",
                      fontWeight: 600,
                      fontSize: "0.938rem",
                      border: "2px solid #0ea5e9",
                      borderRadius: "8px",
                      transition: "all 0.2s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.backgroundColor = "#f0f9ff";
                      e.target.style.borderColor = "#0284c7";
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.backgroundColor = "transparent";
                      e.target.style.borderColor = "#0ea5e9";
                    }}
                  >
                    Sign In to Your Account
                  </Link>
                </Box>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    </Container>
  );
};

export default Register;
