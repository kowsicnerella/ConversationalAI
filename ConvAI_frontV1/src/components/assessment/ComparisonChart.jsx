/**
 * ComparisonChart Component
 * 
 * Visualizes comparison between multiple assessment attempts with:
 * - Theta progression over time
 * - Skill improvement comparison
 * - Score trends
 * - Performance metrics side-by-side
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
  ToggleButton,
  ToggleButtonGroup,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert
} from '@mui/material';
import {
  TrendingUp as ImprovementIcon,
  TrendingDown as DeclineIcon,
  Remove as NoChangeIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis
} from 'recharts';
import {
  formatDate,
  formatTheta,
  thetaToPercentile,
  getSkillScoreColor
} from '../../services/assessmentService';

const ComparisonChart = ({ attempts, comparisonData }) => {
  const [chartType, setChartType] = useState('theta');

  if (!attempts || attempts.length < 2) {
    return (
      <Alert severity="info">
        Need at least 2 attempts to compare. Complete more assessments to see your progress.
      </Alert>
    );
  }

  // Prepare theta progression data
  const thetaData = attempts.map((attempt, index) => ({
    attempt: `Attempt ${index + 1}`,
    date: formatDate(attempt.completed_at),
    theta: attempt.final_theta,
    percentile: thetaToPercentile(attempt.final_theta),
    score: attempt.score
  }));

  // Prepare skill comparison data
  const skillComparisonData = comparisonData?.skill_comparison || [];

  // Calculate overall improvement
  const firstAttempt = attempts[0];
  const lastAttempt = attempts[attempts.length - 1];
  const thetaImprovement = lastAttempt.final_theta - firstAttempt.final_theta;
  const scoreImprovement = lastAttempt.score - firstAttempt.score;

  return (
    <Box>
      {/* Overall Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Total Attempts
              </Typography>
              <Typography variant="h3" fontWeight="bold">
                {attempts.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Theta Improvement
                </Typography>
                {getTrendIcon(thetaImprovement)}
              </Box>
              <Typography
                variant="h3"
                fontWeight="bold"
                color={thetaImprovement > 0 ? 'success.main' : thetaImprovement < 0 ? 'error.main' : 'text.primary'}
              >
                {thetaImprovement > 0 ? '+' : ''}{formatTheta(thetaImprovement)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {formatTheta(firstAttempt.final_theta)} → {formatTheta(lastAttempt.final_theta)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  Score Improvement
                </Typography>
                {getTrendIcon(scoreImprovement)}
              </Box>
              <Typography
                variant="h3"
                fontWeight="bold"
                color={scoreImprovement > 0 ? 'success.main' : scoreImprovement < 0 ? 'error.main' : 'text.primary'}
              >
                {scoreImprovement > 0 ? '+' : ''}{scoreImprovement.toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {firstAttempt.score.toFixed(1)}% → {lastAttempt.score.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Chart Type Selector */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
        <ToggleButtonGroup
          value={chartType}
          exclusive
          onChange={(e, newType) => newType && setChartType(newType)}
          aria-label="chart type"
        >
          <ToggleButton value="theta">Theta Progression</ToggleButton>
          <ToggleButton value="score">Score Trends</ToggleButton>
          <ToggleButton value="skills">Skill Comparison</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Charts */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          {chartType === 'theta' && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Theta Progression Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={thetaData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="attempt" />
                  <YAxis
                    yAxisId="left"
                    label={{ value: 'Theta', angle: -90, position: 'insideLeft' }}
                  />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    label={{ value: 'Percentile', angle: 90, position: 'insideRight' }}
                  />
                  <Tooltip
                    content={({ payload }) => {
                      if (!payload || payload.length === 0) return null;
                      const data = payload[0].payload;
                      return (
                        <Paper sx={{ p: 2 }}>
                          <Typography variant="subtitle2">{data.attempt}</Typography>
                          <Typography variant="body2">{data.date}</Typography>
                          <Typography variant="body2">Theta: {formatTheta(data.theta)}</Typography>
                          <Typography variant="body2">Percentile: {data.percentile.toFixed(1)}%</Typography>
                          <Typography variant="body2">Score: {data.score.toFixed(1)}%</Typography>
                        </Paper>
                      );
                    }}
                  />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="theta"
                    stroke="#2196f3"
                    strokeWidth={2}
                    name="Theta"
                    dot={{ r: 6 }}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="percentile"
                    stroke="#4caf50"
                    strokeWidth={2}
                    name="Percentile"
                    dot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          )}

          {chartType === 'score' && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Score Trends
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={thetaData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="attempt" />
                  <YAxis label={{ value: 'Score (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip
                    content={({ payload }) => {
                      if (!payload || payload.length === 0) return null;
                      const data = payload[0].payload;
                      return (
                        <Paper sx={{ p: 2 }}>
                          <Typography variant="subtitle2">{data.attempt}</Typography>
                          <Typography variant="body2">{data.date}</Typography>
                          <Typography variant="body2">Score: {data.score.toFixed(1)}%</Typography>
                        </Paper>
                      );
                    }}
                  />
                  <Legend />
                  <Bar
                    dataKey="score"
                    fill="#2196f3"
                    name="Score"
                  />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          )}

          {chartType === 'skills' && skillComparisonData.length > 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Skill Comparison (First vs Latest)
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={skillComparisonData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="skill_name" />
                  <PolarRadiusAxis domain={[0, 100]} />
                  <Radar
                    name="First Attempt"
                    dataKey="first_score"
                    stroke="#ff9800"
                    fill="#ff9800"
                    fillOpacity={0.3}
                  />
                  <Radar
                    name="Latest Attempt"
                    dataKey="latest_score"
                    stroke="#4caf50"
                    fill="#4caf50"
                    fillOpacity={0.5}
                  />
                  <Legend />
                  <Tooltip
                    content={({ payload }) => {
                      if (!payload || payload.length === 0) return null;
                      const data = payload[0].payload;
                      return (
                        <Paper sx={{ p: 2 }}>
                          <Typography variant="subtitle2">{data.skill_name}</Typography>
                          <Typography variant="body2">
                            First: {(data.first_score || 0).toFixed(1)}%
                          </Typography>
                          <Typography variant="body2">
                            Latest: {(data.latest_score || 0).toFixed(1)}%
                          </Typography>
                          <Typography variant="body2" color={data.improvement > 0 ? 'success.main' : 'error.main'}>
                            Change: {data.improvement > 0 ? '+' : ''}{(data.improvement || 0).toFixed(1)}%
                          </Typography>
                        </Paper>
                      );
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Detailed Comparison Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Attempt Details
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Attempt</strong></TableCell>
                  <TableCell><strong>Date</strong></TableCell>
                  <TableCell align="right"><strong>Score</strong></TableCell>
                  <TableCell align="right"><strong>Theta</strong></TableCell>
                  <TableCell align="right"><strong>Percentile</strong></TableCell>
                  <TableCell align="right"><strong>Questions</strong></TableCell>
                  <TableCell align="right"><strong>Duration</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {attempts.map((attempt, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Chip
                        label={`#${index + 1}`}
                        size="small"
                        color={index === attempts.length - 1 ? 'primary' : 'default'}
                      />
                    </TableCell>
                    <TableCell>{formatDate(attempt.completed_at)}</TableCell>
                    <TableCell align="right">
                      <Typography
                        variant="body2"
                        fontWeight="bold"
                        color={getSkillScoreColor(attempt.score)}
                      >
                        {attempt.score.toFixed(1)}%
                      </Typography>
                    </TableCell>
                    <TableCell align="right">{formatTheta(attempt.final_theta)}</TableCell>
                    <TableCell align="right">
                      {thetaToPercentile(attempt.final_theta).toFixed(1)}%
                    </TableCell>
                    <TableCell align="right">{attempt.questions_answered || 'N/A'}</TableCell>
                    <TableCell align="right">
                      {attempt.completion_time ? `${attempt.completion_time} min` : 'N/A'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Skill-by-Skill Improvement */}
      {skillComparisonData.length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Skill-by-Skill Progress
            </Typography>
            <Grid container spacing={2}>
              {skillComparisonData.map((skill, index) => (
                <Grid item xs={12} sm={6} md={4} key={index}>
                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle2">{skill.skill_name}</Typography>
                      {getTrendIcon(skill.improvement)}
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        First: {(skill.first_score || 0).toFixed(1)}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Latest: {(skill.latest_score || 0).toFixed(1)}%
                      </Typography>
                    </Box>
                    <Typography
                      variant="body2"
                      fontWeight="bold"
                      color={skill.improvement > 0 ? 'success.main' : skill.improvement < 0 ? 'error.main' : 'text.secondary'}
                      textAlign="center"
                    >
                      {skill.improvement > 0 ? '+' : ''}{(skill.improvement || 0).toFixed(1)}% change
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

// Helper function
const getTrendIcon = (value) => {
  if (value > 0.1) {
    return <ImprovementIcon sx={{ color: 'success.main' }} />;
  } else if (value < -0.1) {
    return <DeclineIcon sx={{ color: 'error.main' }} />;
  } else {
    return <NoChangeIcon sx={{ color: 'text.secondary' }} />;
  }
};

export default ComparisonChart;
