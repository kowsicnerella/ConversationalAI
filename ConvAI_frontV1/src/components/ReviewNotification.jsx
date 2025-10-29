import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  NotificationsActive, 
  DateRange,
  TrendingUp, 
  Close, 
  CheckCircle
} from '@mui/icons-material';
import {
  Box,
  Paper,
  Button,
  Typography,
  Stack,
  Chip,
  LinearProgress,
  IconButton,
  Alert,
  Divider
} from '@mui/material';

const ReviewNotification = () => {
  const [dueReviews, setDueReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const navigate = useNavigate();

  const token = localStorage.getItem('token');

  const fetchDueReviews = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        'http://localhost:5000/api/learning-path/spaced-repetition/due',
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.data.success) {
        setDueReviews(response.data.data.due_reviews);
      }
    } catch (err) {
      console.error('Error fetching due reviews:', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    // Check if notification was dismissed in this session
    const isDismissed = sessionStorage.getItem('reviewNotificationDismissed');
    if (isDismissed) {
      setDismissed(true);
      return;
    }

    if (token) {
      fetchDueReviews();
    }
  }, [token, fetchDueReviews]);

  const handleDismiss = () => {
    setDismissed(true);
    sessionStorage.setItem('reviewNotificationDismissed', 'true');
  };

  const handleStartReview = (review) => {
    if (review) {
      sessionStorage.setItem('currentActivity', JSON.stringify({
        id: review.activity_id,
        content: review.activity_content
      }));
      navigate('/activities', {
        state: {
          activityData: review.activity_content,
          isReview: true,
          activityId: review.activity_id
        }
      });
    }
  };

  const getMasteryColor = (level) => {
    const colors = {
      mastered: 'success',
      proficient: 'info',
      learning: 'warning',
      not_started: 'default'
    };
    return colors[level] || 'default';
  };

  const getUrgencyColor = (daysOverdue) => {
    if (daysOverdue > 7) return 'error';
    if (daysOverdue > 3) return 'warning';
    if (daysOverdue > 0) return 'warning';
    return 'info';
  };

  if (loading || dismissed || dueReviews.length === 0) {
    return null;
  }

  // Compact notification banner
  if (!showDetails) {
    return (
      <Paper 
        elevation={3}
        sx={{
          background: 'linear-gradient(135deg, #f97316 0%, #dc2626 100%)',
          color: 'white',
          p: 2,
          mb: 3,
          borderRadius: 2,
          border: '1px solid rgba(255, 255, 255, 0.2)'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
            <Box 
              sx={{
                p: 1,
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                borderRadius: '50%',
                display: 'flex',
                animation: 'pulse 2s infinite'
              }}
            >
              <NotificationsActive />
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                📚 Time to Review!
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.9 }}>
                You have <strong>{dueReviews.length}</strong> {dueReviews.length === 1 ? 'activity' : 'activities'} ready for review
              </Typography>
            </Box>
          </Box>

          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              color="inherit"
              size="small"
              onClick={() => setShowDetails(true)}
            >
              View Details
            </Button>
            <Button
              variant="contained"
              color="inherit"
              size="small"
              onClick={() => handleStartReview(dueReviews[0])}
            >
              Start Reviewing
            </Button>
            <IconButton
              size="small"
              onClick={handleDismiss}
              sx={{ color: 'inherit' }}
            >
              <Close fontSize="small" />
            </IconButton>
          </Stack>
        </Box>
      </Paper>
    );
  }

  // Detailed review list
  return (
    <Paper 
      elevation={2}
      sx={{
        background: 'linear-gradient(135deg, rgba(249, 115, 22, 0.05) 0%, rgba(220, 38, 38, 0.05) 100%)',
        p: 3,
        mb: 3,
        borderRadius: 2,
        border: '1px solid rgba(249, 115, 22, 0.2)'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <NotificationsActive sx={{ color: 'warning.main', fontSize: 28 }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Review Schedule - Strengthen Your Memory
          </Typography>
        </Box>
        <IconButton
          onClick={() => setShowDetails(false)}
          sx={{ color: 'text.secondary' }}
        >
          <Close />
        </IconButton>
      </Box>

      <Alert 
        severity="info" 
        sx={{ mb: 2 }}
        icon={<TrendingUp />}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <DateRange sx={{ fontSize: 18 }} />
          <Typography variant="body2">
            <strong>Spaced Repetition Active:</strong> Review now for better retention
          </Typography>
        </Box>
      </Alert>

      <Stack spacing={2} sx={{ maxHeight: 400, overflowY: 'auto', mb: 2 }}>
        {dueReviews.map((review, index) => (
          <Paper 
            key={index}
            variant="outlined"
            sx={{
              p: 2,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              borderColor: review.days_overdue > 0 ? 'warning.main' : 'divider',
              '&:hover': {
                boxShadow: 2,
                borderColor: 'primary.main'
              }
            }}
            onClick={() => handleStartReview(review)}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 0.5 }}>
                  {review.learning_node_id.replace(/_/g, ' ')}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  {review.activity_type?.replace(/_/g, ' ') || 'Practice Activity'}
                </Typography>
              </Box>

              <Box sx={{ display: 'flex', gap: 1 }}>
                {review.days_overdue > 0 && (
                  <Chip
                    label={`${review.days_overdue} ${review.days_overdue === 1 ? 'day' : 'days'} overdue`}
                    color={getUrgencyColor(review.days_overdue)}
                    size="small"
                    variant="filled"
                  />
                )}
                <Chip
                  label={review.mastery_level}
                  color={getMasteryColor(review.mastery_level)}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </Box>

            <Stack direction="row" spacing={2} sx={{ mb: 1, fontSize: 'small' }}>
              <Typography variant="caption">
                Last score: <strong>{(review.last_performance_score * 100).toFixed(0)}%</strong>
              </Typography>
              <Typography variant="caption">
                Review #{review.review_count + 1}
              </Typography>
            </Stack>

            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Mastery Progress
                </Typography>
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  {(review.last_performance_score * 100).toFixed(0)}%
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={review.last_performance_score * 100}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: 'rgba(0, 0, 0, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3,
                    backgroundColor: 
                      review.last_performance_score >= 0.8 ? '#22c55e' :
                      review.last_performance_score >= 0.6 ? '#3b82f6' :
                      '#eab308'
                  }
                }}
              />
            </Box>

            <Button
              variant="contained"
              size="small"
              fullWidth
              startIcon={<CheckCircle sx={{ fontSize: 18 }} />}
              onClick={(e) => {
                e.stopPropagation();
                handleStartReview(review);
              }}
              sx={{ mt: 1 }}
            >
              Review Now
            </Button>
          </Paper>
        ))}
      </Stack>

      <Divider sx={{ my: 2 }} />

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
        <Button
          variant="contained"
          color="warning"
          fullWidth
          startIcon={<CheckCircle />}
          onClick={() => handleStartReview(dueReviews[0])}
        >
          Start Reviewing All ({dueReviews.length})
        </Button>
        <Button
          variant="outlined"
          fullWidth
          onClick={handleDismiss}
        >
          Dismiss
        </Button>
      </Stack>
    </Paper>
  );
};

export default ReviewNotification;
