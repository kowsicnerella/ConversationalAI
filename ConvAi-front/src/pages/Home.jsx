import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import PropTypes from "prop-types";
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Avatar,
  Rating,
  useTheme,
  useMediaQuery,
  Paper,
} from "@mui/material";
import {
  PlayArrow,
  School,
  EmojiEvents,
  Chat,
  Analytics,
  ArrowForward,
  Language,
  Psychology,
  Groups,
} from "@mui/icons-material";
import { motion, useAnimation, useInView } from "framer-motion";
import { useAuthStore } from "../store/index.js";

const features = [
  {
    icon: <School sx={{ fontSize: 40 }} />,
    title: "Interactive Learning",
    description:
      "Engage with AI-powered lessons tailored to your learning style and pace.",
    color: "#667eea",
  },
  {
    icon: <Chat sx={{ fontSize: 40 }} />,
    title: "AI Tutor",
    description:
      "Practice conversations with our intelligent Telugu-English AI tutor.",
    color: "#764ba2",
  },
  {
    icon: <EmojiEvents sx={{ fontSize: 40 }} />,
    title: "Gamification",
    description:
      "Earn badges, climb leaderboards, and celebrate your progress.",
    color: "#f093fb",
  },
  {
    icon: <Analytics sx={{ fontSize: 40 }} />,
    title: "Progress Tracking",
    description:
      "Monitor your learning journey with detailed analytics and insights.",
    color: "#f5576c",
  },
];

const testimonials = [
  {
    name: "Priya Sharma",
    avatar: "/avatars/priya.jpg",
    rating: 5,
    comment:
      "This platform revolutionized my English learning! The AI tutor is incredibly helpful.",
    location: "Hyderabad, India",
  },
  {
    name: "Ravi Kumar",
    avatar: "/avatars/ravi.jpg",
    rating: 5,
    comment:
      "The gamification features keep me motivated. I ve learned more in 3 months than in years!",
    location: "Bangalore, India",
  },
  {
    name: "Lakshmi Devi",
    avatar: "/avatars/lakshmi.jpg",
    rating: 5,
    comment:
      "Perfect for busy professionals. I can learn anytime, anywhere with personalized lessons.",
    location: "Chennai, India",
  },
];

const stats = [
  { number: "10K+", label: "Active Learners" },
  { number: "95%", label: "Success Rate" },
  { number: "50+", label: "Interactive Lessons" },
  { number: "24/7", label: "AI Support" },
];

// Animated Section Component
const AnimatedSection = ({ children, delay = 0 }) => {
  const controls = useAnimation();
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (inView) {
      controls.start("visible");
    }
  }, [controls, inView]);

  return (
    <motion.div
      ref={ref}
      animate={controls}
      initial="hidden"
      variants={{
        hidden: { opacity: 0, y: 75 },
        visible: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.6, delay },
        },
      }}
    >
      {children}
    </motion.div>
  );
};

AnimatedSection.propTypes = {
  children: PropTypes.node.isRequired,
  delay: PropTypes.number,
};

const Home = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const handleGetStarted = () => {
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      navigate("/register");
    }
  };

  const heroVariants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.8,
        when: "beforeChildren",
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <Box sx={{ overflow: "hidden" }}>
      {/* Hero Section */}
      <Box
        sx={{
          minHeight: "100vh",
          background: `linear-gradient(135deg, 
            ${theme.palette.primary.main}15 0%, 
            ${theme.palette.secondary.main}15 100%)`,
          display: "flex",
          alignItems: "center",
          position: "relative",
          "&::before": {
            content: '""',
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'url("/patterns/hero-pattern.svg")',
            opacity: 0.1,
            zIndex: -1,
          },
        }}
      >
        <Container maxWidth="xl" sx={{ px: { xs: 2, sm: 3 } }}>
          <motion.div
            variants={heroVariants}
            initial="hidden"
            animate="visible"
          >
            <Grid container spacing={{ xs: 3, md: 4 }} alignItems="center">
              <Grid item xs={12} md={6}>
                <Box sx={{ textAlign: { xs: "center", md: "left" } }}>
                  <motion.div variants={itemVariants}>
                    <Typography
                      variant="h1"
                      sx={{
                        fontSize: {
                          xs: "2rem",
                          sm: "2.5rem",
                          md: "3.5rem",
                          lg: "4rem",
                        },
                        fontWeight: "bold",
                        background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                        backgroundClip: "text",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                        mb: { xs: 1.5, md: 2 },
                        lineHeight: { xs: 1.3, md: 1.2 },
                      }}
                    >
                      Master Telugu & English
                    </Typography>
                  </motion.div>

                  <motion.div variants={itemVariants}>
                    <Typography
                      variant="h2"
                      sx={{
                        fontSize: { xs: "1.25rem", sm: "1.5rem", md: "2rem" },
                        fontWeight: 600,
                        color: theme.palette.text.primary,
                        mb: { xs: 2, md: 3 },
                        opacity: 0.9,
                      }}
                    >
                      with AI-Powered Learning
                    </Typography>
                  </motion.div>

                  <motion.div variants={itemVariants}>
                    <Typography
                      variant="h6"
                      sx={{
                        fontSize: { xs: "0.9rem", sm: "1rem", md: "1.25rem" },
                        color: theme.palette.text.secondary,
                        mb: { xs: 3, md: 4 },
                        lineHeight: 1.6,
                        maxWidth: { xs: "100%", md: "600px" },
                        mx: { xs: "auto", md: 0 },
                      }}
                    >
                      Experience personalized language learning with our
                      intelligent AI tutor. Interactive lessons, real-time
                      feedback, and gamified progress tracking make learning
                      Telugu and English engaging and effective.
                    </Typography>
                  </motion.div>

                  <motion.div variants={itemVariants}>
                    <Box
                      sx={{
                        display: "flex",
                        gap: { xs: 1.5, sm: 2 },
                        flexWrap: "wrap",
                        justifyContent: { xs: "center", md: "flex-start" },
                        flexDirection: { xs: "column", sm: "row" },
                      }}
                    >
                      <Button
                        variant="contained"
                        size={isMobile ? "medium" : "large"}
                        onClick={handleGetStarted}
                        endIcon={<ArrowForward />}
                        component={motion.button}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        sx={{
                          px: { xs: 3, sm: 4 },
                          py: { xs: 1.25, sm: 1.5 },
                          fontSize: { xs: "1rem", sm: "1.1rem" },
                          borderRadius: 3,
                          background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                          boxShadow: `0 8px 25px ${theme.palette.primary.main}40`,
                          "&:hover": {
                            boxShadow: `0 12px 35px ${theme.palette.primary.main}60`,
                          },
                          width: { xs: "100%", sm: "auto" },
                        }}
                      >
                        {isAuthenticated
                          ? "Go to Dashboard"
                          : "Start Learning Free"}
                      </Button>

                      <Button
                        variant="outlined"
                        size={isMobile ? "medium" : "large"}
                        startIcon={<PlayArrow />}
                        component={motion.button}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        sx={{
                          px: { xs: 3, sm: 4 },
                          py: { xs: 1.25, sm: 1.5 },
                          fontSize: { xs: "1rem", sm: "1.1rem" },
                          borderRadius: 3,
                          borderWidth: 2,
                          "&:hover": {
                            borderWidth: 2,
                            background: `${theme.palette.primary.main}10`,
                          },
                          width: { xs: "100%", sm: "auto" },
                        }}
                      >
                        Watch Demo
                      </Button>
                    </Box>
                  </motion.div>
                </Box>
              </Grid>

              <Grid item xs={12} md={6}>
                <motion.div
                  variants={itemVariants}
                  whileHover={{ scale: 1.02 }}
                  transition={{ duration: 0.3 }}
                >
                  <Box
                    sx={{
                      position: "relative",
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <Paper
                      elevation={20}
                      sx={{
                        p: 4,
                        borderRadius: 4,
                        background: `linear-gradient(135deg, 
                          ${theme.palette.background.paper}95, 
                          ${theme.palette.primary.main}10)`,
                        backdropFilter: "blur(20px)",
                        border: `1px solid ${theme.palette.primary.main}30`,
                        maxWidth: 400,
                      }}
                    >
                      <Box sx={{ textAlign: "center" }}>
                        <Typography variant="h5" gutterBottom color="primary">
                          🎯 Your Learning Journey
                        </Typography>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-around",
                            my: 3,
                          }}
                        >
                          <Box sx={{ textAlign: "center" }}>
                            <Language
                              sx={{
                                fontSize: 40,
                                color: theme.palette.primary.main,
                                mb: 1,
                              }}
                            />
                            <Typography variant="caption">
                              Interactive
                            </Typography>
                          </Box>
                          <Box sx={{ textAlign: "center" }}>
                            <Psychology
                              sx={{
                                fontSize: 40,
                                color: theme.palette.secondary.main,
                                mb: 1,
                              }}
                            />
                            <Typography variant="caption">
                              AI-Powered
                            </Typography>
                          </Box>
                          <Box sx={{ textAlign: "center" }}>
                            <Groups
                              sx={{
                                fontSize: 40,
                                color: theme.palette.success.main,
                                mb: 1,
                              }}
                            />
                            <Typography variant="caption">Community</Typography>
                          </Box>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          Join thousands of learners mastering languages with
                          our proven methodology
                        </Typography>
                      </Box>
                    </Paper>
                  </Box>
                </motion.div>
              </Grid>
            </Grid>
          </motion.div>
        </Container>

        {/* Floating Elements */}
        {!isMobile && (
          <>
            <motion.div
              animate={{
                y: [-20, 20, -20],
                rotate: [0, 180, 360],
              }}
              transition={{
                duration: 6,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              style={{
                position: "absolute",
                top: "20%",
                right: "10%",
                opacity: 0.3,
              }}
            >
              <School
                sx={{ fontSize: 60, color: theme.palette.primary.main }}
              />
            </motion.div>

            <motion.div
              animate={{
                y: [20, -20, 20],
                rotate: [0, -180, -360],
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: "easeInOut",
                delay: 1,
              }}
              style={{
                position: "absolute",
                bottom: "20%",
                left: "5%",
                opacity: 0.3,
              }}
            >
              <Chat
                sx={{ fontSize: 50, color: theme.palette.secondary.main }}
              />
            </motion.div>
          </>
        )}
      </Box>

      {/* Stats Section */}
      <AnimatedSection>
        <Box sx={{ py: 8, background: theme.palette.background.default }}>
          <Container maxWidth="lg">
            <Grid container spacing={4}>
              {stats.map((stat, index) => (
                <Grid item xs={6} md={3} key={index}>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Box sx={{ textAlign: "center" }}>
                      <Typography
                        variant="h3"
                        sx={{
                          fontWeight: "bold",
                          background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                          backgroundClip: "text",
                          WebkitBackgroundClip: "text",
                          WebkitTextFillColor: "transparent",
                          mb: 1,
                        }}
                      >
                        {stat.number}
                      </Typography>
                      <Typography variant="h6" color="text.secondary">
                        {stat.label}
                      </Typography>
                    </Box>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Container>
        </Box>
      </AnimatedSection>

      {/* Features Section */}
      <AnimatedSection delay={0.2}>
        <Box sx={{ py: 10 }}>
          <Container maxWidth="lg">
            <Box sx={{ textAlign: "center", mb: 8 }}>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: "bold",
                  mb: 2,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                Why Choose Our Platform?
              </Typography>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{ maxWidth: 600, mx: "auto" }}
              >
                Discover the features that make language learning engaging,
                effective, and enjoyable
              </Typography>
            </Box>

            <Grid container spacing={4}>
              {features.map((feature, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                  <motion.div
                    whileHover={{ scale: 1.05, y: -10 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Card
                      sx={{
                        height: "100%",
                        background: `linear-gradient(135deg, ${feature.color}10, ${feature.color}05)`,
                        border: `1px solid ${feature.color}30`,
                        borderRadius: 3,
                        overflow: "hidden",
                        position: "relative",
                        "&::before": {
                          content: '""',
                          position: "absolute",
                          top: 0,
                          left: 0,
                          right: 0,
                          height: "4px",
                          background: `linear-gradient(90deg, ${feature.color}, ${feature.color}80)`,
                        },
                      }}
                    >
                      <CardContent sx={{ p: 3, textAlign: "center" }}>
                        <Box
                          sx={{
                            mb: 2,
                            color: feature.color,
                            display: "flex",
                            justifyContent: "center",
                          }}
                        >
                          {feature.icon}
                        </Box>
                        <Typography
                          variant="h6"
                          sx={{ fontWeight: "bold", mb: 2 }}
                        >
                          {feature.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {feature.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Container>
        </Box>
      </AnimatedSection>

      {/* Testimonials Section */}
      <AnimatedSection delay={0.4}>
        <Box
          sx={{
            py: 10,
            background: `linear-gradient(135deg, ${theme.palette.primary.main}05, ${theme.palette.secondary.main}05)`,
          }}
        >
          <Container maxWidth="lg">
            <Box sx={{ textAlign: "center", mb: 8 }}>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: "bold",
                  mb: 2,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                  backgroundClip: "text",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                What Our Learners Say
              </Typography>
              <Typography variant="h6" color="text.secondary">
                Join thousands of satisfied learners worldwide
              </Typography>
            </Box>

            <Grid container spacing={4}>
              {testimonials.map((testimonial, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <motion.div
                    whileHover={{ scale: 1.02 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Card
                      sx={{
                        height: "100%",
                        borderRadius: 3,
                        background: theme.palette.background.paper,
                        boxShadow: `0 8px 25px ${theme.palette.primary.main}15`,
                      }}
                    >
                      <CardContent sx={{ p: 3 }}>
                        <Box
                          sx={{ display: "flex", alignItems: "center", mb: 3 }}
                        >
                          <Avatar
                            src={testimonial.avatar}
                            sx={{
                              width: 60,
                              height: 60,
                              mr: 2,
                              background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                            }}
                          >
                            {testimonial.name.charAt(0)}
                          </Avatar>
                          <Box>
                            <Typography
                              variant="h6"
                              sx={{ fontWeight: "bold" }}
                            >
                              {testimonial.name}
                            </Typography>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              {testimonial.location}
                            </Typography>
                            <Box sx={{ mt: 0.5 }}>
                              <Rating
                                value={testimonial.rating}
                                readOnly
                                size="small"
                              />
                            </Box>
                          </Box>
                        </Box>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ fontStyle: "italic" }}
                        >
                          &ldquo;{testimonial.comment}&rdquo;
                        </Typography>
                      </CardContent>
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </Container>
        </Box>
      </AnimatedSection>

      {/* CTA Section */}
      <AnimatedSection delay={0.6}>
        <Box
          sx={{
            py: 10,
            background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
            color: "white",
            textAlign: "center",
          }}
        >
          <Container maxWidth="md">
            <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
              Ready to Start Your Journey?
            </Typography>
            <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
              Join thousands of learners and start mastering Telugu and English
              today!
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={handleGetStarted}
              endIcon={<ArrowForward />}
              component={motion.button}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              sx={{
                px: 6,
                py: 2,
                fontSize: "1.2rem",
                borderRadius: 3,
                background: "rgba(255, 255, 255, 0.2)",
                backdropFilter: "blur(10px)",
                border: "1px solid rgba(255, 255, 255, 0.3)",
                color: "white",
                "&:hover": {
                  background: "rgba(255, 255, 255, 0.3)",
                  boxShadow: "0 12px 35px rgba(255, 255, 255, 0.3)",
                },
              }}
            >
              {isAuthenticated ? "Continue Learning" : "Get Started Now"}
            </Button>
          </Container>
        </Box>
      </AnimatedSection>
    </Box>
  );
};

export default Home;
