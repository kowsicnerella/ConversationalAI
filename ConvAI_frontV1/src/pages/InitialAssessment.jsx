import { useState, useEffect } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Radio,
  RadioGroup,
  FormControlLabel,
  TextField,
  Alert,
  CircularProgress,
  Chip,
} from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import axiosInstance, { API_ENDPOINTS } from "../config/api";
import { ArrowForward, CheckCircle, Timer } from "@mui/icons-material";

const InitialAssessment = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [assessment, setAssessment] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeStarted, setTimeStarted] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAssessment();
  }, []);

  const fetchAssessment = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.post(
        API_ENDPOINTS.ASSESSMENT.GENERATE,
        {
          assessment_type: "comprehensive" // Can be 'quick', 'adaptive', or 'comprehensive'
        }
      );
      setAssessment(response.data.assessment);
      setTimeStarted(Date.now());
    } catch (err) {
      console.error("Error fetching assessment:", err);
      setError("Failed to load assessment. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const handleNext = async () => {
    const currentQuestion = assessment.questions[currentQuestionIndex];
    const answer = answers[currentQuestion.id];

    if (!answer || answer.trim() === "") {
      setError("Please provide an answer before proceeding.");
      return;
    }

    try {
      // Submit the answer for this question using the new endpoint
      const response = await axiosInstance.post(
        API_ENDPOINTS.ASSESSMENT.SUBMIT_ANSWER(assessment.assessment_id),
        {
          question_id: currentQuestion.question_id,
          answer: answer,
        }
      );

      setError("");
      
      const result = response.data.result;

      // Show feedback briefly (optional)
      if (result.evaluation) {
        console.log("Answer feedback:", result.evaluation.feedback);
      }

      // Move to next question
      if (currentQuestionIndex < assessment.questions.length - 1) {
        setCurrentQuestionIndex((prev) => prev + 1);
      } else {
        // All questions answered, complete assessment
        handleComplete();
      }
    } catch (err) {
      console.error("Error submitting answer:", err);
      setError(
        err.response?.data?.error || "Failed to submit answer. Please try again."
      );
    }
  };

  const handleComplete = async () => {
    try {
      setSubmitting(true);
      const timeSpent = Math.floor((Date.now() - timeStarted) / 1000); // in seconds

      // Complete the assessment
      const response = await axiosInstance.post(
        API_ENDPOINTS.ASSESSMENT.COMPLETE(assessment.assessment_id),
        {
          time_spent_seconds: timeSpent,
        }
      );

      // Navigate to results page with assessment data
      const fromOnboarding = location.state?.fromOnboarding || false;

      navigate("/assessment-results", {
        state: {
          results: response.data.results,
          assessmentId: assessment.assessment_id,
          fromOnboarding: fromOnboarding,
        },
      });
    } catch (err) {
      console.error("Error completing assessment:", err);
      setError(
        err.response?.data?.error || "Failed to complete assessment. Please try again."
      );
      setSubmitting(false);
    }
  };

  const currentQuestion = assessment?.questions?.[currentQuestionIndex] || null;
  const progress =
    ((currentQuestionIndex + 1) / (assessment?.questions?.length || 1)) * 100;
  const currentAnswer = currentQuestion
    ? answers[currentQuestion.question_id] || ""
    : "";

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 3 }}>
          Loading Assessment...
        </Typography>
      </Container>
    );
  }

  if (!assessment || !currentQuestion) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="error">
          {error || "Failed to load assessment. Please try again."}
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate("/dashboard")}
          sx={{ mt: 2 }}
        >
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          📝 Initial Assessment
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Help us understand your English proficiency level
        </Typography>
      </Box>

      {/* Progress Bar */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
            <Typography variant="body2" fontWeight={600}>
              Question {currentQuestionIndex + 1} of{" "}
              {assessment.questions.length}
            </Typography>
            <Chip
              icon={<Timer />}
              label={`${Math.round(progress)}% Complete`}
              color="primary"
              size="small"
            />
          </Box>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* Question Card */}
      <Card
        sx={{
          mb: 3,
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
        }}
      >
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
            <Chip
              label={currentQuestion.skill_area || "General"}
              sx={{
                backgroundColor: "rgba(255,255,255,0.2)",
                color: "white",
                fontWeight: 600,
              }}
            />
            <Chip
              label={currentQuestion.difficulty_level || "Mixed"}
              sx={{
                backgroundColor: "rgba(255,255,255,0.2)",
                color: "white",
              }}
            />
          </Box>

          <Typography variant="h5" fontWeight={600} sx={{ mt: 3, mb: 2 }}>
            {currentQuestion.question_text}
          </Typography>

          {currentQuestion.telugu_hint && (
            <Typography
              variant="body1"
              sx={{ opacity: 0.9, fontStyle: "italic" }}
            >
              💡 {currentQuestion.telugu_hint}
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Answer Input */}
      <Card>
        <CardContent sx={{ p: 4 }}>
          {currentQuestion.question_type === "multiple_choice" ? (
            <RadioGroup
              value={currentAnswer}
              onChange={(e) =>
                handleAnswerChange(currentQuestion.question_id, e.target.value)
              }
            >
              {currentQuestion.options?.map((option, index) => (
                <FormControlLabel
                  key={index}
                  value={option}
                  control={<Radio />}
                  label={
                    <Typography variant="body1" sx={{ py: 1 }}>
                      {option}
                    </Typography>
                  }
                  sx={{
                    mb: 1,
                    p: 2,
                    border: "1px solid",
                    borderColor:
                      currentAnswer === option ? "primary.main" : "divider",
                    borderRadius: 2,
                    backgroundColor:
                      currentAnswer === option
                        ? "rgba(102, 126, 234, 0.05)"
                        : "transparent",
                    "&:hover": {
                      backgroundColor: "rgba(102, 126, 234, 0.05)",
                    },
                  }}
                />
              ))}
            </RadioGroup>
          ) : (
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Type your answer here..."
              value={currentAnswer}
              onChange={(e) =>
                handleAnswerChange(currentQuestion.question_id, e.target.value)
              }
              variant="outlined"
              sx={{
                "& .MuiOutlinedInput-root": {
                  fontSize: "1.1rem",
                },
              }}
            />
          )}

          {/* Navigation Buttons */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mt: 4,
            }}
          >
            <Button
              variant="outlined"
              onClick={() =>
                setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))
              }
              disabled={currentQuestionIndex === 0 || submitting}
            >
              Previous
            </Button>

            {currentQuestionIndex < assessment.questions.length - 1 ? (
              <Button
                variant="contained"
                size="large"
                endIcon={<ArrowForward />}
                onClick={handleNext}
                disabled={!currentAnswer || submitting}
              >
                Next Question
              </Button>
            ) : (
              <Button
                variant="contained"
                size="large"
                color="success"
                endIcon={
                  submitting ? <CircularProgress size={20} /> : <CheckCircle />
                }
                onClick={handleNext}
                disabled={!currentAnswer || submitting}
              >
                {submitting ? "Submitting..." : "Complete Assessment"}
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Help Text */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          💡 <strong>Tip:</strong> Take your time and answer honestly. This
          assessment helps us create a personalized learning path just for you!
        </Typography>
      </Alert>
    </Container>
  );
};

export default InitialAssessment;
