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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
} from "@mui/material";
import {
  Visibility,
  VisibilityOff,
  PersonAdd,
  Email,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { useAuthStore } from "../../store/index.js";
import { toast } from "react-hot-toast";

const registerSchema = yup.object().shape({
  username: yup
    .string()
    .min(3, "Username must be at least 3 characters")
    .required("Username is required"),
  email: yup
    .string()
    .email("Invalid email format")
    .required("Email is required"),
  password: yup
    .string()
    .min(6, "Password must be at least 6 characters")
    .required("Password is required"),
  confirmPassword: yup
    .string()
    .oneOf([yup.ref("password"), null], "Passwords must match")
    .required("Please confirm your password"),
  nativeLanguage: yup.string().required("Native language is required"),
  targetLanguage: yup.string().required("Target language is required"),
});

const learningGoalsOptions = [
  "conversation",
  "business",
  "academic",
  "travel",
  "general",
];

const Register = () => {
  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [learningGoals, setLearningGoals] = useState([]);

  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm({
    resolver: yupResolver(registerSchema),
    defaultValues: {
      nativeLanguage: "Telugu",
      targetLanguage: "English",
    },
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      const registrationData = {
        ...data,
        learning_goals: learningGoals,
      };
      delete registrationData.confirmPassword;

      const result = await register(registrationData);
      if (result && result.user) {
        toast.success(
          "Registration successful! Let's assess your current level."
        );
        // Redirect to initial assessment instead of login
        navigate("/initial-assessment", {
          state: {
            userId: result.user.id,
            isNewUser: true,
          },
        });
      } else {
        toast.success("Registration successful! Please log in.");
        navigate("/login");
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || "Registration failed";
      setError("root", { message: errorMessage });
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLearningGoalsChange = (event) => {
    const value = event.target.value;
    setLearningGoals(typeof value === "string" ? value.split(",") : value);
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
    <Container maxWidth="md">
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
                      <PersonAdd
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
                      Join Us Today!
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Start your Telugu learning adventure
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

                    <Box
                      sx={{
                        display: "grid",
                        gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
                        gap: 2,
                      }}
                    >
                      <motion.div variants={itemVariants}>
                        <TextField
                          {...registerField("username")}
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
                          {...registerField("email")}
                          fullWidth
                          label="Email"
                          type="email"
                          margin="normal"
                          error={!!errors.email}
                          helperText={errors.email?.message}
                          InputProps={{
                            startAdornment: (
                              <InputAdornment position="start">
                                <Email />
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
                        <TextField
                          {...registerField("password")}
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
                        <TextField
                          {...registerField("confirmPassword")}
                          fullWidth
                          label="Confirm Password"
                          type={showConfirmPassword ? "text" : "password"}
                          margin="normal"
                          error={!!errors.confirmPassword}
                          helperText={errors.confirmPassword?.message}
                          InputProps={{
                            endAdornment: (
                              <InputAdornment position="end">
                                <IconButton
                                  onClick={() =>
                                    setShowConfirmPassword(!showConfirmPassword)
                                  }
                                  edge="end"
                                >
                                  {showConfirmPassword ? (
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
                        <FormControl fullWidth margin="normal">
                          <InputLabel>Native Language</InputLabel>
                          <Select
                            {...registerField("nativeLanguage")}
                            label="Native Language"
                            error={!!errors.nativeLanguage}
                            sx={{ borderRadius: 2 }}
                          >
                            <MenuItem value="Telugu">Telugu</MenuItem>
                            <MenuItem value="Hindi">Hindi</MenuItem>
                            <MenuItem value="Tamil">Tamil</MenuItem>
                            <MenuItem value="Kannada">Kannada</MenuItem>
                            <MenuItem value="Malayalam">Malayalam</MenuItem>
                          </Select>
                        </FormControl>
                      </motion.div>

                      <motion.div variants={itemVariants}>
                        <FormControl fullWidth margin="normal">
                          <InputLabel>Target Language</InputLabel>
                          <Select
                            {...registerField("targetLanguage")}
                            label="Target Language"
                            error={!!errors.targetLanguage}
                            sx={{ borderRadius: 2 }}
                          >
                            <MenuItem value="English">English</MenuItem>
                            <MenuItem value="Hindi">Hindi</MenuItem>
                            <MenuItem value="Spanish">Spanish</MenuItem>
                            <MenuItem value="French">French</MenuItem>
                          </Select>
                        </FormControl>
                      </motion.div>
                    </Box>

                    <motion.div variants={itemVariants}>
                      <FormControl fullWidth margin="normal">
                        <InputLabel>Learning Goals</InputLabel>
                        <Select
                          multiple
                          value={learningGoals}
                          onChange={handleLearningGoalsChange}
                          input={<OutlinedInput label="Learning Goals" />}
                          renderValue={(selected) => (
                            <Box
                              sx={{
                                display: "flex",
                                flexWrap: "wrap",
                                gap: 0.5,
                              }}
                            >
                              {selected.map((value) => (
                                <Chip key={value} label={value} size="small" />
                              ))}
                            </Box>
                          )}
                          sx={{ borderRadius: 2 }}
                        >
                          {learningGoalsOptions.map((goal) => (
                            <MenuItem key={goal} value={goal}>
                              {goal.charAt(0).toUpperCase() + goal.slice(1)}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
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
                          "Create Account"
                        )}
                      </Button>
                    </motion.div>

                    <motion.div variants={itemVariants}>
                      <Box sx={{ textAlign: "center", mt: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Already have an account?{" "}
                          <Link
                            to="/login"
                            style={{
                              color: "#667eea",
                              textDecoration: "none",
                              fontWeight: "bold",
                            }}
                          >
                            Sign in here
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

export default Register;
