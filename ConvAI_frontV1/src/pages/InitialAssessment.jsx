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
  Dialog,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import axiosInstance, { API_ENDPOINTS } from "../config/api";
import { ArrowForward, CheckCircle, Timer, Close, Check } from "@mui/icons-material";

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

  // Auto-advance timer ref
  const autoAdvanceTimerRef = useRef(null);

  // Auto-advance to next question after showing feedback
  const autoAdvanceToNext = () => {
    // Clear any existing timer
    if (autoAdvanceTimerRef.current) {
      clearTimeout(autoAdvanceTimerRef.current);
    }
    
    // Wait 2.5 seconds then advance
    autoAdvanceTimerRef.current = setTimeout(() => {
      setShowFeedback(false);
      
      if (nextQuestionData?.is_complete || progress.answered >= progress.total) {
        handleComplete();
      } else if (nextQuestionData?.next_question) {
        handleContinue();
      }
    }, 2500);
  };

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (autoAdvanceTimerRef.current) {
        clearTimeout(autoAdvanceTimerRef.current);
      }
    };
  }, []);

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

      // Show feedback in dialog popup
      if (result.evaluation) {
        setFeedback(result.evaluation);
        setShowFeedback(true);
        // Auto-advance after showing feedback
        autoAdvanceToNext();
      }

      // Store the complete result for auto-advance
      setNextQuestionData(result);
      
      if (result.is_complete) {
        console.log("🎉 Assessment complete!");
      } else if (result.next_question) {
        console.log("➡️ Next question ready:", result.next_question.question_id);
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
    <Container maxWidth="md" sx={{ py: 4, minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          📝 Initial Assessment
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Help us understand your English proficiency level
        </Typography>
      </Box>

      {/* Progress Bar */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ py: 2 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 1,
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
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* Question Card - Fixed height for consistency */}
      <Card
        sx={{
          mb: 2,
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          color: "white",
          minHeight: "180px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2, mb: 2 }}>
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

          <Typography variant="h5" fontWeight={600}>
            {currentQuestion.question_text}
          </Typography>
          {/* Telugu translation of the question */}
          {currentQuestion.question_telugu && (
            <Typography 
              variant="body1" 
              sx={{ 
                mt: 1, 
                color: 'rgba(255,255,255,0.8)', 
                fontStyle: 'italic',
                fontSize: '1.1rem'
              }}
            >
              {currentQuestion.question_telugu}
            </Typography>
          )}
          {/* Telugu hint for additional context */}
          {currentQuestion.telugu_hint && (
            <Typography 
              variant="body2" 
              sx={{ 
                mt: 1, 
                color: 'rgba(255,255,255,0.7)',
                backgroundColor: 'rgba(255,255,255,0.1)',
                px: 2,
                py: 0.5,
                borderRadius: 1,
                display: 'inline-block'
              }}
            >
              💡 {currentQuestion.telugu_hint}
            </Typography>
          )}
        </CardContent>
      </Card>

      {/* Answer Input - Fixed height area */}
      <Card sx={{ flexGrow: 1, display: "flex", flexDirection: "column" }}>
        <CardContent sx={{ p: 3, flexGrow: 1 }}>
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

          {/* Submit Button - Single action, auto-advances after feedback */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              mt: 3,
            }}
          >
            <Button
              variant="contained"
              size="large"
              fullWidth
              endIcon={submitting ? null : <ArrowForward />}
              onClick={handleNext}
              disabled={!currentAnswer || submitting || isAnswered}
              sx={{
                py: 1.5,
                fontSize: "1.1rem",
              }}
            >
              {submitting ? (
                <>
                  <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
                  Submitting...
                </>
              ) : (
                "Submit Answer"
              )}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Feedback Dialog - Shows after each answer with auto-advance */}
      <Dialog
        open={showFeedback && feedback !== null}
        onClose={() => {}}  // Prevent closing by clicking outside
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            overflow: "hidden",
          }
        }}
      >
        <Box
          sx={{
            background: feedback?.correct 
              ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" 
              : "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
            color: "white",
            py: 3,
            px: 3,
            textAlign: "center",
          }}
        >
          <Box sx={{ fontSize: 48, mb: 1 }}>
            {feedback?.correct ? <Check sx={{ fontSize: 64 }} /> : <Close sx={{ fontSize: 64 }} />}
          </Box>
          <Typography variant="h5" fontWeight={700}>
            {feedback?.correct ? "Correct! 🎉" : "Not Quite Right"}
          </Typography>
        </Box>
        <DialogContent sx={{ py: 3, px: 3 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>
            {feedback?.explanation}
          </Typography>
          {/* Telugu explanation */}
          {feedback?.explanation_telugu && (
            <Typography 
              variant="body2" 
              sx={{ 
                mb: 2, 
                color: 'text.secondary',
                fontStyle: 'italic',
                pl: 2,
                borderLeft: '3px solid',
                borderColor: 'primary.main'
              }}
            >
              {feedback.explanation_telugu}
            </Typography>
          )}
          {!feedback?.correct && feedback?.correct_answer && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Correct Answer:</strong> {feedback.correct_answer}
              </Typography>
            </Alert>
          )}
          <Box sx={{ 
            display: "flex", 
            justifyContent: "center", 
            alignItems: "center",
            gap: 1,
            mt: 2,
            p: 2,
            bgcolor: "grey.100",
            borderRadius: 2,
          }}>
            <Typography variant="h6" fontWeight={700} color="primary">
              +{feedback?.points_earned || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              / {feedback?.points_possible || 0} points
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>
            Auto-advancing in a moment...
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => {
              // Clear auto-advance timer and manually advance
              if (autoAdvanceTimerRef.current) {
                clearTimeout(autoAdvanceTimerRef.current);
              }
              setShowFeedback(false);
              if (nextQuestionData?.is_complete || progress.answered >= progress.total) {
                handleComplete();
              } else if (nextQuestionData?.next_question) {
                handleContinue();
              }
            }}
            endIcon={<ArrowForward />}
          >
            {progress.answered >= progress.total ? "View Results" : "Next Question"}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default InitialAssessment;
