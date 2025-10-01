import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
  LinearProgress,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Avatar,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  TextField,
  FormGroup,
  Divider,
  Alert,
  CircularProgress,
  Fab,
} from "@mui/material";
import {
  Assessment,
  Timer,
  CheckCircle,
  Cancel,
  PlayArrow,
  Pause,
  Stop,
  RestartAlt,
  TrendingUp,
  School,
  Star,
  EmojiEvents,
  Close,
  NavigateNext,
  NavigateBefore,
  Flag,
  Lightbulb,
  Psychology,
  Speed,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";
import { assessmentAPI } from "../services/api";

const assessmentTypes = [
  {
    id: "placement",
    title: "Placement Test",
    description:
      "Comprehensive assessment to determine your current Telugu proficiency level",
    duration: 45,
    questions: 50,
    difficulty: "Adaptive",
    icon: Psychology,
    color: "#2196f3",
    badge: "Essential",
  },
  {
    id: "chapter",
    title: "Chapter Assessment",
    description:
      "Test your understanding of specific chapter content and concepts",
    duration: 20,
    questions: 25,
    difficulty: "Chapter-based",
    icon: School,
    color: "#4caf50",
    badge: "Regular",
  },
  {
    id: "skill",
    title: "Skill Assessment",
    description:
      "Focus on specific skills like reading, writing, speaking, or listening",
    duration: 30,
    questions: 35,
    difficulty: "Skill-focused",
    icon: Speed,
    color: "#ff9800",
    badge: "Targeted",
  },
  {
    id: "progress",
    title: "Progress Evaluation",
    description: "Regular evaluation to track your learning progress over time",
    duration: 25,
    questions: 30,
    difficulty: "Mixed",
    icon: TrendingUp,
    color: "#9c27b0",
    badge: "Weekly",
  },
];

// Mock data removed - using real API data from assessmentAPI

const AssessmentPage = () => {
  const navigate = useNavigate();
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [showAssessmentDialog, setShowAssessmentDialog] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isActive, setIsActive] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [assessmentResults, setAssessmentResults] = useState(null);
  const [flaggedQuestions, setFlaggedQuestions] = useState(new Set());
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [loading, setLoading] = useState(false);
  const [assessmentHistory, setAssessmentHistory] = useState([]);

  const handleSubmitAssessment = async () => {
    setIsActive(false);
    setLoading(true);

    try {
      // Submit assessment answers to API
      const response = await assessmentAPI.submitAssessment(
        selectedAssessment.id,
        answers
      );

      if (response.data.success) {
        setAssessmentResults(response.data.assessment_results);
        setShowResults(true);
        toast.success("Assessment completed successfully!");
      } else {
        toast.error("Failed to submit assessment");
      }
    } catch (error) {
      console.error("Error submitting assessment:", error);
      toast.error("Failed to submit assessment");

      // Fallback to local calculation
      const correctAnswers = selectedAssessment.questions.filter((question) => {
        const userAnswer = answers[question.id];
        return userAnswer === question.correctAnswer;
      });

      const totalPoints = selectedAssessment.questions.reduce(
        (sum, q) => sum + q.points,
        0
      );
      const earnedPoints = correctAnswers.reduce((sum, q) => sum + q.points, 0);
      const percentage = Math.round((earnedPoints / totalPoints) * 100);

      const results = {
        totalQuestions: selectedAssessment.questions.length,
        answeredQuestions: Object.keys(answers).length,
        correctAnswers: correctAnswers.length,
        incorrectAnswers: Object.keys(answers).length - correctAnswers.length,
        unansweredQuestions:
          selectedAssessment.questions.length - Object.keys(answers).length,
        totalPoints,
        earnedPoints,
        percentage,
        timeSpent: selectedAssessment.timeLimit - timeRemaining,
        proficiencyLevel:
          percentage >= 80
            ? "Advanced"
            : percentage >= 60
            ? "Intermediate"
            : "Beginner",
      };

      setAssessmentResults(results);
      setShowResults(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let interval = null;
    if (isActive && !isPaused && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(timeRemaining - 1);
      }, 1000);
    } else if (timeRemaining === 0 && isActive) {
      handleSubmitAssessment();
    }
    return () => clearInterval(interval);
  }, [isActive, isPaused, timeRemaining]);

  const handleStartAssessment = async (assessmentType) => {
    setLoading(true);

    try {
      // Generate assessment using API
      const response = await assessmentAPI.generateAssessment(assessmentType);

      if (response.data.success) {
        const assessmentData = response.data.assessment;
        const assessment = assessmentTypes.find((a) => a.id === assessmentType);

        setSelectedAssessment({
          ...assessment,
          ...assessmentData,
          id: assessmentData.assessment_id,
        });
        setTimeRemaining(assessmentData.time_limit || 2700); // Default 45 minutes
        setCurrentQuestion(0);
        setAnswers({});
        setFlaggedQuestions(new Set());
        setShowAssessmentDialog(true);
        setIsActive(true);
        setIsPaused(false);
        toast.success("Assessment generated successfully!");
      } else {
        toast.error("Failed to generate assessment");
      }
    } catch (error) {
      console.error("Error generating assessment:", error);
      toast.error("Failed to generate assessment. Please try again later.");
      // No fallback to mock data - encourage user to try again or contact support
    } finally {
      setLoading(false);
    }
  };

  // Load assessment history on component mount
  useEffect(() => {
    const loadAssessmentHistory = async () => {
      try {
        const response = await assessmentAPI.getHistory();
        if (response.data.success) {
          setAssessmentHistory(response.data.assessments || []);
        }
      } catch (error) {
        console.error("Error loading assessment history:", error);
      }
    };

    loadAssessmentHistory();
  }, []);

  const handleAnswerChange = (questionId, answer) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestion < selectedAssessment.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleFlagQuestion = () => {
    const questionId = selectedAssessment.questions[currentQuestion].id;
    setFlaggedQuestions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(questionId)) {
        newSet.delete(questionId);
      } else {
        newSet.add(questionId);
      }
      return newSet;
    });
  };

  const handlePauseResume = () => {
    setIsPaused(!isPaused);
  };

  const calculateCategoryScores = () => {
    const categories = {};
    selectedAssessment.questions.forEach((question) => {
      if (!categories[question.category]) {
        categories[question.category] = { total: 0, correct: 0 };
      }
      categories[question.category].total += 1;
      if (answers[question.id] === question.correctAnswer) {
        categories[question.category].correct += 1;
      }
    });

    return Object.entries(categories).map(([category, data]) => ({
      category,
      percentage: Math.round((data.correct / data.total) * 100),
      correct: data.correct,
      total: data.total,
    }));
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  const handleCloseAssessment = () => {
    if (isActive && !showResults) {
      setShowConfirmDialog(true);
    } else {
      setShowAssessmentDialog(false);
      setSelectedAssessment(null);
      setShowResults(false);
      setAssessmentResults(null);
      setIsActive(false);
    }
  };

  const handleConfirmClose = () => {
    setShowConfirmDialog(false);
    setShowAssessmentDialog(false);
    setSelectedAssessment(null);
    setIsActive(false);
    toast.error("Assessment cancelled");
  };

  const AssessmentCard = ({ assessment, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      whileHover={{ y: -5 }}
    >
      <Card
        sx={{
          height: "100%",
          borderRadius: 3,
          overflow: "hidden",
          cursor: "pointer",
          transition: "all 0.3s ease-in-out",
          "&:hover": {
            boxShadow: "0 12px 40px rgba(0,0,0,0.15)",
          },
        }}
        onClick={() => handleStartAssessment(assessment.id)}
      >
        <Box
          sx={{
            height: 120,
            background: `linear-gradient(135deg, ${assessment.color}22, ${assessment.color}44)`,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            p: 3,
            position: "relative",
          }}
        >
          <assessment.icon
            sx={{ fontSize: 60, color: assessment.color, opacity: 0.8 }}
          />
          <Chip
            label={assessment.badge}
            size="small"
            sx={{
              backgroundColor: assessment.color,
              color: "white",
              fontWeight: "bold",
            }}
          />
        </Box>

        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: "bold", mb: 1 }}>
            {assessment.title}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {assessment.description}
          </Typography>

          <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Timer sx={{ fontSize: 16, color: "text.secondary" }} />
              <Typography variant="caption" color="text.secondary">
                {assessment.duration} min
              </Typography>
            </Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Assessment sx={{ fontSize: 16, color: "text.secondary" }} />
              <Typography variant="caption" color="text.secondary">
                {assessment.questions} questions
              </Typography>
            </Box>
          </Box>

          <Chip
            label={assessment.difficulty}
            size="small"
            variant="outlined"
            sx={{ mb: 2 }}
          />
        </CardContent>

        <CardActions sx={{ p: 3, pt: 0 }}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={(e) => {
              e.stopPropagation();
              handleStartAssessment(assessment.id);
            }}
            sx={{
              borderRadius: 2,
              backgroundColor: assessment.color,
              "&:hover": {
                backgroundColor: assessment.color,
                filter: "brightness(0.9)",
              },
            }}
          >
            Start Assessment
          </Button>
        </CardActions>
      </Card>
    </motion.div>
  );

  const QuestionComponent = ({ question, answer, onAnswerChange }) => {
    switch (question.type) {
      case "multiple-choice":
        return (
          <RadioGroup
            value={answer || ""}
            onChange={(e) => onAnswerChange(question.id, e.target.value)}
          >
            {question.options.map((option, index) => (
              <FormControlLabel
                key={index}
                value={option}
                control={<Radio />}
                label={option}
                sx={{ mb: 1 }}
              />
            ))}
          </RadioGroup>
        );

      case "fill-blank":
        return (
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your answer here..."
            value={answer || ""}
            onChange={(e) => onAnswerChange(question.id, e.target.value)}
            sx={{ mt: 2 }}
          />
        );

      case "audio-comprehension":
        return (
          <Box>
            <Button
              variant="outlined"
              startIcon={<PlayArrow />}
              sx={{ mb: 2 }}
              onClick={() => {
                // Simulate audio play
                toast.success("Audio playing...");
              }}
            >
              Play Audio
            </Button>
            <RadioGroup
              value={answer || ""}
              onChange={(e) => onAnswerChange(question.id, e.target.value)}
            >
              {question.options.map((option, index) => (
                <FormControlLabel
                  key={index}
                  value={option}
                  control={<Radio />}
                  label={option}
                  sx={{ mb: 1 }}
                />
              ))}
            </RadioGroup>
          </Box>
        );

      case "reading-comprehension":
        return (
          <Box>
            <Paper sx={{ p: 2, mb: 2, backgroundColor: "grey.50" }}>
              <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
                {question.passage}
              </Typography>
            </Paper>
            <RadioGroup
              value={answer || ""}
              onChange={(e) => onAnswerChange(question.id, e.target.value)}
            >
              {question.options.map((option, index) => (
                <FormControlLabel
                  key={index}
                  value={option}
                  control={<Radio />}
                  label={option}
                  sx={{ mb: 1 }}
                />
              ))}
            </RadioGroup>
          </Box>
        );

      default:
        return <Typography>Question type not supported</Typography>;
    }
  };

  QuestionComponent.propTypes = {
    question: PropTypes.object.isRequired,
    answer: PropTypes.string,
    onAnswerChange: PropTypes.func.isRequired,
  };

  AssessmentCard.propTypes = {
    assessment: PropTypes.object.isRequired,
    index: PropTypes.number.isRequired,
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Header */}
        <Paper
          elevation={3}
          sx={{
            p: 4,
            mb: 4,
            borderRadius: 3,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            textAlign: "center",
          }}
        >
          <Assessment sx={{ fontSize: 60, mb: 2 }} />
          <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
            Assessment Center
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9 }}>
            Evaluate your Telugu proficiency with comprehensive assessments
          </Typography>
        </Paper>

        {/* Assessment Types Grid */}
        <Grid container spacing={3}>
          {assessmentTypes.map((assessment, index) => (
            <Grid item xs={12} sm={6} lg={3} key={assessment.id}>
              <AssessmentCard assessment={assessment} index={index} />
            </Grid>
          ))}
        </Grid>
      </motion.div>

      {/* Assessment Dialog */}
      <Dialog
        open={showAssessmentDialog}
        onClose={handleCloseAssessment}
        maxWidth="lg"
        fullWidth
        fullScreen
      >
        <DialogTitle
          sx={{
            p: 2,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box>
            <Typography variant="h6" sx={{ fontWeight: "bold" }}>
              {selectedAssessment?.title}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Question {currentQuestion + 1} of{" "}
              {selectedAssessment?.questions.length}
            </Typography>
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Chip
              icon={<Timer />}
              label={formatTime(timeRemaining)}
              color={timeRemaining < 300 ? "error" : "primary"}
              variant="outlined"
            />
            <IconButton onClick={handlePauseResume}>
              {isPaused ? <PlayArrow /> : <Pause />}
            </IconButton>
            <IconButton onClick={handleCloseAssessment} edge="end">
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 3 }}>
          {!showResults && selectedAssessment && (
            <Box>
              {/* Progress Bar */}
              <LinearProgress
                variant="determinate"
                value={
                  ((currentQuestion + 1) /
                    selectedAssessment.questions.length) *
                  100
                }
                sx={{ mb: 3, height: 8, borderRadius: 4 }}
              />

              {/* Question */}
              <Paper sx={{ p: 3, mb: 3 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    mb: 2,
                  }}
                >
                  <Box>
                    <Chip
                      label={
                        selectedAssessment.questions[currentQuestion].category
                      }
                      size="small"
                      sx={{ mb: 1 }}
                    />
                    <Chip
                      label={
                        selectedAssessment.questions[currentQuestion].difficulty
                      }
                      size="small"
                      color={
                        selectedAssessment.questions[currentQuestion]
                          .difficulty === "easy"
                          ? "success"
                          : selectedAssessment.questions[currentQuestion]
                              .difficulty === "medium"
                          ? "warning"
                          : "error"
                      }
                      sx={{ mb: 1, ml: 1 }}
                    />
                  </Box>
                  <IconButton
                    onClick={handleFlagQuestion}
                    color={
                      flaggedQuestions.has(
                        selectedAssessment.questions[currentQuestion].id
                      )
                        ? "warning"
                        : "default"
                    }
                  >
                    <Flag />
                  </IconButton>
                </Box>

                <Typography variant="h6" sx={{ mb: 3, fontWeight: "bold" }}>
                  {selectedAssessment.questions[currentQuestion].question}
                </Typography>

                <QuestionComponent
                  question={selectedAssessment.questions[currentQuestion]}
                  answer={
                    answers[selectedAssessment.questions[currentQuestion].id]
                  }
                  onAnswerChange={handleAnswerChange}
                />
              </Paper>

              {/* Navigation */}
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Button
                  startIcon={<NavigateBefore />}
                  onClick={handlePreviousQuestion}
                  disabled={currentQuestion === 0}
                >
                  Previous
                </Button>

                <Box sx={{ display: "flex", gap: 1 }}>
                  {currentQuestion ===
                  selectedAssessment.questions.length - 1 ? (
                    <Button
                      variant="contained"
                      color="success"
                      startIcon={<CheckCircle />}
                      onClick={handleSubmitAssessment}
                    >
                      Submit Assessment
                    </Button>
                  ) : (
                    <Button
                      endIcon={<NavigateNext />}
                      onClick={handleNextQuestion}
                      variant="outlined"
                    >
                      Next
                    </Button>
                  )}
                </Box>
              </Box>
            </Box>
          )}

          {/* Results */}
          {showResults && assessmentResults && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Box sx={{ textAlign: "center", mb: 4 }}>
                <EmojiEvents
                  sx={{
                    fontSize: { xs: 56, sm: 64 },
                    color: assessmentResults.passed ? "#4caf50" : "#ff9800",
                    mb: 2,
                  }}
                />
                <Typography variant="h4" sx={{ fontWeight: "bold", mb: 1 }}>
                  {assessmentResults.passed
                    ? "Congratulations!"
                    : "Keep Learning!"}
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  You scored {assessmentResults.percentage}% -{" "}
                  {assessmentResults.level} Level
                </Typography>
              </Box>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                      Overall Performance
                    </Typography>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 1,
                      }}
                    >
                      <Typography>Correct Answers:</Typography>
                      <Typography color="success.main">
                        {assessmentResults.correctAnswers}
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 1,
                      }}
                    >
                      <Typography>Incorrect Answers:</Typography>
                      <Typography color="error.main">
                        {assessmentResults.incorrectAnswers}
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 1,
                      }}
                    >
                      <Typography>Unanswered:</Typography>
                      <Typography color="warning.main">
                        {assessmentResults.unansweredQuestions}
                      </Typography>
                    </Box>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 1,
                      }}
                    >
                      <Typography>Time Spent:</Typography>
                      <Typography>
                        {formatTime(assessmentResults.timeSpent)}
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                      Category Breakdown
                    </Typography>
                    {assessmentResults.categoryScores.map((category, index) => (
                      <Box key={index} sx={{ mb: 2 }}>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            mb: 1,
                          }}
                        >
                          <Typography variant="body2">
                            {category.category}
                          </Typography>
                          <Typography variant="body2">
                            {category.percentage}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={category.percentage}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    ))}
                  </Paper>
                </Grid>
              </Grid>

              <Box sx={{ textAlign: "center", mt: 3 }}>
                <Button
                  variant="contained"
                  startIcon={<RestartAlt />}
                  onClick={() => {
                    setShowResults(false);
                    setShowAssessmentDialog(false);
                    toast.success("Ready for another assessment!");
                  }}
                  sx={{ mr: 2 }}
                >
                  Take Another Assessment
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate("/dashboard")}
                >
                  Back to Dashboard
                </Button>
              </Box>
            </motion.div>
          )}
        </DialogContent>
      </Dialog>

      {/* Confirm Close Dialog */}
      <Dialog
        open={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
      >
        <DialogTitle>
          <Typography variant="h6" sx={{ fontWeight: "bold" }}>
            Cancel Assessment?
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to cancel this assessment? Your progress will
            be lost.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDialog(false)}>
            Continue Assessment
          </Button>
          <Button
            onClick={handleConfirmClose}
            color="error"
            variant="contained"
          >
            Cancel Assessment
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for Pause/Resume */}
      {isActive && !showResults && (
        <Fab
          color="primary"
          sx={{ position: "fixed", bottom: 16, right: 16 }}
          onClick={handlePauseResume}
        >
          {isPaused ? <PlayArrow /> : <Pause />}
        </Fab>
      )}
    </Container>
  );
};

export default AssessmentPage;
