import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Card,
  CardContent,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp,
  EmojiEvents,
  AccessTime,
  Speed,
  Warning
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadarController,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Radar, Pie } from 'react-chartjs-2';
import axios from 'axios';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadarController,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
);

const AnalyticsDashboard = () => {
  const [timeRange, setTimeRange] = useState('30days');
  const [loading, setLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState(null);
  const [skillData, setSkillData] = useState(null);
  const [activityData, setActivityData] = useState(null);
  const [timeData, setTimeData] = useState(null);
  const [velocityData, setVelocityData] = useState(null);
  const [weakAreas, setWeakAreas] = useState([]);

  useEffect(() => {
    fetchAllAnalytics();
  }, [timeRange]);

  const fetchAllAnalytics = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const baseURL = 'http://localhost:5000/api/analytics-v2';

      const [performance, skills, activities, time, velocity, weak] = await Promise.all([
        axios.get(`${baseURL}/performance-trends?time_range=${timeRange}`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${baseURL}/skill-breakdown`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${baseURL}/activity-summary`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${baseURL}/time-analytics`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${baseURL}/learning-velocity`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${baseURL}/weak-areas`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      setPerformanceData(performance.data.data);
      setSkillData(skills.data.data);
      setActivityData(activities.data.data);
      setTimeData(time.data.data);
      setVelocityData(velocity.data.data);
      setWeakAreas(weak.data.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange !== null) {
      setTimeRange(newRange);
    }
  };

  // Performance Trend Chart Data
  const performanceTrendData = performanceData ? {
    labels: performanceData.dates,
    datasets: [
      {
        label: 'Accuracy Score',
        data: performanceData.scores,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.4
      }
    ]
  } : null;

  // Skill Breakdown Radar Chart Data
  const skillBreakdownData = skillData ? {
    labels: ['Listening', 'Speaking', 'Reading', 'Writing', 'Vocabulary', 'Grammar'],
    datasets: [
      {
        label: 'Skill Level',
        data: [
          skillData.listening,
          skillData.speaking,
          skillData.reading,
          skillData.writing,
          skillData.vocabulary,
          skillData.grammar
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgb(54, 162, 235)',
        borderWidth: 2
      }
    ]
  } : null;

  // Activity Distribution Pie Chart Data
  const activityDistributionData = activityData ? {
    labels: Object.keys(activityData.by_type || {}),
    datasets: [
      {
        data: Object.values(activityData.by_type || {}),
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)'
        ]
      }
    ]
  } : null;

  // Time Investment Bar Chart Data
  const timeInvestmentData = performanceData ? {
    labels: performanceData.dates,
    datasets: [
      {
        label: 'Time Spent (minutes)',
        data: performanceData.time_spent,
        backgroundColor: 'rgba(153, 102, 255, 0.8)'
      }
    ]
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      }
    }
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          📊 Learning Analytics Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Track your progress, identify strengths, and improve weak areas
        </Typography>

        {/* Time Range Selector */}
        <Box mt={2}>
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={handleTimeRangeChange}
            aria-label="time range"
          >
            <ToggleButton value="7days" aria-label="7 days">
              7 Days
            </ToggleButton>
            <ToggleButton value="30days" aria-label="30 days">
              30 Days
            </ToggleButton>
            <ToggleButton value="90days" aria-label="90 days">
              90 Days
            </ToggleButton>
            <ToggleButton value="all" aria-label="all time">
              All Time
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Box>

      {/* Quick Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <EmojiEvents color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Activities/Week</Typography>
              </Box>
              <Typography variant="h4">
                {velocityData?.activities_per_week || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {velocityData?.learning_pace || 'N/A'} pace
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AccessTime color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Time Investment</Typography>
              </Box>
              <Typography variant="h4">
                {timeData?.total_hours || 0}h
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {timeData?.daily_average || 0} min/day
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Improvement</Typography>
              </Box>
              <Typography variant="h4">
                {velocityData?.improvement_rate >= 0 ? '+' : ''}
                {velocityData?.improvement_rate || 0}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 2 weeks
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Speed color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Consistency</Typography>
              </Box>
              <Typography variant="h4">
                {velocityData?.consistency_score || 0}/10
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(velocityData?.consistency_score || 0) * 10} 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Weak Areas Alert */}
      {weakAreas && weakAreas.length > 0 && (
        <Alert severity="warning" icon={<Warning />} sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>
            <strong>Areas Needing Focus:</strong>
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {weakAreas.map((area, index) => (
              <Chip
                key={index}
                label={`${area.skill}: ${area.score}%`}
                color={area.priority === 'high' ? 'error' : 'warning'}
                size="small"
              />
            ))}
          </Box>
        </Alert>
      )}

      {/* Charts Grid */}
      <Grid container spacing={3}>
        {/* Performance Trend */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Performance Trend
            </Typography>
            {performanceTrendData && (
              <Box height="calc(100% - 40px)">
                <Line data={performanceTrendData} options={chartOptions} />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Skill Breakdown Radar */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Skill Breakdown
            </Typography>
            {skillBreakdownData && (
              <Box height="calc(100% - 40px)">
                <Radar data={skillBreakdownData} options={{
                  ...chartOptions,
                  scales: {
                    r: {
                      beginAtZero: true,
                      max: 100
                    }
                  }
                }} />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Activity Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Activity Distribution
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Favorite: {activityData?.favorite_type || 'N/A'}
            </Typography>
            {activityDistributionData && (
              <Box height="calc(100% - 60px)">
                <Pie data={activityDistributionData} options={chartOptions} />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Time Investment */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              Time Investment
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Most active: {timeData?.most_active_day || 'N/A'}
            </Typography>
            {timeInvestmentData && (
              <Box height="calc(100% - 60px)">
                <Bar data={timeInvestmentData} options={chartOptions} />
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AnalyticsDashboard;
