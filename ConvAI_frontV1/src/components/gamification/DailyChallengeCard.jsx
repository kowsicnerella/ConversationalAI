/**
 * DailyChallengeCard - Daily Challenge Display
 * Shows today's 3 AI-generated personalized challenges:
 * - Challenge type and description
 * - Difficulty level
 * - Progress tracking
 * - Points reward
 * - Streak bonus
 * - Completion status
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Button,
  Grid,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  RadioButtonUnchecked as UncheckedIcon,
  Star as StarIcon,
  Whatshot as FireIcon,
  Refresh as RefreshIcon,
  Timer as TimerIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';
import gamificationService from '../../services/gamificationService';

// Challenge type icons mapping
const challengeTypeIcons = {
  vocabulary: '📚',
  grammar: '✏️',
  reading: '📖',
  writing: '✍️',
  speaking: '🗣️',
  listening: '👂',
  study_time: '⏱️',
  activity_count: '🎯',
  accuracy: '🎯',
  streak_bonus: '🔥',
};

// Difficulty colors
const difficultyColors = {
  easy: 'success',
  medium: 'warning',
  hard: 'error',
};

const DailyChallengeCard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [challenges, setChallenges] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [completingId, setCompletingId] = useState(null);

  useEffect(() => {
    fetchChallenges();
  }, []);

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await gamificationService.getDailyChallenges();
      setChallenges(data.challenges || []);
    } catch (err) {
      setError(err.message || 'Failed to load daily challenges');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchChallenges();
    setRefreshing(false);
  };

  const handleCompleteChallenge = async (challengeId) => {
    try {
      setCompletingId(challengeId);
      await gamificationService.completeChallenge(challengeId);
      // Refresh to get updated data
      await fetchChallenges();
    } catch (err) {
      setError(err.message || 'Failed to complete challenge');
    } finally {
      setCompletingId(null);
    }
  };

  const getTimeRemaining = () => {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    
    const diff = tomorrow - now;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${hours}h ${minutes}m`;
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error" action={
            <Button color="inherit" size="small" onClick={fetchChallenges}>
              Retry
            </Button>
          }>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const completedCount = challenges.filter(c => c.is_completed).length;
  const totalPoints = challenges.reduce((sum, c) => sum + (c.points_reward || 0), 0);
  const earnedPoints = challenges
    .filter(c => c.is_completed)
    .reduce((sum, c) => sum + (c.points_reward || 0), 0);

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h5" component="h2" gutterBottom>
              Today's Challenges
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AI-powered personalized challenges
            </Typography>
          </Box>
          <IconButton onClick={handleRefresh} disabled={refreshing}>
            <RefreshIcon />
          </IconButton>
        </Box>

        {/* Summary Stats */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={4}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary">
                {completedCount}/{challenges.length}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Completed
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box textAlign="center">
              <Typography variant="h4" color="warning.main">
                {earnedPoints}/{totalPoints}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Points
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box textAlign="center" display="flex" flexDirection="column" alignItems="center">
              <Box display="flex" alignItems="center">
                <TimerIcon fontSize="small" color="action" sx={{ mr: 0.5 }} />
                <Typography variant="h6">
                  {getTimeRemaining()}
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Remaining
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Progress Bar */}
        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" mb={1}>
            <Typography variant="body2">Overall Progress</Typography>
            <Typography variant="body2" color="primary">
              {Math.round((completedCount / challenges.length) * 100)}%
            </Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={(completedCount / challenges.length) * 100}
            sx={{ height: 10, borderRadius: 5 }}
          />
        </Box>

        {/* Challenges List */}
        <Box>
          {challenges.map((challenge, index) => (
            <Card 
              key={challenge.id} 
              variant="outlined" 
              sx={{ 
                mb: 2,
                borderLeft: challenge.is_completed ? 4 : 0,
                borderColor: 'success.main',
                bgcolor: challenge.is_completed ? 'action.hover' : 'inherit'
              }}
            >
              <CardContent>
                <Box display="flex" alignItems="start" justifyContent="space-between">
                  {/* Challenge Info */}
                  <Box flex={1}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <Typography variant="h6" sx={{ mr: 1 }}>
                        {challengeTypeIcons[challenge.challenge_type] || '🎯'}
                      </Typography>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {challenge.title}
                      </Typography>
                      {challenge.is_completed && (
                        <CheckIcon color="success" sx={{ ml: 1 }} />
                      )}
                    </Box>

                    <Typography variant="body2" color="text.secondary" mb={2}>
                      {challenge.description}
                    </Typography>

                    {/* Chips */}
                    <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                      <Chip 
                        label={challenge.difficulty}
                        size="small"
                        color={difficultyColors[challenge.difficulty] || 'default'}
                      />
                      <Chip 
                        label={`${challenge.challenge_type.replace('_', ' ')}`}
                        size="small"
                        variant="outlined"
                      />
                      <Chip 
                        icon={<StarIcon />}
                        label={`${challenge.points_reward} pts`}
                        size="small"
                        color="warning"
                      />
                      {challenge.streak_bonus && (
                        <Chip 
                          icon={<FireIcon />}
                          label={`+${challenge.streak_bonus} bonus`}
                          size="small"
                          color="error"
                        />
                      )}
                    </Box>

                    {/* Progress */}
                    {!challenge.is_completed && (
                      <Box>
                        <Box display="flex" justifyContent="space-between" mb={0.5}>
                          <Typography variant="caption" color="text.secondary">
                            Progress: {challenge.current_progress || 0} / {challenge.target_value}
                          </Typography>
                          <Typography variant="caption" color="primary">
                            {Math.round(((challenge.current_progress || 0) / challenge.target_value) * 100)}%
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={((challenge.current_progress || 0) / challenge.target_value) * 100}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    )}

                    {challenge.is_completed && (
                      <Box display="flex" alignItems="center" mt={1}>
                        <TrophyIcon sx={{ fontSize: 16, color: 'gold', mr: 0.5 }} />
                        <Typography variant="caption" color="success.main" fontWeight="bold">
                          Challenge Completed! +{challenge.points_reward} points
                          {challenge.streak_bonus && ` (+${challenge.streak_bonus} streak bonus)`}
                        </Typography>
                      </Box>
                    )}
                  </Box>

                  {/* Complete Button */}
                  {!challenge.is_completed && challenge.current_progress >= challenge.target_value && (
                    <Tooltip title="Mark as complete">
                      <Button
                        variant="contained"
                        color="success"
                        onClick={() => handleCompleteChallenge(challenge.id)}
                        disabled={completingId === challenge.id}
                        sx={{ ml: 2 }}
                      >
                        {completingId === challenge.id ? (
                          <CircularProgress size={24} color="inherit" />
                        ) : (
                          'Complete'
                        )}
                      </Button>
                    </Tooltip>
                  )}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Completion Message */}
        {completedCount === challenges.length && (
          <Alert severity="success" icon={<TrophyIcon />} sx={{ mt: 2 }}>
            🎉 Congratulations! You've completed all challenges today! Come back tomorrow for new challenges.
          </Alert>
        )}

        {/* Motivation Message */}
        {completedCount === 0 && (
          <Alert severity="info" sx={{ mt: 2 }}>
            💪 Ready to conquer today's challenges? Each challenge is personalized based on your learning progress!
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default DailyChallengeCard;
