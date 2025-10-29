/**
 * StreakTracker - Learning Streak Display
 * Shows streak status with:
 * - Current streak count
 * - Longest streak record
 * - Streak freeze availability
 * - Status indicator (active/at-risk/broken)
 * - Next milestone progress
 * - Calendar view of streak days
 * - Recovery challenge (if applicable)
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  CircularProgress,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Whatshot as FireIcon,
  AcUnit as FreezeIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';
import gamificationService from '../../services/gamificationService';

// Streak status config
const streakStatus = {
  active: {
    color: 'success',
    icon: <CheckIcon />,
    message: 'Your streak is active! Keep it up!',
  },
  at_risk: {
    color: 'warning',
    icon: <WarningIcon />,
    message: 'Complete an activity today to maintain your streak!',
  },
  broken: {
    color: 'error',
    icon: <WarningIcon />,
    message: 'Your streak was broken. Start a new one today!',
  },
};

// Milestone thresholds
const milestones = [
  { days: 3, title: 'On Fire', icon: '🔥' },
  { days: 7, title: 'Week Warrior', icon: '⚡' },
  { days: 30, title: 'Month Master', icon: '👑' },
  { days: 100, title: 'Century Streaker', icon: '💯' },
  { days: 365, title: 'Year Champion', icon: '🏆' },
];

const StreakTracker = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [streak, setStreak] = useState(null);
  const [freezeDialogOpen, setFreezeDialogOpen] = useState(false);
  const [usingFreeze, setUsingFreeze] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchStreak();
  }, []);

  const fetchStreak = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await gamificationService.getStreak();
      setStreak(data.streak);
    } catch (err) {
      setError(err.message || 'Failed to load streak data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchStreak();
    setRefreshing(false);
  };

  const handleUseFreeze = async () => {
    try {
      setUsingFreeze(true);
      await gamificationService.useStreakFreeze();
      setFreezeDialogOpen(false);
      await fetchStreak();
    } catch (err) {
      setError(err.message || 'Failed to use streak freeze');
    } finally {
      setUsingFreeze(false);
    }
  };

  const getNextMilestone = () => {
    if (!streak) return null;
    return milestones.find(m => m.days > streak.current_streak) || null;
  };

  const getMilestoneProgress = () => {
    if (!streak) return 0;
    const next = getNextMilestone();
    if (!next) return 100;
    
    const prev = milestones.filter(m => m.days <= streak.current_streak).pop();
    const prevDays = prev ? prev.days : 0;
    const range = next.days - prevDays;
    const progress = streak.current_streak - prevDays;
    
    return (progress / range) * 100;
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
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
            <Button color="inherit" size="small" onClick={fetchStreak}>
              Retry
            </Button>
          }>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!streak) return null;

  const statusConfig = streakStatus[streak.status] || streakStatus.active;
  const nextMilestone = getNextMilestone();
  const milestoneProgress = getMilestoneProgress();

  return (
    <Box>
      <Card>
        <CardContent>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" component="h2">
              Learning Streak
            </Typography>
            <IconButton onClick={handleRefresh} disabled={refreshing}>
              <RefreshIcon />
            </IconButton>
          </Box>

          {/* Status Alert */}
          <Alert 
            severity={statusConfig.color} 
            icon={statusConfig.icon}
            sx={{ mb: 3 }}
          >
            {statusConfig.message}
          </Alert>

          {/* Main Streak Display */}
          <Box textAlign="center" mb={4}>
            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 200,
                height: 200,
                borderRadius: '50%',
                background: streak.current_streak > 0
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : 'linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%)',
                color: 'white',
                flexDirection: 'column',
                mb: 2,
              }}
            >
              <FireIcon sx={{ fontSize: 64, mb: 1 }} />
              <Typography variant="h2" component="div" fontWeight="bold">
                {streak.current_streak}
              </Typography>
              <Typography variant="h6">
                {streak.current_streak === 1 ? 'Day' : 'Days'}
              </Typography>
            </Box>

            <Typography variant="h6" color="text.secondary">
              Current Streak
            </Typography>
          </Box>

          {/* Stats Grid */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={6}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <TrendingIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="h4">
                    {streak.longest_streak}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Longest Streak
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <FreezeIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                  <Typography variant="h4">
                    {streak.streak_freezes_available}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Freezes Available
                  </Typography>
                  {streak.freeze_used_today && (
                    <Chip 
                      label="Used Today"
                      size="small"
                      color="info"
                      sx={{ mt: 1 }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Streak Freeze Button */}
          {streak.streak_freezes_available > 0 && streak.status === 'at_risk' && !streak.freeze_used_today && (
            <Button
              fullWidth
              variant="contained"
              color="info"
              startIcon={<FreezeIcon />}
              onClick={() => setFreezeDialogOpen(true)}
              sx={{ mb: 3 }}
            >
              Use Streak Freeze
            </Button>
          )}

          {/* Next Milestone */}
          {nextMilestone && (
            <Box mb={3}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="subtitle1" fontWeight="bold">
                  {nextMilestone.icon} Next: {nextMilestone.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {nextMilestone.days - streak.current_streak} days to go
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={milestoneProgress}
                sx={{ height: 10, borderRadius: 5 }}
              />
              <Box display="flex" justifyContent="space-between" mt={0.5}>
                <Typography variant="caption" color="text.secondary">
                  {streak.current_streak} days
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {nextMilestone.days} days
                </Typography>
              </Box>
            </Box>
          )}

          {/* Milestones Achieved */}
          {streak.current_streak > 0 && (
            <Box>
              <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                Milestones Achieved
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {milestones.map((milestone) => (
                  <Tooltip 
                    key={milestone.days}
                    title={`${milestone.title} - ${milestone.days} days`}
                  >
                    <Chip
                      icon={<TrophyIcon />}
                      label={`${milestone.icon} ${milestone.days}`}
                      color={streak.current_streak >= milestone.days ? 'primary' : 'default'}
                      variant={streak.current_streak >= milestone.days ? 'filled' : 'outlined'}
                    />
                  </Tooltip>
                ))}
              </Box>
            </Box>
          )}

          {/* Recovery Challenge */}
          {streak.recovery_challenge_available && (
            <Alert severity="info" icon={<TrophyIcon />} sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Recovery Challenge Available!
              </Typography>
              <Typography variant="body2">
                Complete a special challenge to recover your broken streak. This is a one-time opportunity!
              </Typography>
            </Alert>
          )}

          {/* Tips */}
          {streak.current_streak === 0 && (
            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Start Your Streak Today!
              </Typography>
              <Typography variant="body2">
                Complete any learning activity to start building your streak. Consistency is key to language learning success!
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Freeze Confirmation Dialog */}
      <Dialog open={freezeDialogOpen} onClose={() => setFreezeDialogOpen(false)}>
        <DialogTitle>Use Streak Freeze?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to use a streak freeze? This will protect your current streak for today, even if you don&apos;t complete any activities.
          </Typography>
          <Box mt={2}>
            <Alert severity="info">
              You have {streak?.streak_freezes_available} freeze(s) available. Use them wisely!
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFreezeDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleUseFreeze}
            variant="contained"
            color="info"
            disabled={usingFreeze}
            startIcon={<FreezeIcon />}
          >
            {usingFreeze ? <CircularProgress size={24} /> : 'Use Freeze'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StreakTracker;
