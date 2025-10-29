/**
 * Analytics Dashboard - Phase 7
 * Main analytics dashboard with 4 tabs for comprehensive learning insights
 * 
 * Features:
 * - Overview Tab: Weekly report, skills radar, velocity
 * - Progress Tab: Timeline charts, skill progress, milestones
 * - Predictions Tab: Level completion, skill mastery predictions
 * - Insights Tab: AI insights, patterns, comparisons
 * 
 * @author GitHub Copilot
 * @date October 20, 2025
 * @phase 7 - Learning Analytics & Insights
 */

import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Container,
  Paper,
  Tabs,
  Tab,
  Typography,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Psychology as PsychologyIcon,
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';
import learningAnalyticsService from '../../services/learningAnalyticsService';
import SkillRadarChart from './SkillRadarChart';
import ProgressTimeline from './ProgressTimeline';
import PredictionPanel from './PredictionPanel';

// Tab Panel Component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analytics-tabpanel-${index}`}
      aria-labelledby={`analytics-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  value: PropTypes.number.isRequired,
  index: PropTypes.number.isRequired,
};

/**
 * Analytics Dashboard Component
 * Main container for all analytics visualizations
 */
const AnalyticsDashboard = () => {
  // Tab state
  const [currentTab, setCurrentTab] = useState(0);

  // Data states
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [skills, setSkills] = useState(null);
  const [velocity, setVelocity] = useState(null);
  const [insights, setInsights] = useState([]);
  const [prediction, setPrediction] = useState(null);

  // UI states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch all dashboard data on mount
   */
  useEffect(() => {
    fetchDashboardData();
  }, []);

  /**
   * Fetch dashboard data from API
   */
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await learningAnalyticsService.getDashboardData();

      setWeeklyReport(data.weeklyReport);
      setSkills(data.skills);
      setVelocity(data.velocity);
      setInsights(data.insights);
      setPrediction(data.prediction);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError(err.message || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle tab change
   */
  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  /**
   * Get velocity trend color
   */
  const getVelocityColor = (trend) => {
    switch (trend) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'error';
      default:
        return 'info';
    }
  };

  /**
   * Get momentum icon and color
   */
  const getMomentumDisplay = (momentum) => {
    const displays = {
      increasing: { label: 'Accelerating', color: 'success' },
      steady: { label: 'Steady', color: 'info' },
      decreasing: { label: 'Slowing', color: 'warning' },
    };
    return displays[momentum] || displays.steady;
  };

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading your analytics...
          </Typography>
        </Box>
      </Container>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 36 }} />
          Learning Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track your progress, get predictions, and discover personalized insights
        </Typography>
      </Box>

      {/* Main Content */}
      <Paper elevation={3}>
        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            aria-label="analytics tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab
              icon={<TrendingUpIcon />}
              label="Overview"
              id="analytics-tab-0"
              aria-controls="analytics-tabpanel-0"
            />
            <Tab
              icon={<TimelineIcon />}
              label="Progress"
              id="analytics-tab-1"
              aria-controls="analytics-tabpanel-1"
            />
            <Tab
              icon={<TrophyIcon />}
              label="Predictions"
              id="analytics-tab-2"
              aria-controls="analytics-tabpanel-2"
            />
            <Tab
              icon={<PsychologyIcon />}
              label="Insights"
              id="analytics-tab-3"
              aria-controls="analytics-tabpanel-3"
            />
          </Tabs>
        </Box>

        {/* Tab Panels */}
        
        {/* Overview Tab */}
        <TabPanel value={currentTab} index={0}>
          <Grid container spacing={3}>
            {/* Weekly Summary */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    This Week&apos;s Summary
                  </Typography>
                  {weeklyReport && (
                    <>
                      <Grid container spacing={2} sx={{ mt: 1 }}>
                        <Grid item xs={12} sm={4}>
                          <Box textAlign="center">
                            <Typography variant="h4" color="primary">
                              {weeklyReport.study_time_minutes || 0}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Minutes Studied
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Box textAlign="center">
                            <Typography variant="h4" color="primary">
                              {weeklyReport.activities_completed || 0}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Activities Completed
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={12} sm={4}>
                          <Box textAlign="center">
                            <Typography variant="h4" color="primary">
                              {weeklyReport.points_earned || 0}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Points Earned
                            </Typography>
                          </Box>
                        </Grid>
                      </Grid>

                      {/* AI Insights */}
                      {weeklyReport.ai_insights && (
                        <Box sx={{ mt: 3, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
                          <Typography variant="body1">
                            {weeklyReport.ai_insights}
                          </Typography>
                        </Box>
                      )}

                      {/* Consistency Score */}
                      <Box sx={{ mt: 3 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="body2" color="text.secondary">
                            Consistency Score
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {weeklyReport.consistency_score?.toFixed(0) || 0}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={weeklyReport.consistency_score || 0}
                          sx={{ height: 8, borderRadius: 4 }}
                        />
                      </Box>
                    </>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Skills Overview */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Skill Proficiency
                  </Typography>
                  {skills && (
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      {Object.entries(skills).map(([skill, value]) => (
                        <Grid item xs={12} key={skill}>
                          <Box>
                            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                {skill}
                              </Typography>
                              <Typography variant="body2" fontWeight="bold">
                                {value?.toFixed(1) || 0}%
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={value || 0}
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Velocity Tracker */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                    <Typography variant="h6">
                      <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Learning Velocity
                    </Typography>
                    {velocity && (
                      <Chip
                        label={getMomentumDisplay(velocity.momentum).label}
                        color={getMomentumDisplay(velocity.momentum).color}
                        size="small"
                      />
                    )}
                  </Box>
                  {velocity && (
                    <Box>
                      <Grid container spacing={2}>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Current Velocity
                          </Typography>
                          <Typography variant="h5" color={getVelocityColor(velocity.trend)}>
                            {velocity.current_velocity?.toFixed(1) || 0}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            points/week
                          </Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="body2" color="text.secondary">
                            Acceleration
                          </Typography>
                          <Typography variant="h5" color={getVelocityColor(velocity.trend)}>
                            {velocity.acceleration >= 0 ? '+' : ''}
                            {velocity.acceleration?.toFixed(1) || 0}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            change in velocity
                          </Typography>
                        </Grid>
                      </Grid>

                      <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                        <Typography variant="body2">
                          <strong>Trend:</strong> Your learning velocity is{' '}
                          <strong style={{ color: velocity.trend === 'positive' ? 'green' : velocity.trend === 'negative' ? 'red' : 'inherit' }}>
                            {velocity.trend}
                          </strong>
                          {velocity.momentum === 'increasing' && '. Keep up the great momentum! 🚀'}
                          {velocity.momentum === 'decreasing' && '. Try to maintain consistency.'}
                          {velocity.momentum === 'steady' && '. Maintaining a steady pace.'}
                        </Typography>
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Progress Tab */}
        <TabPanel value={currentTab} index={1}>
          <Grid container spacing={3}>
            {/* Progress Timeline Chart */}
            <Grid item xs={12}>
              <ProgressTimeline />
            </Grid>

            {/* Skill Radar Chart */}
            <Grid item xs={12}>
              <SkillRadarChart />
            </Grid>
          </Grid>
        </TabPanel>

        {/* Predictions Tab */}
        <TabPanel value={currentTab} index={2}>
          <Grid container spacing={3}>
            {/* Level Completion Prediction */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <TrophyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Next Level Prediction
                  </Typography>
                  {prediction && (
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Current Level
                        </Typography>
                        <Typography variant="h4" color="primary">
                          {prediction.current_level}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">
                          Next Level
                        </Typography>
                        <Typography variant="h4" color="secondary">
                          {prediction.next_level || 'N/A'}
                        </Typography>
                      </Grid>

                      {prediction.predicted_date && (
                        <>
                          <Grid item xs={12} sm={4}>
                            <Typography variant="body2" color="text.secondary">
                              Predicted Date
                            </Typography>
                            <Typography variant="h6">
                              {new Date(prediction.predicted_date).toLocaleDateString()}
                            </Typography>
                          </Grid>
                          <Grid item xs={12} sm={4}>
                            <Typography variant="body2" color="text.secondary">
                              Days Remaining
                            </Typography>
                            <Typography variant="h6">
                              {prediction.days_remaining} days
                            </Typography>
                          </Grid>
                          <Grid item xs={12} sm={4}>
                            <Typography variant="body2" color="text.secondary">
                              Confidence
                            </Typography>
                            <Typography variant="h6">
                              {(prediction.confidence * 100).toFixed(0)}%
                            </Typography>
                          </Grid>
                        </>
                      )}

                      {prediction.message && (
                        <Grid item xs={12}>
                          <Alert severity="info">{prediction.message}</Alert>
                        </Grid>
                      )}
                    </Grid>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Skill Mastery Predictions */}
            <Grid item xs={12}>
              <PredictionPanel />
            </Grid>
          </Grid>
        </TabPanel>

        {/* Insights Tab */}
        <TabPanel value={currentTab} index={3}>
          <Typography variant="h6" gutterBottom>
            <PsychologyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            AI-Powered Insights
          </Typography>
          {insights && insights.length > 0 ? (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              {insights.map((insight, index) => (
                <Grid item xs={12} key={index}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                        <Typography variant="h6">{insight.title}</Typography>
                        <Chip
                          label={insight.type}
                          color={
                            insight.type === 'strength' ? 'success' :
                            insight.type === 'weakness' ? 'error' :
                            insight.type === 'recommendation' ? 'info' :
                            'default'
                          }
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {insight.description}
                      </Typography>
                      {insight.action_items && insight.action_items.length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Action Items:
                          </Typography>
                          <ul style={{ margin: 0, paddingLeft: 20 }}>
                            {insight.action_items.map((action, idx) => (
                              <li key={idx}>
                                <Typography variant="body2">{action}</Typography>
                              </li>
                            ))}
                          </ul>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          ) : (
            <Alert severity="info" sx={{ mt: 2 }}>
              No insights available yet. Keep learning to generate personalized insights!
            </Alert>
          )}
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default AnalyticsDashboard;
