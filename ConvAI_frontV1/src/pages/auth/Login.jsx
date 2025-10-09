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
} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
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
    <Box sx={{ position: "relative", width: "100%", maxWidth: 450 }}>
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
            transition: "all 0.3s ease",
          }}
        >
          <CardContent sx={{ p: 4 }}>
            {/* Header */}
            <Box sx={{ textAlign: "center", mb: 4 }}>
              <GradientText variant="h4" sx={{ mb: 1, fontWeight: 800 }}>
                Welcome Back!
              </GradientText>
              <Typography
                variant="body2"
                sx={{ color: "text.secondary", opacity: 0.8 }}
              >
                Sign in to continue your learning journey
              </Typography>
            </Box>

            {/* Error Alert */}
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
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
                    mb: 2.5,
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
                  label="Password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={handleChange}
                  onFocus={() => setFocusedField("password")}
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
              </motion.div>

              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 3,
                }}
              >
                <motion.div
                  initial={{ x: -10, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={rememberMe}
                        onChange={(e) => setRememberMe(e.target.checked)}
                        sx={{
                          color: "#0ea5e9",
                          "&.Mui-checked": {
                            color: "#0ea5e9",
                          },
                        }}
                      />
                    }
                    label={
                      <Typography
                        variant="body2"
                        sx={{ color: "rgba(0, 0, 0, 0.7)" }}
                      >
                        Remember me
                      </Typography>
                    }
                  />
                </motion.div>
                <motion.div
                  initial={{ x: 10, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  <Link
                    to="/forgot-password"
                    style={{
                      color: "#0ea5e9",
                      textDecoration: "none",
                      fontSize: "0.875rem",
                      fontWeight: 600,
                      transition: "all 0.2s ease",
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.textDecoration = "underline";
                      e.target.style.color = "#0284c7";
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.textDecoration = "none";
                      e.target.style.color = "#0ea5e9";
                    }}
                  >
                    Forgot password?
                  </Link>
                </motion.div>
              </Box>

              <motion.div
                initial={{ y: 10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.5 }}
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
                        🔄
                      </motion.div>
                      Signing in...
                    </Box>
                  ) : (
                    "Sign In"
                  )}
                </AnimatedButton>
              </motion.div>

              <Divider sx={{ mb: 3 }}>
                <Typography
                  variant="body2"
                  sx={{ color: "text.secondary", px: 2 }}
                >
                  or
                </Typography>
              </Divider>

              <Typography
                variant="body2"
                textAlign="center"
                sx={{ color: "text.primary", opacity: 0.9 }}
              >
                Don&apos;t have an account?{" "}
                <Link
                  to="/register"
                  style={{
                    color: "#0ea5e9",
                    textDecoration: "none",
                    fontWeight: 600,
                  }}
                >
                  Sign up
                </Link>
              </Typography>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
};

export default Login;
