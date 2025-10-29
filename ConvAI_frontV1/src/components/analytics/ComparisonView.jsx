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
  Tabs,
  Tab,
  useTheme,
  LinearProgress,
} from '@mui/material';
import {
  CompareArrows,
  TrendingUp,
  TrendingDown,
  Person,
  Group,
  Timeline,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';
import learningAnalyticsService from '../../services/learningAnalyticsService';

/**
 * Custom Tooltip for Comparison Chart
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
          {data.metric}
        </Typography>
        <Typography variant="body2" color="primary">
          Your Value: {data.yourValue.toFixed(1)}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Peer Average: {data.peerValue.toFixed(1)}
        </Typography>
        <Typography variant="body2" color="success.main">
          Difference: {data.difference > 0 ? '+' : ''}{data.difference.toFixed(1)}
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
 * Tab Panel Component
 */
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`comparison-tabpanel-${index}`}
      aria-labelledby={`comparison-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  value: PropTypes.number.isRequired,
  index: PropTypes.number.isRequired,
};

/**
 * Comparison View Component
 * Peer comparison visualization with multiple comparison types
 */
// eslint-disable-next-line no-unused-vars
const ComparisonView = ({ userId }) => {
  const theme = useTheme();
  const [comparisons, setComparisons] = useState([]);
  const [percentiles, setPercentiles] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentTab, setCurrentTab] = useState(0);

  // Fetch comparison data
  const fetchComparisonData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch all comparison insights
      const comparisonData = await learningAnalyticsService.getComparisonInsights();
      setComparisons(comparisonData);

      // Fetch percentiles for key metrics
      const metrics = [
        'overall_proficiency',
        'study_time',
        'activities_completed',
        'consistency_score',
      ];
      const percentileData = {};
      await Promise.all(
        metrics.map(async (metric) => {
          try {
            const result = await learningAnalyticsService.getPercentileRanking(metric);
            percentileData[metric] = result;
          } catch (err) {
            console.error(`Failed to fetch percentile for ${metric}:`, err);
          }
        })
      );
      setPercentiles(percentileData);
    } catch (err) {
      console.error('Failed to fetch comparison data:', err);
      setError(err.response?.data?.error || 'Failed to load comparison data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComparisonData();
  }, []);

  // Filter comparisons by type
  const getComparisonsByType = (type) => {
    return comparisons.filter((c) => c.comparison_type === type);
  };

  // Get comparison color
  const getComparisonColor = (difference) => {
    if (difference > 5) return theme.palette.success.main;
    if (difference > 0) return theme.palette.info.main;
    if (difference > -5) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  // Get percentile color
  const getPercentileColor = (percentile) => {
    if (percentile >= 90) return 'success';
    if (percentile >= 75) return 'info';
    if (percentile >= 50) return 'warning';
    return 'error';
  };

  // Transform data for chart
  const getChartData = (type) => {
    const filtered = getComparisonsByType(type);
    return filtered.map((comp) => ({
      metric: comp.metric_name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
      yourValue: comp.your_value || 0,
      peerValue: comp.peer_average || 0,
      difference: (comp.your_value || 0) - (comp.peer_average || 0),
    }));
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
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
          <Alert severity="error" onClose={() => fetchComparisonData()}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (comparisons.length === 0) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            No comparison data available yet. Complete more activities to see how you compare to peers!
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const vsSelfData = getChartData('vs_self');
  const vsPeersData = getChartData('vs_peers');
  const vsExpectedData = getChartData('vs_expected');

  return (
    <Box>
      {/* Percentile Rankings Card */}
      {Object.keys(percentiles).length > 0 && (
        <Card elevation={3} sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <CompareArrows color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Your Percentile Rankings
              </Typography>
            </Box>
            <Grid container spacing={2}>
              {Object.entries(percentiles).map(([metric, data]) => (
                <Grid item xs={12} sm={6} md={3} key={metric}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="caption" color="text.secondary" gutterBottom>
                        {metric.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                      </Typography>
                      <Box display="flex" alignItems="baseline" gap={1} mb={1}>
                        <Typography variant="h3" fontWeight="bold" color="primary">
                          {data.percentile}
                        </Typography>
                        <Typography variant="h5" color="text.secondary">
                          %
                        </Typography>
                      </Box>
                      <Chip
                        label={`Top ${100 - data.percentile}%`}
                        color={getPercentileColor(data.percentile)}
                        size="small"
                      />
                      <Box mt={2}>
                        <LinearProgress
                          variant="determinate"
                          value={data.percentile}
                          color={getPercentileColor(data.percentile)}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                        Better than {data.percentile}% of peers
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Comparison Tabs */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Timeline color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Detailed Comparisons
            </Typography>
          </Box>

          <Tabs value={currentTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tab icon={<Person />} label="vs Self" />
            <Tab icon={<Group />} label="vs Peers" />
            <Tab icon={<Timeline />} label="vs Expected" />
          </Tabs>

          {/* vs Self Tab */}
          <TabPanel value={currentTab} index={0}>
            {vsSelfData.length > 0 ? (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Compare your current performance to your past performance. Positive values indicate improvement!
                </Alert>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={vsSelfData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                    <XAxis dataKey="metric" stroke={theme.palette.text.secondary} />
                    <YAxis stroke={theme.palette.text.secondary} />
                    <RechartsTooltip content={<CustomTooltip />} />
                    <ReferenceLine y={0} stroke={theme.palette.text.disabled} />
                    <Bar dataKey="difference" name="Change from Past">
                      {vsSelfData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getComparisonColor(entry.difference)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  {vsSelfData.map((comp, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            {comp.metric}
                          </Typography>
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="body2" color="text.secondary">
                              Past: {comp.peerValue.toFixed(1)}
                            </Typography>
                            <Typography variant="body2" color="primary" fontWeight="bold">
                              Now: {comp.yourValue.toFixed(1)}
                            </Typography>
                            <Chip
                              icon={comp.difference >= 0 ? <TrendingUp /> : <TrendingDown />}
                              label={`${comp.difference > 0 ? '+' : ''}${comp.difference.toFixed(1)}`}
                              color={comp.difference >= 0 ? 'success' : 'error'}
                              size="small"
                            />
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </>
            ) : (
              <Alert severity="info">No self-comparison data available yet.</Alert>
            )}
          </TabPanel>

          {/* vs Peers Tab */}
          <TabPanel value={currentTab} index={1}>
            {vsPeersData.length > 0 ? (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Compare your performance to anonymized peer averages at your level. See how you stack up!
                </Alert>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={vsPeersData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                    <XAxis dataKey="metric" stroke={theme.palette.text.secondary} />
                    <YAxis stroke={theme.palette.text.secondary} />
                    <RechartsTooltip content={<CustomTooltip />} />
                    <Bar dataKey="yourValue" name="Your Value" fill={theme.palette.primary.main} />
                    <Bar dataKey="peerValue" name="Peer Average" fill={theme.palette.secondary.main} />
                  </BarChart>
                </ResponsiveContainer>
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  {vsPeersData.map((comp, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            {comp.metric}
                          </Typography>
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="body2" color="text.secondary">
                              Peers: {comp.peerValue.toFixed(1)}
                            </Typography>
                            <Typography variant="body2" color="primary" fontWeight="bold">
                              You: {comp.yourValue.toFixed(1)}
                            </Typography>
                            <Chip
                              icon={comp.difference >= 0 ? <TrendingUp /> : <TrendingDown />}
                              label={`${comp.difference > 0 ? '+' : ''}${comp.difference.toFixed(1)}`}
                              color={comp.difference >= 0 ? 'success' : 'warning'}
                              size="small"
                            />
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </>
            ) : (
              <Alert severity="info">No peer comparison data available yet.</Alert>
            )}
          </TabPanel>

          {/* vs Expected Tab */}
          <TabPanel value={currentTab} index={2}>
            {vsExpectedData.length > 0 ? (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Compare your performance to expected benchmarks for your level. Are you on track?
                </Alert>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={vsExpectedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                    <XAxis dataKey="metric" stroke={theme.palette.text.secondary} />
                    <YAxis stroke={theme.palette.text.secondary} />
                    <RechartsTooltip content={<CustomTooltip />} />
                    <Bar dataKey="yourValue" name="Your Value" fill={theme.palette.primary.main} />
                    <Bar dataKey="peerValue" name="Expected Value" fill={theme.palette.warning.main} />
                  </BarChart>
                </ResponsiveContainer>
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  {vsExpectedData.map((comp, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            {comp.metric}
                          </Typography>
                          <Box display="flex" justifyContent="space-between" alignItems="center">
                            <Typography variant="body2" color="text.secondary">
                              Expected: {comp.peerValue.toFixed(1)}
                            </Typography>
                            <Typography variant="body2" color="primary" fontWeight="bold">
                              You: {comp.yourValue.toFixed(1)}
                            </Typography>
                            <Chip
                              icon={comp.difference >= 0 ? <TrendingUp /> : <TrendingDown />}
                              label={`${comp.difference > 0 ? '+' : ''}${comp.difference.toFixed(1)}`}
                              color={comp.difference >= 0 ? 'success' : 'info'}
                              size="small"
                            />
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </>
            ) : (
              <Alert severity="info">No expected comparison data available yet.</Alert>
            )}
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
};

ComparisonView.propTypes = {
  userId: PropTypes.number,
};

export default ComparisonView;
