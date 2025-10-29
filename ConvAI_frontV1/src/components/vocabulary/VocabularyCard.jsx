import { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  Chip,
  Tooltip,
  LinearProgress,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  VolumeUp,
  Bookmark,
  BookmarkBorder,
  MoreVert,
  Star,
  StarBorder,
  TrendingUp,
  FlipToFront,
  Edit,
  Lightbulb,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

/**
 * VocabularyCard Component
 * Displays a vocabulary word with SM-2 mastery indicators
 */
const VocabularyCard = ({
  word,
  onFlip,
  onFavorite,
  onPractice,
  onReview,
  isFlipped = false,
  showMasteryInfo = true,
}) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const playPronunciation = () => {
    if (word.audio_url) {
      const audio = new Audio(word.audio_url);
      setIsPlayingAudio(true);
      audio.play();
      audio.onended = () => setIsPlayingAudio(false);
    } else if (word.pronunciation) {
      // Use Web Speech API if available
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(word.word);
        utterance.lang = word.language_code || 'en-US';
        window.speechSynthesis.speak(utterance);
      }
    }
  };

  const getMasteryColor = () => {
    if (!word.mastery_level) return 'default';
    const levels = {
      new: 'info',
      learning: 'warning',
      familiar: 'primary',
      mastered: 'success',
    };
    return levels[word.mastery_level] || 'default';
  };

  const getMasteryProgress = () => {
    if (!word.mastery_level) return 0;
    const progressMap = {
      new: 10,
      learning: 35,
      familiar: 70,
      mastered: 100,
    };
    return progressMap[word.mastery_level] || 0;
  };

  const formatNextReview = () => {
    if (!word.next_review) return 'Not scheduled';
    const date = new Date(word.next_review);
    const now = new Date();
    const diffMs = date - now;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffMs < 0) return 'Due now';
    if (diffHours < 1) return 'Due in < 1 hour';
    if (diffHours < 24) return `Due in ${diffHours}h`;
    return `Due in ${diffDays}d`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        sx={{
          height: '100%',
          position: 'relative',
          background: isFlipped
            ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
            : 'background.paper',
          color: isFlipped ? 'white' : 'text.primary',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: 6,
          },
        }}
        onClick={onFlip}
      >
        <CardContent>
          {/* Header Actions */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              mb: 2,
            }}
          >
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              <Chip
                label={word.difficulty || 'Intermediate'}
                size="small"
                color={getMasteryColor()}
                sx={{ fontWeight: 600 }}
              />
              {word.topic && (
                <Chip
                  label={word.topic}
                  size="small"
                  variant="outlined"
                  sx={{ opacity: isFlipped ? 0.8 : 1 }}
                />
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 0 }}>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  playPronunciation();
                }}
                sx={{ color: isFlipped ? 'white' : 'primary.main' }}
                disabled={isPlayingAudio}
              >
                <VolumeUp fontSize="small" />
              </IconButton>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  onFavorite?.();
                }}
                sx={{ color: isFlipped ? 'white' : 'text.secondary' }}
              >
                {word.is_favorite ? (
                  <Bookmark fontSize="small" />
                ) : (
                  <BookmarkBorder fontSize="small" />
                )}
              </IconButton>
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleMenuOpen(e);
                }}
                sx={{ color: isFlipped ? 'white' : 'text.secondary' }}
              >
                <MoreVert fontSize="small" />
              </IconButton>
            </Box>
          </Box>

          {!isFlipped ? (
            // Front Side - Word
            <>
              <Box sx={{ textAlign: 'center', py: 3 }}>
                <Typography
                  variant="h3"
                  sx={{
                    fontWeight: 700,
                    mb: 1,
                    wordBreak: 'break-word',
                  }}
                >
                  {word.word}
                </Typography>
                {word.pronunciation && (
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ fontStyle: 'italic' }}
                  >
                    /{word.pronunciation}/
                  </Typography>
                )}
                {word.part_of_speech && (
                  <Typography
                    variant="caption"
                    sx={{
                      mt: 1,
                      display: 'block',
                      color: 'text.secondary',
                      textTransform: 'uppercase',
                      letterSpacing: 1,
                    }}
                  >
                    {word.part_of_speech}
                  </Typography>
                )}
              </Box>

              {showMasteryInfo && word.mastery_level && (
                <Box sx={{ mt: 3 }}>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      mb: 1,
                    }}
                  >
                    <Typography variant="caption" color="text.secondary">
                      Mastery: {word.mastery_level}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {getMasteryProgress()}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={getMasteryProgress()}
                    color={getMasteryColor()}
                    sx={{ height: 6, borderRadius: 1 }}
                  />
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      mt: 1,
                    }}
                  >
                    <Tooltip title="Confidence Score">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <TrendingUp fontSize="small" color="action" />
                        <Typography variant="caption">
                          {Math.round((word.confidence_score || 0) * 100)}%
                        </Typography>
                      </Box>
                    </Tooltip>
                    <Tooltip title="Next Review">
                      <Typography variant="caption" color="text.secondary">
                        {formatNextReview()}
                      </Typography>
                    </Tooltip>
                  </Box>
                </Box>
              )}
            </>
          ) : (
            // Back Side - Definition & Examples
            <>
              <Box sx={{ py: 2 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Definition
                </Typography>
                <Typography variant="body1" sx={{ mb: 3, lineHeight: 1.7 }}>
                  {word.definition || 'No definition available'}
                </Typography>

                {word.translation && (
                  <>
                    <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                      Translation
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 3 }}>
                      {word.translation}
                    </Typography>
                  </>
                )}

                {word.example_sentences && word.example_sentences.length > 0 && (
                  <>
                    <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                      Example
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontStyle: 'italic',
                        pl: 2,
                        borderLeft: '3px solid rgba(255,255,255,0.3)',
                      }}
                    >
                      {word.example_sentences[0]}
                    </Typography>
                  </>
                )}

                {word.collocations && word.collocations.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                      Common Collocations:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {word.collocations.slice(0, 3).map((collocation, idx) => (
                        <Chip
                          key={idx}
                          label={collocation}
                          size="small"
                          sx={{
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            color: 'white',
                          }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>

              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  mt: 2,
                  opacity: 0.8,
                }}
              >
                <FlipToFront fontSize="small" />
                <Typography variant="caption">Click to flip back</Typography>
              </Box>
            </>
          )}
        </CardContent>

        {/* Action Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          onClick={(e) => e.stopPropagation()}
        >
          <MenuItem
            onClick={() => {
              onPractice?.();
              handleMenuClose();
            }}
          >
            <Lightbulb fontSize="small" sx={{ mr: 1 }} />
            Practice
          </MenuItem>
          <MenuItem
            onClick={() => {
              onReview?.();
              handleMenuClose();
            }}
          >
            <Star fontSize="small" sx={{ mr: 1 }} />
            Review Now
          </MenuItem>
          <MenuItem
            onClick={() => {
              handleMenuClose();
              // Open word detail modal
            }}
          >
            <Edit fontSize="small" sx={{ mr: 1 }} />
            View Details
          </MenuItem>
        </Menu>
      </Card>
    </motion.div>
  );
};

export default VocabularyCard;
