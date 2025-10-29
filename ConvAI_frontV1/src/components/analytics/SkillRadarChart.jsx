import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardContent,
  Typography,
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
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from 'recharts';
import learningAnalyticsService from '../../services/learningAnalyticsService';

/**
 * Custom Tooltip for Radar Chart
 */
const CustomTooltip = ({ active, payload }) => {
  const theme = useTheme();

  if (active && payload && payload.length) {
    const data = payload[0];
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
          {data.payload.skill}
        </Typography>
        <Typography variant="body2" color="primary">
          Proficiency: {data.value.toFixed(1)}%
        </Typography>
        {data.payload.level && (
          <Typography variant="caption" color="text.secondary">
            Level: {data.payload.level}
          </Typography>
        )}
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
 * Skill Radar Chart Component
 * Displays 6D radar chart for language skill proficiencies
 */
// eslint-disable-next-line no-unused-vars
const SkillRadarChart = ({ userId }) => {
  const theme = useTheme();
  const [skillData, setSkillData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('current');
  const [comparisonData, setComparisonData] = useState(null);

  // Fetch skill radar data
  const fetchSkillData = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await learningAnalyticsService.getSkillRadarData();
      setSkillData(data);

      // Optionally fetch comparison data (peer average)
      if (timeRange === 'comparison') {
        try {
          const comparisons = await learningAnalyticsService.getComparisonInsights();
          if (comparisons && comparisons.length > 0) {
            // Extract peer averages for each skill
            const peerData = comparisons
              .filter(c => c.comparison_type === 'vs_peers')
              .map(c => ({
                skill: c.metric_name.replace('_proficiency', '').replace('_', ' '),
                peerValue: c.peer_average || 0,
              }));
            setComparisonData(peerData);
          }
        } catch (err) {
          console.error('Failed to fetch comparison data:', err);
          // Non-critical error, continue with current data
        }
      }
    } catch (err) {
      console.error('Failed to fetch skill radar data:', err);
      setError(err.response?.data?.error || 'Failed to load skill data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkillData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeRange]);

  // Transform data for radar chart
  const getChartData = () => {
    if (!skillData) return [];

    const skills = [
      { key: 'reading', name: 'Reading' },
      { key: 'writing', name: 'Writing' },
      { key: 'listening', name: 'Listening' },
      { key: 'speaking', name: 'Speaking' },
      { key: 'grammar', name: 'Grammar' },
      { key: 'vocabulary', name: 'Vocabulary' },
    ];

    return skills.map(skill => {
      const currentValue = skillData[`${skill.key}_proficiency`] || 0;
      const dataPoint = {
        skill: skill.name,
        current: currentValue,
        level: getProficiencyLevel(currentValue),
      };

      // Add peer comparison if available
      if (timeRange === 'comparison' && comparisonData) {
        const peerSkill = comparisonData.find(
          p => p.skill.toLowerCase() === skill.name.toLowerCase()
        );
        if (peerSkill) {
          dataPoint.peer = peerSkill.peerValue;
        }
      }

      return dataPoint;
    });
  };

  // Get proficiency level label
  const getProficiencyLevel = (value) => {
    if (value >= 90) return 'Expert';
    if (value >= 75) return 'Advanced';
    if (value >= 60) return 'Intermediate';
    if (value >= 40) return 'Developing';
    if (value >= 20) return 'Beginning';
    return 'Novice';
  };

  // Get color based on proficiency
  const getProficiencyColor = (value) => {
    if (value >= 90) return theme.palette.success.main;
    if (value >= 75) return theme.palette.info.main;
    if (value >= 60) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  // Calculate average proficiency
  const getAverageProficiency = () => {
    if (!skillData) return 0;
    const skills = ['reading', 'writing', 'listening', 'speaking', 'grammar', 'vocabulary'];
    const sum = skills.reduce(
      (acc, skill) => acc + (skillData[`${skill}_proficiency`] || 0),
      0
    );
    return (sum / skills.length).toFixed(1);
  };

  // Handle time range change
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
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
          <Alert severity="error" onClose={() => fetchSkillData()}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const chartData = getChartData();
  const avgProficiency = getAverageProficiency();

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h6" gutterBottom>
              Skill Proficiency Radar
            </Typography>
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="body2" color="text.secondary">
                Average Proficiency:
              </Typography>
              <Chip
                label={`${avgProficiency}%`}
                size="small"
                color={
                  avgProficiency >= 75 ? 'success' : avgProficiency >= 60 ? 'info' : 'warning'
                }
              />
            </Box>
          </Box>

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>View</InputLabel>
            <Select value={timeRange} onChange={handleTimeRangeChange} label="View">
              <MenuItem value="current">Current</MenuItem>
              <MenuItem value="comparison">vs Peers</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Radar Chart */}
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={chartData}>
            <PolarGrid stroke={theme.palette.divider} />
            <PolarAngleAxis
              dataKey="skill"
              tick={{ fill: theme.palette.text.primary, fontSize: 12 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: theme.palette.text.secondary, fontSize: 10 }}
            />
            <Radar
              name="Your Proficiency"
              dataKey="current"
              stroke={theme.palette.primary.main}
              fill={theme.palette.primary.main}
              fillOpacity={0.6}
            />
            {timeRange === 'comparison' && comparisonData && (
              <Radar
                name="Peer Average"
                dataKey="peer"
                stroke={theme.palette.secondary.main}
                fill={theme.palette.secondary.main}
                fillOpacity={0.3}
              />
            )}
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>

        {/* Skill Breakdown */}
        <Box mt={3}>
          <Typography variant="subtitle2" gutterBottom>
            Skill Breakdown
          </Typography>
          <Box display="flex" flexDirection="column" gap={1}>
            {chartData.map((skill) => (
              <Box
                key={skill.skill}
                display="flex"
                justifyContent="space-between"
                alignItems="center"
              >
                <Typography variant="body2" sx={{ minWidth: 100 }}>
                  {skill.skill}
                </Typography>
                <Box display="flex" alignItems="center" gap={1} flex={1}>
                  <Box
                    sx={{
                      height: 8,
                      flex: 1,
                      backgroundColor: theme.palette.grey[200],
                      borderRadius: 4,
                      overflow: 'hidden',
                    }}
                  >
                    <Box
                      sx={{
                        height: '100%',
                        width: `${skill.current}%`,
                        backgroundColor: getProficiencyColor(skill.current),
                        transition: 'width 0.3s ease',
                      }}
                    />
                  </Box>
                  <Typography variant="caption" sx={{ minWidth: 45, textAlign: 'right' }}>
                    {skill.current.toFixed(1)}%
                  </Typography>
                  <Chip
                    label={skill.level}
                    size="small"
                    sx={{
                      minWidth: 100,
                      backgroundColor: `${getProficiencyColor(skill.current)}20`,
                      color: getProficiencyColor(skill.current),
                      fontWeight: 'bold',
                    }}
                  />
                </Box>
              </Box>
            ))}
          </Box>
        </Box>

        {/* Comparison Note */}
        {timeRange === 'comparison' && comparisonData && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Peer comparison shows anonymized average proficiency of learners at your level.
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

SkillRadarChart.propTypes = {
  userId: PropTypes.number,
};

export default SkillRadarChart;
