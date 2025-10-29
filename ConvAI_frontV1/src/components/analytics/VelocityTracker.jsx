import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import {
  Speed,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Schedule,
  Whatshot,
  AccessTime,
} from '@mui/icons-material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import learningAnalyticsService from '../../services/learningAnalyticsService';

/**
 * Custom Tooltip for Velocity Chart
 */
const CustomTooltip = ({ active, payload, label }) => {
  const theme = useTheme();

  if (active && payload && payload.length) {
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
          {label}
        </Typography>
        {payload.map((entry, index) => (
          <Typography key={index} variant="body2" sx={{ color: entry.color }}>
            {entry.name}: {entry.value.toFixed(2)}
          </Typography>
        ))}
      </Box>
    );
  }
  return null;
};

CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.arrayOf(PropTypes.object),
  label: PropTypes.string,
};

/**
 * Velocity Tracker Component
 * Enhanced velocity display with charts, gauges, and study recommendations
 */
// eslint-disable-next-line no-unused-vars
const VelocityTracker = ({ userId }) => {
  const theme = useTheme();
  const [velocity, setVelocity] = useState(null);
  const [schedule, setSchedule] = useState(null);
  const [velocityHistory, setVelocityHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState('week');

  // Fetch velocity data
  const fetchVelocityData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch current velocity
      const velocityData = await learningAnalyticsService.getLearningVelocity(period);
      setVelocity(velocityData);

      // Fetch optimal study schedule
      const scheduleData = await learningAnalyticsService.getOptimalStudySchedule();
      setSchedule(scheduleData);

      // Generate velocity history from snapshots
      const snapshots = await learningAnalyticsService.getSnapshotHistory(30);
      const history = snapshots
        .filter(s => s.learning_velocity !== null)
        .map(s => ({
          date: new Date(s.snapshot_date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
          }),
          velocity: s.learning_velocity,
        }))
        .slice(-14); // Last 14 days
      setVelocityHistory(history);
    } catch (err) {
      console.error('Failed to fetch velocity data:', err);
      setError(err.response?.data?.error || 'Failed to load velocity data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVelocityData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period]);

  // Get momentum display
  const getMomentumDisplay = (momentum) => {
    if (!momentum) return { label: 'Steady', color: 'default', icon: <TrendingFlat /> };
    
    const momentumValue = parseFloat(momentum);
    if (momentumValue > 0.15) {
      return { label: 'Accelerating', color: 'success', icon: <TrendingUp /> };
    } else if (momentumValue < -0.15) {
      return { label: 'Decelerating', color: 'error', icon: <TrendingDown /> };
    } else if (momentumValue > 0) {
      return { label: 'Building', color: 'info', icon: <TrendingUp /> };
    } else if (momentumValue < 0) {
      return { label: 'Slowing', color: 'warning', icon: <TrendingDown /> };
    }
    return { label: 'Steady', color: 'default', icon: <TrendingFlat /> };
  };

  // Get velocity color
  const getVelocityColor = (value) => {
    if (!value) return theme.palette.grey[500];
    if (value >= 1.5) return theme.palette.success.main;
    if (value >= 1.0) return theme.palette.info.main;
    if (value >= 0.5) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  // Get velocity gauge percentage
  const getVelocityGaugePercent = (value) => {
    if (!value) return 0;
    // Map velocity (0-2) to percentage (0-100)
    return Math.min((value / 2) * 100, 100);
  };

  // Get velocity rating
  const getVelocityRating = (value) => {
    if (!value) return 'No Data';
    if (value >= 1.5) return 'Excellent';
    if (value >= 1.0) return 'Good';
    if (value >= 0.5) return 'Fair';
    return 'Needs Improvement';
  };

  // Handle period change
  const handlePeriodChange = (event, newPeriod) => {
    if (newPeriod !== null) {
      setPeriod(newPeriod);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
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
          <Alert severity="error" onClose={() => fetchVelocityData()}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!velocity) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            No velocity data available yet. Complete activities to track your learning velocity!
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const momentum = getMomentumDisplay(velocity.momentum);
  const currentVelocity = velocity.current_velocity || 0;
  const avgVelocity = velocityHistory.length > 0
    ? velocityHistory.reduce((sum, v) => sum + v.velocity, 0) / velocityHistory.length
    : 0;

  return (
    <Box>
      {/* Main Velocity Card */}
      <Card elevation={3} sx={{ mb: 3 }}>
        <CardContent>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Box display="flex" alignItems="center" gap={1}>
              <Speed color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Learning Velocity
              </Typography>
            </Box>
            <ToggleButtonGroup
              value={period}
              exclusive
              onChange={handlePeriodChange}
              size="small"
            >
              <ToggleButton value="week">Week</ToggleButton>
              <ToggleButton value="month">Month</ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {/* Velocity Metrics Grid */}
          <Grid container spacing={2} mb={3}>
            {/* Current Velocity */}
            <Grid item xs={12} md={4}>
              <Card
                variant="outlined"
                sx={{
                  backgroundColor: getVelocityColor(currentVelocity) + '10',
                  borderColor: getVelocityColor(currentVelocity),
                  borderWidth: 2,
                }}
              >
                <CardContent>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Current Velocity
                  </Typography>
                  <Typography variant="h3" fontWeight="bold" sx={{ color: getVelocityColor(currentVelocity) }}>
                    {currentVelocity.toFixed(2)}
                  </Typography>
                  <Box mt={1}>
                    <Box
                      sx={{
                        height: 8,
                        backgroundColor: theme.palette.grey[200],
                        borderRadius: 4,
                        overflow: 'hidden',
                      }}
                    >
                      <Box
                        sx={{
                          height: '100%',
                          width: `${getVelocityGaugePercent(currentVelocity)}%`,
                          backgroundColor: getVelocityColor(currentVelocity),
                          transition: 'width 0.3s ease',
                        }}
                      />
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                      {getVelocityRating(currentVelocity)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Acceleration */}
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Acceleration
                  </Typography>
                  <Box display="flex" alignItems="baseline" gap={1}>
                    <Typography variant="h3" fontWeight="bold">
                      {velocity.acceleration >= 0 ? '+' : ''}
                      {(velocity.acceleration || 0).toFixed(2)}
                    </Typography>
                    {velocity.acceleration >= 0 ? (
                      <TrendingUp color="success" />
                    ) : (
                      <TrendingDown color="error" />
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    Change in velocity
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Momentum */}
            <Grid item xs={12} md={4}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Momentum
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    {momentum.icon}
                    <Typography variant="h4" fontWeight="bold">
                      {momentum.label}
                    </Typography>
                  </Box>
                  <Chip
                    icon={<Whatshot />}
                    label={`${((velocity.momentum || 0) * 100).toFixed(0)}%`}
                    color={momentum.color}
                    size="small"
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Velocity Trend Message */}
          {velocity.trend_message && (
            <Alert
              severity={velocity.acceleration >= 0 ? 'success' : 'info'}
              icon={velocity.acceleration >= 0 ? <TrendingUp /> : <TrendingFlat />}
            >
              {velocity.trend_message}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Velocity History Chart */}
      {velocityHistory.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Velocity Trend (Last 14 Days)
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={velocityHistory} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                <XAxis
                  dataKey="date"
                  stroke={theme.palette.text.secondary}
                  tick={{ fontSize: 11 }}
                />
                <YAxis stroke={theme.palette.text.secondary} domain={[0, 2]} />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine
                  y={avgVelocity}
                  stroke={theme.palette.info.main}
                  strokeDasharray="3 3"
                  label="Average"
                />
                <Area
                  type="monotone"
                  dataKey="velocity"
                  name="Velocity"
                  stroke={theme.palette.primary.main}
                  fill={theme.palette.primary.main}
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
            <Box mt={1}>
              <Typography variant="caption" color="text.secondary">
                Average velocity: {avgVelocity.toFixed(2)} | Current: {currentVelocity.toFixed(2)}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Optimal Study Schedule */}
      {schedule && schedule.recommended_times && schedule.recommended_times.length > 0 && (
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Schedule color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Optimal Study Schedule
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Based on your learning patterns, here are the best times for you to study:
            </Typography>
            <List>
              {schedule.recommended_times.map((time, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <AccessTime color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={time}
                    primaryTypographyProps={{ fontWeight: 'medium' }}
                  />
                </ListItem>
              ))}
            </List>
            {schedule.recommendation && (
              <Alert severity="info" sx={{ mt: 2 }}>
                {schedule.recommendation}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

VelocityTracker.propTypes = {
  userId: PropTypes.number,
};

export default VelocityTracker;
