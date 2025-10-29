/**
 * AdaptiveTestInterface Component
 * 
 * Interactive interface for taking adaptive assessments with:
 * - Real-time question display
 * - Answer input/selection
 * - Progress tracking with IRT metrics
 * - Immediate feedback
 * - Adaptive difficulty visualization
 * 
 * @component
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  RadioGroup,
  FormControlLabel,
  Radio,
  TextField,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
  Grid,
  Paper,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Send as SubmitIcon,
  CheckCircle as CorrectIcon,
  Cancel as WrongIcon,
  Info as InfoIcon,
  TrendingUp as DifficultyIcon,
  Psychology as ThinkingIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import {
  getNextQuestion,
  submitAnswer,
  completeAssessment,
  getAttemptStatus,
  formatTheta,
  thetaToPercentile,
  calculateAdaptiveProgress
} from '../../services/assessmentService';

const AdaptiveTestInterface = ({
  attemptId,
  onComplete,
  onExit
}) => {
  // State management
  const [loading, setLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [openAnswer, setOpenAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [attemptStatus, setAttemptStatus] = useState(null);
  const [questionHistory, setQuestionHistory] = useState([]);
  const [error, setError] = useState(null);

  // Load initial question and status
  useEffect(() => {
    loadNextQuestion();
    loadAttemptStatus();
  }, [attemptId]);

  const loadNextQuestion = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getNextQuestion(attemptId);
      
      if (response.success) {
        setCurrentQuestion(response.question);
        setSelectedAnswer('');
        setOpenAnswer('');
        setShowFeedback(false);
        setFeedback(null);
      } else if (response.message === 'Assessment complete') {
        // Assessment finished
        handleComplete();
      }
    } catch (err) {
      setError(err.message || 'Failed to load question');
    } finally {
      setLoading(false);
    }
  };

  const loadAttemptStatus = async () => {
    try {
      const response = await getAttemptStatus(attemptId);
      if (response.success) {
        setAttemptStatus(response.status);
      }
    } catch (err) {
      console.error('Failed to load attempt status:', err);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!currentQuestion) return;

    const answerValue = currentQuestion.question_type === 'multiple_choice'
      ? selectedAnswer
      : openAnswer;

    if (!answerValue.trim()) {
      setError('Please provide an answer');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const response = await submitAnswer(attemptId, {
        question_id: currentQuestion.id,
        answer: answerValue,
        time_spent: 0 // TODO: Track actual time
      });

      if (response.success) {
        // Show feedback
        setFeedback(response);
        setShowFeedback(true);

        // Update question history
        setQuestionHistory(prev => [...prev, {
          question: currentQuestion,
          answer: answerValue,
          correct: response.is_correct,
          feedback: response.feedback
        }]);

        // Reload status to update theta
        await loadAttemptStatus();
      }
    } catch (err) {
      setError(err.message || 'Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNextQuestion = () => {
    setShowFeedback(false);
    loadNextQuestion();
  };

  const handleComplete = async () => {
    try {
      const response = await completeAssessment(attemptId);
      if (response.success) {
        onComplete(response.results);
      }
    } catch (err) {
      setError(err.message || 'Failed to complete assessment');
    }
  };

  const handleExitConfirm = () => {
    if (window.confirm('Are you sure you want to exit? Your progress will be saved.')) {
      onExit();
    }
  };

  // Calculate progress
  const progress = attemptStatus
    ? calculateAdaptiveProgress(attemptStatus.current_theta_se)
    : 0;

  const questionsAnswered = questionHistory.length;

  if (loading && !currentQuestion) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', p: 3 }}>
      {/* Header with Progress */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" fontWeight="bold">
            Adaptive Assessment
          </Typography>
          
          <Button variant="outlined" color="error" onClick={handleExitConfirm}>
            Exit & Save
          </Button>
        </Box>

        {/* Progress Bar */}
        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Assessment Progress
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {progress.toFixed(0)}% Complete
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ height: 8, borderRadius: 1 }}
          />
        </Box>

        {/* Status Metrics */}
        {attemptStatus && (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="primary.main">
                  {questionsAnswered}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Questions Answered
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Tooltip title={`Theta: ${formatTheta(attemptStatus.current_theta)}`}>
                  <Typography variant="h6" color="success.main">
                    {thetaToPercentile(attemptStatus.current_theta).toFixed(0)}%
                  </Typography>
                </Tooltip>
                <Typography variant="caption" color="text.secondary">
                  Current Performance
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="info.main">
                  {(attemptStatus.current_theta_se * 100).toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Measurement Error
                </Typography>
              </Box>
            </Grid>
          </Grid>
        )}
      </Paper>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Question Card */}
      {currentQuestion && (
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestion.id}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <Card elevation={3}>
              <CardContent sx={{ p: 4 }}>
                {/* Question Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                  <Chip
                    label={`Question ${questionsAnswered + 1}`}
                    color="primary"
                    sx={{ fontWeight: 'bold' }}
                  />
                  
                  {currentQuestion.irt_difficulty && (
                    <Tooltip title={`Difficulty: ${currentQuestion.irt_difficulty.toFixed(2)}`}>
                      <Chip
                        icon={<DifficultyIcon />}
                        label={getDifficultyLabel(currentQuestion.irt_difficulty)}
                        size="small"
                        color={getDifficultyColor(currentQuestion.irt_difficulty)}
                      />
                    </Tooltip>
                  )}
                </Box>

                {/* Question Text */}
                <Typography variant="h6" gutterBottom fontWeight="medium" sx={{ mb: 3 }}>
                  {currentQuestion.question_text}
                </Typography>

                {/* Answer Input */}
                {currentQuestion.question_type === 'multiple_choice' ? (
                  <RadioGroup
                    value={selectedAnswer}
                    onChange={(e) => setSelectedAnswer(e.target.value)}
                  >
                    {currentQuestion.options && currentQuestion.options.map((option, index) => (
                      <FormControlLabel
                        key={index}
                        value={option}
                        control={<Radio />}
                        label={option}
                        disabled={showFeedback}
                        sx={{
                          mb: 1,
                          p: 1.5,
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1,
                          '&:hover': {
                            bgcolor: 'action.hover'
                          }
                        }}
                      />
                    ))}
                  </RadioGroup>
                ) : (
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    placeholder="Enter your answer here..."
                    value={openAnswer}
                    onChange={(e) => setOpenAnswer(e.target.value)}
                    disabled={showFeedback}
                    variant="outlined"
                  />
                )}

                {/* Submit Button */}
                {!showFeedback && (
                  <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={submitting ? <CircularProgress size={20} /> : <SubmitIcon />}
                      onClick={handleSubmitAnswer}
                      disabled={submitting || (!selectedAnswer && !openAnswer)}
                    >
                      {submitting ? 'Submitting...' : 'Submit Answer'}
                    </Button>
                  </Box>
                )}

                {/* Feedback Section */}
                {showFeedback && feedback && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    <Paper
                      elevation={0}
                      sx={{
                        mt: 3,
                        p: 3,
                        bgcolor: feedback.is_correct ? 'success.50' : 'error.50',
                        border: '2px solid',
                        borderColor: feedback.is_correct ? 'success.main' : 'error.main'
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        {feedback.is_correct ? (
                          <CorrectIcon sx={{ color: 'success.main', fontSize: 32, mr: 1 }} />
                        ) : (
                          <WrongIcon sx={{ color: 'error.main', fontSize: 32, mr: 1 }} />
                        )}
                        <Typography variant="h6" fontWeight="bold">
                          {feedback.is_correct ? 'Correct!' : 'Incorrect'}
                        </Typography>
                      </Box>

                      {feedback.feedback && (
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {feedback.feedback}
                        </Typography>
                      )}

                      {!feedback.is_correct && currentQuestion.correct_answer && (
                        <Alert severity="info" sx={{ mb: 2 }}>
                          <strong>Correct Answer:</strong> {currentQuestion.correct_answer}
                        </Alert>
                      )}

                      {currentQuestion.explanation && (
                        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                          <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                            <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                            Explanation
                          </Typography>
                          <Typography variant="body2">
                            {currentQuestion.explanation}
                          </Typography>
                        </Box>
                      )}

                      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                        <Button
                          variant="contained"
                          onClick={handleNextQuestion}
                          size="large"
                        >
                          Next Question
                        </Button>
                      </Box>
                    </Paper>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </AnimatePresence>
      )}

      {/* Question History Progress */}
      {questionHistory.length > 0 && (
        <Paper elevation={1} sx={{ mt: 3, p: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Answer History
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {questionHistory.map((item, index) => (
              <Tooltip
                key={index}
                title={item.correct ? 'Correct' : 'Incorrect'}
              >
                <Box
                  sx={{
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    bgcolor: item.correct ? 'success.main' : 'error.main',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontWeight: 'bold',
                    fontSize: '0.75rem'
                  }}
                >
                  {index + 1}
                </Box>
              </Tooltip>
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

// Helper functions
const getDifficultyLabel = (difficulty) => {
  if (difficulty < -1) return 'Easy';
  if (difficulty < 0) return 'Medium-Easy';
  if (difficulty < 1) return 'Medium';
  if (difficulty < 2) return 'Medium-Hard';
  return 'Hard';
};

const getDifficultyColor = (difficulty) => {
  if (difficulty < -1) return 'success';
  if (difficulty < 0) return 'info';
  if (difficulty < 1) return 'default';
  if (difficulty < 2) return 'warning';
  return 'error';
};

export default AdaptiveTestInterface;
