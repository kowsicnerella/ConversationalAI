import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  Button,
  LinearProgress,
  Chip,
  Alert,
  Paper,
  Grid,
  Fade,
  Slide,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  EmojiEvents as TrophyIcon,
  Timer as TimerIcon,
  Star as StarIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../config/api';
import { API_ENDPOINTS } from '../config/api';

const QuizActivity = ({ topic, level, onComplete }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [quizData, setQuizData] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [error, setError] = useState('');

  // Load quiz on component mount
  useEffect(() => {
    loadQuiz();
    setStartTime(Date.now());
  }, [topic, level]);

  // Track time elapsed
  useEffect(() => {
    if (startTime && !showResults) {
      const timer = setInterval(() => {
        setTimeElapsed(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [startTime, showResults]);

  const loadQuiz = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.GENERATE_QUIZ, {
        topic: topic || 'daily routine',
        level: level || 'beginner',
        num_questions: 5
      });

      if (response.data.success) {
        setQuizData(response.data.data);
      } else {
        setError('Failed to load quiz. Please try again.');
      }
    } catch (err) {
      console.error('Error loading quiz:', err);
      setError(err.response?.data?.error || 'Failed to load quiz. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionId, answer) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionId]: answer
    });
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < quizData.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmitQuiz = async () => {
    try {
      setLoading(true);
      const timeSpentMinutes = Math.ceil(timeElapsed / 60);

      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.SUBMIT, {
        session_id: quizData.session_id,
        activity_type: 'quiz',
        activity_data: quizData,
        user_answers: selectedAnswers,
        time_spent_minutes: timeSpentMinutes
      });

      if (response.data.success) {
        setEvaluation(response.data.evaluation);
        setShowResults(true);
      } else {
        setError('Failed to submit quiz. Please try again.');
      }
    } catch (err) {
      console.error('Error submitting quiz:', err);
      setError(err.response?.data?.error || 'Failed to submit quiz.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetakeQuiz = () => {
    setSelectedAnswers({});
    setCurrentQuestionIndex(0);
    setShowResults(false);
    setEvaluation(null);
    setTimeElapsed(0);
    loadQuiz();
    setStartTime(Date.now());
  };

  const handleFinish = () => {
    if (onComplete) {
      onComplete(evaluation);
    } else {
      navigate('/dashboard');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'success';
    if (percentage >= 60) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Quiz...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
        <Button
          variant="contained"
          color="primary"
          onClick={loadQuiz}
          sx={{ mt: 2 }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (!quizData) {
    return (
      <Box p={3}>
        <Alert severity="info">No quiz data available.</Alert>
      </Box>
    );
  }

  const currentQuestion = quizData.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / quizData.questions.length) * 100;
  const allQuestionsAnswered = quizData.questions.every(
    q => selectedAnswers[q.question_id]
  );

  // Results Dialog
  if (showResults && evaluation) {
    return (
      <Dialog
        open={showResults}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            p: 2
          }
        }}
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="center" flexDirection="column">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", duration: 0.5 }}
            >
              <TrophyIcon sx={{ fontSize: 80, color: getScoreColor(evaluation.score_percentage) === 'success' ? 'gold' : '#ff9800' }} />
            </motion.div>
            <Typography variant="h4" fontWeight="bold" mt={2}>
              Quiz Complete!
            </Typography>
            <Typography variant="h6" color="text.secondary">
              {quizData.quiz_title}
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent>
          {/* Score Summary */}
          <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <Grid container spacing={3} textAlign="center">
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  {evaluation.score_percentage}%
                </Typography>
                <Typography variant="body2">Score</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  {evaluation.correct_answers}/{evaluation.total_questions}
                </Typography>
                <Typography variant="body2">Correct</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  +{evaluation.points_earned}
                </Typography>
                <Typography variant="body2">Points</Typography>
              </Grid>
            </Grid>
          </Paper>

          {/* Feedback Message */}
          <Alert severity={getScoreColor(evaluation.score_percentage)} sx={{ mb: 3 }}>
            <Typography variant="body1" fontWeight="bold">
              {evaluation.feedback_message}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {evaluation.feedback_message_telugu}
            </Typography>
          </Alert>

          {/* Detailed Feedback */}
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Review Answers:
          </Typography>
          <Stack spacing={2}>
            {evaluation.detailed_feedback.map((item, index) => (
              <motion.div
                key={item.question_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card
                  variant="outlined"
                  sx={{
                    border: `2px solid ${item.is_correct ? '#4caf50' : '#f44336'}`,
                    backgroundColor: item.is_correct ? '#f1f8f4' : '#ffebee'
                  }}
                >
                  <CardContent>
                    <Box display="flex" alignItems="flex-start" mb={1}>
                      {item.is_correct ? (
                        <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                      ) : (
                        <CancelIcon sx={{ color: 'error.main', mr: 1 }} />
                      )}
                      <Box flex={1}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          Q{item.question_id}: {item.question_text}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" mt={1}>
                          Your Answer: <strong>{item.user_answer || 'Not answered'}</strong>
                        </Typography>
                        {!item.is_correct && (
                          <Typography variant="body2" color="success.main" mt={0.5}>
                            Correct Answer: <strong>{item.correct_answer}</strong>
                          </Typography>
                        )}
                        <Divider sx={{ my: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          {item.explanation}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </Stack>
        </DialogContent>

        <DialogActions sx={{ p: 3, justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            color="primary"
            onClick={handleRetakeQuiz}
            size="large"
          >
            Retake Quiz
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleFinish}
            size="large"
          >
            Finish
          </Button>
        </DialogActions>
      </Dialog>
    );
  }

  // Quiz Interface
  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          {quizData.quiz_title}
        </Typography>
        <Typography variant="body2">
          {quizData.quiz_title_telugu}
        </Typography>
        <Grid container spacing={2} mt={2}>
          <Grid item xs={6}>
            <Chip
              icon={<TimerIcon />}
              label={`Time: ${formatTime(timeElapsed)}`}
              sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
          </Grid>
          <Grid item xs={6} textAlign="right">
            <Chip
              icon={<StarIcon />}
              label={`${quizData.total_points} Points`}
              sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Progress Bar */}
      <Box mb={3}>
        <Box display="flex" justifyContent="space-between" mb={1}>
          <Typography variant="body2" color="text.secondary">
            Question {currentQuestionIndex + 1} of {quizData.questions.length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {Math.round(progress)}% Complete
          </Typography>
        </Box>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
      </Box>

      {/* Question Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentQuestionIndex}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
        >
          <Card elevation={3} sx={{ p: 3, mb: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                {currentQuestion.question_text}
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={3}>
                {currentQuestion.question_telugu}
              </Typography>

              <RadioGroup
                value={selectedAnswers[currentQuestion.question_id] || ''}
                onChange={(e) => handleAnswerSelect(currentQuestion.question_id, e.target.value)}
              >
                {currentQuestion.options.map((option, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <FormControlLabel
                      value={option}
                      control={<Radio />}
                      label={option}
                      sx={{
                        mb: 1,
                        p: 2,
                        border: '1px solid #e0e0e0',
                        borderRadius: 2,
                        '&:hover': {
                          backgroundColor: '#f5f5f5'
                        },
                        ...(selectedAnswers[currentQuestion.question_id] === option && {
                          backgroundColor: '#e3f2fd',
                          border: '2px solid #2196f3'
                        })
                      }}
                    />
                  </motion.div>
                ))}
              </RadioGroup>

              <Box display="flex" alignItems="center" mt={2}>
                <Chip
                  label={`${currentQuestion.points} points`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>

      {/* Navigation Buttons */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Button
          variant="outlined"
          onClick={handlePreviousQuestion}
          disabled={currentQuestionIndex === 0}
        >
          Previous
        </Button>

        <Typography variant="body2" color="text.secondary">
          {Object.keys(selectedAnswers).length} / {quizData.questions.length} answered
        </Typography>

        {currentQuestionIndex < quizData.questions.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleNextQuestion}
          >
            Next
          </Button>
        ) : (
          <Button
            variant="contained"
            color="success"
            onClick={handleSubmitQuiz}
            disabled={!allQuestionsAnswered || loading}
            startIcon={loading ? <CircularProgress size={20} /> : <CheckCircleIcon />}
          >
            {loading ? 'Submitting...' : 'Submit Quiz'}
          </Button>
        )}
      </Box>

      {/* Warning if not all answered */}
      {currentQuestionIndex === quizData.questions.length - 1 && !allQuestionsAnswered && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Please answer all questions before submitting the quiz.
        </Alert>
      )}
    </Box>
  );
};

export default QuizActivity;
