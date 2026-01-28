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
  Divider,
  Container,
} from "@mui/material";
import { Visibility, VisibilityOff, LockOutlined, PersonOutline } from "@mui/icons-material";
import { motion } from "framer-motion";
import AnimatedButton from "../../components/common/AnimatedButton";
import GradientText from "../../components/common/GradientText";
import FloatingParticles from "../../components/common/FloatingParticles";

const Login = () => {
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
  const [focusedField, setFocusedField] = useState(null);

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
      // Use smart redirect based on onboarding status
      const redirectPath = getOnboardingRedirectPath(result.user);
      navigate(redirectPath);
    } else {
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ position: "relative", width: "100%", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", py: 4 }}>
        <FloatingParticles />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{ width: "100%", maxWidth: 480 }}
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
                <LockOutlined sx={{ fontSize: 32, color: "white" }} />
              </Box>
              <Typography
                variant="h4"
                sx={{ color: "white", fontWeight: 700, mb: 0.5 }}
              >
                Welcome Back
              </Typography>
              <Typography
                variant="body2"
                sx={{ color: "rgba(255, 255, 255, 0.9)" }}
              >
                Sign in to continue your learning journey
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
                <Box sx={{ mb: 2.5 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      mb: 1,
                      fontWeight: 600,
                      color: "text.primary",
                      fontSize: "0.875rem",
                    }}
                  >
                    Username
                  </Typography>
                  <TextField
                    fullWidth
                    placeholder="Enter your username"
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
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography
                    variant="body2"
                    sx={{
                      mb: 1,
                      fontWeight: 600,
                      color: "text.primary",
                      fontSize: "0.875rem",
                    }}
                  >
                    Password
                  </Typography>
                  <TextField
                    fullWidth
                    placeholder="Enter your password"
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
                </Box>

                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 4,
                  }}
                >
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={rememberMe}
                        onChange={(e) => setRememberMe(e.target.checked)}
                        size="small"
                        sx={{
                          color: "#64748b",
                          "&.Mui-checked": {
                            color: "#0ea5e9",
                          },
                        }}
                      />
                    }
                    label={
                      <Typography
                        variant="body2"
                        sx={{ color: "text.secondary", fontSize: "0.875rem" }}
                      >
                        Remember me
                      </Typography>
                    }
                  />
                  <Link
                    to="/forgot-password"
                    style={{
                      color: "#0ea5e9",
                      textDecoration: "none",
                      fontSize: "0.875rem",
                      fontWeight: 600,
                    }}
                  >
                    Forgot password?
                  </Link>
                </Box>

                <AnimatedButton
                  type="submit"
                  fullWidth
                  size="large"
                  disabled={loading}
                  sx={{
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
                  {loading ? "Signing in..." : "Sign In"}
                </AnimatedButton>

                <Divider sx={{ mb: 3, borderColor: "#e2e8f0" }}>
                  <Typography
                    variant="body2"
                    sx={{ color: "text.secondary", px: 2, fontSize: "0.813rem" }}
                  >
                    New to ConvAI Learn?
                  </Typography>
                </Divider>

                <Box sx={{ textAlign: "center" }}>
                  <Typography
                    variant="body2"
                    sx={{ color: "text.secondary", mb: 1 }}
                  >
                    Don&apos;t have an account?
                  </Typography>
                  <Link
                    to="/register"
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
                    Create Account
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

export default Login;
