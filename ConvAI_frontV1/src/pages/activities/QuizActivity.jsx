import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  LinearProgress,
  Chip,
  Grid,
  Stack,
} from "@mui/material";
import {
  CheckCircle,
  Cancel,
  Timer,
  EmojiEvents,
  NavigateNext,
  Home,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import PageTransition from "../../components/common/PageTransition";
import GradientText from "../../components/common/GradientText";
import AnimatedButton from "../../components/common/AnimatedButton";
import axiosInstance, { API_ENDPOINTS } from "../../config/api";
import gamificationService from "../../services/gamificationService";
import AIGeneratingLoader from "../../components/common/AIGeneratingLoader";
import AIGeneratedBadge from "../../components/common/AIGeneratedBadge";

const QuizActivity = () => {
  const { activityId } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [answers, setAnswers] = useState([]);
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes
  const [quizComplete, setQuizComplete] = useState(false);
  const [nextActivityId, setNextActivityId] = useState(null);
  const [learningPathId, setLearningPathId] = useState(null);

  useEffect(() => {
    fetchQuiz();
  }, [activityId]);

  useEffect(() => {
    if (!quizComplete && timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0 && !quizComplete) {
      handleSubmitQuiz();
    }
  }, [timeLeft, quizComplete]);

  const fetchQuiz = async () => {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.ACTIVITIES.GENERATE.replace(":type", "quiz"),
        {
          params: { activityId },
        }
      );
      setQuiz(response.data);
    } catch (error) {
      console.error("Error fetching quiz:", error);
      // Mock data
      setQuiz({
        id: activityId,
        title: "English Vocabulary Quiz",
        description: "Test your knowledge of common English words",
        totalQuestions: 10,
        duration: 300,
        questions: [
          {
            id: 1,
            question: 'What is the meaning of "serendipity"?',
            options: [
              "A feeling of sadness",
              "Finding something good without looking for it",
              "A state of confusion",
              "Extreme happiness",
            ],
            correctAnswer: 1,
            explanation:
              "Serendipity means discovering something pleasant or valuable by chance.",
          },
          {
            id: 2,
            question: 'Choose the correct synonym for "eloquent"',
            options: ["Silent", "Articulate", "Confused", "Boring"],
            correctAnswer: 1,
            explanation:
              "Eloquent means fluent or persuasive in speaking or writing.",
          },
          {
            id: 3,
            question: 'What does "ubiquitous" mean?',
            options: [
              "Rare and unique",
              "Present everywhere",
              "Very old",
              "Extremely small",
            ],
            correctAnswer: 1,
            explanation:
              "Ubiquitous means present, appearing, or found everywhere.",
          },
          {
            id: 4,
            question: 'Select the antonym of "ephemeral"',
            options: ["Permanent", "Temporary", "Quick", "Short-lived"],
            correctAnswer: 0,
            explanation:
              "Ephemeral means lasting for a very short time, so permanent is its antonym.",
          },
          {
            id: 5,
            question: 'What is a "philanthropist"?',
            options: [
              "Someone who loves nature",
              "A person who helps others, especially through charity",
              "A philosopher",
              "A collector of stamps",
            ],
            correctAnswer: 1,
            explanation:
              "A philanthropist is someone who seeks to promote the welfare of others through donations and charitable acts.",
          },
        ],
      });
    }
  };

  // Fetch learning path and next activity
  useEffect(() => {
    const fetchNextActivity = async () => {
      try {
        // Try to get learning path ID from localStorage (set when navigating from LearningPathDetail)
        const pathIdFromStorage = localStorage.getItem("currentLearningPathId");
        if (pathIdFromStorage) {
          setLearningPathId(pathIdFromStorage);
          const pathResponse = await axiosInstance.get(
            API_ENDPOINTS.COURSES.PATH_DETAIL(pathIdFromStorage)
          );
          const activities = pathResponse.data.learning_path.activities;
          const currentIndex = activities.findIndex(
            (a) => a.id === parseInt(activityId)
          );
          
          if (currentIndex !== -1 && currentIndex < activities.length - 1) {
            setNextActivityId(activities[currentIndex + 1]);
          }
        }
      } catch (error) {
        console.error("Error fetching next activity:", error);
      }
    };

    if (quizComplete) {
      fetchNextActivity();
    }
  }, [quizComplete, activityId]);

  const handleAnswerSelect = (answerIndex) => {
    if (!showResult) {
      setSelectedAnswer(answerIndex);
    }
  };

  const handleCheckAnswer = () => {
    const isCorrect =
      selectedAnswer === quiz.questions[currentQuestion].correctAnswer;
    setShowResult(true);
    setAnswers([
      ...answers,
      {
        questionId: quiz.questions[currentQuestion].id,
        selectedAnswer,
        isCorrect,
      },
    ]);
  };

  const handleNextQuestion = () => {
    if (currentQuestion < quiz.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowResult(false);
    } else {
      handleSubmitQuiz();
    }
  };

  const handleSubmitQuiz = async () => {
    // Calculate score
    const correct = answers.filter((a) => a.isCorrect).length;
    const total = answers.length;
    const percentage = total > 0 ? Math.round((correct / total) * 100) : 0;
    
    // Save results to backend
    try {
      // Get activity data from sessionStorage to extract learning_node_id
      const activityData = JSON.parse(sessionStorage.getItem('currentActivity') || '{}');
      
      // Use multiple fallbacks to find learning_node_id
      let learningNodeId = activityData.nodeId;
      
      // If nodeId is not available, try to construct one from available data
      if (!learningNodeId) {
        // Try to use _node_info if available
        const nodeInfo = activityData._node_info;
        if (nodeInfo) {
          learningNodeId = nodeInfo.id 
            || nodeInfo.node_id 
            || `node_${activityData.nodeName?.replace(/\s+/g, '_').toLowerCase() || 'unknown'}`;
        }
      }
      
      // Final fallback: use activity ID as a reference
      if (!learningNodeId) {
        learningNodeId = `node_from_activity_${activityId}`;
        console.warn("⚠️ Using fallback learning_node_id:", learningNodeId);
      }
      
      console.log("Saving quiz activity results:", {
        activityId,
        learningNodeId,
        score: percentage,
        correct,
        total,
        timeTaken: 600 - timeLeft
      });
      
      await axiosInstance.post(
        API_ENDPOINTS.LEARNING_PATH.COMPLETE_ACTIVITY,
        {
          learning_node_id: learningNodeId,
          activity_id: activityId,
          score: percentage,
          time_spent: 600 - timeLeft, // Time spent in seconds
          activity_type: "quiz",
          activity_results: {
            correctAnswers: correct,
            totalQuestions: total,
          },
        }
      );
      
      console.log("✅ Quiz results saved successfully");
    } catch (error) {
      console.error("❌ Error saving quiz results:", error);
      // Continue to show results even if API call fails
    }

    // Update streak after completing activity
    try {
      await gamificationService.updateStreak();
      console.log("✅ Streak updated successfully");
    } catch (error) {
      console.error("Failed to update streak:", error);
    }
    
    setQuizComplete(true);
  };

  const getScore = () => {
    const correct = answers.filter((a) => a.isCorrect).length;
    const total = answers.length;
    const percentage = total > 0 ? Math.round((correct / total) * 100) : 0;
    return { correct, total, percentage };
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  if (!quiz) {
    return (
      <AIGeneratingLoader 
        message="AI is creating your quiz..."
        subMessage="Preparing personalized questions for you"
      />
    );
  }

  if (quizComplete) {
    const score = getScore();
    return (
      <PageTransition>
        <Box sx={{ maxWidth: 800, margin: "0 auto" }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, type: "spring" }}
          >
            <Card sx={{ textAlign: "center", p: 4 }}>
              <EmojiEvents
                sx={{ fontSize: 80, color: "primary.main", mb: 2 }}
              />
              <GradientText variant="h4" sx={{ mb: 2, fontWeight: 700 }}>
                Quiz Complete!
              </GradientText>
              <Typography
                variant="h2"
                color="primary.main"
                fontWeight={700}
                gutterBottom
              >
                {score.percentage}%
              </Typography>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                You got {score.correct} out of {score.total} questions correct
              </Typography>

              <Grid container spacing={2} sx={{ mt: 4, mb: 4 }}>
                <Grid item xs={6}>
                  <Box sx={{ p: 2, bgcolor: "success.light", borderRadius: 2 }}>
                    <Typography variant="h4" fontWeight={700}>
                      {score.correct}
                    </Typography>
                    <Typography variant="body2">Correct</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 2, bgcolor: "error.light", borderRadius: 2 }}>
                    <Typography variant="h4" fontWeight={700}>
                      {score.total - score.correct}
                    </Typography>
                    <Typography variant="body2">Incorrect</Typography>
                  </Box>
                </Grid>
              </Grid>

              <Box sx={{ display: "flex", gap: 2, justifyContent: "center", flexWrap: "wrap" }}>
                {nextActivityId && (
                  <AnimatedButton
                    variant="contained"
                    color="success"
                    startIcon={<NavigateNext />}
                    onClick={() => {
                      // Navigate based on activity type
                      const actType = nextActivityId.type || "quiz";
                      const typeStr = String(actType).toLowerCase();
                      if (typeStr === "flashcard" || typeStr === "flashcards") {
                        navigate(`/activities/flashcards/${nextActivityId.id}`);
                      } else if (typeStr === "quiz") {
                        navigate(`/activities/quiz/${nextActivityId.id}`);
                      } else if (typeStr === "reading") {
                        navigate(`/activities/reading/${nextActivityId.id}`);
                      } else {
                        navigate(`/activities/${nextActivityId.id}`);
                      }
                    }}
                  >
                    Next Activity
                  </AnimatedButton>
                )}
                <AnimatedButton
                  variant="contained"
                  startIcon={<Home />}
                  onClick={() => navigate("/dashboard")}
                >
                  Back to Dashboard
                </AnimatedButton>
                <AnimatedButton
                  variant="outlined"
                  onClick={() => window.location.reload()}
                >
                  Retake Quiz
                </AnimatedButton>
              </Box>
            </Card>
          </motion.div>
        </Box>
      </PageTransition>
    );
  }

  const question = quiz.questions[currentQuestion];
  const progress = ((currentQuestion + 1) / quiz.questions.length) * 100;

  return (
    <PageTransition>
      <Box sx={{ maxWidth: 900, margin: "0 auto" }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Stack direction="row" alignItems="center" spacing={2}>
            <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
              {quiz.title}
            </GradientText>
            <AIGeneratedBadge size="medium" />
          </Stack>
          <Typography variant="body1" color="text.secondary">
            {quiz.description}
          </Typography>
        </Box>

        {/* Progress and Timer */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}
            >
              <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                <Typography variant="body1" fontWeight={600}>
                  Question {currentQuestion + 1} of {quiz.questions.length}
                </Typography>
              </Box>
              <Chip
                icon={<Timer />}
                label={formatTime(timeLeft)}
                color={timeLeft < 60 ? "error" : "primary"}
              />
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </CardContent>
        </Card>

        {/* Question Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestion}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h5" fontWeight={600} gutterBottom>
                  {question.question}
                </Typography>

                <RadioGroup
                  value={selectedAnswer}
                  onChange={(e) => handleAnswerSelect(Number(e.target.value))}
                >
                  {question.options.map((option, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Card
                        sx={{
                          mb: 2,
                          cursor: showResult ? "default" : "pointer",
                          border: 2,
                          borderColor:
                            showResult && index === question.correctAnswer
                              ? "success.main"
                              : showResult &&
                                index === selectedAnswer &&
                                index !== question.correctAnswer
                              ? "error.main"
                              : selectedAnswer === index
                              ? "primary.main"
                              : "transparent",
                          bgcolor:
                            showResult && index === question.correctAnswer
                              ? "success.light"
                              : showResult &&
                                index === selectedAnswer &&
                                index !== question.correctAnswer
                              ? "error.light"
                              : "background.paper",
                          transition: "all 0.3s",
                          "&:hover": {
                            transform: showResult ? "none" : "scale(1.02)",
                          },
                        }}
                        onClick={() => handleAnswerSelect(index)}
                      >
                        <CardContent
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            py: 2,
                          }}
                        >
                          <FormControlLabel
                            value={index}
                            control={<Radio disabled={showResult} />}
                            label={option}
                            sx={{ flex: 1, m: 0 }}
                          />
                          {showResult && index === question.correctAnswer && (
                            <CheckCircle color="success" />
                          )}
                          {showResult &&
                            index === selectedAnswer &&
                            index !== question.correctAnswer && (
                              <Cancel color="error" />
                            )}
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </RadioGroup>

                {showResult && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    transition={{ duration: 0.3 }}
                  >
                    <Box
                      sx={{
                        mt: 3,
                        p: 2,
                        bgcolor:
                          selectedAnswer === question.correctAnswer
                            ? "success.light"
                            : "error.light",
                        borderRadius: 2,
                      }}
                    >
                      <Typography variant="body1" fontWeight={600} gutterBottom>
                        {selectedAnswer === question.correctAnswer
                          ? "✓ Correct!"
                          : "✗ Incorrect"}
                      </Typography>
                      <Typography variant="body2">
                        {question.explanation}
                      </Typography>
                    </Box>
                  </motion.div>
                )}

                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "flex-end",
                    gap: 2,
                    mt: 3,
                  }}
                >
                  {!showResult ? (
                    <AnimatedButton
                      variant="contained"
                      onClick={handleCheckAnswer}
                      disabled={selectedAnswer === null}
                      size="large"
                    >
                      Check Answer
                    </AnimatedButton>
                  ) : (
                    <AnimatedButton
                      variant="contained"
                      endIcon={<NavigateNext />}
                      onClick={handleNextQuestion}
                      size="large"
                    >
                      {currentQuestion < quiz.questions.length - 1
                        ? "Next Question"
                        : "Finish Quiz"}
                    </AnimatedButton>
                  )}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </AnimatePresence>
      </Box>
    </PageTransition>
  );
};

export default QuizActivity;
