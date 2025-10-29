/**
 * MilestoneProgress - Milestone Celebrations
 * Displays progress milestones with:
 * - Uncelebrated milestones list
 * - Milestone cards with icon, title, description
 * - Points awarded display
 * - Badge display (if applicable)
 * - Celebration button with animation
 * - Milestone history view
 * - Filter by milestone type
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
  IconButton,
  Chip,
  ToggleButtonGroup,
  ToggleButton,
  Avatar,
  Divider,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  Celebration as CelebrationIcon,
  CheckCircle as CheckIcon,
  Refresh as RefreshIcon,
  Star as StarIcon,
  Grade as BadgeIcon,
} from '@mui/icons-material';
import gamificationService from '../../services/gamificationService';

// Milestone type config
const milestoneTypes = {
  activity: { icon: '🎯', color: '#3498db' },
  study_time: { icon: '⏱️', color: '#9b59b6' },
  skill_mastery: { icon: '📚', color: '#27ae60' },
  level_completion: { icon: '🎓', color: '#f39c12' },
  achievement: { icon: '🏆', color: '#e74c3c' },
  streak: { icon: '🔥', color: '#e67e22' },
  social: { icon: '👥', color: '#1abc9c' },
};

const MilestoneProgress = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [milestones, setMilestones] = useState([]);
  const [filter, setFilter] = useState('uncelebrated');
  const [celebratingId, setCelebratingId] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [celebrationAnimation, setCelebrationAnimation] = useState(null);

  useEffect(() => {
    fetchMilestones();
  }, []);

  const fetchMilestones = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await gamificationService.getMilestones(null, 50);
      setMilestones(data.milestones || []);
    } catch (err) {
      setError(err.message || 'Failed to load milestones');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchMilestones();
    setRefreshing(false);
  };

  const handleCelebrate = async (milestoneId) => {
    try {
      setCelebratingId(milestoneId);
      setCelebrationAnimation(milestoneId);
      await gamificationService.celebrateMilestone(milestoneId);
      await fetchMilestones();
      
      // Clear animation after 3 seconds
      setTimeout(() => {
        setCelebrationAnimation(null);
      }, 3000);
    } catch (err) {
      setError(err.message || 'Failed to celebrate milestone');
      setCelebrationAnimation(null);
    } finally {
      setCelebratingId(null);
    }
  };

  const filteredMilestones = milestones.filter(milestone => {
    if (filter === 'uncelebrated') return !milestone.celebrated;
    if (filter === 'celebrated') return milestone.celebrated;
    return true;
  });

  const uncelebratedCount = milestones.filter(m => !m.celebrated).length;
  const totalPoints = milestones
    .filter(m => m.celebrated)
    .reduce((sum, m) => sum + (m.points_awarded || 0), 0);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
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
            <Button color="inherit" size="small" onClick={fetchMilestones}>
              Retry
            </Button>
          }>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Progress Milestones
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {uncelebratedCount} milestones to celebrate • {totalPoints} points earned
          </Typography>
        </Box>
        <IconButton onClick={handleRefresh} disabled={refreshing}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Uncelebrated Alert */}
      {uncelebratedCount > 0 && (
        <Alert 
          severity="success" 
          icon={<CelebrationIcon />}
          sx={{ mb: 3 }}
        >
          You have {uncelebratedCount} new milestone{uncelebratedCount !== 1 ? 's' : ''} to celebrate! 
          Celebrate them to claim your rewards!
        </Alert>
      )}

      {/* Filter */}
      <Box mb={3}>
        <ToggleButtonGroup
          value={filter}
          exclusive
          onChange={(e, newValue) => newValue && setFilter(newValue)}
          size="small"
        >
          <ToggleButton value="uncelebrated">
            Uncelebrated ({uncelebratedCount})
          </ToggleButton>
          <ToggleButton value="celebrated">
            Celebrated ({milestones.length - uncelebratedCount})
          </ToggleButton>
          <ToggleButton value="all">
            All ({milestones.length})
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Milestones Grid */}
      <Grid container spacing={3}>
        {filteredMilestones.map((milestone) => {
          const typeConfig = milestoneTypes[milestone.milestone_type] || milestoneTypes.achievement;
          const isCelebrating = celebrationAnimation === milestone.id;

          return (
            <Grid item xs={12} md={6} key={milestone.id}>
              <Card
                sx={{
                  height: '100%',
                  border: !milestone.celebrated ? 2 : 1,
                  borderColor: !milestone.celebrated ? 'primary.main' : 'divider',
                  position: 'relative',
                  overflow: 'visible',
                  transition: 'all 0.3s',
                  ...(isCelebrating && {
                    animation: 'pulse 1s ease-in-out',
                    '@keyframes pulse': {
                      '0%, 100%': { transform: 'scale(1)' },
                      '50%': { transform: 'scale(1.05)' },
                    },
                  }),
                }}
              >
                <CardContent>
                  <Box display="flex" alignItems="start" mb={2}>
                    {/* Icon */}
                    <Avatar
                      sx={{
                        bgcolor: typeConfig.color,
                        width: 60,
                        height: 60,
                        mr: 2,
                        fontSize: 28,
                      }}
                    >
                      {typeConfig.icon}
                    </Avatar>

                    {/* Content */}
                    <Box flex={1}>
                      <Box display="flex" alignItems="center" mb={1}>
                        <Typography variant="h6" component="div">
                          {milestone.title}
                        </Typography>
                        {milestone.celebrated && (
                          <CheckIcon 
                            sx={{ ml: 1, color: 'success.main', fontSize: 20 }} 
                          />
                        )}
                      </Box>

                      <Typography variant="body2" color="text.secondary" paragraph>
                        {milestone.description}
                      </Typography>

                      {/* Chips */}
                      <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                        <Chip
                          label={milestone.milestone_type.replace('_', ' ')}
                          size="small"
                          sx={{ 
                            bgcolor: typeConfig.color,
                            color: 'white',
                          }}
                        />
                        <Chip
                          icon={<StarIcon />}
                          label={`${milestone.points_awarded} points`}
                          size="small"
                          color="warning"
                        />
                        {milestone.badge_url && (
                          <Chip
                            icon={<BadgeIcon />}
                            label="Badge"
                            size="small"
                            color="info"
                          />
                        )}
                      </Box>

                      {/* Achieved Date */}
                      {milestone.achieved_at && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Achieved: {new Date(milestone.achieved_at).toLocaleDateString()}
                        </Typography>
                      )}
                      {milestone.celebrated && milestone.celebrated_at && (
                        <Typography variant="caption" color="success.main" display="block">
                          Celebrated: {new Date(milestone.celebrated_at).toLocaleDateString()}
                        </Typography>
                      )}
                    </Box>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  {/* Action Button */}
                  {!milestone.celebrated ? (
                    <Button
                      fullWidth
                      variant="contained"
                      color="primary"
                      startIcon={<CelebrationIcon />}
                      onClick={() => handleCelebrate(milestone.id)}
                      disabled={celebratingId === milestone.id}
                      size="large"
                    >
                      {celebratingId === milestone.id ? (
                        <CircularProgress size={24} color="inherit" />
                      ) : (
                        'Celebrate Now!'
                      )}
                    </Button>
                  ) : (
                    <Box textAlign="center" py={1}>
                      <Chip
                        icon={<CheckIcon />}
                        label="Celebrated"
                        color="success"
                        sx={{ fontWeight: 'bold' }}
                      />
                    </Box>
                  )}

                  {/* Badge Display */}
                  {milestone.badge_url && milestone.celebrated && (
                    <Box mt={2} textAlign="center">
                      <Avatar
                        src={milestone.badge_url}
                        sx={{
                          width: 80,
                          height: 80,
                          margin: '0 auto',
                          border: 3,
                          borderColor: 'warning.main',
                        }}
                      >
                        <BadgeIcon sx={{ fontSize: 40 }} />
                      </Avatar>
                    </Box>
                  )}
                </CardContent>

                {/* Celebration Animation */}
                {isCelebrating && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: 'rgba(255, 255, 255, 0.9)',
                      zIndex: 1,
                      animation: 'fadeOut 3s',
                      '@keyframes fadeOut': {
                        '0%': { opacity: 1 },
                        '70%': { opacity: 1 },
                        '100%': { opacity: 0 },
                      },
                    }}
                  >
                    <Box textAlign="center">
                      <TrophyIcon 
                        sx={{ 
                          fontSize: 80, 
                          color: 'warning.main',
                          animation: 'bounce 0.5s infinite',
                          '@keyframes bounce': {
                            '0%, 100%': { transform: 'translateY(0)' },
                            '50%': { transform: 'translateY(-20px)' },
                          },
                        }} 
                      />
                      <Typography variant="h4" color="primary" mt={2}>
                        🎉 Congratulations! 🎉
                      </Typography>
                      <Typography variant="h6" color="text.secondary">
                        +{milestone.points_awarded} points!
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Empty State */}
      {filteredMilestones.length === 0 && (
        <Box textAlign="center" py={8}>
          <TrophyIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {filter === 'uncelebrated' 
              ? 'No milestones to celebrate'
              : filter === 'celebrated'
              ? 'No celebrated milestones yet'
              : 'No milestones yet'
            }
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {filter === 'uncelebrated' 
              ? 'Keep learning to unlock new milestones!'
              : 'Complete activities to earn milestones'
            }
          </Typography>
        </Box>
      )}

      {/* Summary Stats */}
      {milestones.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Milestone Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {milestones.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Milestones
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {milestones.length - uncelebratedCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Celebrated
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {uncelebratedCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="info.main">
                    {totalPoints}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Points Earned
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default MilestoneProgress;
