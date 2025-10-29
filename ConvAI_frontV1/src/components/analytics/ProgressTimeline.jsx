import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardContent,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Chip,
  useTheme,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  TrendingUp,
  ShowChart,
  BarChart as BarChartIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import learningAnalyticsService from '../../services/learningAnalyticsService';

/**
 * Custom Tooltip for Progress Charts
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
            {entry.name}: {entry.value.toFixed(1)}
            {entry.name.includes('Proficiency') ? '%' : ''}
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
 * Progress Timeline Component
 * Displays historical progress data with multiple visualization options
 */
// eslint-disable-next-line no-unused-vars
const ProgressTimeline = ({ userId }) => {
  const theme = useTheme();
  // eslint-disable-next-line no-unused-vars
  const [progressData, setProgressData] = useState(null);
  const [snapshotData, setSnapshotData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // View options
  const [timeRange, setTimeRange] = useState('30d');
  const [chartType, setChartType] = useState('line');
  const [metric, setMetric] = useState('overall');

  // Fetch progress data
  const fetchProgressData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch progress visualization data
      const progressViz = await learningAnalyticsService.getProgressVisualization(timeRange);
      setProgressData(progressViz);

      // Fetch snapshot history
      const snapshots = await learningAnalyticsService.getSnapshotHistory(
        getDaysFromTimeRange(timeRange)
      );
      setSnapshotData(snapshots);
    } catch (err) {
      console.error('Failed to fetch progress data:', err);
      setError(err.response?.data?.error || 'Failed to load progress data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProgressData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeRange]);

  // Convert time range to days
  const getDaysFromTimeRange = (range) => {
    const rangeMap = {
      '7d': 7,
      '30d': 30,
      '90d': 90,
      '1y': 365,
      'all': 999,
    };
    return rangeMap[range] || 30;
  };

  // Format date for display
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
    return date.toLocaleDateString();
  };

  // Transform data for charts
  const getChartData = () => {
    if (!snapshotData || snapshotData.length === 0) return [];

    return snapshotData.map(snapshot => {
      const dataPoint = {
        date: formatDate(snapshot.snapshot_date),
        fullDate: new Date(snapshot.snapshot_date).toLocaleDateString(),
      };

      if (metric === 'overall') {
        // Overall progress (average of all skills)
        const avgProficiency =
          (snapshot.reading_proficiency +
            snapshot.writing_proficiency +
            snapshot.listening_proficiency +
            snapshot.speaking_proficiency +
            snapshot.grammar_proficiency +
            snapshot.vocabulary_proficiency) /
          6;
        dataPoint['Overall Proficiency'] = avgProficiency;
      } else if (metric === 'skills') {
        // All 6 skills
        dataPoint['Reading'] = snapshot.reading_proficiency;
        dataPoint['Writing'] = snapshot.writing_proficiency;
        dataPoint['Listening'] = snapshot.listening_proficiency;
        dataPoint['Speaking'] = snapshot.speaking_proficiency;
        dataPoint['Grammar'] = snapshot.grammar_proficiency;
        dataPoint['Vocabulary'] = snapshot.vocabulary_proficiency;
      } else if (metric === 'velocity') {
        // Learning velocity
        dataPoint['Velocity'] = snapshot.learning_velocity || 0;
      } else {
        // Individual skill
        const skillKey = `${metric}_proficiency`;
        dataPoint[metric.charAt(0).toUpperCase() + metric.slice(1)] = snapshot[skillKey] || 0;
      }

      return dataPoint;
    });
  };

  // Get metric options
  const getMetricOptions = () => [
    { value: 'overall', label: 'Overall Progress' },
    { value: 'skills', label: 'All Skills' },
    { value: 'velocity', label: 'Learning Velocity' },
    { value: 'reading', label: 'Reading' },
    { value: 'writing', label: 'Writing' },
    { value: 'listening', label: 'Listening' },
    { value: 'speaking', label: 'Speaking' },
    { value: 'grammar', label: 'Grammar' },
    { value: 'vocabulary', label: 'Vocabulary' },
  ];

  // Get statistics
  const getStatistics = () => {
    if (!snapshotData || snapshotData.length < 2) return null;

    const latest = snapshotData[snapshotData.length - 1];
    const oldest = snapshotData[0];

    let currentValue = 0;
    let oldValue = 0;

    if (metric === 'overall') {
      currentValue =
        (latest.reading_proficiency +
          latest.writing_proficiency +
          latest.listening_proficiency +
          latest.speaking_proficiency +
          latest.grammar_proficiency +
          latest.vocabulary_proficiency) /
        6;
      oldValue =
        (oldest.reading_proficiency +
          oldest.writing_proficiency +
          oldest.listening_proficiency +
          oldest.speaking_proficiency +
          oldest.grammar_proficiency +
          oldest.vocabulary_proficiency) /
        6;
    } else if (metric === 'velocity') {
      currentValue = latest.learning_velocity || 0;
      oldValue = oldest.learning_velocity || 0;
    } else if (metric !== 'skills') {
      const skillKey = `${metric}_proficiency`;
      currentValue = latest[skillKey] || 0;
      oldValue = oldest[skillKey] || 0;
    }

    const change = currentValue - oldValue;
    const percentChange = oldValue > 0 ? ((change / oldValue) * 100).toFixed(1) : 0;

    return {
      current: currentValue.toFixed(1),
      change: change.toFixed(1),
      percentChange,
      trend: change >= 0 ? 'up' : 'down',
    };
  };

  // Handle time range change
  const handleTimeRangeChange = (event, newValue) => {
    if (newValue !== null) {
      setTimeRange(newValue);
    }
  };

  // Handle chart type change
  const handleChartTypeChange = (event, newValue) => {
    if (newValue !== null) {
      setChartType(newValue);
    }
  };

  // Handle metric change
  const handleMetricChange = (event) => {
    setMetric(event.target.value);
  };

  // Render chart based on type
  const renderChart = () => {
    const chartData = getChartData();
    if (chartData.length === 0) return null;

    const colors = [
      theme.palette.primary.main,
      theme.palette.secondary.main,
      theme.palette.success.main,
      theme.palette.warning.main,
      theme.palette.error.main,
      theme.palette.info.main,
    ];

    const dataKeys = Object.keys(chartData[0]).filter(key => key !== 'date' && key !== 'fullDate');

    const commonProps = {
      data: chartData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 },
    };

    const axisProps = {
      xAxis: { dataKey: 'date', stroke: theme.palette.text.secondary },
      yAxis: { stroke: theme.palette.text.secondary, domain: [0, 100] },
      cartesianGrid: { strokeDasharray: '3 3', stroke: theme.palette.divider },
      tooltip: <CustomTooltip />,
      legend: { wrapperStyle: { paddingTop: '20px' } },
    };

    if (chartType === 'line') {
      return (
        <LineChart {...commonProps}>
          <CartesianGrid {...axisProps.cartesianGrid} />
          <XAxis {...axisProps.xAxis} />
          <YAxis {...axisProps.yAxis} />
          <Tooltip content={axisProps.tooltip} />
          <Legend {...axisProps.legend} />
          {dataKeys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      );
    }

    if (chartType === 'area') {
      return (
        <AreaChart {...commonProps}>
          <CartesianGrid {...axisProps.cartesianGrid} />
          <XAxis {...axisProps.xAxis} />
          <YAxis {...axisProps.yAxis} />
          <Tooltip content={axisProps.tooltip} />
          <Legend {...axisProps.legend} />
          {dataKeys.map((key, index) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stroke={colors[index % colors.length]}
              fill={colors[index % colors.length]}
              fillOpacity={0.6}
            />
          ))}
        </AreaChart>
      );
    }

    if (chartType === 'bar') {
      return (
        <BarChart {...commonProps}>
          <CartesianGrid {...axisProps.cartesianGrid} />
          <XAxis {...axisProps.xAxis} />
          <YAxis {...axisProps.yAxis} />
          <Tooltip content={axisProps.tooltip} />
          <Legend {...axisProps.legend} />
          {dataKeys.map((key, index) => (
            <Bar key={key} dataKey={key} fill={colors[index % colors.length]} />
          ))}
        </BarChart>
      );
    }

    return null;
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
          <Alert severity="error" onClose={() => fetchProgressData()}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const stats = getStatistics();

  return (
    <Card>
      <CardContent>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <TimelineIcon color="primary" />
            <Typography variant="h6">Progress Timeline</Typography>
          </Box>

          {stats && (
            <Box display="flex" alignItems="center" gap={1}>
              <Chip
                icon={stats.trend === 'up' ? <TrendingUp /> : undefined}
                label={`${stats.change > 0 ? '+' : ''}${stats.change} (${
                  stats.percentChange > 0 ? '+' : ''
                }${stats.percentChange}%)`}
                color={stats.trend === 'up' ? 'success' : 'error'}
                size="small"
              />
            </Box>
          )}
        </Box>

        {/* Controls */}
        <Box display="flex" gap={2} mb={3} flexWrap="wrap">
          {/* Time Range */}
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={handleTimeRangeChange}
            size="small"
          >
            <ToggleButton value="7d">7 Days</ToggleButton>
            <ToggleButton value="30d">30 Days</ToggleButton>
            <ToggleButton value="90d">90 Days</ToggleButton>
            <ToggleButton value="1y">1 Year</ToggleButton>
            <ToggleButton value="all">All Time</ToggleButton>
          </ToggleButtonGroup>

          {/* Chart Type */}
          <ToggleButtonGroup
            value={chartType}
            exclusive
            onChange={handleChartTypeChange}
            size="small"
          >
            <ToggleButton value="line">
              <ShowChart fontSize="small" />
            </ToggleButton>
            <ToggleButton value="area">
              <TimelineIcon fontSize="small" />
            </ToggleButton>
            <ToggleButton value="bar">
              <BarChartIcon fontSize="small" />
            </ToggleButton>
          </ToggleButtonGroup>

          {/* Metric Selection */}
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Metric</InputLabel>
            <Select value={metric} onChange={handleMetricChange} label="Metric">
              {getMetricOptions().map(option => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {/* Chart */}
        {snapshotData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            {renderChart()}
          </ResponsiveContainer>
        ) : (
          <Alert severity="info">
            No progress data available for the selected time range. Keep learning to see your
            progress!
          </Alert>
        )}

        {/* Data Points Info */}
        {snapshotData.length > 0 && (
          <Box mt={2}>
            <Typography variant="caption" color="text.secondary">
              Showing {snapshotData.length} data points from{' '}
              {new Date(snapshotData[0].snapshot_date).toLocaleDateString()} to{' '}
              {new Date(
                snapshotData[snapshotData.length - 1].snapshot_date
              ).toLocaleDateString()}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

ProgressTimeline.propTypes = {
  userId: PropTypes.number,
};

export default ProgressTimeline;
