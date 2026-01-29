import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  Button,
} from "@mui/material";
import {
  School,
  Chat,
  TrendingUp,
  EmojiEvents,
  ArrowForward,
  AutoStories,
  Psychology,
  Translate,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import GradientText from "../components/common/GradientText";
import AnimatedButton from "../components/common/AnimatedButton";
import LanguageSwitcher from "../components/common/LanguageSwitcher";

// Features will be translated using t() function
const getFeatures = (t) => [
  {
    icon: <School sx={{ fontSize: 48 }} />,
    title: t('landing.features.structuredLearning'),
    description: t('landing.features.structuredLearningDesc'),
  },
  {
    icon: <Chat sx={{ fontSize: 48 }} />,
    title: t('landing.features.aiConversations'),
    description: t('landing.features.aiConversationsDesc'),
  },
  {
    icon: <TrendingUp sx={{ fontSize: 48 }} />,
    title: t('landing.features.adaptiveLearning'),
    description: t('landing.features.adaptiveLearningDesc'),
  },
  {
    icon: <EmojiEvents sx={{ fontSize: 48 }} />,
    title: t('landing.features.gamification'),
    description: t('landing.features.gamificationDesc'),
  },
  {
    icon: <AutoStories sx={{ fontSize: 48 }} />,
    title: t('landing.features.richVocabulary'),
    description: t('landing.features.richVocabularyDesc'),
  },
  {
    icon: <Psychology sx={{ fontSize: 48 }} />,
    title: t('landing.features.smartAnalytics'),
    description: t('landing.features.smartAnalyticsDesc'),
  },
];

const LandingPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { t } = useTranslation();
  
  // Get translated features
  const features = getFeatures(t);

  return (
    <Box sx={{ minHeight: "100vh" }}>
      {/* Navigation */}
      <AppBar
        position="fixed"
        sx={{
          bgcolor: "rgba(255, 255, 255, 0.95)",
          backdropFilter: "blur(10px)",
          color: "text.primary",
          boxShadow: 1,
        }}
      >
        <Toolbar>
          <Box
            sx={{ display: "flex", alignItems: "center", gap: 1, flexGrow: 1 }}
          >
            <Translate color="primary" />
            <Typography
              variant="h6"
              sx={{
                fontWeight: 800,
                background: "linear-gradient(90deg, #0ea5e9 0%, #d946ef 100%)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              ConvAI Learn
            </Typography>
          </Box>
          
          {/* Language Switcher - Always visible for navigation */}
          <LanguageSwitcher />
          
          {isAuthenticated ? (
            <Button variant="contained" onClick={() => navigate("/dashboard")} sx={{ ml: 1 }}>
              {t('common.goToDashboard')}
            </Button>
          ) : (
            <>
              <Button onClick={() => navigate("/login")} sx={{ mr: 1 }}>
                {t('common.signIn')}
              </Button>
              <Button variant="contained" onClick={() => navigate("/register")}>
                {t('common.getStarted')}
              </Button>
            </>
          )}
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          pt: { xs: 15, md: 20 },
          pb: { xs: 10, md: 15 },
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Animated Background */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear",
          }}
          style={{
            position: "absolute",
            top: "-20%",
            right: "-10%",
            width: "60%",
            height: "120%",
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%)",
            filter: "blur(60px)",
          }}
        />

        <Container maxWidth="lg" sx={{ position: "relative", zIndex: 1 }}>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Typography
                  variant="h2"
                  sx={{
                    color: "white",
                    fontWeight: 900,
                    mb: 2,
                    fontSize: { xs: "2.5rem", md: "3.5rem" },
                  }}
                >
                  {t('landing.heroTitle')}
                </Typography>
                <Typography
                  variant="h6"
                  sx={{
                    color: "rgba(255, 255, 255, 0.9)",
                    mb: 4,
                    lineHeight: 1.6,
                  }}
                >
                  {t('landing.heroSubtitle')}
                </Typography>
                <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
                  <AnimatedButton
                    size="large"
                    variant="contained"
                    onClick={() => navigate("/register")}
                    sx={{
                      bgcolor: "white",
                      color: "primary.main",
                      "&:hover": { bgcolor: "rgba(255, 255, 255, 0.9)" },
                    }}
                    endIcon={<ArrowForward />}
                  >
                    {t('common.startLearningFree')}
                  </AnimatedButton>
                  <AnimatedButton
                    size="large"
                    variant="outlined"
                    onClick={() => navigate("/login")}
                    sx={{
                      borderColor: "white",
                      color: "white",
                      "&:hover": {
                        borderColor: "white",
                        bgcolor: "rgba(255, 255, 255, 0.1)",
                      },
                    }}
                  >
                    {t('common.signIn')}
                  </AnimatedButton>
                </Box>
              </motion.div>
            </Grid>
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, delay: 0.2 }}
              >
                <Box
                  sx={{
                    width: "100%",
                    height: { xs: 300, md: 400 },
                    background: "rgba(255, 255, 255, 0.1)",
                    backdropFilter: "blur(10px)",
                    borderRadius: 4,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    border: "2px solid rgba(255, 255, 255, 0.2)",
                  }}
                >
                  <Translate
                    sx={{ fontSize: 120, color: "rgba(255, 255, 255, 0.3)" }}
                  />
                </Box>
              </motion.div>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 8, md: 12 } }}>
        <Box sx={{ textAlign: "center", mb: 8 }}>
          <GradientText variant="h3" sx={{ mb: 2, fontWeight: 800 }}>
            {t('landing.whyChoose')}
          </GradientText>
          <Typography variant="h6" color="text.secondary">
            {t('landing.heroSubtitle')}
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card
                  sx={{
                    height: "100%",
                    transition: "all 0.3s ease",
                    "&:hover": {
                      transform: "translateY(-8px)",
                      boxShadow: 6,
                    },
                  }}
                >
                  <CardContent sx={{ p: 4, textAlign: "center" }}>
                    <Box
                      sx={{
                        color: "primary.main",
                        mb: 2,
                        display: "flex",
                        justifyContent: "center",
                      }}
                    >
                      {feature.icon}
                    </Box>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
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

      {/* CTA Section */}
      <Box
        sx={{
          background: "linear-gradient(135deg, #0ea5e9 0%, #d946ef 100%)",
          py: { xs: 8, md: 12 },
        }}
      >
        <Container maxWidth="md">
          <Box sx={{ textAlign: "center", color: "white" }}>
            <Typography variant="h3" fontWeight={800} gutterBottom>
              {t('landing.readyToStart')}
            </Typography>
            <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
              {t('landing.readyToStartDesc')}
            </Typography>
            <AnimatedButton
              size="large"
              variant="contained"
              onClick={() => navigate("/register")}
              sx={{
                bgcolor: "white",
                color: "primary.main",
                px: 4,
                py: 1.5,
                fontSize: "1.1rem",
                "&:hover": { bgcolor: "rgba(255, 255, 255, 0.9)" },
              }}
              endIcon={<ArrowForward />}
            >
              {t('landing.createFreeAccount')}
            </AnimatedButton>
          </Box>
        </Container>
      </Box>

      {/* Footer */}
      <Box
        sx={{
          bgcolor: "background.paper",
          py: 4,
          borderTop: 1,
          borderColor: "divider",
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary" textAlign="center">
            {t('landing.footer.copyright')}
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;
