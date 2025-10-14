import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  Grid,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Paper
} from '@mui/material';
import {
  AutoAwesome as MagicIcon,
  TrendingUp as TrendIcon,
  InfoOutlined as InfoIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import adaptiveService, {
  getConfidenceColor,
  getConfidenceLabel
} from '../services/adaptiveService';

const RecommendationsWidget = () => {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch recommendations
   */
  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await adaptiveService.getNextActivities({ count: 3 });
      setRecommendations(response.recommendations || []);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  /**
   * Handle activity click
   */
  const handleActivityClick = (activity) => {
    if (activity.id) {
      navigate(`/activities/${activity.id}`);
    }
  };

  /**
   * Render loading state
   */
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <MagicIcon color="primary" />
            <Typography variant="h6">Recommended for You</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  /**
   * Render error state
   */
  if (error) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <MagicIcon color="primary" />
            <Typography variant="h6">Recommended for You</Typography>
          </Box>
          <Alert severity="error" action={
            <IconButton size="small" onClick={fetchRecommendations}>
              <RefreshIcon />
            </IconButton>
          }>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  /**
   * Render empty state
   */
  if (recommendations.length === 0) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <MagicIcon color="primary" />
            <Typography variant="h6">Recommended for You</Typography>
          </Box>
          <Alert severity="info">
            Complete more activities to get personalized recommendations!
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <MagicIcon color="primary" />
            <Typography variant="h6">Recommended for You</Typography>
          </Box>
          <Tooltip title="Refresh recommendations">
            <IconButton size="small" onClick={fetchRecommendations}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          AI-powered suggestions based on your learning progress
        </Typography>

        {/* Recommendations */}
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {recommendations.map((activity, index) => (
            <Grid item xs={12} key={activity.id || index}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                      borderColor: 'primary.main',
                      boxShadow: 2,
                      transform: 'translateY(-2px)'
                    }
                  }}
                  onClick={() => handleActivityClick(activity)}
                >
                  {/* Activity Header */}
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 1 }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" fontWeight="medium">
                        {activity.icon && <span style={{ marginRight: 8 }}>{activity.icon}</span>}
                        {activity.title || activity.topic}
                      </Typography>
                      {activity.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                          {activity.description}
                        </Typography>
                      )}
                    </Box>
                    
                    {/* Confidence Score */}
                    {activity.confidence_score !== undefined && (
                      <Chip
                        size="small"
                        label={getConfidenceLabel(activity.confidence_score)}
                        color={getConfidenceColor(activity.confidence_score)}
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Box>

                  {/* Activity Meta */}
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center', mt: 1.5 }}>
                    {/* Type */}
                    {activity.activity_type && (
                      <Chip
                        size="small"
                        label={activity.activity_type}
                        variant="outlined"
                      />
                    )}
                    
                    {/* Difficulty */}
                    {activity.difficulty_level && (
                      <Chip
                        size="small"
                        label={activity.difficulty_level}
                        variant="outlined"
                        color={
                          activity.difficulty_level === 'beginner' ? 'success' :
                          activity.difficulty_level === 'intermediate' ? 'warning' :
                          'error'
                        }
                      />
                    )}

                    {/* Estimated Time */}
                    {activity.estimated_time && (
                      <Chip
                        size="small"
                        label={`${activity.estimated_time} min`}
                        variant="outlined"
                      />
                    )}

                    {/* Points */}
                    {activity.points && (
                      <Chip
                        size="small"
                        label={`${activity.points} pts`}
                        variant="outlined"
                        color="primary"
                      />
                    )}
                  </Box>

                  {/* Recommendation Reason */}
                  {activity.recommendation_reason && (
                    <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'start', gap: 1 }}>
                      <InfoIcon sx={{ fontSize: 16, color: 'info.main', mt: 0.25 }} />
                      <Typography variant="caption" color="text.secondary">
                        {activity.recommendation_reason}
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* View All Button */}
        <Button
          fullWidth
          variant="outlined"
          startIcon={<TrendIcon />}
          onClick={() => navigate('/activities')}
          sx={{ mt: 2 }}
        >
          View All Activities
        </Button>
      </CardContent>
    </Card>
  );
};

export default RecommendationsWidget;
