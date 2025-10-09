import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Box,
  Container,
  Stepper,
  Step,
  StepLabel,
  Typography,
  Card,
  CardContent,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";
import axiosInstance, { API_ENDPOINTS } from "../config/api";
import LearningPathSelector from "../components/LearningPathSelector";
import GradientText from "../components/common/GradientText";
import AnimatedButton from "../components/common/AnimatedButton";

const steps = [
  { label: "Welcome", teluguLabel: "స్వాగతం" },
  { label: "Assessment Info", teluguLabel: "మూల్యాంకన సమాచారం" },
  { label: "Take Assessment", teluguLabel: "మూల్యాంకనం తీసుకోండి" },
  { label: "View Results", teluguLabel: "ఫలితాలు చూడండి" },
  { label: "Choose Path", teluguLabel: "మార్గాన్ని ఎంచుకోండి" },
  { label: "Get Started", teluguLabel: "ప్రారంభించండి" },
];

const Onboarding = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [onboardingStatus, setOnboardingStatus] = useState(null);
  const [assessmentResults, setAssessmentResults] = useState(null);
  const [selectedPath, setSelectedPath] = useState(null);

  useEffect(() => {
    fetchOnboardingStatus();
    // Check for assessment results in navigation state
    const navState = window.history.state?.usr;
    if (navState?.assessmentResults) {
      setAssessmentResults(navState.assessmentResults);
      setActiveStep(3); // Go to results step
    }
  }, []);

  const fetchOnboardingStatus = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(API_ENDPOINTS.ONBOARDING.STATUS);
      const status = response.data.onboarding_status;
      setOnboardingStatus(status);

      // Determine which step to show based on status
      if (status.onboarding_completed) {
        navigate("/dashboard");
        return;
      }

      switch (status.current_step) {
        case "welcome":
          setActiveStep(0);
          break;
        case "assessment_needed":
          setActiveStep(1);
          break;
        case "assessment_in_progress":
          setActiveStep(2);
          break;
        case "choose_learning_path":
          setActiveStep(4);
          break;
        case "ready_to_start":
          setActiveStep(5);
          break;
        default:
          setActiveStep(0);
      }
    } catch (err) {
      console.error("Error fetching onboarding status:", err);
      setError("Failed to load onboarding status");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    setActiveStep((prev) => Math.min(prev + 1, steps.length - 1));
  };

  const handleBack = () => {
    setActiveStep((prev) => Math.max(prev - 1, 0));
  };

  const handleStartAssessment = () => {
    navigate("/assessment", {
      state: {
        fromOnboarding: true,
      },
    });
  };

  const handleCompleteOnboarding = async () => {
    try {
      setLoading(true);
      await axiosInstance.post(API_ENDPOINTS.ONBOARDING.COMPLETE);
      navigate("/dashboard");
    } catch (err) {
      console.error("Error completing onboarding:", err);
      setError("Failed to complete onboarding");
    } finally {
      setLoading(false);
    }
  };

  if (loading && !onboardingStatus) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        py: 4,
      }}
    >
      <Container maxWidth="lg">
        {/* Header */}
        <Box textAlign="center" mb={4}>
          <GradientText variant="h3" sx={{ mb: 2, fontWeight: 700 }}>
            Welcome to Your English Learning Journey
          </GradientText>
          <Typography variant="h5" color="white" sx={{ opacity: 0.9 }}>
            మీ ఇంగ్లీష్ నేర్చుకునే ప్రయాణానికి స్వాగతం
          </Typography>
        </Box>

        {/* Stepper */}
        <Card sx={{ mb: 4, borderRadius: 3 }}>
          <CardContent sx={{ py: 4 }}>
            <Stepper activeStep={activeStep} alternativeLabel>
              {steps.map((step, index) => (
                <Step key={index}>
                  <StepLabel>
                    <Typography variant="body2" fontWeight={600}>
                      {step.label}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {step.teluguLabel}
                    </Typography>
                  </StepLabel>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
            {error}
          </Alert>
        )}

        {/* Step Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeStep}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <Card
              sx={{
                borderRadius: 3,
                minHeight: 400,
                display: "flex",
                flexDirection: "column",
              }}
            >
              <CardContent sx={{ flex: 1, p: 4 }}>
                {activeStep === 0 && <WelcomeStep user={user} />}
                {activeStep === 1 && <AssessmentInfoStep />}
                {activeStep === 2 && (
                  <AssessmentStep onComplete={() => setActiveStep(3)} />
                )}
                {activeStep === 3 && (
                  <ResultsStep
                    assessmentResults={assessmentResults}
                    onContinue={() => setActiveStep(4)}
                  />
                )}
                {activeStep === 4 && (
                  <ChoosePathStep
                    assessmentResults={assessmentResults}
                    onPathSelected={(path) => {
                      setSelectedPath(path);
                      setActiveStep(5);
                    }}
                  />
                )}
                {activeStep === 5 && <GetStartedStep />}
              </CardContent>

              {/* Navigation Buttons */}
              <Box
                sx={{
                  p: 3,
                  borderTop: 1,
                  borderColor: "divider",
                  display: "flex",
                  justifyContent: "space-between",
                }}
              >
                <Button
                  onClick={handleBack}
                  disabled={activeStep === 0 || activeStep === 2}
                  variant="outlined"
                >
                  Back
                </Button>

                <Box>
                  {activeStep < 2 && (
                    <AnimatedButton
                      variant="contained"
                      onClick={
                        activeStep === 1 ? handleStartAssessment : handleNext
                      }
                    >
                      {activeStep === 1 ? "Start Assessment" : "Continue"}
                    </AnimatedButton>
                  )}
                  {activeStep === 5 && (
                    <AnimatedButton
                      variant="contained"
                      onClick={handleCompleteOnboarding}
                      disabled={loading}
                    >
                      {loading ? (
                        <CircularProgress size={24} color="inherit" />
                      ) : (
                        "Complete & Start Learning"
                      )}
                    </AnimatedButton>
                  )}
                </Box>
              </Box>
            </Card>
          </motion.div>
        </AnimatePresence>
      </Container>
    </Box>
  );
};

// Step Components
const WelcomeStep = ({ user }) => (
  <Box textAlign="center" py={4}>
    <Typography variant="h4" gutterBottom fontWeight={700}>
      Welcome, {user?.username}! 🎉
    </Typography>
    <Typography variant="h5" color="text.secondary" gutterBottom>
      స్వాగతం, {user?.username}!
    </Typography>

    <Box mt={4}>
      <Typography variant="body1" paragraph sx={{ fontSize: "1.1rem" }}>
        We're excited to help you master the English language! This platform
        uses AI-powered learning to create a personalized journey just for you.
      </Typography>
      <Typography
        variant="body1"
        paragraph
        color="text.secondary"
        sx={{ fontSize: "1.1rem" }}
      >
        ఇంగ్లీష్ భాషను నేర్చుకోవడంలో మీకు సహాయం చేయడానికి మేము ఉత్సాహంగా
        ఉన్నాము! ఈ ప్లాట్‌ఫారమ్ మీ కోసం వ్యక్తిగతీకరించిన ప్రయాణాన్ని
        సృష్టించడానికి AI-ఆధారిత అభ్యాసాన్ని ఉపయోగిస్తుంది.
      </Typography>
    </Box>

    <Box mt={4}>
      <Typography variant="h6" gutterBottom>
        What to Expect:
      </Typography>
      <Box textAlign="left" maxWidth={600} mx="auto" mt={2}>
        <Typography variant="body1" paragraph>
          ✅ Comprehensive assessment to understand your level
        </Typography>
        <Typography variant="body1" paragraph>
          ✅ Personalized learning paths based on your goals
        </Typography>
        <Typography variant="body1" paragraph>
          ✅ AI-powered feedback after every lesson
        </Typography>
        <Typography variant="body1" paragraph>
          ✅ Track your progress to English mastery
        </Typography>
      </Box>
    </Box>
  </Box>
);

const AssessmentInfoStep = () => (
  <Box py={4}>
    <Typography variant="h4" gutterBottom fontWeight={700} textAlign="center">
      About the Assessment 📝
    </Typography>
    <Typography
      variant="h5"
      color="text.secondary"
      gutterBottom
      textAlign="center"
    >
      మూల్యాంకన గురించి
    </Typography>

    <Box mt={4} maxWidth={800} mx="auto">
      <Typography variant="body1" paragraph sx={{ fontSize: "1.1rem" }}>
        Before we create your personalized learning path, we need to understand
        your current English proficiency level.
      </Typography>

      <Box mt={3}>
        <Typography variant="h6" gutterBottom>
          The assessment includes:
        </Typography>
        <Box ml={2}>
          <Typography variant="body1" paragraph>
            📚 <strong>Vocabulary:</strong> Test your word knowledge
          </Typography>
          <Typography variant="body1" paragraph>
            ✏️ <strong>Grammar:</strong> Sentence structure and rules
          </Typography>
          <Typography variant="body1" paragraph>
            📖 <strong>Reading:</strong> Comprehension skills
          </Typography>
          <Typography variant="body1" paragraph>
            ✍️ <strong>Writing:</strong> Expression abilities
          </Typography>
          <Typography variant="body1" paragraph>
            👂 <strong>Listening:</strong> Understanding spoken English
          </Typography>
          <Typography variant="body1" paragraph>
            🗣️ <strong>Speaking:</strong> Pronunciation basics
          </Typography>
        </Box>
      </Box>

      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Estimated Time:</strong> 15-20 minutes
          <br />
          <strong>Questions:</strong> ~20-30 adaptive questions
          <br />
          <strong>Note:</strong> Don't worry about getting everything right!
          This helps us create the perfect learning plan for you.
        </Typography>
      </Alert>
    </Box>
  </Box>
);

const AssessmentStep = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Navigate to assessment page
    navigate("/assessment");
  }, [navigate]);

  return (
    <Box textAlign="center" py={8}>
      <CircularProgress size={80} />
      <Typography variant="h5" mt={3}>
        Redirecting to Assessment...
      </Typography>
    </Box>
  );
};

const ResultsStep = ({ assessmentResults, onContinue }) => {
  if (!assessmentResults) {
    return (
      <Box textAlign="center" py={4}>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Assessment Not Completed Yet
          </Typography>
          <Typography variant="body2">
            Please complete your initial assessment to see your results and get
            personalized learning paths.
          </Typography>
        </Alert>
        <Button
          variant="contained"
          onClick={() => (window.location.href = "/assessment")}
          sx={{ mt: 2 }}
        >
          Take Assessment Now
        </Button>
      </Box>
    );
  }

  return (
    <Box py={4}>
      <Typography variant="h4" gutterBottom textAlign="center">
        🎉 Assessment Complete!
      </Typography>
      <Alert severity="success" sx={{ mb: 3 }}>
        <Typography variant="h6">
          Overall Score: {assessmentResults.overall_score}%
        </Typography>
        <Typography variant="body2">
          Proficiency Level: {assessmentResults.overall_proficiency_level}
        </Typography>
      </Alert>
      <Button
        variant="contained"
        onClick={onContinue}
        sx={{ mt: 3 }}
        fullWidth
        size="large"
      >
        View Your Personalized Learning Paths
      </Button>
    </Box>
  );
};

const ChoosePathStep = ({ assessmentResults, onPathSelected }) => {
  if (!assessmentResults) {
    return (
      <Box textAlign="center" py={4}>
        <Alert severity="warning">
          Please complete the assessment first to see personalized learning
          paths.
        </Alert>
      </Box>
    );
  }

  return (
    <Box py={4}>
      <LearningPathSelector
        assessmentResults={assessmentResults}
        onPathSelected={onPathSelected}
      />
    </Box>
  );
};

const GetStartedStep = () => (
  <Box textAlign="center" py={4}>
    <Typography variant="h3" gutterBottom fontWeight={700}>
      You're All Set! 🎊
    </Typography>
    <Typography variant="h5" color="text.secondary" gutterBottom>
      మీరు సిద్ధంగా ఉన్నారు!
    </Typography>

    <Box mt={4}>
      <Typography variant="body1" paragraph sx={{ fontSize: "1.1rem" }}>
        Your personalized learning journey is ready. Let's start building your
        English mastery!
      </Typography>
      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ fontSize: "1.1rem" }}
      >
        మీ వ్యక్తిగతీకరించిన అభ్యాస ప్రయాణం సిద్ధంగా ఉంది. మీ ఇంగ్లీష్
        ప్రావీణ్యాన్ని నిర్మించడం ప్రారంభిద్దాం!
      </Typography>
    </Box>

    <Box mt={4}>
      <Alert severity="success">
        <Typography variant="body2">
          🎁 You've earned 50 points for completing onboarding!
        </Typography>
      </Alert>
    </Box>
  </Box>
);

export default Onboarding;
