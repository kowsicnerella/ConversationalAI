import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import { CheckCircle, Cancel, Lightbulb } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { vocabularyService } from '../../services/vocabularyService';

/**
 * VocabularyPracticeActivity Component
 * Generates and displays various practice activities for vocabulary
 * Types: definition_match, fill_blank, sentence_creation, synonym_antonym, usage_context
 */
const VocabularyPracticeActivity = ({ word, onComplete, onClose }) => {
  const [activity, setActivity] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userAnswer, setUserAnswer] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [feedback, setFeedback] = useState('');
  const [activityType, setActivityType] = useState('definition_match');

  const activityTypes = [
    { value: 'definition_match', label: 'Definition Match' },
    { value: 'fill_blank', label: 'Fill in the Blank' },
    { value: 'sentence_creation', label: 'Create Sentence' },
    { value: 'synonym_antonym', label: 'Synonyms & Antonyms' },
    { value: 'usage_context', label: 'Usage Context' },
  ];

  const generateActivity = async (type) => {
    try {
      setLoading(true);
      setSubmitted(false);
      setUserAnswer('');
      setActivityType(type);

      const response = await vocabularyService.generatePracticeActivity(word.word_id || word.id, type);
      setActivity(response.activity);
    } catch (error) {
      console.error('Error generating activity:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = () => {
    if (!activity) return;

    setSubmitted(true);

    // Simple validation logic
    if (activity.activity_type === 'definition_match') {
      const correct = userAnswer.toLowerCase() === activity.correct_answer?.toLowerCase();
      setIsCorrect(correct);
      setFeedback(
        correct
          ? '✓ Correct! Well done!'
          : `✗ Not quite. The correct answer is: ${activity.correct_answer}`
      );
    } else if (activity.activity_type === 'fill_blank') {
      const correct = userAnswer.toLowerCase().trim() === word.word.toLowerCase();
      setIsCorrect(correct);
      setFeedback(correct ? '✓ Perfect!' : `✗ The word is: ${word.word}`);
    } else if (activity.activity_type === 'sentence_creation') {
      // For sentence creation, we accept any non-empty answer
      const hasWord = userAnswer.toLowerCase().includes(word.word.toLowerCase());
      setIsCorrect(hasWord && userAnswer.length > 10);
      setFeedback(
        hasWord && userAnswer.length > 10
          ? '✓ Great sentence! You used the word correctly.'
          : `✗ Try to create a longer sentence using "${word.word}"`
      );
    } else {
      // For other types, check if answer matches any correct option
      const correct =
        activity.correct_answer?.toLowerCase() === userAnswer.toLowerCase() ||
        activity.options?.some((opt) => opt.toLowerCase() === userAnswer.toLowerCase() && opt.is_correct);
      setIsCorrect(correct);
      setFeedback(correct ? '✓ Correct!' : `✗ Try again. ${activity.explanation || ''}`);
    }
  };

  const handleComplete = () => {
    onComplete?.({
      word_id: word.word_id || word.id,
      activity_type: activityType,
      is_correct: isCorrect,
      user_answer: userAnswer,
    });
  };

  const renderActivityContent = () => {
    if (!activity) {
      return (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Select a practice type to begin
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 2 }}>
            {activityTypes.map((type) => (
              <Button
                key={type.value}
                variant="outlined"
                onClick={() => generateActivity(type.value)}
                sx={{ minWidth: 160 }}
              >
                {type.label}
              </Button>
            ))}
          </Box>
        </Box>
      );
    }

    if (activity.activity_type === 'definition_match') {
      return (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>
            {activity.question || 'Match the word to its definition'}
          </Typography>
          <FormControl component="fieldset" fullWidth>
            <RadioGroup value={userAnswer} onChange={(e) => setUserAnswer(e.target.value)}>
              {activity.options?.map((option, idx) => (
                <FormControlLabel
                  key={idx}
                  value={option}
                  control={<Radio />}
                  label={option}
                  disabled={submitted}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    p: 1,
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                />
              ))}
            </RadioGroup>
          </FormControl>
        </Box>
      );
    }

    if (activity.activity_type === 'fill_blank') {
      return (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Fill in the Blank
          </Typography>
          <Typography variant="body1" sx={{ mb: 3, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
            {activity.sentence || activity.question}
          </Typography>
          <TextField
            fullWidth
            label="Your answer"
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            disabled={submitted}
            placeholder="Type the missing word..."
            variant="outlined"
          />
          {activity.hint && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 2 }}>
              <Lightbulb color="primary" fontSize="small" />
              <Typography variant="caption" color="text.secondary">
                Hint: {activity.hint}
              </Typography>
            </Box>
          )}
        </Box>
      );
    }

    if (activity.activity_type === 'sentence_creation') {
      return (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Create a Sentence
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            Write a sentence using the word <strong>{word.word}</strong>
          </Alert>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Your sentence"
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            disabled={submitted}
            placeholder={`Write a creative sentence using "${word.word}"...`}
            variant="outlined"
          />
        </Box>
      );
    }

    // Default render for other activity types
    return (
      <Box>
        <Typography variant="h6" sx={{ mb: 2 }}>
          {activity.question || 'Answer the question'}
        </Typography>
        {activity.options ? (
          <FormControl component="fieldset" fullWidth>
            <RadioGroup value={userAnswer} onChange={(e) => setUserAnswer(e.target.value)}>
              {activity.options.map((option, idx) => (
                <FormControlLabel
                  key={idx}
                  value={option}
                  control={<Radio />}
                  label={option}
                  disabled={submitted}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    p: 1,
                  }}
                />
              ))}
            </RadioGroup>
          </FormControl>
        ) : (
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Your answer"
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            disabled={submitted}
            variant="outlined"
          />
        )}
      </Box>
    );
  };

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Practice: {word.word}
              </Typography>
              {activity && (
                <Chip
                  label={activityTypes.find((t) => t.value === activityType)?.label}
                  size="small"
                  color="primary"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
              <CircularProgress />
            </Box>
          ) : (
            <motion.div
              key={activityType}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {renderActivityContent()}
            </motion.div>
          )}

          {/* Feedback */}
          {submitted && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
            >
              <Alert
                severity={isCorrect ? 'success' : 'error'}
                icon={isCorrect ? <CheckCircle /> : <Cancel />}
                sx={{ mt: 3 }}
              >
                {feedback}
              </Alert>
            </motion.div>
          )}

          {/* Actions */}
          <Box sx={{ display: 'flex', gap: 2, mt: 3, justifyContent: 'flex-end' }}>
            {!submitted && activity && (
              <Button
                variant="contained"
                onClick={handleSubmit}
                disabled={!userAnswer.trim()}
                size="large"
              >
                Submit Answer
              </Button>
            )}
            {submitted && (
              <>
                <Button variant="outlined" onClick={() => generateActivity(activityType)}>
                  Try Another
                </Button>
                <Button variant="contained" onClick={handleComplete}>
                  {isCorrect ? 'Continue' : 'Got It'}
                </Button>
              </>
            )}
            {!activity && (
              <Button variant="outlined" onClick={onClose}>
                Cancel
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default VocabularyPracticeActivity;
