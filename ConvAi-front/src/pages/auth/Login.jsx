import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  IconButton,
  InputAdornment,
  Alert,
  CircularProgress,
  Paper,
  Container,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  Login as LoginIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { useAuthStore } from "../../store/index.js";
import { toast } from "react-hot-toast";

const loginSchema = yup.object().shape({
  username: yup.string().required("Username is required"),
  password: yup.string().required("Password is required"),
});

const Login = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm({
    resolver: yupResolver(loginSchema),
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      await login(data.username, data.password);
      toast.success("Login successful!");
      navigate("/dashboard");
    } catch (error) {
      const errorMessage = error.response?.data?.error || "Login failed";
      setError("root", { message: errorMessage });
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        when: "beforeChildren",
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          py: 4,
        }}
      >
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          style={{ width: "100%" }}
        >
          <Paper
            component={motion.div}
            elevation={12}
            sx={{
              borderRadius: 4,
              overflow: "hidden",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              p: 0.2,
            }}
          >
            <Card
              sx={{
                borderRadius: 4,
                background: (theme) =>
                  theme.palette.mode === "dark"
                    ? "rgba(30, 30, 30, 0.95)"
                    : "rgba(255, 255, 255, 0.95)",
                backdropFilter: "blur(20px)",
              }}
            >
              <CardContent sx={{ p: 4 }}>
                <motion.div variants={itemVariants}>
                  <Box sx={{ textAlign: "center", mb: 4 }}>
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{
                        delay: 0.2,
                        type: "spring",
                        stiffness: 260,
                        damping: 20,
                      }}
                    >
                      <LoginIcon
                        sx={{
                          fontSize: 64,
                          color: "primary.main",
                          mb: 2,
                        }}
                      />
                    </motion.div>
                    <Typography
                      variant="h4"
                      component="h1"
                      gutterBottom
                      sx={{
                        fontWeight: "bold",
                        background: "linear-gradient(45deg, #667eea, #764ba2)",
                        backgroundClip: "text",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                      }}
                    >
                      Welcome Back!
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Continue your Telugu learning journey
                    </Typography>
                  </Box>
                </motion.div>

                <motion.div variants={itemVariants}>
                  <Box
                    component="form"
                    onSubmit={handleSubmit(onSubmit)}
                    noValidate
                  >
                    {errors.root && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                      >
                        <Alert severity="error" sx={{ mb: 2 }}>
                          {errors.root.message}
                        </Alert>
                      </motion.div>
                    )}

                    <motion.div variants={itemVariants}>
                      <TextField
                        {...register("username")}
                        fullWidth
                        label="Username"
                        margin="normal"
                        error={!!errors.username}
                        helperText={errors.username?.message}
                        sx={{
                          "& .MuiOutlinedInput-root": {
                            borderRadius: 2,
                            transition: "all 0.3s ease",
                            "&:hover": {
                              transform: "translateY(-2px)",
                              boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
                            },
                          },
                        }}
                      />
                    </motion.div>

                    <motion.div variants={itemVariants}>
                      <TextField
                        {...register("password")}
                        fullWidth
                        label="Password"
                        type={showPassword ? "text" : "password"}
                        margin="normal"
                        error={!!errors.password}
                        helperText={errors.password?.message}
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
                        sx={{
                          "& .MuiOutlinedInput-root": {
                            borderRadius: 2,
                            transition: "all 0.3s ease",
                            "&:hover": {
                              transform: "translateY(-2px)",
                              boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
                            },
                          },
                        }}
                      />
                    </motion.div>

                    <motion.div variants={itemVariants}>
                      <Button
                        type="submit"
                        fullWidth
                        variant="contained"
                        disabled={isLoading}
                        component={motion.button}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        sx={{
                          mt: 3,
                          mb: 2,
                          py: 1.5,
                          borderRadius: 2,
                          fontSize: "1.1rem",
                          fontWeight: "bold",
                          background:
                            "linear-gradient(45deg, #667eea, #764ba2)",
                          boxShadow: "0 4px 15px rgba(102, 126, 234, 0.4)",
                          "&:hover": {
                            boxShadow: "0 6px 20px rgba(102, 126, 234, 0.6)",
                          },
                        }}
                      >
                        {isLoading ? (
                          <CircularProgress size={24} color="inherit" />
                        ) : (
                          "Sign In"
                        )}
                      </Button>
                    </motion.div>

                    <motion.div variants={itemVariants}>
                      <Box sx={{ textAlign: "center", mt: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Don&apos;t have an account?{" "}
                          <Link
                            to="/register"
                            style={{
                              color: "#667eea",
                              textDecoration: "none",
                              fontWeight: "bold",
                            }}
                          >
                            Sign up here
                          </Link>
                        </Typography>
                      </Box>
                    </motion.div>
                  </Box>
                </motion.div>
              </CardContent>
            </Card>
          </Paper>
        </motion.div>
      </Box>
    </Container>
  );
};

export default Login;
