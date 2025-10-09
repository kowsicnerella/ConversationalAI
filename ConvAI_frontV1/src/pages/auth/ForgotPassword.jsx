import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Typography,
  Alert,
} from "@mui/material";
import { motion } from "framer-motion";
import AnimatedButton from "../../components/common/AnimatedButton";
import GradientText from "../../components/common/GradientText";
import FloatingParticles from "../../components/common/FloatingParticles";
import axiosInstance, { API_ENDPOINTS } from "../../config/api";

const ForgotPassword = () => {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await axiosInstance.post(API_ENDPOINTS.AUTH.FORGOT_PASSWORD, { email });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to send reset link");
    }

    setLoading(false);
  };

  return (
    <Box sx={{ position: "relative", width: "100%", maxWidth: 450 }}>
      <FloatingParticles />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <Card
          sx={{
            backdropFilter: "blur(20px)",
            background: "rgba(255, 255, 255, 0.95)",
            boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
            position: "relative",
            zIndex: 1,
          }}
        >
          <CardContent sx={{ p: 4 }}>
            {/* Header */}
            <Box sx={{ textAlign: "center", mb: 4 }}>
              <GradientText variant="h4" sx={{ mb: 1, fontWeight: 800 }}>
                Reset Password
              </GradientText>
              <Typography variant="body2" color="text.secondary">
                Enter your email to receive a password reset link
              </Typography>
            </Box>

            {/* Success Message */}
            {success && (
              <Alert severity="success" sx={{ mb: 3 }}>
                Password reset link sent! Check your email.
              </Alert>
            )}

            {/* Error Alert */}
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            {!success && (
              <form onSubmit={handleSubmit}>
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  sx={{ mb: 3 }}
                  autoFocus
                />

                <AnimatedButton
                  type="submit"
                  fullWidth
                  size="large"
                  disabled={loading}
                  sx={{ mb: 2 }}
                >
                  {loading ? "Sending..." : "Send Reset Link"}
                </AnimatedButton>

                <Typography
                  variant="body2"
                  textAlign="center"
                  color="text.secondary"
                >
                  Remember your password?{" "}
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
            )}

            {success && (
              <AnimatedButton
                fullWidth
                size="large"
                component={Link}
                to="/login"
              >
                Back to Sign In
              </AnimatedButton>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </Box>
  );
};

export default ForgotPassword;
