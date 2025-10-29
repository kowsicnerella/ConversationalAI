import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  ButtonGroup,
  LinearProgress,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  VolumeUp,
  ArrowForward,
  CheckCircle,
  Cancel,
  Info,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { vocabularyService } from '../../services/vocabularyService';

/**
 * SpacedRepetitionReview Component
 * Implements SM-2 spaced repetition review interface
 * Quality ratings: 0-5 (0=blackout, 5=perfect recall)
 */
const SpacedRepetitionReview = ({ onComplete, onClose }) => {
  const [words, setWords] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    loadWordsDue();
  }, []);

  const loadWordsDue = async () => {
    try {
      setLoading(true);
      const response = await vocabularyService.getWordsDue(20);
      setWords(response.words || []);
    } catch (error) {
      console.error('Error loading words:', error);
    } finally {
      setLoading(false);
    }
  };

  const currentWord = words[currentIndex];
  const progress = words.length > 0 ? ((currentIndex + 1) / words.length) * 100 : 0;

  const handleQualityRating = async (quality) => {
    if (!currentWord) return;

    setSubmitting(true);
    try {
      const response = await vocabularyService.submitReview({
        word_id: currentWord.word_id,
        quality_rating: quality,
        response_time_seconds: 30, // Could track actual time
        context: 'spaced_repetition_review',
      });

      // Store result
      setResults([...results, { word: currentWord, quality, ...response }]);

      // Move to next word
      if (currentIndex < words.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setIsFlipped(false);
      } else {
        // All words reviewed
        setShowResults(true);
      }
    } catch (error) {
      console.error('Error submitting review:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const playAudio = () => {
    if (currentWord?.audio_url) {
      const audio = new Audio(currentWord.audio_url);
      audio.play();
    } else if ('speechSynthesis' in window && currentWord?.word) {
      const utterance = new SpeechSynthesisUtterance(currentWord.word);
      utterance.lang = 'en-US';
      window.speechSynthesis.speak(utterance);
    }
  };

  const getQualityLabel = (quality) => {
    const labels = {
      0: 'Complete Blackout',
      1: 'Incorrect, but familiar',
      2: 'Incorrect, but remembered',
      3: 'Correct with difficulty',
      4: 'Correct with hesitation',
      5: 'Perfect recall',
    };
    return labels[quality] || '';
  };

  const getQualityColor = (quality) => {
    if (quality < 3) return 'error';
    if (quality === 3) return 'warning';
    if (quality === 4) return 'info';
    return 'success';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (words.length === 0) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            All Caught Up!
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            You have no words due for review right now. Great job!
          </Typography>
          <Button variant="contained" onClick={onClose}>
            Back to Vocabulary
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (showResults) {
    const avgQuality = results.reduce((sum, r) => sum + r.quality, 0) / results.length;
    const masteredCount = results.filter((r) => r.quality >= 4).length;

    return (
      <Card>
        <CardContent>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
            <Typography variant="h4" gutterBottom>
              Review Complete!
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              You've reviewed {results.length} words
            </Typography>

            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, mb: 4 }}>
              <Box>
                <Typography variant="h3" color="success.main">
                  {masteredCount}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Well Recalled
                </Typography>
              </Box>
              <Box>
                <Typography variant="h3" color="warning.main">
                  {results.length - masteredCount}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Need Practice
                </Typography>
              </Box>
              <Box>
                <Typography variant="h3" color="primary.main">
                  {avgQuality.toFixed(1)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Quality
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button variant="contained" onClick={() => onComplete?.(results)}>
                Continue Learning
              </Button>
              <Button variant="outlined" onClick={onClose}>
                View All Words
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Progress Bar */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Word {currentIndex + 1} of {words.length}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {Math.round(progress)}% Complete
          </Typography>
        </Box>
        <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 1 }} />
      </Box>

      {/* Info Alert */}
      <Alert severity="info" icon={<Info />} sx={{ mb: 3 }}>
        Rate how well you recalled this word. Your rating determines when you'll see it again (SM-2 algorithm).
      </Alert>

      {/* Word Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
        >
          <Card
            sx={{
              minHeight: 400,
              background: isFlipped
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'background.paper',
              color: isFlipped ? 'white' : 'text.primary',
              cursor: 'pointer',
              mb: 3,
            }}
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
                <Chip
                  label={currentWord?.mastery_level || 'Learning'}
                  color="primary"
                  size="small"
                />
                <IconButton onClick={(e) => { e.stopPropagation(); playAudio(); }} sx={{ color: isFlipped ? 'white' : 'inherit' }}>
                  <VolumeUp />
                </IconButton>
              </Box>

              {!isFlipped ? (
                // Front - Word
                <Box sx={{ textAlign: 'center', py: 6 }}>
                  <Typography variant="h2" sx={{ fontWeight: 700, mb: 2 }}>
                    {currentWord?.word}
                  </Typography>
                  {currentWord?.pronunciation && (
                    <Typography variant="h6" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                      /{currentWord.pronunciation}/
                    </Typography>
                  )}
                  <Typography variant="body1" sx={{ mt: 4, color: 'text.secondary' }}>
                    Click to reveal definition
                  </Typography>
                </Box>
              ) : (
                // Back - Definition
                <Box sx={{ py: 4 }}>
                  <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                    Definition
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.8 }}>
                    {currentWord?.definition}
                  </Typography>

                  {currentWord?.translation && (
                    <>
                      <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                        Translation
                      </Typography>
                      <Typography variant="body1" sx={{ mb: 3 }}>
                        {currentWord.translation}
                      </Typography>
                    </>
                  )}

                  {currentWord?.example_sentences?.[0] && (
                    <>
                      <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                        Example
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          fontStyle: 'italic',
                          pl: 2,
                          borderLeft: '3px solid rgba(255,255,255,0.5)',
                        }}
                      >
                        {currentWord.example_sentences[0]}
                      </Typography>
                    </>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </AnimatePresence>

      {/* Quality Rating Buttons */}
      {isFlipped && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2, textAlign: 'center' }}>
            How well did you recall this word?
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {[5, 4, 3, 2, 1, 0].map((quality) => (
              <Button
                key={quality}
                variant="outlined"
                color={getQualityColor(quality)}
                onClick={() => handleQualityRating(quality)}
                disabled={submitting}
                sx={{
                  justifyContent: 'space-between',
                  py: 1.5,
                  textAlign: 'left',
                  '&:hover': {
                    transform: 'translateX(8px)',
                  },
                  transition: 'all 0.2s',
                }}
              >
                <Box>
                  <Typography variant="body1" sx={{ fontWeight: 600 }}>
                    {quality} - {getQualityLabel(quality)}
                  </Typography>
                </Box>
                <ArrowForward />
              </Button>
            ))}
          </Box>
        </Box>
      )}

      {!isFlipped && (
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Think about the definition, then click the card to reveal it
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SpacedRepetitionReview;
