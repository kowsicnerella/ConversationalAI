import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Chip,
  LinearProgress,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Avatar,
  Fade,
  Zoom,
} from "@mui/material";
import {
  CheckCircle,
  Cancel,
  Timer,
  Lightbulb,
  Refresh,
  PlayArrow,
  Star,
  TrendingUp,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";

const QuizActivity = ({ quizData, onComplete, onNext }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [timeLeft, setTimeLeft] = useState(quizData.timeLimit || 300); // 5 minutes default
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState("");
  const [showExplanation, setShowExplanation] = useState(false);
  const [isAnswered, setIsAnswered] = useState(false);

  useEffect(() => {
    if (timeLeft > 0 && !showResults) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0) {
      handleQuizComplete();
    }
  }, [timeLeft, showResults]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleAnswerSelect = (questionIndex, answer) => {
    if (isAnswered) return;

    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: answer,
    });

    // Immediate feedback for current question
    const question = quizData.questions[questionIndex];
    const isCorrect = answer === question.correctAnswer;

    setIsAnswered(true);
    setFeedback(isCorrect ? "Correct!" : "Incorrect");

    if (isCorrect) {
      setScore(score + question.points);
      toast.success("Correct answer! 🎉");
    } else {
      toast.error("Incorrect answer 😔");
    }

    // Show explanation after a brief delay
    setTimeout(() => {
      setShowExplanation(true);
    }, 1000);
  };

  const handleNextQuestion = () => {
    if (currentQuestion < quizData.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setIsAnswered(false);
      setFeedback("");
      setShowExplanation(false);
      setShowHint(false);
    } else {
      handleQuizComplete();
    }
  };

  const handleQuizComplete = () => {
    setShowResults(true);
    const totalQuestions = quizData.questions.length;
    const correctAnswers = Object.entries(selectedAnswers).filter(
      ([questionIndex, answer]) =>
        answer === quizData.questions[questionIndex].correctAnswer
    ).length;

    const finalScore = Math.round((correctAnswers / totalQuestions) * 100);
    onComplete({
      score: finalScore,
      correctAnswers,
      totalQuestions,
      timeSpent: (quizData.timeLimit || 300) - timeLeft,
      answers: selectedAnswers,
    });
  };

  const handleRestart = () => {
    setCurrentQuestion(0);
    setSelectedAnswers({});
    setShowResults(false);
    setTimeLeft(quizData.timeLimit || 300);
    setScore(0);
    setFeedback("");
    setShowExplanation(false);
    setIsAnswered(false);
    setShowHint(false);
  };

  const question = quizData.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / quizData.questions.length) * 100;

  if (showResults) {
    const totalQuestions = quizData.questions.length;
    const correctAnswers = Object.entries(selectedAnswers).filter(
      ([questionIndex, answer]) =>
        answer === quizData.questions[questionIndex].correctAnswer
    ).length;
    const percentage = Math.round((correctAnswers / totalQuestions) * 100);

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Card
          sx={{
            maxWidth: 800,
            mx: "auto",
            borderRadius: 4,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            overflow: "hidden",
          }}
        >
          <CardContent sx={{ p: 4, textAlign: "center" }}>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
            >
              <Avatar
                sx={{
                  width: 80,
                  height: 80,
                  mx: "auto",
                  mb: 3,
                  bgcolor:
                    percentage >= 70
                      ? "#4caf50"
                      : percentage >= 50
                      ? "#ff9800"
                      : "#f44336",
                }}
              >
                <Star sx={{ fontSize: 40 }} />
              </Avatar>
            </motion.div>

            <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
              Quiz Complete!
            </Typography>

            <Typography variant="h1" sx={{ fontWeight: "bold", mb: 1 }}>
              {percentage}%
            </Typography>

            <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
              {correctAnswers} out of {totalQuestions} correct
            </Typography>

            <Box
              sx={{ display: "flex", justifyContent: "center", gap: 4, mb: 4 }}
            >
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                  {score}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Points Earned
                </Typography>
              </Box>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                  {formatTime((quizData.timeLimit || 300) - timeLeft)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Time Spent
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={handleRestart}
                sx={{
                  bgcolor: "rgba(255,255,255,0.2)",
                  "&:hover": { bgcolor: "rgba(255,255,255,0.3)" },
                  borderRadius: 3,
                }}
              >
                Try Again
              </Button>
              {onNext && (
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={onNext}
                  sx={{
                    bgcolor: "#4caf50",
                    "&:hover": { bgcolor: "#45a049" },
                    borderRadius: 3,
                  }}
                >
                  Next Activity
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: "auto" }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card sx={{ mb: 3, borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="h5" sx={{ fontWeight: "bold" }}>
                {quizData.title}
              </Typography>
              <Chip
                icon={<Timer />}
                label={formatTime(timeLeft)}
                color={timeLeft < 60 ? "error" : "primary"}
                sx={{ fontWeight: "bold" }}
              />
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Question {currentQuestion + 1} of {quizData.questions.length}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary">
                {Math.round(progress)}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </motion.div>

      {/* Question Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestion}
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -100 }}
          transition={{ duration: 0.3 }}
        >
          <Card sx={{ mb: 3, borderRadius: 3 }}>
            <CardContent sx={{ p: 4 }}>
              <Box
                sx={{
                  display: "flex",
                  justify: "space-between",
                  alignItems: "flex-start",
                  mb: 3,
                }}
              >
                <Typography variant="h6" sx={{ flexGrow: 1, mr: 2 }}>
                  {question.question}
                </Typography>
                <Box sx={{ display: "flex", gap: 1 }}>
                  {question.hint && (
                    <IconButton
                      onClick={() => setShowHint(true)}
                      color="primary"
                      size="small"
                    >
                      <Lightbulb />
                    </IconButton>
                  )}
                  <Chip
                    label={`${question.points} pts`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Box>
              </Box>

              {question.image && (
                <Box sx={{ mb: 3, textAlign: "center" }}>
                  <img
                    src={question.image}
                    alt="Question"
                    style={{
                      maxWidth: "100%",
                      maxHeight: 300,
                      borderRadius: 8,
                      objectFit: "contain",
                    }}
                  />
                </Box>
              )}

              <FormControl component="fieldset" fullWidth>
                <RadioGroup
                  value={selectedAnswers[currentQuestion] || ""}
                  onChange={(e) =>
                    handleAnswerSelect(currentQuestion, e.target.value)
                  }
                >
                  <AnimatePresence>
                    {question.options.map((option, index) => {
                      const isSelected =
                        selectedAnswers[currentQuestion] === option;
                      const isCorrect = option === question.correctAnswer;
                      const shouldShowResult = isAnswered;

                      let backgroundColor = "transparent";
                      let borderColor = "divider";

                      if (shouldShowResult) {
                        if (isSelected && isCorrect) {
                          backgroundColor = "rgba(76, 175, 80, 0.1)";
                          borderColor = "#4caf50";
                        } else if (isSelected && !isCorrect) {
                          backgroundColor = "rgba(244, 67, 54, 0.1)";
                          borderColor = "#f44336";
                        } else if (!isSelected && isCorrect) {
                          backgroundColor = "rgba(76, 175, 80, 0.05)";
                          borderColor = "#4caf50";
                        }
                      } else if (isSelected) {
                        backgroundColor = "rgba(25, 118, 210, 0.1)";
                        borderColor = "#1976d2";
                      }

                      return (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          whileHover={!isAnswered ? { scale: 1.02 } : {}}
                          whileTap={!isAnswered ? { scale: 0.98 } : {}}
                        >
                          <Paper
                            variant="outlined"
                            sx={{
                              p: 2,
                              mb: 2,
                              borderRadius: 2,
                              backgroundColor,
                              borderColor,
                              borderWidth: 2,
                              cursor: isAnswered ? "default" : "pointer",
                              transition: "all 0.3s ease",
                              position: "relative",
                              overflow: "hidden",
                            }}
                          >
                            <FormControlLabel
                              value={option}
                              control={<Radio disabled={isAnswered} />}
                              label={option}
                              sx={{ width: "100%", m: 0 }}
                            />

                            {shouldShowResult && (
                              <motion.div
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                transition={{ delay: 0.5 }}
                                style={{
                                  position: "absolute",
                                  right: 16,
                                  top: "50%",
                                  transform: "translateY(-50%)",
                                }}
                              >
                                {isCorrect ? (
                                  <CheckCircle sx={{ color: "#4caf50" }} />
                                ) : isSelected ? (
                                  <Cancel sx={{ color: "#f44336" }} />
                                ) : null}
                              </motion.div>
                            )}
                          </Paper>
                        </motion.div>
                      );
                    })}
                  </AnimatePresence>
                </RadioGroup>
              </FormControl>

              {/* Feedback */}
              <AnimatePresence>
                {feedback && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Box
                      sx={{
                        mt: 3,
                        p: 2,
                        borderRadius: 2,
                        backgroundColor:
                          feedback === "Correct!"
                            ? "rgba(76, 175, 80, 0.1)"
                            : "rgba(244, 67, 54, 0.1)",
                        border: `2px solid ${
                          feedback === "Correct!" ? "#4caf50" : "#f44336"
                        }`,
                      }}
                    >
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: "bold", mb: 1 }}
                      >
                        {feedback}
                      </Typography>
                      {showExplanation && question.explanation && (
                        <Typography variant="body2" color="text.secondary">
                          {question.explanation}
                        </Typography>
                      )}
                    </Box>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Next Button */}
              {isAnswered && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1 }}
                >
                  <Box sx={{ textAlign: "center", mt: 3 }}>
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handleNextQuestion}
                      sx={{ borderRadius: 3, px: 4 }}
                    >
                      {currentQuestion < quizData.questions.length - 1
                        ? "Next Question"
                        : "Finish Quiz"}
                    </Button>
                  </Box>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>

      {/* Hint Dialog */}
      <Dialog
        open={showHint}
        onClose={() => setShowHint(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>💡 Hint</DialogTitle>
        <DialogContent>
          <Typography>{question.hint}</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHint(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

QuizActivity.propTypes = {
  quizData: PropTypes.shape({
    title: PropTypes.string.isRequired,
    timeLimit: PropTypes.number,
    questions: PropTypes.arrayOf(
      PropTypes.shape({
        question: PropTypes.string.isRequired,
        options: PropTypes.arrayOf(PropTypes.string).isRequired,
        correctAnswer: PropTypes.string.isRequired,
        explanation: PropTypes.string,
        hint: PropTypes.string,
        points: PropTypes.number.isRequired,
        image: PropTypes.string,
      })
    ).isRequired,
  }).isRequired,
  onComplete: PropTypes.func.isRequired,
  onNext: PropTypes.func,
};

export default QuizActivity;
