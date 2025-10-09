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
  Container,
  Stack,
  Paper,
  LinearProgress,
  Grid,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  PersonAdd as PersonAddIcon,
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

    // eslint-disable-next-line no-unused-vars
    const { confirmPassword, ...registerData } = formData;
    const result = await register(registerData);

    if (result.success) {
      navigate("/onboarding");
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 3,
      }}
    >
      <Container maxWidth="md">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Paper
            elevation={24}
            sx={{
              borderRadius: 4,
              overflow: "hidden",
              background: "linear-gradient(to bottom, #ffffff, #f8f9fa)",
              maxHeight: "90vh",
              overflowY: "auto",
            }}
          >
            <Box
              sx={{
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                padding: 4,
                textAlign: "center",
                color: "white",
              }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
              >
                <PersonAddIcon sx={{ fontSize: 60, mb: 2 }} />
              </motion.div>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Join ConvAI Learn
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Start your language learning journey today
              </Typography>
            </Box>

            <CardContent sx={{ padding: 4 }}>
              {error && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                >
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                </motion.div>
              )}

              <form onSubmit={handleSubmit}>
                <Stack spacing={3}>
                  <TextField
                    fullWidth
                    label="Username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    required
                    autoFocus
                    variant="outlined"
                    sx={{
                      "& .MuiOutlinedInput-root": {
                        backgroundColor: "white",
                        "& fieldset": {
                          borderColor: "rgba(0, 0, 0, 0.23)",
                          borderWidth: 2,
                        },
                        "&:hover fieldset": {
                          borderColor: "#667eea",
                        },
                        "&.Mui-focused fieldset": {
                          borderColor: "#667eea",
                        },
                      },
                      "& .MuiInputLabel-root": {
                        color: "rgba(0, 0, 0, 0.7)",
                        fontWeight: 600,
                      },
                      "& .MuiInputLabel-root.Mui-focused": {
                        color: "#667eea",
                      },
                      "& input": {
                        color: "black",
                        fontSize: "1rem",
                      },
                    }}
                  />

                  <TextField
                    fullWidth
                    label="Email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    variant="outlined"
                    sx={{
                      "& .MuiOutlinedInput-root": {
                        backgroundColor: "white",
                        "& fieldset": {
                          borderColor: "rgba(0, 0, 0, 0.23)",
                          borderWidth: 2,
                        },
                        "&:hover fieldset": {
                          borderColor: "#667eea",
                        },
                        "&.Mui-focused fieldset": {
                          borderColor: "#667eea",
                        },
                      },
                      "& .MuiInputLabel-root": {
                        color: "rgba(0, 0, 0, 0.7)",
                        fontWeight: 600,
                      },
                      "& .MuiInputLabel-root.Mui-focused": {
                        color: "#667eea",
                      },
                      "& input": {
                        color: "black",
                        fontSize: "1rem",
                      },
                    }}
                  />

                  <Box>
                    <TextField
                      fullWidth
                      label="Password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleChange}
                      required
                      variant="outlined"
                      sx={{
                        "& .MuiOutlinedInput-root": {
                          backgroundColor: "white",
                          "& fieldset": {
                            borderColor: "rgba(0, 0, 0, 0.23)",
                            borderWidth: 2,
                          },
                          "&:hover fieldset": {
                            borderColor: "#667eea",
                          },
                          "&.Mui-focused fieldset": {
                            borderColor: "#667eea",
                          },
                        },
                        "& .MuiInputLabel-root": {
                          color: "rgba(0, 0, 0, 0.7)",
                          fontWeight: 600,
                        },
                        "& .MuiInputLabel-root.Mui-focused": {
                          color: "#667eea",
                        },
                        "& input": {
                          color: "black",
                          fontSize: "1rem",
                        },
                      }}
                      InputProps={{
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              onClick={() => setShowPassword(!showPassword)}
                              edge="end"
                            >
                              {showPassword ? (
                                <VisibilityOff />
                              ) : (
                                <Visibility />
                              )}
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
                          <Typography
                            variant="caption"
                            sx={{
                              color: "rgba(0, 0, 0, 0.7)",
                              fontWeight: 600,
                            }}
                          >
                            Password Strength:
                          </Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              color: getPasswordStrengthColor(passwordStrength),
                              fontWeight: 700,
                            }}
                          >
                            {getPasswordStrengthLabel(passwordStrength)}
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={passwordStrength}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: "rgba(0, 0, 0, 0.1)",
                            "& .MuiLinearProgress-bar": {
                              backgroundColor:
                                getPasswordStrengthColor(passwordStrength),
                              borderRadius: 4,
                            },
                          }}
                        />
                      </Box>
                    )}
                  </Box>

                  <TextField
                    fullWidth
                    label="Confirm Password"
                    name="confirmPassword"
                    type={showPassword ? "text" : "password"}
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required
                    variant="outlined"
                    sx={{
                      "& .MuiOutlinedInput-root": {
                        backgroundColor: "white",
                        "& fieldset": {
                          borderColor: "rgba(0, 0, 0, 0.23)",
                          borderWidth: 2,
                        },
                        "&:hover fieldset": {
                          borderColor: "#667eea",
                        },
                        "&.Mui-focused fieldset": {
                          borderColor: "#667eea",
                        },
                      },
                      "& .MuiInputLabel-root": {
                        color: "rgba(0, 0, 0, 0.7)",
                        fontWeight: 600,
                      },
                      "& .MuiInputLabel-root.Mui-focused": {
                        color: "#667eea",
                      },
                      "& input": {
                        color: "black",
                        fontSize: "1rem",
                      },
                    }}
                  />

                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        select
                        label="Native Language"
                        name="native_language"
                        value={formData.native_language}
                        onChange={handleChange}
                        variant="outlined"
                        sx={{
                          "& .MuiOutlinedInput-root": {
                            backgroundColor: "white",
                            "& fieldset": {
                              borderColor: "rgba(0, 0, 0, 0.23)",
                              borderWidth: 2,
                            },
                            "&:hover fieldset": {
                              borderColor: "#667eea",
                            },
                            "&.Mui-focused fieldset": {
                              borderColor: "#667eea",
                            },
                          },
                          "& .MuiInputLabel-root": {
                            color: "rgba(0, 0, 0, 0.7)",
                            fontWeight: 600,
                          },
                          "& .MuiInputLabel-root.Mui-focused": {
                            color: "#667eea",
                          },
                          "& .MuiSelect-select": {
                            color: "black",
                            fontSize: "1rem",
                          },
                        }}
                      >
                        <MenuItem value="Telugu">Telugu</MenuItem>
                        <MenuItem value="Hindi">Hindi</MenuItem>
                        <MenuItem value="Tamil">Tamil</MenuItem>
                      </TextField>
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        fullWidth
                        select
                        label="Target Language"
                        name="target_language"
                        value={formData.target_language}
                        onChange={handleChange}
                        variant="outlined"
                        sx={{
                          "& .MuiOutlinedInput-root": {
                            backgroundColor: "white",
                            "& fieldset": {
                              borderColor: "rgba(0, 0, 0, 0.23)",
                              borderWidth: 2,
                            },
                            "&:hover fieldset": {
                              borderColor: "#667eea",
                            },
                            "&.Mui-focused fieldset": {
                              borderColor: "#667eea",
                            },
                          },
                          "& .MuiInputLabel-root": {
                            color: "rgba(0, 0, 0, 0.7)",
                            fontWeight: 600,
                          },
                          "& .MuiInputLabel-root.Mui-focused": {
                            color: "#667eea",
                          },
                          "& .MuiSelect-select": {
                            color: "black",
                            fontSize: "1rem",
                          },
                        }}
                      >
                        <MenuItem value="English">English</MenuItem>
                        <MenuItem value="Spanish">Spanish</MenuItem>
                        <MenuItem value="French">French</MenuItem>
                      </TextField>
                    </Grid>
                  </Grid>

                  <Box>
                    <Typography
                      variant="body2"
                      sx={{
                        mb: 1.5,
                        color: "rgba(0, 0, 0, 0.8)",
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
                          sx={{
                            backgroundColor: formData.learning_goals.includes(
                              goal
                            )
                              ? "#667eea"
                              : "white",
                            color: formData.learning_goals.includes(goal)
                              ? "white"
                              : "rgba(0, 0, 0, 0.7)",
                            border: "2px solid",
                            borderColor: formData.learning_goals.includes(goal)
                              ? "#667eea"
                              : "rgba(0, 0, 0, 0.23)",
                            fontWeight: 600,
                            "&:hover": {
                              backgroundColor: formData.learning_goals.includes(
                                goal
                              )
                                ? "#5568d3"
                                : "rgba(102, 126, 234, 0.1)",
                            },
                          }}
                        />
                      ))}
                    </Box>
                  </Box>

                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Box
                      component="button"
                      type="submit"
                      disabled={loading}
                      sx={{
                        width: "100%",
                        padding: "16px",
                        border: "none",
                        borderRadius: "12px",
                        background:
                          "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        color: "white",
                        fontSize: "1.1rem",
                        fontWeight: "bold",
                        cursor: loading ? "not-allowed" : "pointer",
                        opacity: loading ? 0.7 : 1,
                        boxShadow: "0 4px 15px rgba(102, 126, 234, 0.4)",
                        transition: "all 0.3s ease",
                        "&:hover": {
                          boxShadow: loading
                            ? "0 4px 15px rgba(102, 126, 234, 0.4)"
                            : "0 6px 20px rgba(102, 126, 234, 0.6)",
                          transform: loading ? "none" : "translateY(-2px)",
                        },
                      }}
                    >
                      {loading ? "Creating Account..." : "Sign Up"}
                    </Box>
                  </motion.div>
                </Stack>
              </form>

              <Box sx={{ textAlign: "center", mt: 3 }}>
                <Typography sx={{ color: "rgba(0, 0, 0, 0.7)" }}>
                  Already have an account?{" "}
                  <Link
                    to="/login"
                    style={{
                      color: "#667eea",
                      textDecoration: "none",
                      fontWeight: 700,
                    }}
                  >
                    Sign in
                  </Link>
                </Typography>
              </Box>
            </CardContent>
          </Paper>
        </motion.div>
      </Container>
    </Box>
  );
};

export default NewRegister;
