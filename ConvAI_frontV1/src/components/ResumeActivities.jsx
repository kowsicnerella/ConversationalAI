import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  PlayArrow, 
  Schedule, 
  School, 
  Error as ErrorIcon,
  ArrowForward,
  PauseCircle
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
  Chip
} from '@mui/material';

const ResumeActivities = () => {
  const [incompleteActivities, setIncompleteActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const token = localStorage.getItem('token');

  const fetchIncompleteActivities = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        'http://localhost:5000/api/learning-path/activities/incomplete',
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.data.success) {
        setIncompleteActivities(response.data.data.activities);
      }
    } catch (err) {
      console.error('Error fetching incomplete activities:', err);
      setError('Failed to load incomplete activities');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      fetchIncompleteActivities();
    }
  }, [token, fetchIncompleteActivities]);

  const handleResume = async (activity) => {
    try {
      // Mark activity as resumed
      const response = await axios.put(
        `http://localhost:5000/api/learning-path/activities/${activity.id}/resume`,
        {},
        {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        // Store activity in sessionStorage
        sessionStorage.setItem('currentActivity', JSON.stringify(response.data.data));
        
        // Navigate to activities page
        navigate('/activities', {
          state: {
            activityData: response.data.data,
            isResume: true
          }
        });
      }
    } catch (err) {
      console.error('Error resuming activity:', err);
      alert('Failed to resume activity. Please try again.');
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
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2 }}>
          <CircularProgress size={24} />
          <Typography>Loading incomplete activities...</Typography>
        </Box>
      </Paper>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error" 
        sx={{ borderRadius: 2 }}
        icon={<ErrorIcon />}
      >
        {error}
      </Alert>
    );
  }

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
