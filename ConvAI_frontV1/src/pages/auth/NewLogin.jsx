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
  Checkbox,
  FormControlLabel,
  Container,
  Stack,
  Paper,
  useTheme,
  useMediaQuery,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Language as LanguageIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";

const NewLogin = () => {
  const navigate = useNavigate();
  const { login, getOnboardingRedirectPath } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

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
        width: "100%",
        display: "flex",
        flexDirection: { xs: "column", md: "row" },
        background: "#f8fafc",
      }}
    >
      {/* Left Side - Branding (Hidden on mobile) */}
      <Box
        sx={{
          display: { xs: "none", md: "flex" },
          flex: 1,
          background: "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: { md: 4, lg: 6 },
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
          style={{ textAlign: "center", zIndex: 1, maxWidth: 450 }}
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
              fontSize: { md: "2rem", lg: "2.5rem" },
            }}
          >
            ConvAI Learn
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: "rgba(255, 255, 255, 0.9)",
              maxWidth: 400,
              lineHeight: 1.6,
              fontWeight: 400,
              mx: "auto",
            }}
          >
            Master languages through AI-powered conversations and personalized learning paths
          </Typography>
          
          {/* Features List */}
          <Stack spacing={2} sx={{ mt: 6, textAlign: "left", px: 2 }}>
            {[
              "Personalized learning paths",
              "AI-powered conversations",
              "Track your progress",
              "Gamified experience",
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

      {/* Right Side - Login Form */}
      <Box
        sx={{
          flex: { xs: 1, md: "0 0 50%" },
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: { xs: 2, sm: 4, md: 6 },
          minHeight: { xs: "100vh", md: "auto" },
          overflowY: "auto",
        }}
      >
        {/* Mobile Header */}
        <Box
          sx={{
            display: { xs: "flex", md: "none" },
            alignItems: "center",
            gap: 2,
            mb: 4,
          }}
        >
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: "12px",
              background: "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <LanguageIcon sx={{ fontSize: 28, color: "white" }} />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700, color: "#1e293b" }}>
            ConvAI Learn
          </Typography>
        </Box>

        <Box sx={{ width: "100%", maxWidth: 440, px: { xs: 1, sm: 0 } }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Paper
              elevation={0}
              sx={{
                p: { xs: 3, sm: 4 },
                borderRadius: 3,
                background: "white",
                boxShadow: "0 4px 24px rgba(0, 0, 0, 0.06)",
                border: "1px solid #e2e8f0",
              }}
            >
              <Box sx={{ mb: 4 }}>
                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    color: "#1e293b",
                    mb: 1,
                    fontSize: { xs: "1.5rem", sm: "1.75rem" },
                  }}
                >
                  Welcome back
                </Typography>
                <Typography sx={{ color: "#64748b", fontSize: { xs: "0.875rem", sm: "1rem" } }}>
                  Sign in to continue your learning journey
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
                <Stack spacing={2.5}>
                  <Box>
                    <Typography
                      variant="body2"
                      sx={{ mb: 1, fontWeight: 600, color: "#374151" }}
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
                      autoFocus={!isMobile}
                      size={isMobile ? "small" : "medium"}
                      sx={{
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
                      }}
                    />
                  </Box>

                  <Box>
                    <Typography
                      variant="body2"
                      sx={{ mb: 1, fontWeight: 600, color: "#374151" }}
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
                      size={isMobile ? "small" : "medium"}
                      sx={{
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
                      }}
                      InputProps={{
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
                      }}
                    />
                  </Box>

                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      flexWrap: "wrap",
                      gap: 1,
                    }}
                  >
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={rememberMe}
                          onChange={(e) => setRememberMe(e.target.checked)}
                          size="small"
                          sx={{
                            color: "#94a3b8",
                            "&.Mui-checked": { color: "#0ea5e9" },
                          }}
                        />
                      }
                      label={
                        <Typography variant="body2" sx={{ color: "#64748b" }}>
                          Remember me
                        </Typography>
                      }
                    />
                    <Link
                      to="/forgot-password"
                      style={{
                        color: "#0ea5e9",
                        textDecoration: "none",
                        fontWeight: 600,
                        fontSize: "0.875rem",
                      }}
                    >
                      Forgot password?
                    </Link>
                  </Box>

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
                      "&:hover": {
                        boxShadow: loading ? "none" : "0 6px 20px rgba(14, 165, 233, 0.4)",
                        transform: loading ? "none" : "translateY(-1px)",
                      },
                      "&:active": {
                        transform: "translateY(0)",
                      },
                    }}
                  >
                    {loading ? "Signing in..." : "Sign In"}
                  </Box>
                </Stack>
              </form>

              <Box sx={{ textAlign: "center", mt: 3, pt: 3, borderTop: "1px solid #e2e8f0" }}>
                <Typography sx={{ color: "#64748b", fontSize: { xs: "0.875rem", sm: "1rem" } }}>
                  Don't have an account?{" "}
                  <Link
                    to="/register"
                    style={{
                      color: "#0ea5e9",
                      textDecoration: "none",
                      fontWeight: 600,
                    }}
                  >
                    Create account
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

export default NewLogin;
