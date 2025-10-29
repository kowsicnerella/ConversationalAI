/**
 * SkillDiagnosticView Component
 * 
 * Displays comprehensive skill diagnostics with:
 * - Skill proficiency radar chart
 * - Sub-skill breakdown
 * - Error pattern analysis
 * - Improvement strategies
 * - Strength/weakness identification
 * 
 * @component
 */

import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Divider,
  Alert,
  Tab,
  Tabs
} from '@mui/material';
import {
  ExpandMore as ExpandIcon,
  TrendingUp as StrengthIcon,
  TrendingDown as WeaknessIcon,
  Lightbulb as StrategyIcon,
  Error as ErrorIcon,
  CheckCircle as MasteredIcon,
  Warning as NeedsWorkIcon
} from '@mui/icons-material';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell
} from 'recharts';
import { getSkillScoreColor, getPriorityColor } from '../../services/assessmentService';

const SkillDiagnosticView = ({ diagnostics, showStrategies = true }) => {
  const [tabValue, setTabValue] = useState(0);

  if (!diagnostics || diagnostics.length === 0) {
    return (
      <Alert severity="info">
        No diagnostic data available. Complete an assessment to see your skill analysis.
      </Alert>
    );
  }

  // Prepare radar chart data
  const radarData = diagnostics.map(skill => ({
    skill: skill.skill_name.length > 15 
      ? skill.skill_name.substring(0, 15) + '...' 
      : skill.skill_name,
    fullName: skill.skill_name,
    score: parseFloat((skill.score * 100).toFixed(1)),
    mastery: skill.mastery_level
  }));

  // Categorize skills
  const strengths = diagnostics.filter(s => s.mastery_level === 'mastered' || s.score >= 0.8);
  const needsWork = diagnostics.filter(s => s.mastery_level === 'needs_work' || s.score < 0.6);
  const inProgress = diagnostics.filter(s => !strengths.includes(s) && !needsWork.includes(s));

  // Get all error patterns
  const allErrorPatterns = diagnostics
    .flatMap(skill => skill.error_patterns || [])
    .filter((pattern, index, self) => 
      index === self.findIndex(p => p.pattern === pattern.pattern)
    )
    .sort((a, b) => b.frequency - a.frequency);

  return (
    <Box>
      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
          variant="fullWidth"
        >
          <Tab label="Overview" />
          <Tab label="Skill Analysis" />
          <Tab label="Error Patterns" />
          {showStrategies && <Tab label="Improvement" />}
        </Tabs>
      </Paper>

      {/* Tab 0: Overview */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Overall Statistics */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <StrengthIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'success.main' }} />
                  Strengths
                </Typography>
                <Typography variant="h3" color="success.main" gutterBottom>
                  {strengths.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Skills you've mastered
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <TrendingUp sx={{ verticalAlign: 'middle', mr: 1, color: 'info.main' }} />
                  In Progress
                </Typography>
                <Typography variant="h3" color="info.main" gutterBottom>
                  {inProgress.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Skills you're developing
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <WeaknessIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'error.main' }} />
                  Needs Work
                </Typography>
                <Typography variant="h3" color="error.main" gutterBottom>
                  {needsWork.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Skills requiring focus
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Radar Chart */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Skill Proficiency Map
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="skill" />
                    <PolarRadiusAxis domain={[0, 100]} />
                    <Radar
                      name="Score"
                      dataKey="score"
                      stroke="#2196f3"
                      fill="#2196f3"
                      fillOpacity={0.6}
                    />
                    <Tooltip
                      content={({ payload }) => {
                        if (!payload || payload.length === 0) return null;
                        const data = payload[0].payload;
                        return (
                          <Paper sx={{ p: 2 }}>
                            <Typography variant="subtitle2">{data.fullName}</Typography>
                            <Typography variant="body2">Score: {data.score}%</Typography>
                            <Chip
                              label={data.mastery}
                              size="small"
                              color={getMasteryColor(data.mastery)}
                              sx={{ mt: 1 }}
                            />
                          </Paper>
                        );
                      }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tab 1: Skill Analysis */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          {diagnostics.map((skill, index) => (
            <Grid item xs={12} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h6">
                        {skill.skill_name}
                      </Typography>
                      <Chip
                        size="small"
                        label={skill.mastery_level}
                        color={getMasteryColor(skill.mastery_level)}
                        icon={getMasteryIcon(skill.mastery_level)}
                      />
                    </Box>
                    <Typography variant="h5" fontWeight="bold" color={getSkillScoreColor(skill.score * 100)}>
                      {(skill.score * 100).toFixed(0)}%
                    </Typography>
                  </Box>

                  <LinearProgress
                    variant="determinate"
                    value={skill.score * 100}
                    sx={{
                      height: 10,
                      borderRadius: 1,
                      mb: 2,
                      bgcolor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: getSkillScoreColor(skill.score * 100)
                      }
                    }}
                  />

                  {/* Sub-skills */}
                  {skill.sub_skills && skill.sub_skills.length > 0 && (
                    <Accordion defaultExpanded={false}>
                      <AccordionSummary expandIcon={<ExpandIcon />}>
                        <Typography variant="subtitle2">
                          Sub-Skills ({skill.sub_skills.length})
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Grid container spacing={2}>
                          {skill.sub_skills.map((subSkill, subIndex) => (
                            <Grid item xs={12} sm={6} key={subIndex}>
                              <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                  <Typography variant="body2" fontWeight="medium">
                                    {subSkill.name}
                                  </Typography>
                                  <Typography variant="body2" fontWeight="bold">
                                    {(subSkill.score * 100).toFixed(0)}%
                                  </Typography>
                                </Box>
                                <LinearProgress
                                  variant="determinate"
                                  value={subSkill.score * 100}
                                  sx={{
                                    height: 6,
                                    borderRadius: 1,
                                    '& .MuiLinearProgress-bar': {
                                      bgcolor: getSkillScoreColor(subSkill.score * 100)
                                    }
                                  }}
                                />
                              </Box>
                            </Grid>
                          ))}
                        </Grid>
                      </AccordionDetails>
                    </Accordion>
                  )}

                  {/* Related Topics */}
                  {skill.related_topics && skill.related_topics.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                        Related Topics
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {skill.related_topics.map((topic, topicIndex) => (
                          <Chip key={topicIndex} label={topic} size="small" variant="outlined" />
                        ))}
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Tab 2: Error Patterns */}
      {tabValue === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <ErrorIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'error.main' }} />
              Common Error Patterns
            </Typography>

            {allErrorPatterns.length === 0 ? (
              <Alert severity="success">
                No significant error patterns detected. Great job!
              </Alert>
            ) : (
              <List>
                {allErrorPatterns.map((pattern, index) => (
                  <div key={index}>
                    <ListItem>
                      <ListItemIcon>
                        <Chip
                          label={pattern.frequency}
                          size="small"
                          color={getPriorityColor(pattern.frequency > 5 ? 'high' : pattern.frequency > 2 ? 'medium' : 'low')}
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={pattern.pattern}
                        secondary={pattern.suggestion || 'Focus on improving this area'}
                      />
                    </ListItem>
                    {index < allErrorPatterns.length - 1 && <Divider />}
                  </div>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tab 3: Improvement Strategies */}
      {tabValue === 3 && showStrategies && (
        <Grid container spacing={3}>
          {diagnostics
            .filter(skill => skill.improvement_strategies && skill.improvement_strategies.length > 0)
            .map((skill, index) => (
              <Grid item xs={12} key={index}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <StrategyIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'warning.main' }} />
                      {skill.skill_name}
                    </Typography>
                    
                    <List>
                      {skill.improvement_strategies.map((strategy, stratIndex) => (
                        <ListItem key={stratIndex}>
                          <ListItemIcon>
                            <Chip label={stratIndex + 1} size="small" color="primary" />
                          </ListItemIcon>
                          <ListItemText
                            primary={strategy}
                            primaryTypographyProps={{ variant: 'body2' }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    {skill.recommended_resources && skill.recommended_resources.length > 0 && (
                      <Box sx={{ mt: 2, p: 2, bgcolor: 'info.50', borderRadius: 1 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Recommended Resources
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {skill.recommended_resources.map((resource, resIndex) => (
                            <Chip
                              key={resIndex}
                              label={resource}
                              size="small"
                              color="info"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
        </Grid>
      )}
    </Box>
  );
};

// Helper functions
const getMasteryColor = (mastery) => {
  switch (mastery) {
    case 'mastered': return 'success';
    case 'proficient': return 'info';
    case 'developing': return 'warning';
    case 'needs_work': return 'error';
    default: return 'default';
  }
};

const getMasteryIcon = (mastery) => {
  switch (mastery) {
    case 'mastered': return <MasteredIcon />;
    case 'needs_work': return <NeedsWorkIcon />;
    default: return <TrendingUp />;
  }
};

export default SkillDiagnosticView;
