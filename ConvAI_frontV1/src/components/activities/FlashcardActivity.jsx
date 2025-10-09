import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Alert,
  Paper,
  IconButton,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Grid
} from '@mui/material';
import {
  ThumbUp as ThumbUpIcon,
  School as SchoolIcon,
  NavigateBefore as PrevIcon,
  NavigateNext as NextIcon,
  CheckCircle as CheckIcon,
  Timer as TimerIcon,
  Star as StarIcon,
  VolumeUp as SpeakIcon
} from '@mui/icons-material';
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../config/api';
import { API_ENDPOINTS } from '../config/api';

const FlashcardActivity = ({ topic, level, onComplete }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [flashcardData, setFlashcardData] = useState(null);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [cardResponses, setCardResponses] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [startTime, setStartTime] = useState(null);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [error, setError] = useState('');

  // Motion values for swipe gestures
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-25, 25]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0.5, 1, 1, 1, 0.5]);

  useEffect(() => {
    loadFlashcards();
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

  const loadFlashcards = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.GENERATE_FLASHCARDS, {
        topic: topic || 'food',
        level: level || 'beginner',
        num_cards: 10
      });

      if (response.data.success) {
        setFlashcardData(response.data.data);
      } else {
        setError('Failed to load flashcards. Please try again.');
      }
    } catch (err) {
      console.error('Error loading flashcards:', err);
      setError(err.response?.data?.error || 'Failed to load flashcards.');
    } finally {
      setLoading(false);
    }
  };

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleMarkAsKnown = () => {
    const currentCard = flashcardData.flashcards[currentCardIndex];
    setCardResponses([
      ...cardResponses,
      {
        card_id: currentCard.id,
        marked_as_known: true,
        reviewed_at: new Date().toISOString()
      }
    ]);
    moveToNextCard();
  };

  const handleMarkAsPractice = () => {
    const currentCard = flashcardData.flashcards[currentCardIndex];
    setCardResponses([
      ...cardResponses,
      {
        card_id: currentCard.id,
        marked_as_known: false,
        reviewed_at: new Date().toISOString()
      }
    ]);
    moveToNextCard();
  };

  const moveToNextCard = () => {
    setIsFlipped(false);
    x.set(0); // Reset swipe position

    if (currentCardIndex < flashcardData.flashcards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1);
    } else {
      handleSubmitSession();
    }
  };

  const handlePreviousCard = () => {
    if (currentCardIndex > 0) {
      setIsFlipped(false);
      setCurrentCardIndex(currentCardIndex - 1);
      // Remove last response
      setCardResponses(cardResponses.slice(0, -1));
    }
  };

  const handleSubmitSession = async () => {
    try {
      setLoading(true);
      const timeSpentMinutes = Math.ceil(timeElapsed / 60);

      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.SUBMIT, {
        session_id: flashcardData.session_id,
        activity_type: 'flashcard',
        activity_data: flashcardData,
        user_answers: {
          responses: cardResponses,
          time_spent_minutes: timeSpentMinutes
        },
        time_spent_minutes: timeSpentMinutes
      });

      if (response.data.success) {
        setEvaluation(response.data.evaluation);
        setShowResults(true);
      } else {
        setError('Failed to submit flashcard session.');
      }
    } catch (err) {
      console.error('Error submitting flashcards:', err);
      setError(err.response?.data?.error || 'Failed to submit session.');
    } finally {
      setLoading(false);
    }
  };

  const handleRetake = () => {
    setCardResponses([]);
    setCurrentCardIndex(0);
    setShowResults(false);
    setEvaluation(null);
    setTimeElapsed(0);
    setIsFlipped(false);
    loadFlashcards();
    setStartTime(Date.now());
  };

  const handleFinish = () => {
    if (onComplete) {
      onComplete(evaluation);
    } else {
      navigate('/dashboard');
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.9;
      speechSynthesis.speak(utterance);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle swipe gestures
  const handleDragEnd = (event, info) => {
    if (info.offset.x > 100) {
      // Swipe right - Mark as Known
      handleMarkAsKnown();
    } else if (info.offset.x < -100) {
      // Swipe left - Mark as Practice
      handleMarkAsPractice();
    } else {
      // Return to center
      x.set(0);
    }
  };

  if (loading && !flashcardData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ ml: 2 }}>
          Loading Flashcards...
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
        <Button variant="contained" onClick={loadFlashcards} sx={{ mt: 2 }}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!flashcardData) {
    return (
      <Box p={3}>
        <Alert severity="info">No flashcard data available.</Alert>
      </Box>
    );
  }

  const currentCard = flashcardData.flashcards[currentCardIndex];
  const progress = ((currentCardIndex + 1) / flashcardData.total_cards) * 100;
  const cardsReviewed = cardResponses.length;

  // Results Dialog
  if (showResults && evaluation) {
    return (
      <Dialog
        open={showResults}
        maxWidth="sm"
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
              <CheckIcon sx={{ fontSize: 80, color: 'success.main' }} />
            </motion.div>
            <Typography variant="h4" fontWeight="bold" mt={2}>
              Session Complete!
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {flashcardData.title}
            </Typography>
          </Box>
        </DialogTitle>

        <DialogContent>
          <Paper elevation={3} sx={{ p: 3, mb: 2, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <Grid container spacing={2} textAlign="center">
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  {evaluation.total_cards}
                </Typography>
                <Typography variant="body2">Cards</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  {evaluation.cards_known}
                </Typography>
                <Typography variant="body2">Known</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography variant="h3" fontWeight="bold">
                  +{evaluation.points_earned}
                </Typography>
                <Typography variant="body2">Points</Typography>
              </Grid>
            </Grid>
          </Paper>

          <Alert severity="success" sx={{ mb: 2 }}>
            <Typography variant="body1" fontWeight="bold">
              {evaluation.feedback_message}
            </Typography>
            <Typography variant="body2">
              {evaluation.feedback_message_telugu}
            </Typography>
          </Alert>

          <Stack spacing={1}>
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Cards to Practice:
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {evaluation.cards_to_practice}
              </Typography>
            </Box>
            <Box display="flex" justifyContent="space-between">
              <Typography variant="body2" color="text.secondary">
                Time Spent:
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {evaluation.time_spent_minutes} minutes
              </Typography>
            </Box>
          </Stack>
        </DialogContent>

        <DialogActions sx={{ p: 3, justifyContent: 'space-between' }}>
          <Button variant="outlined" onClick={handleRetake} size="large">
            Practice Again
          </Button>
          <Button variant="contained" onClick={handleFinish} size="large">
            Finish
          </Button>
        </DialogActions>
      </Dialog>
    );
  }

  // Flashcard Interface
  return (
    <Box sx={{ maxWidth: 700, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          {flashcardData.title}
        </Typography>
        <Typography variant="body2">
          {flashcardData.title_telugu}
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
              label={`${flashcardData.total_cards} Cards`}
              sx={{ backgroundColor: 'rgba(255,255,255,0.2)', color: 'white' }}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Progress */}
      <Box mb={3}>
        <Box display="flex" justifyContent="space-between" mb={1}>
          <Typography variant="body2" color="text.secondary">
            Card {currentCardIndex + 1} of {flashcardData.total_cards}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {cardsReviewed} reviewed
          </Typography>
        </Box>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
      </Box>

      {/* Flashcard */}
      <Box sx={{ perspective: '1000px', mb: 3, minHeight: '400px' }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={currentCardIndex}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            style={{ x, rotate, opacity }}
            onDragEnd={handleDragEnd}
            whileTap={{ cursor: 'grabbing' }}
          >
            <motion.div
              animate={{ rotateY: isFlipped ? 180 : 0 }}
              transition={{ duration: 0.6 }}
              style={{ transformStyle: 'preserve-3d' }}
              onClick={handleFlip}
            >
              <Card
                elevation={8}
                sx={{
                  minHeight: '400px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  backfaceVisibility: 'hidden',
                  background: isFlipped
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                  position: 'relative'
                }}
              >
                <CardContent sx={{ textAlign: 'center', width: '100%', p: 4 }}>
                  {!isFlipped ? (
                    // Front Side - English
                    <Box>
                      <Typography variant="h3" fontWeight="bold" color="text.primary" mb={2}>
                        {currentCard.front}
                      </Typography>
                      <IconButton
                        onClick={(e) => {
                          e.stopPropagation();
                          speakText(currentCard.front);
                        }}
                        sx={{ mt: 2 }}
                      >
                        <SpeakIcon fontSize="large" />
                      </IconButton>
                      <Typography variant="body2" color="text.secondary" mt={3}>
                        Tap to see Telugu translation
                      </Typography>
                    </Box>
                  ) : (
                    // Back Side - Telugu
                    <Box sx={{ transform: 'rotateY(180deg)' }}>
                      <Typography variant="h3" fontWeight="bold" color="white" mb={3}>
                        {currentCard.back}
                      </Typography>
                      {currentCard.example_sentence && (
                        <>
                          <Typography variant="body1" color="rgba(255,255,255,0.9)" mt={3}>
                            Example: {currentCard.example_sentence}
                          </Typography>
                          <Typography variant="body2" color="rgba(255,255,255,0.8)" mt={1}>
                            {currentCard.example_telugu}
                          </Typography>
                        </>
                      )}
                      {currentCard.pronunciation && (
                        <Typography variant="body2" color="rgba(255,255,255,0.7)" mt={2}>
                          Pronunciation: {currentCard.pronunciation}
                        </Typography>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </AnimatePresence>
      </Box>

      {/* Swipe Hint */}
      <Alert severity="info" icon={false} sx={{ mb: 2 }}>
        <Box display="flex" justifyContent="space-around" alignItems="center">
          <Box textAlign="center">
            <Typography variant="caption">← Swipe Left</Typography>
            <Typography variant="body2" fontWeight="bold">Need Practice</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">OR</Typography>
          <Box textAlign="center">
            <Typography variant="caption">Swipe Right →</Typography>
            <Typography variant="body2" fontWeight="bold">Already Know</Typography>
          </Box>
        </Box>
      </Alert>

      {/* Action Buttons */}
      <Grid container spacing={2}>
        <Grid item xs={4}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<PrevIcon />}
            onClick={handlePreviousCard}
            disabled={currentCardIndex === 0}
          >
            Previous
          </Button>
        </Grid>
        <Grid item xs={4}>
          <Button
            fullWidth
            variant="contained"
            color="warning"
            startIcon={<SchoolIcon />}
            onClick={handleMarkAsPractice}
          >
            Practice
          </Button>
        </Grid>
        <Grid item xs={4}>
          <Button
            fullWidth
            variant="contained"
            color="success"
            startIcon={<ThumbUpIcon />}
            onClick={handleMarkAsKnown}
          >
            Known
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FlashcardActivity;
