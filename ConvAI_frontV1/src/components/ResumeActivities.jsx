import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../config/api';
import { 
  PlayArrow, 
  Schedule, 
  School, 
  Error as ErrorIcon,
  ArrowForward,
  PauseCircle,
  Refresh
} from '@mui/icons-material';
import {
  Box,
  Card,
  CardContent,
  Button,
  Typography,
  CircularProgress,
  Alert,
  Stack,
  Paper,
  Chip,
  Skeleton
} from '@mui/material';

const ResumeActivities = () => {
  const [incompleteActivities, setIncompleteActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const navigate = useNavigate();

  const MAX_RETRIES = 3;

  const fetchIncompleteActivities = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axiosInstance.get('/learning-path/activities/incomplete');

      if (response.data.success) {
        setIncompleteActivities(response.data.data?.activities || []);
        setRetryCount(0);
      } else {
        // Handle API returning success: false
        setIncompleteActivities([]);
      }
    } catch (err) {
      console.error('Error fetching incomplete activities:', err);
      
      // Handle different error types gracefully
      if (err.response?.status === 401) {
        // User not authenticated - don't show error, just hide component
        setIncompleteActivities([]);
        setError(null);
      } else if (err.response?.status === 404) {
        // Endpoint doesn't exist or no activities - graceful handling
        setIncompleteActivities([]);
        setError(null);
      } else if (err.response?.status >= 500) {
        // Server error - show retry option
        setError('Server is temporarily unavailable. Please try again.');
      } else {
        // Network or other error
        setError('Unable to load activities. Check your connection.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchIncompleteActivities();
    } else {
      setLoading(false);
      setIncompleteActivities([]);
    }
  }, [fetchIncompleteActivities]);

  const handleRetry = () => {
    if (retryCount < MAX_RETRIES) {
      setRetryCount(prev => prev + 1);
      fetchIncompleteActivities();
    }
  };

  const handleResume = async (activity) => {
    try {
      const response = await axiosInstance.put(
        `/learning-path/activities/${activity.id}/resume`
      );

      if (response.data.success) {
        sessionStorage.setItem('currentActivity', JSON.stringify(response.data.data));
        navigate('/activities', {
          state: {
            activityData: response.data.data,
            isResume: true
          }
        });
      }
    } catch (err) {
      console.error('Error resuming activity:', err);
      // Try navigating anyway with existing data
      sessionStorage.setItem('currentActivity', JSON.stringify(activity));
      navigate('/activities', {
        state: {
          activityData: activity,
          isResume: true
        }
      });
    }
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

  if (loading) {
    return (
      <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Skeleton variant="circular" width={28} height={28} />
          <Skeleton variant="text" width={150} height={28} />
        </Box>
        <Stack spacing={2}>
          {[1, 2].map((i) => (
            <Skeleton key={i} variant="rounded" height={80} />
          ))}
        </Stack>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper elevation={2} sx={{ p: 3, borderRadius: 2 }}>
        <Alert 
          severity="warning" 
          sx={{ borderRadius: 2 }}
          icon={<ErrorIcon />}
          action={
            retryCount < MAX_RETRIES ? (
              <Button 
                color="inherit" 
                size="small" 
                startIcon={<Refresh />}
                onClick={handleRetry}
              >
                Retry
              </Button>
            ) : null
          }
        >
          {error}
        </Alert>
      </Paper>
    );
  }

  // Don't render anything if no incomplete activities
  if (incompleteActivities.length === 0) {
    return null;
  }

  return (
    <Paper 
      elevation={2}
      sx={{
        p: 3,
        borderRadius: 2,
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(99, 102, 241, 0.05) 100%)',
        border: '1px solid rgba(59, 130, 246, 0.2)'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <PlayArrow sx={{ fontSize: 28, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Continue Learning
          </Typography>
        </Box>
        <Chip 
          label={`${incompleteActivities.length} ${incompleteActivities.length === 1 ? 'activity' : 'activities'}`}
          color="primary"
          variant="outlined"
          size="small"
        />
      </Box>

      <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
        Pick up where you left off with these activities:
      </Typography>

      <Stack spacing={2}>
        {incompleteActivities.map((activity) => (
          <Card
            key={activity.id}
            sx={{
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                boxShadow: 4,
                transform: 'translateY(-2px)',
                borderColor: 'primary.main'
              },
              border: '1px solid',
              borderColor: 'divider'
            }}
            onClick={() => handleResume(activity)}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2 }}>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
                    {activity.content?.activity_title || 'Untitled Activity'}
                  </Typography>
                  
                  <Stack direction="row" spacing={2} sx={{ mb: 1, flexWrap: 'wrap' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <School sx={{ fontSize: 18, color: 'text.secondary' }} />
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {activity.activity_type?.replace(/_/g, ' ') || 'Practice'}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Schedule sx={{ fontSize: 18, color: 'text.secondary' }} />
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Started {formatDate(activity.created_at)}
                      </Typography>
                    </Box>
                  </Stack>

                  {activity.content?.exercises && (
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {activity.content.exercises.length} exercises
                    </Typography>
                  )}
                </Box>

                <Button
                  variant="contained"
                  color="primary"
                  size="small"
                  endIcon={<ArrowForward sx={{ fontSize: 16 }} />}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleResume(activity);
                  }}
                  sx={{
                    whiteSpace: 'nowrap',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      transform: 'scale(1.05)'
                    }
                  }}
                >
                  Resume
                </Button>
              </Box>

              {activity.status === 'in_progress' && (
                <Alert 
                  severity="info" 
                  icon={<PauseCircle sx={{ fontSize: 20 }} />}
                  sx={{ mt: 2, py: 0.75 }}
                >
                  <Typography variant="caption">
                    In Progress - Continue your practice
                  </Typography>
                </Alert>
              )}
            </CardContent>
          </Card>
        ))}
      </Stack>
    </Paper>
  );
};

export default ResumeActivities;
