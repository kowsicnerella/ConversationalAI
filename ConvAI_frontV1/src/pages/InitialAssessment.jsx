import { useState, useEffect, useRef } from "react";
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
  
  // Simplified state - just track current question, not an array!
  const [assessmentId, setAssessmentId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [nextQuestionData, setNextQuestionData] = useState(null); // Store the full response with next question
  
  const [timeStarted, setTimeStarted] = useState(null);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [progress, setProgress] = useState({ answered: 0, total: 0, percentage: 0 });
  const [isAnswered, setIsAnswered] = useState(false);
  const [fetchedComplete, setFetchedComplete] = useState(false);
  const completingRef = useRef(false);
  const nextSubmittingRef = useRef(false);

  useEffect(() => {
    // Check if assessment data was passed from registration/onboarding
    const passedAssessment = location.state?.assessmentData;
    
    if (passedAssessment) {
      console.log("Using assessment data from registration:", passedAssessment);
      setAssessmentId(passedAssessment.assessment_id);
      setCurrentQuestion(passedAssessment.questions?.[0]);
      setTimeStarted(Date.now());
      setLoading(false);
    } else {
      // Fetch new assessment if not passed
      fetchAssessment();
    }
  }, [location.state]);

  // Log when current question changes
  useEffect(() => {
    if (currentQuestion) {
      console.log("=== CURRENT QUESTION ===");
      console.log("Question ID:", currentQuestion.question_id);
      console.log("Question Text:", currentQuestion.question_text?.substring(0, 50) + "...");
      console.log("Skill Area:", currentQuestion.skill_area);
      console.log("Difficulty:", currentQuestion.difficulty_level);
    }
  }, [currentQuestion]);

  const fetchAssessment = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.post(
        API_ENDPOINTS.ASSESSMENT.GENERATE,
        {
          assessment_type: "comprehensive"
        }
      );
      const assessmentData = response.data.assessment;
      
      console.log("📥 Fetched assessment:", assessmentData);
      console.log("📥 Assessment ID:", assessmentData.assessment_id);
      console.log("📥 Questions array length:", assessmentData.questions?.length);
      console.log("📥 Current question index:", assessmentData.current_question_index);
      
      // Store assessment ID
      setAssessmentId(assessmentData.assessment_id);
      
      // Get the current question to display - ensure index is within bounds
      const questionIndex = assessmentData.current_question_index || 0;
      const questions = assessmentData.questions || [];
      
      // Validate that the question index is within the questions array
      // If index equals the number of questions, treat the assessment as already completed
      if (questionIndex > questions.length) {
        console.error(`❌ Invalid question index: ${questionIndex}, but only ${questions.length} questions available`);
        setError(`Invalid assessment state. Please start a new assessment.`);
        setLoading(false);
        return;
      }

      if (questionIndex === questions.length) {
        console.warn(`⚠️ Assessment appears complete: index ${questionIndex} === questions.length ${questions.length}`);
        // Mark progress as complete
        setProgress({ answered: questions.length, total: questions.length, percentage: 100 });
        setTimeStarted(Date.now());
        setFetchedComplete(true);
        setLoading(false);
        return;
      }
      
      const questionToShow = questions[questionIndex];
      
      if (!questionToShow) {
        console.error(`❌ No question found at index ${questionIndex}`);
        setError("Failed to load first question. Please try again.");
        setLoading(false);
        return;
      }
      
      console.log(`✅ Starting at question index ${questionIndex}:`, questionToShow?.question_id);
      
      setCurrentQuestion(questionToShow);
      
      // Update progress from metadata
      if (assessmentData.metadata) {
        setProgress({
          answered: assessmentData.metadata.answered_questions || 0,
          total: assessmentData.metadata.total_questions || 0,
          percentage: ((assessmentData.metadata.answered_questions || 0) / (assessmentData.metadata.total_questions || 1)) * 100
        });
      }
      
      setTimeStarted(Date.now());
    } catch (err) {
      console.error("Error fetching assessment:", err);
      setError("Failed to load assessment. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (answer) => {
    console.log(`✅ Answer selected: ${answer} for question ${currentQuestion?.question_id}`);
    setCurrentAnswer(answer);
  };

  const handleNext = async () => {
    console.log("📤 Submitting answer:", currentAnswer, "for question:", currentQuestion?.question_id);

    // Prevent duplicate submissions
    if (nextSubmittingRef.current) {
      console.log("handleNext already in progress - ignoring duplicate call");
      return;
    }

    if (!currentAnswer || currentAnswer.trim() === "") {
      setError("Please provide an answer before proceeding.");
      return;
    }

    try {
      nextSubmittingRef.current = true;
      setSubmitting(true);
      setError("");

      const response = await axiosInstance.post(
        API_ENDPOINTS.ASSESSMENT.SUBMIT_ANSWER(assessmentId),
        {
          question_id: currentQuestion.question_id,
          answer: currentAnswer,
        }
      );

      setSubmitting(false);
      const result = response.data.result;

      console.log("📥 Received response:", result);

      // Update progress
      if (result.progress) {
        setProgress(result.progress);
      }

      // Show feedback
      if (result.evaluation) {
        setFeedback(result.evaluation);
        setShowFeedback(true);
      }

      // Store the complete result for when user clicks Continue
      setNextQuestionData(result);
      
      if (result.is_complete) {
        console.log("🎉 Assessment complete!");
      } else if (result.next_question) {
        console.log("➡️ Next question ready:", result.next_question.question_id);
        console.log("Will display after user clicks Continue");
      }

      setIsAnswered(true);
    } catch (err) {
      console.error("Error submitting answer:", err);
      setError(
        err.response?.data?.error || "Failed to submit answer. Please try again."
      );
      setSubmitting(false);
    }
    finally {
      nextSubmittingRef.current = false;
      setSubmitting(false);
    }
  };

  const handleContinue = () => {
    console.log("⏭️ CONTINUE CLICKED - Moving to next question");
    console.log("Current state - isAnswered:", isAnswered);
    console.log("Next question data:", nextQuestionData);
    
    if (!nextQuestionData) {
      console.error("❌ No next question data available!");
      return;
    }
    
    if (!nextQuestionData.next_question) {
      console.error("❌ No next_question in data!");
      console.log("Data:", nextQuestionData);
      return;
    }
    
    console.log("✅ Next question exists:", nextQuestionData.next_question.question_id);
    
    // Hide feedback first
    setShowFeedback(false);
    setFeedback(null);
    
    // Clear the previous answer BEFORE loading new question
    console.log("Clearing previous answer...");
    setCurrentAnswer("");
    
    // Now load the next question
    console.log("Loading next question:", nextQuestionData.next_question.question_id);
    console.log("Question text:", nextQuestionData.next_question.question_text?.substring(0, 50));
    setCurrentQuestion(nextQuestionData.next_question);
    
    // Reset states
    setIsAnswered(false);
    setNextQuestionData(null);
    
    console.log("✅ State updated - ready for next answer");
  };

  const handleComplete = async () => {
    // Prevent duplicate completion requests (guard with ref)
    if (completingRef.current) {
      console.log("handleComplete already in progress - ignoring duplicate call");
      return;
    }

    try {
      completingRef.current = true;
      setSubmitting(true);
      const timeSpent = Math.floor((Date.now() - timeStarted) / 1000);

      let resultsData = null;
      
      try {
        // Try to complete the assessment (fresh assessments)
        const response = await axiosInstance.post(
          API_ENDPOINTS.ASSESSMENT.COMPLETE(assessmentId),
          {
            time_spent_seconds: timeSpent,
          }
        );
        resultsData = response.data.results;
        console.log("✅ Assessment completed successfully");
      } catch (completeErr) {
        // If assessment is already completed, fetch results from the results endpoint
        if (completeErr.response?.status === 400 && 
            completeErr.response?.data?.error === "Assessment is already completed") {
          console.warn("⚠️ Assessment already completed, fetching results...");
          const resultsResponse = await axiosInstance.get(
            API_ENDPOINTS.ASSESSMENT.RESULTS(assessmentId)
          );
          resultsData = resultsResponse.data.results;
          console.log("✅ Results fetched for already-completed assessment");
        } else {
          // Re-throw if it's a different error
          throw completeErr;
        }
      }

      const fromOnboarding = location.state?.fromOnboarding || false;

      navigate("/assessment-results", {
        state: {
          results: resultsData,
          assessmentId: assessmentId,
          fromOnboarding: fromOnboarding,
        },
      });
    } catch (err) {
      console.error("Error completing assessment:", err);
      setError(
        err.response?.data?.error || "Failed to complete assessment."
      );
      setSubmitting(false);
      completingRef.current = false;
    }
    finally {
      // Ensure we clear the guard when done
      completingRef.current = false;
      setSubmitting(false);
    }
  };

  // Calculate progress percentage
  const progressPercentage = progress.percentage || 0;

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

  const handleResetAssessment = async () => {
    try {
      setLoading(true);
      // Clear the current state
      setCurrentQuestion(null);
      setCurrentAnswer("");
      setAssessmentId(null);
      setError("");
      
      // Fetch a fresh assessment
      await fetchAssessment();
    } catch (err) {
      console.error("Error resetting assessment:", err);
      setError("Failed to reset assessment. Please try again.");
      setLoading(false);
    }
  };

  if (!currentQuestion) {
    // If we fetched the assessment and it is already complete (index === length), show a completion CTA
    if (fetchedComplete) {
      return (
        <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            It looks like you have already completed this assessment. You can view your results or start a new assessment.
          </Alert>
          <Box sx={{ mt: 2, display: "flex", gap: 2, justifyContent: "center" }}>
            <Button
              variant="contained"
              onClick={handleComplete}
              disabled={loading || submitting}
            >
              {submitting ? <CircularProgress size={20} /> : "View Results"}
            </Button>
            <Button
              variant="outlined"
              onClick={handleResetAssessment}
            >
              Start New Assessment
            </Button>
          </Box>
        </Container>
      );
    }

    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="error">
          {error || "Failed to load assessment. Please try again."}
        </Alert>
        <Box sx={{ mt: 2, display: "flex", gap: 2 }}>
          <Button
            variant="contained"
            onClick={handleResetAssessment}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Retry Assessment"}
          </Button>
          <Button
            variant="outlined"
            onClick={() => navigate("/dashboard")}
          >
            Back to Dashboard
          </Button>
        </Box>
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
              Question {progress.answered + 1} of {progress.total}
            </Typography>
            <Chip
              icon={<Timer />}
              label={`${Math.round(progressPercentage)}% Complete`}
              color="primary"
              size="small"
            />
          </Box>
          <LinearProgress
            variant="determinate"
            value={progressPercentage}
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

      {/* Feedback Alert - Shows after each answer */}
      {showFeedback && feedback && (
        <Alert 
          severity={feedback.correct ? "success" : "warning"}
          sx={{ 
            mb: 3,
            animation: "slideInDown 0.3s ease-out",
            "@keyframes slideInDown": {
              from: {
                opacity: 0,
                transform: "translateY(-20px)"
              },
              to: {
                opacity: 1,
                transform: "translateY(0)"
              }
            }
          }}
          icon={feedback.correct ? "✅" : "❌"}
        >
          <Typography variant="h6" fontWeight={600} gutterBottom>
            {feedback.correct ? "Correct! Well done!" : "Not quite right"}
          </Typography>
          <Typography variant="body1" sx={{ mb: 1 }}>
            {feedback.explanation}
          </Typography>
          {!feedback.correct && (
            <Typography variant="body2" color="text.secondary">
              Correct answer: <strong>{feedback.correct_answer}</strong>
            </Typography>
          )}
          <Typography variant="body1" fontWeight="bold" color="primary" sx={{ mt: 1 }}>
            Points earned: +{feedback.points_earned} / {feedback.points_possible}
          </Typography>
          {feedback.feedback_telugu && (
            <Typography variant="body2" sx={{ mt: 1, fontStyle: "italic" }}>
              {feedback.feedback_telugu}
            </Typography>
          )}
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
              onChange={(e) => handleAnswerChange(e.target.value)}
            >
              {currentQuestion.options?.map((option, index) => {
                // Convert index to letter (0->A, 1->B, 2->C, 3->D)
                const optionLetter = String.fromCharCode(65 + index);
                const isSelected = currentAnswer === optionLetter;
                
                return (
                  <FormControlLabel
                    key={index}
                    value={optionLetter}
                    control={<Radio />}
                    label={
                      <Typography variant="body1" sx={{ py: 1 }}>
                        <strong>{optionLetter}.</strong> {option}
                      </Typography>
                    }
                    sx={{
                      mb: 1,
                      p: 2,
                      border: "1px solid",
                      borderColor:
                        isSelected ? "primary.main" : "divider",
                      borderRadius: 2,
                      backgroundColor:
                        isSelected
                          ? "rgba(102, 126, 234, 0.05)"
                          : "transparent",
                      "&:hover": {
                        backgroundColor: "rgba(102, 126, 234, 0.05)",
                      },
                    }}
                  />
                );
              })}
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
            {!isAnswered ? (
              // Submit Answer Button
              <Button
                variant="contained"
                size="large"
                fullWidth
                endIcon={<ArrowForward />}
                onClick={handleNext}
                disabled={!currentAnswer || submitting}
              >
                {submitting ? "Submitting..." : "Submit Answer"}
              </Button>
            ) : (
              // Continue Button (after answer submitted)
              <Button
                variant="contained"
                size="large"
                fullWidth
                color="primary"
                endIcon={<ArrowForward />}
                onClick={() => {
                  console.log("🖱️ Continue button clicked!");
                  console.log("Progress:", progress.answered, "/", progress.total);
                  console.log("Next question data:", nextQuestionData);
                  console.log("Is complete?", nextQuestionData?.is_complete || progress.answered >= progress.total);
                  
                  // Check if assessment is complete (either from backend flag or progress count)
                  if (nextQuestionData?.is_complete || progress.answered >= progress.total) {
                    // All questions answered
                    console.log("✅ Calling handleComplete - Assessment finished!");
                    handleComplete();
                  } else {
                    // Continue to next question
                    console.log("➡️ Calling handleContinue - More questions remaining");
                    handleContinue();
                  }
                }}
                disabled={submitting}
                sx={{
                  animation: "pulse 1.5s infinite",
                  "@keyframes pulse": {
                    "0%, 100%": { transform: "scale(1)" },
                    "50%": { transform: "scale(1.03)" }
                  }
                }}
              >
                {progress.answered >= progress.total
                  ? "View Results"
                  : "Continue to Next Question"}
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
