import { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  Alert,
  Paper,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Grid
} from '@mui/material';
import {
  Create as WriteIcon,
  CheckCircle as CheckIcon,
  Cancel as ErrorIcon,
  EmojiEvents as TrophyIcon,
  Timer as TimerIcon,
  Star as StarIcon,
  Lightbulb as TipIcon,
  TrendingUp as ImprovementIcon,
  ThumbUp as StrengthIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../config/api';
import { API_ENDPOINTS } from '../config/api';

const WritingActivity = ({ topic, level, onComplete }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [promptData, setPromptData] = useState(null);
  const [userText, setUserText] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadPrompt = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.GENERATE_WRITING_PROMPT, {
        topic: topic || 'family',
        level: level || 'beginner'
      });

      if (response.data.success) {
        setPromptData({
          ...response.data.prompt_data,
          session_id: response.data.session_id
        });
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load writing prompt');
      console.error('Error loading prompt:', err);
    } finally {
      setLoading(false);
    }
  }, [topic, level]);

  useEffect(() => {
    loadPrompt();
    setStartTime(Date.now());
  }, [loadPrompt]);

  // Track time elapsed
  useEffect(() => {
    if (startTime && !showFeedback) {
      const timer = setInterval(() => {
        setTimeElapsed(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [startTime, showFeedback]);

  const handleTextChange = (event) => {
    setUserText(event.target.value);
  };

  const handleSubmit = async () => {
    // Validate minimum length
    const sentences = userText.split(/[.!?]+/).filter(s => s.trim().length > 0);
    const minRequired = promptData?.min_sentences || 5;

    if (sentences.length < minRequired) {
      setError(`Please write at least ${minRequired} sentences. You have written ${sentences.length}.`);
      return;
    }

    if (userText.trim().length < 50) {
      setError('Please write more content. Your writing seems too short.');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      const timeSpentMinutes = Math.ceil(timeElapsed / 60);

      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.SUBMIT, {
        session_id: promptData.session_id,
        activity_type: 'writing',
        activity_data: promptData,
        user_answers: {
          user_text: userText
        },
        time_spent_minutes: timeSpentMinutes
      });

      if (response.data.success) {
        setFeedback(response.data.evaluation);
        setShowFeedback(true);
      } else {
        setError('Failed to get feedback. Please try again.');
      }
    } catch (err) {
      console.error('Error submitting writing:', err);
      setError(err.response?.data?.error || 'Failed to submit writing.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetry = () => {
    setUserText('');
    setShowFeedback(false);
    setFeedback(null);
    setTimeElapsed(0);
    loadPrompt();
    setStartTime(Date.now());
  };

  const handleFinish = () => {
    if (onComplete) {
      onComplete(feedback);
    } else {
      navigate('/dashboard');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const countWords = () => {
    return userText.trim().split(/\s+/).filter(w => w.length > 0).length;
  };

  const countSentences = () => {
    return userText.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Writing Prompt...
        </Typography>
      </Box>
    );
  }

  if (error && !promptData) {
    return (
      <Box p={3}>
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
        <Button variant="contained" onClick={loadPrompt} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!promptData) {
    return (
      <Box p={3}>
        <Alert severity="info">No prompt data available.</Alert>
      </Box>
    );
  }

  const wordCount = countWords();
  const sentenceCount = countSentences();
  const minRequired = promptData.min_sentences || 5;
  const meetsRequirement = sentenceCount >= minRequired;

  // Feedback Dialog
  if (showFeedback && feedback) {
    return (
      <Dialog
        open={showFeedback}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, p: 2 }
        }}
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="center" flexDirection="column">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", duration: 0.5 }}
            >
              <TrophyIcon sx={{ fontSize: 80, color: 'gold' }} />
            </motion.div>
            <Typography variant="h4" fontWeight="bold" mt={2}>
              Writing Complete!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {promptData.topic.charAt(0).toUpperCase() + promptData.topic.slice(1)} - {promptData.level}
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent>
          {/* Score Summary */}
          <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <Grid container spacing={2} textAlign="center">
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  {feedback.overall_score || 0}
                </Typography>
                <Typography variant="body2">Overall Score</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  {feedback.grammar_score || 0}
                </Typography>
                <Typography variant="body2">Grammar</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  +{feedback.points_earned || 0}
                </Typography>
                <Typography variant="body2">Points</Typography>
              </Grid>
            </Grid>
          </Paper>

          {/* Encouragement */}
          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography variant="body1" fontWeight="bold">
              {feedback.encouragement}
            </Typography>
            <Typography variant="body2">
              {feedback.encouragement_telugu}
            </Typography>
          </Alert>

          {/* Corrected Text */}
          {feedback.corrected_text && (
            <Paper sx={{ p: 2, mb: 3, backgroundColor: '#f5f5f5' }}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom color="primary">
                ✓ Corrected Version:
              </Typography>
              <Typography variant="body1" sx={{ fontStyle: 'italic', lineHeight: 1.8 }}>
                {feedback.corrected_text}
              </Typography>
            </Paper>
          )}

          {/* Errors & Corrections */}
          {feedback.errors && feedback.errors.length > 0 && (
            <Box mb={3}>
              <Typography variant="h6" fontWeight="bold" gutterBottom color="error">
                Corrections Needed:
              </Typography>
              <List>
                {feedback.errors.map((error, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <ListItem
                      sx={{
                        border: '1px solid #ffcdd2',
                        borderRadius: 2,
                        mb: 1,
                        backgroundColor: '#ffebee'
                      }}
                    >
                      <ListItemIcon>
                        <ErrorIcon color="error" />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box>
                            <Typography variant="body2" component="span" sx={{ textDecoration: 'line-through', color: 'error.main' }}>
                              {error.original_phrase}
                            </Typography>
                            {' → '}
                            <Typography variant="body2" component="span" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                              {error.correction}
                            </Typography>
                            <Chip label={error.error_type} size="small" sx={{ ml: 1 }} />
                          </Box>
                        }
                        secondary={
                          <>
                            <Typography variant="body2" color="text.primary">
                              {error.explanation}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                              {error.explanation_telugu}
                            </Typography>
                          </>
                        }
                      />
                    </ListItem>
                  </motion.div>
                ))}
              </List>
            </Box>
          )}

          {/* Strengths */}
          {feedback.strengths && feedback.strengths.length > 0 && (
            <Box mb={2}>
              <Typography variant="h6" fontWeight="bold" gutterBottom color="success.main">
                <StrengthIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                What You Did Well:
              </Typography>
              <List dense>
                {feedback.strengths.map((strength, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckIcon color="success" />
                    </ListItemIcon>
                    <ListItemText primary={strength} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}

          {/* Improvements */}
          {feedback.improvements && feedback.improvements.length > 0 && (
            <Box>
              <Typography variant="h6" fontWeight="bold" gutterBottom color="warning.main">
                <ImprovementIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Areas to Improve:
              </Typography>
              <List dense>
                {feedback.improvements.map((improvement, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <TipIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText primary={improvement} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 3, justifyContent: 'space-between' }}>
          <Button variant="outlined" onClick={handleRetry} size="large">
            Write Again
          </Button>
          <Button variant="contained" onClick={handleFinish} size="large">
            Finish
          </Button>
        </DialogActions>
      </Dialog>
    );
  }

  // Writing Interface
  return (
    <Box sx={{ maxWidth: 900, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
        <Box display="flex" alignItems="center" mb={2}>
          <WriteIcon sx={{ fontSize: 40, mr: 2 }} />
          <Box flex={1}>
            <Typography variant="h5" fontWeight="bold">
              Writing Practice
            </Typography>
            <Typography variant="body2">
              {promptData.topic.charAt(0).toUpperCase() + promptData.topic.slice(1)} - {promptData.level}
            </Typography>
          </Box>
        </Box>
        <Grid container spacing={2}>
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
              label="Up to 90 Points"
              sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Prompt Section */}
      <Card elevation={3} sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" gutterBottom color="primary">
            Your Writing Task:
          </Typography>
          <Typography variant="body1" paragraph>
            {promptData.prompt}
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            {promptData.prompt_telugu}
          </Typography>

          <Divider sx={{ my: 2 }} />

          {/* Guidelines */}
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            <TipIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'warning.main' }} />
            Guidelines:
          </Typography>
          <List dense>
            {promptData.guidelines?.map((guideline, index) => (
              <ListItem key={index}>
                <ListItemText
                  primary={guideline}
                  secondary={promptData.guidelines_telugu?.[index]}
                />
              </ListItem>
            ))}
          </List>

          {/* Example */}
          {promptData.example_sentence && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2" fontWeight="bold">
                Example:
              </Typography>
              <Typography variant="body2">
                {promptData.example_sentence}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {promptData.example_sentence_telugu}
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Writing Area */}
      <Card elevation={3} sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            Write Here:
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={12}
            value={userText}
            onChange={handleTextChange}
            placeholder="Start writing your sentences here..."
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                fontSize: '1.1rem',
                lineHeight: 1.8
              }
            }}
          />

          {/* Stats */}
          <Box display="flex" justifyContent="space-between" mt={2}>
            <Stack direction="row" spacing={2}>
              <Chip
                label={`${wordCount} words`}
                color="default"
                variant="outlined"
              />
              <Chip
                label={`${sentenceCount} / ${minRequired} sentences`}
                color={meetsRequirement ? 'success' : 'warning'}
                variant="outlined"
              />
            </Stack>
            <Typography variant="caption" color="text.secondary">
              {userText.length} characters
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert severity="warning" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Submit Button */}
      <Box display="flex" justifyContent="center">
        <Button
          variant="contained"
          size="large"
          color="primary"
          onClick={handleSubmit}
          disabled={!meetsRequirement || submitting || userText.trim().length < 50}
          startIcon={submitting ? <CircularProgress size={20} /> : <CheckIcon />}
          sx={{ minWidth: 200 }}
        >
          {submitting ? 'Getting Feedback...' : 'Get Feedback'}
        </Button>
      </Box>

      {!meetsRequirement && userText.length > 0 && (
        <Typography variant="caption" color="text.secondary" align="center" display="block" mt={1}>
          Write at least {minRequired - sentenceCount} more sentence(s) to submit
        </Typography>
      )}
    </Box>
  );
};

WritingActivity.propTypes = {
  topic: PropTypes.string,
  level: PropTypes.string,
  onComplete: PropTypes.func
};

export default WritingActivity;
