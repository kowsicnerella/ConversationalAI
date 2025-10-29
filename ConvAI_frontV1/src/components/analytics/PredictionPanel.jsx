import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  CircularProgress,
  Alert,
  useTheme,
} from '@mui/material';
import {
  TrendingUp,
  EmojiEvents,
  AccessTime,
  Psychology,
  CheckCircle,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import learningAnalyticsService from '../../services/learningAnalyticsService';

/**
 * Custom Tooltip for Prediction Chart
 */
const CustomTooltip = ({ active, payload }) => {
  const theme = useTheme();

  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <Box
        sx={{
          backgroundColor: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 1,
          p: 1.5,
          boxShadow: theme.shadows[3],
        }}
      >
        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
          {data.skill}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Current: {data.current}%
        </Typography>
        <Typography variant="body2" color="primary">
          Target: {data.target}%
        </Typography>
        <Typography variant="body2" color="success.main">
          Days to mastery: {data.days}
        </Typography>
      </Box>
    );
  }
  return null;
};

CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.arrayOf(PropTypes.object),
};

/**
 * Prediction Panel Component
 * Displays skill mastery predictions with progress tracking
 */
// eslint-disable-next-line no-unused-vars
const PredictionPanel = ({ userId }) => {
  const theme = useTheme();
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all skill predictions
  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await learningAnalyticsService.getAllSkillPredictions();
      setPredictions(data);
    } catch (err) {
      console.error('Failed to fetch predictions:', err);
      setError(err.response?.data?.error || 'Failed to load predictions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, []);

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'info';
    if (confidence >= 0.4) return 'warning';
    return 'error';
  };

  // Get confidence label
  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    if (confidence >= 0.4) return 'Low';
    return 'Very Low';
  };

  // Get skill icon color based on progress
  const getSkillColor = (current, target) => {
    const progress = (current / target) * 100;
    if (progress >= 90) return theme.palette.success.main;
    if (progress >= 75) return theme.palette.info.main;
    if (progress >= 60) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  // Calculate days until date
  const getDaysUntil = (dateString) => {
    if (!dateString) return null;
    const targetDate = new Date(dateString);
    const today = new Date();
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 0;
  };

  // Get priority recommendations
  const getPriorityRecommendations = () => {
    if (predictions.length === 0) return [];

    // Sort by days to mastery (ascending) - skills that will master soonest
    const sorted = [...predictions].sort((a, b) => {
      const daysA = getDaysUntil(a.predicted_date) || 999;
      const daysB = getDaysUntil(b.predicted_date) || 999;
      return daysA - daysB;
    });

    return sorted.slice(0, 3); // Top 3 priorities
  };

  // Transform data for chart
  const getChartData = () => {
    return predictions.map(pred => ({
      skill: pred.skill_name.charAt(0).toUpperCase() + pred.skill_name.slice(1),
      current: pred.current_proficiency,
      target: pred.predicted_proficiency,
      days: getDaysUntil(pred.predicted_date) || 0,
      confidence: pred.confidence,
    }));
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
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
          <Alert severity="error" onClose={() => fetchPredictions()}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (predictions.length === 0) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            No prediction data available yet. Complete more activities to generate predictions!
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const chartData = getChartData();
  const priorities = getPriorityRecommendations();

  return (
    <Box>
      {/* Priority Recommendations */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <EmojiEvents color="warning" />
            <Typography variant="h6">Priority Focus Areas</Typography>
          </Box>
          <Grid container spacing={2}>
            {priorities.map((pred, index) => {
              const days = getDaysUntil(pred.predicted_date);
              return (
                <Grid item xs={12} md={4} key={pred.skill_name}>
                  <Card
                    variant="outlined"
                    sx={{
                      borderColor:
                        index === 0
                          ? theme.palette.warning.main
                          : theme.palette.divider,
                      borderWidth: index === 0 ? 2 : 1,
                    }}
                  >
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {pred.skill_name.charAt(0).toUpperCase() + pred.skill_name.slice(1)}
                        </Typography>
                        {index === 0 && (
                          <Chip label="Top Priority" color="warning" size="small" />
                        )}
                      </Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {pred.current_proficiency.toFixed(1)}% → {pred.predicted_proficiency.toFixed(1)}%
                      </Typography>
                      <Box display="flex" alignItems="center" gap={0.5} mt={1}>
                        <AccessTime fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {days} days to mastery
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </CardContent>
      </Card>

      {/* Skill Mastery Predictions Grid */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Psychology color="primary" />
            <Typography variant="h6">Skill Mastery Predictions</Typography>
          </Box>
          <Grid container spacing={2}>
            {predictions.map(pred => {
              const days = getDaysUntil(pred.predicted_date);
              const progress = (pred.current_proficiency / pred.predicted_proficiency) * 100;
              const skillColor = getSkillColor(pred.current_proficiency, pred.predicted_proficiency);

              return (
                <Grid item xs={12} md={6} key={pred.skill_name}>
                  <Card variant="outlined">
                    <CardContent>
                      {/* Skill Header */}
                      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <TrendingUp sx={{ color: skillColor }} />
                          <Typography variant="h6">
                            {pred.skill_name.charAt(0).toUpperCase() + pred.skill_name.slice(1)}
                          </Typography>
                        </Box>
                        <Chip
                          label={getConfidenceLabel(pred.confidence)}
                          color={getConfidenceColor(pred.confidence)}
                          size="small"
                        />
                      </Box>

                      {/* Current vs Target */}
                      <Box mb={2}>
                        <Box display="flex" justifyContent="space-between" mb={0.5}>
                          <Typography variant="body2" color="text.secondary">
                            Current: {pred.current_proficiency.toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" color="primary">
                            Target: {pred.predicted_proficiency.toFixed(1)}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min(progress, 100)}
                          sx={{
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: theme.palette.grey[200],
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: skillColor,
                            },
                          }}
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                          {progress.toFixed(0)}% of target achieved
                        </Typography>
                      </Box>

                      {/* Prediction Details */}
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Box
                            sx={{
                              backgroundColor: theme.palette.grey[50],
                              borderRadius: 1,
                              p: 1,
                            }}
                          >
                            <Typography variant="caption" color="text.secondary">
                              Predicted Date
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {formatDate(pred.predicted_date)}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={6}>
                          <Box
                            sx={{
                              backgroundColor: theme.palette.grey[50],
                              borderRadius: 1,
                              p: 1,
                            }}
                          >
                            <Typography variant="caption" color="text.secondary">
                              Days to Mastery
                            </Typography>
                            <Typography variant="body2" fontWeight="bold" color="success.main">
                              {days !== null ? `${days} days` : 'Unknown'}
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>

                      {/* Milestone Indicator */}
                      {progress >= 90 && (
                        <Box
                          display="flex"
                          alignItems="center"
                          gap={0.5}
                          mt={1}
                          sx={{
                            backgroundColor: theme.palette.success.light + '20',
                            borderRadius: 1,
                            p: 0.5,
                          }}
                        >
                          <CheckCircle fontSize="small" color="success" />
                          <Typography variant="caption" color="success.main" fontWeight="bold">
                            Nearly there! Keep up the excellent work!
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </CardContent>
      </Card>

      {/* Prediction Timeline Chart */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Mastery Timeline Comparison
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Compare current proficiency vs target proficiency across all skills
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
              <XAxis
                dataKey="skill"
                stroke={theme.palette.text.secondary}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                stroke={theme.palette.text.secondary}
                domain={[0, 100]}
                label={{ value: 'Proficiency %', angle: -90, position: 'insideLeft' }}
              />
              <RechartsTooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="current" name="Current Proficiency" fill={theme.palette.info.main}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={getSkillColor(entry.current, entry.target)}
                  />
                ))}
              </Bar>
              <Bar dataKey="target" name="Target Proficiency" fill={theme.palette.success.main} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Info Note */}
      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="body2">
          Predictions are based on your current learning velocity, consistency, and historical
          progress. Keep maintaining your study routine to achieve these targets!
        </Typography>
      </Alert>
    </Box>
  );
};

PredictionPanel.propTypes = {
  userId: PropTypes.number,
};

export default PredictionPanel;
