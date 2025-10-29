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
  Checkbox,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import {
  Psychology,
  ExpandMore,
  Lightbulb,
  TrendingUp,
  Warning,
  CheckCircle,
  Star,
  Timeline,
  Speed,
  EmojiEvents,
} from '@mui/icons-material';
import learningAnalyticsService from '../../services/learningAnalyticsService';

/**
 * Insights Panel Component
 * Enhanced AI insights with categorization, priority sorting, and action tracking
 */
// eslint-disable-next-line no-unused-vars
const InsightsPanel = ({ userId }) => {
  // eslint-disable-next-line no-unused-vars
  const theme = useTheme();
  const [insights, setInsights] = useState([]);
  const [patterns, setPatterns] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState('all');
  const [completedActions, setCompletedActions] = useState(new Set());

  // Fetch insights data
  const fetchInsightsData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch AI insights
      const insightsData = await learningAnalyticsService.getPersonalizedInsights();
      setInsights(insightsData);

      // Fetch learning patterns
      const patternsData = await learningAnalyticsService.getLearningPatterns();
      setPatterns(patternsData);
    } catch (err) {
      console.error('Failed to fetch insights:', err);
      setError(err.response?.data?.error || 'Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsightsData();
  }, []);

  // Filter insights by type
  const getFilteredInsights = () => {
    if (filterType === 'all') return insights;
    return insights.filter((insight) => insight.insight_type === filterType);
  };

  // Get insight icon
  const getInsightIcon = (type) => {
    switch (type) {
      case 'strength':
        return <Star color="success" />;
      case 'weakness':
        return <Warning color="warning" />;
      case 'recommendation':
        return <Lightbulb color="primary" />;
      case 'prediction':
        return <Timeline color="info" />;
      default:
        return <Psychology color="primary" />;
    }
  };

  // Get insight color
  const getInsightColor = (type) => {
    switch (type) {
      case 'strength':
        return 'success';
      case 'weakness':
        return 'warning';
      case 'recommendation':
        return 'primary';
      case 'prediction':
        return 'info';
      default:
        return 'default';
    }
  };

  // Get priority color
  const getPriorityColor = (priority) => {
    if (priority >= 0.8) return 'error';
    if (priority >= 0.6) return 'warning';
    return 'info';
  };

  // Get priority label
  const getPriorityLabel = (priority) => {
    if (priority >= 0.8) return 'High Priority';
    if (priority >= 0.6) return 'Medium Priority';
    return 'Low Priority';
  };

  // Handle action checkbox
  const handleActionToggle = (insightId, actionIndex) => {
    const key = `${insightId}-${actionIndex}`;
    setCompletedActions((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  // Handle filter change
  const handleFilterChange = (event, newFilter) => {
    if (newFilter !== null) {
      setFilterType(newFilter);
    }
  };

  // Get pattern icon
  const getPatternIcon = (patternType) => {
    if (patternType.includes('time')) return <Speed />;
    if (patternType.includes('skill')) return <TrendingUp />;
    if (patternType.includes('achievement')) return <EmojiEvents />;
    return <Timeline />;
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
          <Alert severity="error" onClose={() => fetchInsightsData()}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (insights.length === 0 && !patterns) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            No insights available yet. Complete more activities to get personalized AI insights!
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const filteredInsights = getFilteredInsights();
  const sortedInsights = [...filteredInsights].sort((a, b) => b.priority_score - a.priority_score);

  return (
    <Box>
      {/* Learning Patterns Summary */}
      {patterns && (
        <Card elevation={3} sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <Timeline color="primary" />
              <Typography variant="h6" fontWeight="bold">
                Your Learning Patterns
              </Typography>
            </Box>
            <Grid container spacing={2}>
              {/* Best Time to Study */}
              {patterns.best_study_time && (
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Speed color="primary" />
                        <Typography variant="subtitle2" fontWeight="bold">
                          Best Study Time
                        </Typography>
                      </Box>
                      <Typography variant="h5" color="primary">
                        {patterns.best_study_time}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        You perform best during this time
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {/* Strongest Skill */}
              {patterns.strongest_skill && (
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Star color="success" />
                        <Typography variant="subtitle2" fontWeight="bold">
                          Strongest Skill
                        </Typography>
                      </Box>
                      <Typography variant="h5" color="success.main">
                        {patterns.strongest_skill.charAt(0).toUpperCase() + patterns.strongest_skill.slice(1)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Keep up the great work!
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {/* Area Needing Focus */}
              {patterns.needs_focus && (
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Warning color="warning" />
                        <Typography variant="subtitle2" fontWeight="bold">
                          Needs Focus
                        </Typography>
                      </Box>
                      <Typography variant="h5" color="warning.main">
                        {patterns.needs_focus.charAt(0).toUpperCase() + patterns.needs_focus.slice(1)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Recommended focus area
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>

            {/* Additional Patterns */}
            {patterns.patterns && patterns.patterns.length > 0 && (
              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Identified Patterns
                </Typography>
                <Grid container spacing={1}>
                  {patterns.patterns.map((pattern, index) => (
                    <Grid item xs={12} sm={6} key={index}>
                      <Card variant="outlined">
                        <CardContent sx={{ py: 1 }}>
                          <Box display="flex" alignItems="center" gap={1}>
                            {getPatternIcon(pattern)}
                            <Typography variant="body2">{pattern}</Typography>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Insights Section */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box display="flex" alignItems="center" gap={1}>
              <Psychology color="primary" />
              <Typography variant="h6" fontWeight="bold">
                AI-Powered Insights ({sortedInsights.length})
              </Typography>
            </Box>

            {/* Filter Buttons */}
            <ToggleButtonGroup
              value={filterType}
              exclusive
              onChange={handleFilterChange}
              size="small"
            >
              <ToggleButton value="all">All</ToggleButton>
              <ToggleButton value="strength">Strengths</ToggleButton>
              <ToggleButton value="weakness">Weaknesses</ToggleButton>
              <ToggleButton value="recommendation">Tips</ToggleButton>
            </ToggleButtonGroup>
          </Box>

          {sortedInsights.length === 0 ? (
            <Alert severity="info">No insights found for the selected filter.</Alert>
          ) : (
            <Box>
              {sortedInsights.map((insight, index) => (
                <Accordion key={index} defaultExpanded={index === 0}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" alignItems="center" gap={2} width="100%">
                      {getInsightIcon(insight.insight_type)}
                      <Box flex={1}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {insight.title}
                        </Typography>
                        <Box display="flex" gap={1} mt={0.5}>
                          <Chip
                            label={insight.insight_type}
                            color={getInsightColor(insight.insight_type)}
                            size="small"
                          />
                          {insight.priority_score && (
                            <Chip
                              label={getPriorityLabel(insight.priority_score)}
                              color={getPriorityColor(insight.priority_score)}
                              size="small"
                            />
                          )}
                          {insight.confidence_score && (
                            <Chip
                              label={`${(insight.confidence_score * 100).toFixed(0)}% confident`}
                              variant="outlined"
                              size="small"
                            />
                          )}
                        </Box>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {/* Description */}
                    <Typography variant="body2" paragraph>
                      {insight.description}
                    </Typography>

                    {/* Context */}
                    {insight.context && (
                      <Alert severity="info" sx={{ mb: 2 }}>
                        {insight.context}
                      </Alert>
                    )}

                    {/* Action Items */}
                    {insight.action_items && insight.action_items.length > 0 && (
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                          Action Items
                        </Typography>
                        <List dense>
                          {insight.action_items.map((action, actionIndex) => (
                            <ListItem key={actionIndex} disablePadding>
                              <ListItemIcon sx={{ minWidth: 40 }}>
                                <FormControlLabel
                                  control={
                                    <Checkbox
                                      checked={completedActions.has(`${index}-${actionIndex}`)}
                                      onChange={() => handleActionToggle(index, actionIndex)}
                                      size="small"
                                    />
                                  }
                                  label=""
                                  sx={{ m: 0 }}
                                />
                              </ListItemIcon>
                              <ListItemText
                                primary={action}
                                primaryTypographyProps={{
                                  variant: 'body2',
                                  sx: {
                                    textDecoration: completedActions.has(`${index}-${actionIndex}`)
                                      ? 'line-through'
                                      : 'none',
                                    color: completedActions.has(`${index}-${actionIndex}`)
                                      ? 'text.secondary'
                                      : 'text.primary',
                                  },
                                }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}

                    {/* Identified Date */}
                    {insight.identified_date && (
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                        Identified on {new Date(insight.identified_date).toLocaleDateString()}
                      </Typography>
                    )}
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}

          {/* Progress Summary */}
          {sortedInsights.length > 0 && (
            <Box mt={3}>
              <Alert severity="success" icon={<CheckCircle />}>
                <Typography variant="body2" fontWeight="bold">
                  You&apos;ve completed {completedActions.size} action items!
                </Typography>
                <Typography variant="caption">
                  Keep taking action on these insights to accelerate your learning progress.
                </Typography>
              </Alert>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

InsightsPanel.propTypes = {
  userId: PropTypes.number,
};

export default InsightsPanel;
