import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Divider,
  LinearProgress,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Star,
  Lightbulb,
  Psychology,
  EmojiEvents,
} from '@mui/icons-material';
import learningAnalyticsService from '../../services/learningAnalyticsService';

/**
 * Weekly Report Card Component
 * Enhanced weekly summary with AI insights, strengths, weaknesses, and recommendations
 */
// eslint-disable-next-line no-unused-vars
const WeeklyReportCard = ({ userId, weekOffset = 0 }) => {
  const theme = useTheme();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch weekly report
  const fetchWeeklyReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await learningAnalyticsService.getWeeklyReport(weekOffset);
      setReport(data);
    } catch (err) {
      console.error('Failed to fetch weekly report:', err);
      setError(err.response?.data?.error || 'Failed to load weekly report');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeeklyReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weekOffset]);

  // Format duration (minutes to hours/minutes)
  const formatDuration = (minutes) => {
    if (!minutes) return '0m';
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  // Get consistency color
  const getConsistencyColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'info';
    if (score >= 0.4) return 'warning';
    return 'error';
  };

  // Get trend icon
  const getTrendIcon = (change) => {
    return change >= 0 ? <TrendingUp color="success" /> : <TrendingDown color="error" />;
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
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
          <Alert severity="error" onClose={() => fetchWeeklyReport()}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!report) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            No weekly report available yet. Complete some activities to generate your report!
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card elevation={3}>
      <CardContent>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h5" fontWeight="bold">
              Weekly Learning Report
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {new Date(report.week_start).toLocaleDateString()} -{' '}
              {new Date(report.week_end).toLocaleDateString()}
            </Typography>
          </Box>
          <Chip
            icon={<EmojiEvents />}
            label={`${report.total_points || 0} Points`}
            color="primary"
            size="large"
          />
        </Box>

        {/* Key Metrics Grid */}
        <Grid container spacing={2} mb={3}>
          {/* Study Time */}
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined" sx={{ backgroundColor: theme.palette.primary.light + '10' }}>
              <CardContent>
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  Study Time
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="primary">
                  {formatDuration(report.total_study_time)}
                </Typography>
                {report.study_time_change !== undefined && (
                  <Box display="flex" alignItems="center" gap={0.5} mt={1}>
                    {getTrendIcon(report.study_time_change)}
                    <Typography variant="caption" color="text.secondary">
                      {report.study_time_change > 0 ? '+' : ''}
                      {report.study_time_change}% from last week
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Activities Completed */}
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined" sx={{ backgroundColor: theme.palette.success.light + '10' }}>
              <CardContent>
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  Activities
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {report.activities_completed || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Completed this week
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Consistency Score */}
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined" sx={{ backgroundColor: theme.palette.info.light + '10' }}>
              <CardContent>
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  Consistency
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="info.main">
                  {((report.consistency_score || 0) * 100).toFixed(0)}%
                </Typography>
                <Box mt={1}>
                  <LinearProgress
                    variant="determinate"
                    value={(report.consistency_score || 0) * 100}
                    color={getConsistencyColor(report.consistency_score)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Streak Days */}
          <Grid item xs={12} sm={6} md={3}>
            <Card variant="outlined" sx={{ backgroundColor: theme.palette.warning.light + '10' }}>
              <CardContent>
                <Typography variant="caption" color="text.secondary" gutterBottom>
                  Current Streak
                </Typography>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  {report.streak_days || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Days in a row
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        {/* AI Insights Section */}
        {report.ai_insights && (
          <Box mb={3}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Psychology color="primary" />
              <Typography variant="h6" fontWeight="bold">
                AI Insights
              </Typography>
            </Box>
            <Card
              variant="outlined"
              sx={{
                backgroundColor: theme.palette.info.light + '05',
                borderColor: theme.palette.info.main,
              }}
            >
              <CardContent>
                <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                  {report.ai_insights}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        )}

        {/* Strengths Section */}
        {report.strengths && report.strengths.length > 0 && (
          <Box mb={3}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Star color="success" />
              <Typography variant="h6" fontWeight="bold">
                Your Strengths
              </Typography>
            </Box>
            <Card
              variant="outlined"
              sx={{
                backgroundColor: theme.palette.success.light + '05',
                borderColor: theme.palette.success.main,
              }}
            >
              <CardContent>
                <List dense>
                  {report.strengths.map((strength, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <CheckCircle color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={strength}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Box>
        )}

        {/* Areas for Improvement */}
        {report.areas_for_improvement && report.areas_for_improvement.length > 0 && (
          <Box mb={3}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <TrendingUp color="warning" />
              <Typography variant="h6" fontWeight="bold">
                Areas for Improvement
              </Typography>
            </Box>
            <Card
              variant="outlined"
              sx={{
                backgroundColor: theme.palette.warning.light + '05',
                borderColor: theme.palette.warning.main,
              }}
            >
              <CardContent>
                <List dense>
                  {report.areas_for_improvement.map((area, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <TrendingUp color="warning" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={area} primaryTypographyProps={{ variant: 'body2' }} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Box>
        )}

        {/* Recommendations */}
        {report.recommendations && report.recommendations.length > 0 && (
          <Box>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Lightbulb color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Recommendations
              </Typography>
            </Box>
            <Card
              variant="outlined"
              sx={{
                backgroundColor: theme.palette.primary.light + '05',
                borderColor: theme.palette.primary.main,
              }}
            >
              <CardContent>
                <List dense>
                  {report.recommendations.map((rec, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        <Lightbulb color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText primary={rec} primaryTypographyProps={{ variant: 'body2' }} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Box>
        )}

        {/* Achievements */}
        {report.achievements && report.achievements.length > 0 && (
          <Box mt={3}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <EmojiEvents color="warning" />
              <Typography variant="h6" fontWeight="bold">
                Achievements This Week
              </Typography>
            </Box>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {report.achievements.map((achievement, index) => (
                <Chip
                  key={index}
                  label={achievement}
                  color="warning"
                  icon={<Star />}
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

WeeklyReportCard.propTypes = {
  userId: PropTypes.number,
  weekOffset: PropTypes.number,
};

export default WeeklyReportCard;
