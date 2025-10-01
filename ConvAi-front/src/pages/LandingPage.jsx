import {
  Box,
  Typography,
  Container,
  Button,
  Grid,
  Avatar,
  Chip,
  Paper,
  useTheme,
  alpha,
} from "@mui/material";
import { motion, useScroll, useTransform } from "framer-motion";
import {
  PlayArrow,
  AutoAwesome,
  Psychology,
  Chat,
  TrendingUp,
  EmojiEvents,
  School,
  Language,
  Star,
  CheckCircle,
  RocketLaunch,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import {
  GlassCard,
  GradientText,
  FloatingElement,
  NeuralBackground,
  AnimatedCounter,
} from "../components/ui/AIComponents";

const LandingPage = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);

  const features = [
    {
      icon: <Psychology sx={{ fontSize: 40 }} />,
      title: "AI-Powered Learning",
      description:
        "Personalized learning paths adapted to your pace and style with advanced AI technology",
      color: theme.palette.primary.main,
      gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    },
    {
      icon: <Chat sx={{ fontSize: 40 }} />,
      title: "Interactive Conversations",
      description:
        "Practice real-world conversations with our intelligent AI tutor in both Telugu and English",
      color: theme.palette.secondary.main,
      gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40 }} />,
      title: "Progress Tracking",
      description:
        "Monitor your learning journey with detailed analytics and personalized insights",
      color: theme.palette.success.main,
      gradient: "linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%)",
    },
    {
      icon: <EmojiEvents sx={{ fontSize: 40 }} />,
      title: "Gamified Experience",
      description:
        "Earn badges, compete with friends, and stay motivated with our engaging reward system",
      color: theme.palette.warning.main,
      gradient: "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)",
    },
  ];

  const stats = [
    { number: 10000, label: "Active Learners", suffix: "+" },
    { number: 95, label: "Success Rate", suffix: "%" },
    { number: 50, label: "Languages Supported", suffix: "+" },
    { number: 4.9, label: "User Rating", suffix: "/5" },
  ];

  const testimonials = [
    {
      name: "Priya Sharma",
      role: "Software Engineer",
      avatar: "PS",
      rating: 5,
      text: "This platform transformed my English communication skills! The AI tutor understands Telugu context perfectly.",
      gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    },
    {
      name: "Ravi Kumar",
      role: "Student",
      avatar: "RK",
      rating: 5,
      text: "Interactive lessons and personalized feedback helped me gain confidence in speaking English fluently.",
      gradient: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    },
    {
      name: "Lakshmi Reddy",
      role: "Business Owner",
      avatar: "LR",
      rating: 5,
      text: "Perfect blend of technology and traditional learning. Highly recommend for Telugu speakers learning English!",
      gradient: "linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%)",
    },
  ];

  return (
    <Box sx={{ position: "relative", overflow: "hidden" }}>
      <NeuralBackground opacity={0.03} />

      {/* Hero Section */}
      <Box
        sx={{
          minHeight: "100vh",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          position: "relative",
          display: "flex",
          alignItems: "center",
        }}
      >
        <FloatingElement
          delay={0}
          sx={{
            position: "absolute",
            top: "10%",
            left: "5%",
            fontSize: "3rem",
            color: "rgba(255,255,255,0.1)",
          }}
        >
          <Language />
        </FloatingElement>
        <FloatingElement
          delay={1}
          sx={{
            position: "absolute",
            top: "20%",
            right: "10%",
            fontSize: "2.5rem",
            color: "rgba(255,255,255,0.1)",
          }}
        >
          <AutoAwesome />
        </FloatingElement>
        <FloatingElement
          delay={2}
          sx={{
            position: "absolute",
            bottom: "15%",
            left: "8%",
            fontSize: "2rem",
            color: "rgba(255,255,255,0.1)",
          }}
        >
          <School />
        </FloatingElement>

        <Container maxWidth="lg" sx={{ position: "relative", zIndex: 1 }}>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={7}>
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Chip
                  label="🚀 AI-Powered Language Learning"
                  sx={{
                    mb: 3,
                    background: "rgba(255,255,255,0.2)",
                    color: "white",
                    fontWeight: 600,
                  }}
                />
                <Typography
                  variant="h1"
                  component="h1"
                  sx={{
                    color: "#fff",
                    fontWeight: 800,
                    mb: 2,
                    fontSize: { xs: "2.5rem", md: "3.5rem", lg: "4rem" },
                    lineHeight: 1.1,
                    textShadow: "0 2px 4px rgba(0,0,0,0.3)",
                  }}
                >
                  Master English with{" "}
                  <Box
                    component="span"
                    sx={{
                      background: "linear-gradient(45deg, #FFD700, #FFA500)",
                      backgroundClip: "text",
                      WebkitBackgroundClip: "text",
                      WebkitTextFillColor: "transparent",
                    }}
                  >
                    AI-Powered
                  </Box>{" "}
                  Telugu Support
                </Typography>
                <Typography
                  variant="h5"
                  sx={{
                    color: "rgba(255,255,255,0.9)",
                    mb: 4,
                    fontWeight: 400,
                    lineHeight: 1.4,
                  }}
                >
                  Transform your English communication skills with personalized
                  AI tutoring, interactive conversations, and gamified learning
                  experiences tailored for Telugu speakers.
                </Typography>
                <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<RocketLaunch />}
                    onClick={() => navigate("/auth/signup")}
                    sx={{
                      background:
                        "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)",
                      color: "#000",
                      fontWeight: 700,
                      py: 1.5,
                      px: 4,
                      fontSize: "1.1rem",
                      borderRadius: 3,
                      boxShadow: "0 4px 20px rgba(255,215,0,0.4)",
                      "&:hover": {
                        background:
                          "linear-gradient(135deg, #FFA500 0%, #FF8C00 100%)",
                        transform: "translateY(-2px)",
                        boxShadow: "0 6px 25px rgba(255,215,0,0.6)",
                      },
                    }}
                  >
                    Start Learning Free
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<PlayArrow />}
                    sx={{
                      borderColor: "rgba(255,255,255,0.5)",
                      color: "white",
                      fontWeight: 600,
                      py: 1.5,
                      px: 4,
                      fontSize: "1.1rem",
                      borderRadius: 3,
                      "&:hover": {
                        borderColor: "white",
                        background: "rgba(255,255,255,0.1)",
                        transform: "translateY(-2px)",
                      },
                    }}
                  >
                    Watch Demo
                  </Button>
                </Box>
              </motion.div>
            </Grid>
            <Grid item xs={12} md={5}>
              <motion.div
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                style={{ y }}
              >
                <GlassCard sx={{ p: 4, textAlign: "center" }}>
                  <Avatar
                    sx={{
                      width: 100,
                      height: 100,
                      margin: "0 auto 2rem",
                      background:
                        "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)",
                      fontSize: "2.5rem",
                    }}
                  >
                    🤖
                  </Avatar>
                  <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
                    Meet Your AI Tutor
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Personalized lessons, real-time feedback, and adaptive
                    learning powered by advanced AI technology
                  </Typography>
                </GlassCard>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Stats Section */}
      <Box sx={{ py: 8, background: theme.palette.background.default }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            {stats.map((stat, index) => (
              <Grid item xs={6} md={3} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      textAlign: "center",
                      background: `linear-gradient(135deg, ${theme.palette.primary.main}10, ${theme.palette.secondary.main}05)`,
                      border: `1px solid ${theme.palette.divider}`,
                      borderRadius: 3,
                    }}
                  >
                    <Typography
                      variant="h3"
                      sx={{
                        fontWeight: 800,
                        background:
                          "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                        backgroundClip: "text",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                        mb: 1,
                      }}
                    >
                      <AnimatedCounter end={stat.number} suffix={stat.suffix} />
                    </Typography>
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ fontWeight: 600 }}
                    >
                      {stat.label}
                    </Typography>
                  </Paper>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: 10, background: alpha(theme.palette.primary.main, 0.02) }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <Box sx={{ textAlign: "center", mb: 8 }}>
              <GradientText
                variant="h2"
                gradient="primary"
                sx={{ mb: 2, fontWeight: 800 }}
              >
                Why Choose Our Platform?
              </GradientText>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{ maxWidth: 600, mx: "auto" }}
              >
                Experience the future of language learning with cutting-edge AI
                technology and personalized Telugu-English education
              </Typography>
            </Box>
          </motion.div>

          <Grid container spacing={4}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={6} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -5 }}
                >
                  <GlassCard
                    sx={{
                      p: 4,
                      height: "100%",
                      background: `${feature.gradient}08`,
                      border: `1px solid ${feature.color}20`,
                      "&:hover": {
                        borderColor: `${feature.color}40`,
                        boxShadow: `0 10px 40px ${feature.color}20`,
                      },
                    }}
                  >
                    <Avatar
                      sx={{
                        background: feature.gradient,
                        color: "white",
                        width: 70,
                        height: 70,
                        mb: 3,
                      }}
                    >
                      {feature.icon}
                    </Avatar>
                    <Typography variant="h5" sx={{ mb: 2, fontWeight: 700 }}>
                      {feature.title}
                    </Typography>
                    <Typography
                      variant="body1"
                      color="text.secondary"
                      sx={{ lineHeight: 1.6 }}
                    >
                      {feature.description}
                    </Typography>
                  </GlassCard>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Testimonials Section */}
      <Box sx={{ py: 10, background: theme.palette.background.default }}>
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <Box sx={{ textAlign: "center", mb: 8 }}>
              <GradientText
                variant="h2"
                gradient="secondary"
                sx={{ mb: 2, fontWeight: 800 }}
              >
                What Our Learners Say
              </GradientText>
              <Typography variant="h6" color="text.secondary">
                Join thousands of successful English learners from the Telugu
                community
              </Typography>
            </Box>
          </motion.div>

          <Grid container spacing={4}>
            {testimonials.map((testimonial, index) => (
              <Grid item xs={12} md={4} key={index}>
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -5 }}
                >
                  <GlassCard sx={{ p: 4, height: "100%" }}>
                    <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
                      <Avatar
                        sx={{
                          background: testimonial.gradient,
                          color: "white",
                          mr: 2,
                          width: 50,
                          height: 50,
                          fontWeight: 700,
                        }}
                      >
                        {testimonial.avatar}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {testimonial.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {testimonial.role}
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: "flex", mb: 2 }}>
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} sx={{ color: "#FFD700", fontSize: 20 }} />
                      ))}
                    </Box>
                    <Typography
                      variant="body1"
                      sx={{ fontStyle: "italic", lineHeight: 1.6 }}
                    >
                      &ldquo;{testimonial.text}&rdquo;
                    </Typography>
                  </GlassCard>
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box
        sx={{
          py: 10,
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          position: "relative",
        }}
      >
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <Box sx={{ textAlign: "center", color: "white" }}>
              <Typography
                variant="h2"
                sx={{
                  fontWeight: 800,
                  mb: 2,
                  textShadow: "0 2px 4px rgba(0,0,0,0.3)",
                }}
              >
                Ready to Start Your Journey?
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
                Join thousands of Telugu speakers mastering English with
                AI-powered learning
              </Typography>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  gap: 2,
                  flexWrap: "wrap",
                }}
              >
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<CheckCircle />}
                  onClick={() => navigate("/auth/signup")}
                  sx={{
                    background:
                      "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)",
                    color: "#000",
                    fontWeight: 700,
                    py: 2,
                    px: 6,
                    fontSize: "1.2rem",
                    borderRadius: 3,
                    boxShadow: "0 4px 20px rgba(255,215,0,0.4)",
                    "&:hover": {
                      background:
                        "linear-gradient(135deg, #FFA500 0%, #FF8C00 100%)",
                      transform: "translateY(-2px)",
                      boxShadow: "0 6px 25px rgba(255,215,0,0.6)",
                    },
                  }}
                >
                  Get Started Free
                </Button>
              </Box>
              <Typography variant="body2" sx={{ mt: 2, opacity: 0.8 }}>
                No credit card required • 7-day free trial • Cancel anytime
              </Typography>
            </Box>
          </motion.div>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;
