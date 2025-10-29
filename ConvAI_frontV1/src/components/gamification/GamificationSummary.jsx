/**
 * GamificationSummary - Overview Dashboard
 * Displays a comprehensive summary of all gamification features:
 * - Current streak status
 * - Today's challenges
 * - Achievement progress
 * - Leaderboard position
 * - Recent milestones
 * - Social feed preview
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  Avatar,
  IconButton,
  Divider,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  Whatshot as FireIcon,
  TrendingUp as TrendingIcon,
  Star as StarIcon,
  CheckCircle as CheckIcon,
  People as PeopleIcon,
  Refresh as RefreshIcon,
  NavigateNext as NextIcon,
} from '@mui/icons-material';
import gamificationService from '../../services/gamificationService';

const GamificationSummary = ({ onNavigate }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await gamificationService.getGamificationSummary();
      setSummary(data);
    } catch (err) {
      setError(err.message || 'Failed to load gamification summary');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchSummary();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={fetchSummary}>
            Retry
          </Button>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  if (!summary) return null;

  const { streak, challenges, achievements, leaderboard, milestones, social } = summary;

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Gamification Dashboard
        </Typography>
        <IconButton onClick={handleRefresh} disabled={refreshing}>
          <RefreshIcon />
        </IconButton>
      </Box>

      <Grid container spacing={3}>
        {/* Streak Card */}
        <Grid item xs={12} md={6} lg={3}>
          <Card 
            sx={{ 
              height: '100%',
              background: streak?.current_streak > 0 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'inherit',
              color: streak?.current_streak > 0 ? 'white' : 'inherit'
            }}
          >
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <FireIcon sx={{ mr: 1, fontSize: 32 }} />
                <Typography variant="h6">Learning Streak</Typography>
              </Box>
              <Typography variant="h3" component="div" gutterBottom>
                {streak?.current_streak || 0} days
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Longest: {streak?.longest_streak || 0} days
              </Typography>
              {streak?.streak_freezes_available > 0 && (
                <Chip 
                  label={`${streak.streak_freezes_available} freezes available`}
                  size="small"
                  sx={{ mt: 1, bgcolor: 'rgba(255,255,255,0.2)' }}
                />
              )}
              {streak?.status === 'at_risk' && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Complete an activity today to maintain your streak!
                </Alert>
              )}
              <Button 
                fullWidth 
                variant="contained" 
                sx={{ mt: 2, bgcolor: 'rgba(255,255,255,0.2)' }}
                endIcon={<NextIcon />}
                onClick={() => onNavigate?.('streak')}
              >
                View Details
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Challenges Card */}
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <CheckIcon sx={{ mr: 1, fontSize: 32, color: 'success.main' }} />
                <Typography variant="h6">Daily Challenges</Typography>
              </Box>
              <Typography variant="h3" component="div" gutterBottom>
                {challenges?.completed || 0}/{challenges?.total || 3}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Challenges completed today
              </Typography>
              {challenges?.total_points && (
                <Typography variant="body2" color="primary">
                  +{challenges.total_points} points available
                </Typography>
              )}
              <LinearProgress 
                variant="determinate" 
                value={(challenges?.completed / (challenges?.total || 3)) * 100}
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
              />
              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                endIcon={<NextIcon />}
                onClick={() => onNavigate?.('challenges')}
              >
                View Challenges
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Achievements Card */}
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrophyIcon sx={{ mr: 1, fontSize: 32, color: 'warning.main' }} />
                <Typography variant="h6">Achievements</Typography>
              </Box>
              <Typography variant="h3" component="div" gutterBottom>
                {achievements?.unlocked || 0}/{achievements?.total || 52}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Achievements unlocked
              </Typography>
              {achievements?.recent_unlock && (
                <Box display="flex" alignItems="center" mt={1}>
                  <StarIcon sx={{ fontSize: 16, color: 'gold', mr: 0.5 }} />
                  <Typography variant="caption">
                    Latest: {achievements.recent_unlock.title}
                  </Typography>
                </Box>
              )}
              <LinearProgress 
                variant="determinate" 
                value={(achievements?.unlocked / (achievements?.total || 52)) * 100}
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
              />
              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                endIcon={<NextIcon />}
                onClick={() => onNavigate?.('achievements')}
              >
                View All
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Leaderboard Card */}
        <Grid item xs={12} md={6} lg={3}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <TrendingIcon sx={{ mr: 1, fontSize: 32, color: 'info.main' }} />
                <Typography variant="h6">Leaderboard</Typography>
              </Box>
              <Typography variant="h3" component="div" gutterBottom>
                #{leaderboard?.rank || '-'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {leaderboard?.category || 'Overall'} ranking
              </Typography>
              {leaderboard?.percentile && (
                <Typography variant="body2" color="primary">
                  Top {leaderboard.percentile}%
                </Typography>
              )}
              {leaderboard?.rank_change && (
                <Chip 
                  label={leaderboard.rank_change > 0 ? `↑ ${leaderboard.rank_change}` : `↓ ${Math.abs(leaderboard.rank_change)}`}
                  size="small"
                  color={leaderboard.rank_change > 0 ? 'success' : 'error'}
                  sx={{ mt: 1 }}
                />
              )}
              <Button 
                fullWidth 
                variant="outlined" 
                sx={{ mt: 2 }}
                endIcon={<NextIcon />}
                onClick={() => onNavigate?.('leaderboard')}
              >
                View Rankings
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Milestones */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Milestones
              </Typography>
              {milestones && milestones.length > 0 ? (
                <Box>
                  {milestones.slice(0, 3).map((milestone, index) => (
                    <Box key={milestone.id}>
                      {index > 0 && <Divider sx={{ my: 1.5 }} />}
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box display="flex" alignItems="center">
                          <Avatar 
                            sx={{ 
                              bgcolor: milestone.celebrated ? 'success.light' : 'grey.300',
                              mr: 2,
                              width: 48,
                              height: 48
                            }}
                          >
                            <TrophyIcon />
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle1">
                              {milestone.title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {milestone.description}
                            </Typography>
                            <Box mt={0.5}>
                              <Chip 
                                label={`+${milestone.points_awarded} points`}
                                size="small"
                                color="primary"
                              />
                            </Box>
                          </Box>
                        </Box>
                        {!milestone.celebrated && (
                          <Button 
                            size="small" 
                            variant="contained"
                            onClick={() => onNavigate?.('milestones')}
                          >
                            Celebrate
                          </Button>
                        )}
                      </Box>
                    </Box>
                  ))}
                  <Button 
                    fullWidth 
                    sx={{ mt: 2 }}
                    endIcon={<NextIcon />}
                    onClick={() => onNavigate?.('milestones')}
                  >
                    View All Milestones
                  </Button>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No milestones yet. Keep learning to unlock milestones!
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Social Feed Preview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">
                  Social Feed
                </Typography>
                <PeopleIcon color="action" />
              </Box>
              {social && social.length > 0 ? (
                <Box>
                  {social.slice(0, 3).map((post, index) => (
                    <Box key={post.id}>
                      {index > 0 && <Divider sx={{ my: 1.5 }} />}
                      <Box display="flex" alignItems="start">
                        <Avatar 
                          sx={{ mr: 2 }}
                          src={post.user_avatar}
                        >
                          {post.user_name?.[0]}
                        </Avatar>
                        <Box flex={1}>
                          <Typography variant="subtitle2">
                            {post.user_name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Unlocked: {post.achievement_title}
                          </Typography>
                          {post.caption && (
                            <Typography variant="caption" color="text.secondary">
                              {post.caption}
                            </Typography>
                          )}
                          <Box display="flex" alignItems="center" mt={0.5}>
                            <Chip 
                              label={`❤️ ${post.likes || 0}`}
                              size="small"
                              variant="outlined"
                            />
                            <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                              {new Date(post.shared_at).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </Box>
                      </Box>
                    </Box>
                  ))}
                  <Button 
                    fullWidth 
                    sx={{ mt: 2 }}
                    endIcon={<NextIcon />}
                    onClick={() => onNavigate?.('social')}
                  >
                    View Full Feed
                  </Button>
                </Box>
              ) : (
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Connect with other learners to see their achievements!
                  </Typography>
                  <Button 
                    fullWidth 
                    variant="outlined"
                    sx={{ mt: 2 }}
                    onClick={() => onNavigate?.('social')}
                  >
                    Find Friends
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default GamificationSummary;
