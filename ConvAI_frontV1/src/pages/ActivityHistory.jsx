import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Schedule,
  TrendingUp,
  EmojiEvents,
  DateRange,
  School,
  CheckCircle,
  Error as ErrorIcon,
  TimelapseOutlined,
  Whatshot,
  Assessment,
  History,
  LocalFireDepartment
} from '@mui/icons-material';
import {
  Container,
  Box,
  Typography,
  Paper,
  Grid,
  LinearProgress,
  Button,
  Chip,
  Stack,
  Card,
  CardContent,
  CircularProgress,
  ButtonGroup,
  Divider
} from '@mui/material';

const ActivityHistory = () => {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const navigate = useNavigate();

  const token = localStorage.getItem('token');

  const fetchActivityHistory = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        'http://localhost:5000/api/learning-path/activity-history',
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.data.success) {
        setHistory(response.data.data);
      }
    } catch (err) {
      console.error('Error fetching activity history:', err);
      setError('Failed to load activity history');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      fetchActivityHistory();
    }
  }, [token, fetchActivityHistory]);

  const getMasteryColor = (level) => {
    const colors = {
      mastered: 'success',
      proficient: 'info',
      learning: 'warning',
      not_started: 'default'
    };
    return colors[level] || 'default';
  };

  const getMasteryIcon = (level) => {
    if (level === 'mastered') return <EmojiEvents sx={{ fontSize: 18 }} />;
    if (level === 'proficient') return <CheckCircle sx={{ fontSize: 18 }} />;
    if (level === 'learning') return <School sx={{ fontSize: 18 }} />;
    return <Assessment sx={{ fontSize: 18 }} />;
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const getScoreColor = (score) => {
    if (score >= 0.9) return '#22c55e';
    if (score >= 0.7) return '#3b82f6';
    if (score >= 0.5) return '#eab308';
    return '#ef4444';
  };

  const filteredTimeline = history?.recent_timeline.filter(item => {
    if (selectedFilter === 'all') return true;
    return item.mastery_level === selectedFilter;
  }) || [];

  if (loading) {
    return (
      <Container sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography sx={{ color: 'text.secondary' }}>Loading your learning journey...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <ErrorIcon sx={{ fontSize: 48, color: 'error.main', mb: 2 }} />
          <Typography sx={{ color: 'error.main', mb: 2 }}>{error}</Typography>
          <Button 
            variant="contained" 
            onClick={fetchActivityHistory}
          >
            Try Again
          </Button>
        </Box>
      </Container>
    );
  }

  if (!history) return null;

  const stats = history.statistics;
  const totalHours = Math.floor(stats.total_time_spent_seconds / 3600);
  const totalMinutes = Math.floor((stats.total_time_spent_seconds % 3600) / 60);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 4 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Whatshot sx={{ fontSize: 32, color: 'warning.main' }} />
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              Your Learning Journey
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>
            Track your progress and celebrate your achievements
          </Typography>
        </Box>

        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Total Activities */}
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={1} sx={{ height: '100%', transition: 'all 0.3s', '&:hover': { boxShadow: 3 } }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="caption">
                      Activities Completed
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, my: 1 }}>
                      {stats.total_activities_completed}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'success.main' }}>
                      <TrendingUp sx={{ fontSize: 16 }} />
                      <Typography variant="caption">Keep it up!</Typography>
                    </Box>
                  </Box>
                  <Box sx={{ p: 1.5, bgcolor: 'info.light', borderRadius: 2 }}>
                    <CheckCircle sx={{ color: 'info.main', fontSize: 28 }} />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Average Score */}
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={1} sx={{ height: '100%', transition: 'all 0.3s', '&:hover': { boxShadow: 3 } }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="caption">
                      Average Score
                    </Typography>
                    <Typography 
                      variant="h4" 
                      sx={{ fontWeight: 700, my: 1, color: getScoreColor(stats.average_performance_score) }}
                    >
                      {(stats.average_performance_score * 100).toFixed(0)}%
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {stats.average_performance_score >= 0.8 ? 'Excellent!' : 'Keep practicing'}
                    </Typography>
                  </Box>
                  <Box sx={{ p: 1.5, bgcolor: 'warning.light', borderRadius: 2 }}>
                    <Assessment sx={{ color: 'warning.main', fontSize: 28 }} />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Time Spent */}
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={1} sx={{ height: '100%', transition: 'all 0.3s', '&:hover': { boxShadow: 3 } }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="caption">
                      Time Spent
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, my: 1 }}>
                      {totalHours > 0 ? `${totalHours}h` : `${totalMinutes}m`}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {totalMinutes} minutes total
                    </Typography>
                  </Box>
                  <Box sx={{ p: 1.5, bgcolor: 'success.light', borderRadius: 2 }}>
                    <Schedule sx={{ color: 'success.main', fontSize: 28 }} />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Mastered Topics */}
          <Grid item xs={12} sm={6} md={3}>
            <Card elevation={1} sx={{ height: '100%', transition: 'all 0.3s', '&:hover': { boxShadow: 3 } }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="caption">
                      Mastered Topics
                    </Typography>
                    <Typography variant="h4" sx={{ fontWeight: 700, my: 1, color: 'success.main' }}>
                      {stats.mastery_breakdown.mastered}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {stats.mastery_breakdown.proficient} proficient
                    </Typography>
                  </Box>
                  <Box sx={{ p: 1.5, bgcolor: 'primary.light', borderRadius: 2 }}>
                    <LocalFireDepartment sx={{ fontSize: 28, color: '#1976d2' }} />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Mastery Breakdown Chart */}
        <Paper elevation={1} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <Assessment sx={{ color: 'primary.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Mastery Level Breakdown
            </Typography>
          </Box>

          <Stack spacing={3}>
            {/* Mastered */}
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <EmojiEvents sx={{ color: 'success.main', fontSize: 20 }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Mastered
                  </Typography>
                </Box>
                <Chip 
                  label={stats.mastery_breakdown.mastered} 
                  color="success" 
                  variant="outlined"
                  size="small"
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={(stats.mastery_breakdown.mastered / stats.total_activities_completed) * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            {/* Proficient */}
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle sx={{ color: 'info.main', fontSize: 20 }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Proficient
                  </Typography>
                </Box>
                <Chip 
                  label={stats.mastery_breakdown.proficient} 
                  color="info" 
                  variant="outlined"
                  size="small"
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={(stats.mastery_breakdown.proficient / stats.total_activities_completed) * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            {/* Learning */}
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1, alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <School sx={{ color: 'warning.main', fontSize: 20 }} />
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    Learning
                  </Typography>
                </Box>
                <Chip 
                  label={stats.mastery_breakdown.learning} 
                  color="warning" 
                  variant="outlined"
                  size="small"
                />
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={(stats.mastery_breakdown.learning / stats.total_activities_completed) * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </Stack>
        </Paper>

        {/* Review Schedule */}
        {history.needs_review.length > 0 && (
          <Paper 
            elevation={1} 
            sx={{ 
              p: 3, 
              mb: 4, 
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(249, 115, 22, 0.05) 0%, rgba(220, 38, 38, 0.05) 100%)',
              border: '1px solid rgba(249, 115, 22, 0.2)'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <DateRange sx={{ color: 'warning.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Review Schedule
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
              These activities are ready for review to strengthen your memory:
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              {history.needs_review.slice(0, 6).map((review, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card variant="outlined" sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {review.learning_node_id.replace(/_/g, ' ')}
                      </Typography>
                      <Chip
                        label={review.mastery_level}
                        color={getMasteryColor(review.mastery_level)}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 1, fontSize: 'small' }}>
                      <Typography variant="caption">
                        Last score: <strong>{(review.last_score * 100).toFixed(0)}%</strong>
                      </Typography>
                      <Typography variant="caption">
                        {formatDate(review.next_review_date)}
                      </Typography>
                    </Box>
                  </Card>
                </Grid>
              ))}
            </Grid>
            <Button 
              variant="contained" 
              fullWidth
              color="warning"
            >
              Start Reviewing ({history.needs_review.length} activities)
            </Button>
          </Paper>
        )}

        {/* Activity Timeline */}
        <Paper elevation={1} sx={{ p: 3, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TimelapseOutlined sx={{ color: 'primary.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Recent Activity Timeline
              </Typography>
            </Box>

            {/* Filter Buttons */}
            <ButtonGroup size="small" variant="outlined">
              <Button
                onClick={() => setSelectedFilter('all')}
                variant={selectedFilter === 'all' ? 'contained' : 'outlined'}
              >
                All
              </Button>
              <Button
                onClick={() => setSelectedFilter('mastered')}
                variant={selectedFilter === 'mastered' ? 'contained' : 'outlined'}
                color={selectedFilter === 'mastered' ? 'success' : 'inherit'}
              >
                Mastered
              </Button>
              <Button
                onClick={() => setSelectedFilter('learning')}
                variant={selectedFilter === 'learning' ? 'contained' : 'outlined'}
                color={selectedFilter === 'learning' ? 'warning' : 'inherit'}
              >
                Learning
              </Button>
            </ButtonGroup>
          </Box>

          <Divider sx={{ mb: 2 }} />

          <Stack spacing={2} sx={{ maxHeight: 600, overflowY: 'auto' }}>
            {filteredTimeline.map((item, index) => (
              <Card 
                key={index}
                variant="outlined"
                sx={{ 
                  p: 2, 
                  cursor: 'pointer', 
                  transition: 'all 0.3s',
                  '&:hover': { boxShadow: 2 }
                }}
                onClick={() => navigate(`/activities/${item.activity_id}`)}
              >
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                  {/* Icon */}
                  <Box 
                    sx={{ 
                      p: 1, 
                      borderRadius: 1, 
                      bgcolor: getMasteryColor(item.mastery_level) + '.light',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {getMasteryIcon(item.mastery_level)}
                  </Box>

                  {/* Content */}
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {item.learning_node_id.replace(/_/g, ' ')}
                      </Typography>
                      <Typography 
                        variant="subtitle2" 
                        sx={{ fontWeight: 700, color: getScoreColor(item.performance_score) }}
                      >
                        {(item.performance_score * 100).toFixed(0)}%
                      </Typography>
                    </Box>

                    <Stack direction="row" spacing={2} sx={{ mb: 1, flexWrap: 'wrap' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <School sx={{ fontSize: 16, color: 'text.secondary' }} />
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          {item.activity_type.replace(/_/g, ' ')}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Schedule sx={{ fontSize: 16, color: 'text.secondary' }} />
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          {formatTime(item.time_spent_seconds)}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <DateRange sx={{ fontSize: 16, color: 'text.secondary' }} />
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                          {formatDate(item.completed_at)}
                        </Typography>
                      </Box>
                    </Stack>
                  </Box>

                  {/* Mastery Badge */}
                  <Chip
                    label={item.mastery_level}
                    color={getMasteryColor(item.mastery_level)}
                    variant="outlined"
                    size="small"
                  />
                </Box>
              </Card>
            ))}
          </Stack>

          {filteredTimeline.length === 0 && (
            <Typography variant="body2" sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
              No activities found for this filter
            </Typography>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default ActivityHistory;
