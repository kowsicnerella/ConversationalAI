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
  Checkbox,
  FormControlLabel,
  Container,
  Stack,
  Paper,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Login as LoginIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";

const NewLogin = () => {
  const navigate = useNavigate();
  const { login, getOnboardingRedirectPath } = useAuth();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const result = await login(formData.username, formData.password);

    if (result.success) {
      const redirectPath = getOnboardingRedirectPath(result.user);
      navigate(redirectPath);
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
        padding: 2,
      }}
    >
      <Container maxWidth="sm">
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
                <LoginIcon sx={{ fontSize: 60, mb: 2 }} />
              </motion.div>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Welcome Back!
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Sign in to continue your learning journey
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
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                  />

                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={rememberMe}
                          onChange={(e) => setRememberMe(e.target.checked)}
                          sx={{
                            color: "#667eea",
                            "&.Mui-checked": {
                              color: "#667eea",
                            },
                          }}
                        />
                      }
                      label={
                        <Typography sx={{ color: "rgba(0, 0, 0, 0.8)" }}>
                          Remember me
                        </Typography>
                      }
                    />
                    <Link
                      to="/forgot-password"
                      style={{
                        color: "#667eea",
                        textDecoration: "none",
                        fontWeight: 600,
                      }}
                    >
                      Forgot password?
                    </Link>
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
                      {loading ? "Signing in..." : "Sign In"}
                    </Box>
                  </motion.div>
                </Stack>
              </form>

              <Box sx={{ textAlign: "center", mt: 3 }}>
                <Typography sx={{ color: "rgba(0, 0, 0, 0.7)" }}>
                  Don't have an account?{" "}
                  <Link
                    to="/register"
                    style={{
                      color: "#667eea",
                      textDecoration: "none",
                      fontWeight: 700,
                    }}
                  >
                    Sign up
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

export default NewLogin;
