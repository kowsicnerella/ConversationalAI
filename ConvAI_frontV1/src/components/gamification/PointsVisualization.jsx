/**
 * PointsVisualization Component - Phase 2 Gamification
 * Displays points earned with history chart and breakdown
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Tab,
  Tabs,
  Paper,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Star as StarIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const PointsVisualization = () => {
  const [pointsData, setPointsData] = useState(null);
  const [timeRange, setTimeRange] = useState('week'); // week, month, all
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPointsData();
  }, [timeRange]);

  const fetchPointsData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:5000/api/gamification/points?range=${timeRange}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPointsData(data);
      }
    } catch (error) {
      console.error('Error fetching points:', error);
      // Set mock data for demonstration
      setPointsData(getMockPointsData());
    } finally {
      setLoading(false);
    }
  };

  const getMockPointsData = () => ({
    total_points: 2450,
    rank: 'Gold',
    next_milestone: 3000,
    points_to_next_milestone: 550,
    history: {
      dates: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      points: [50, 75, 100, 80, 120, 90, 150],
    },
    breakdown: {
      'Quiz Completion': 850,
      'Activity Streak': 450,
      'Perfect Scores': 600,
      'Daily Login': 350,
      'Challenges': 200,
    },
    recent_activities: [
      { name: 'Grammar Quiz', points: 50, date: '2025-10-19' },
      { name: 'Vocabulary Practice', points: 30, date: '2025-10-19' },
      { name: 'Reading Exercise', points: 70, date: '2025-10-18' },
      { name: 'Daily Login', points: 10, date: '2025-10-18' },
      { name: 'Perfect Score Bonus', points: 100, date: '2025-10-17' },
    ],
  });

  const handleTimeRangeChange = (event, newValue) => {
    setTimeRange(newValue);
  };

  // Chart configurations
  const lineChartData = {
    labels: pointsData?.history?.dates || [],
    datasets: [
      {
        label: 'Points Earned',
        data: pointsData?.history?.points || [],
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: '#1976d2',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
    ],
  };

  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleFont: { size: 14, weight: 'bold' },
        bodyFont: { size: 13 },
        callbacks: {
          label: (context) => `${context.parsed.y} points`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
        ticks: {
          callback: (value) => `${value}`,
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  const doughnutChartData = {
    labels: Object.keys(pointsData?.breakdown || {}),
    datasets: [
      {
        data: Object.values(pointsData?.breakdown || {}),
        backgroundColor: [
          '#1976d2',
          '#2e7d32',
          '#ed6c02',
          '#9c27b0',
          '#d32f2f',
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 15,
          font: { size: 12 },
          generateLabels: (chart) => {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              return data.labels.map((label, i) => {
                const value = data.datasets[0].data[i];
                return {
                  text: `${label}: ${value} pts`,
                  fillStyle: data.datasets[0].backgroundColor[i],
                  hidden: false,
                  index: i,
                };
              });
            }
            return [];
          },
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.parsed} points`,
        },
      },
    },
  };

  if (loading) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography>Loading points data...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          ⭐ Your Points
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track your learning progress and achievements
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StarIcon sx={{ fontSize: 40, mr: 1 }} />
                <Typography variant="h6">Total Points</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {pointsData?.total_points?.toLocaleString()}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                Keep earning to reach new milestones!
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrophyIcon sx={{ fontSize: 40, mr: 1 }} />
                <Typography variant="h6">Current Rank</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {pointsData?.rank}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                {pointsData?.points_to_next_milestone} points to next rank
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
              color: 'white',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUpIcon sx={{ fontSize: 40, mr: 1 }} />
                <Typography variant="h6">Next Milestone</Typography>
              </Box>
              <Typography variant="h3" fontWeight="bold">
                {pointsData?.next_milestone?.toLocaleString()}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1, opacity: 0.9 }}>
                {Math.round(
                  ((pointsData?.total_points || 0) / (pointsData?.next_milestone || 1)) * 100
                )}
                % complete
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Points History Chart */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" fontWeight="bold">
                Points History
              </Typography>
              <Tabs value={timeRange} onChange={handleTimeRangeChange} size="small">
                <Tab label="Week" value="week" />
                <Tab label="Month" value="month" />
                <Tab label="All Time" value="all" />
              </Tabs>
            </Box>
            <Box sx={{ height: 300 }}>
              <Line data={lineChartData} options={lineChartOptions} />
            </Box>
          </Paper>
        </Grid>

        {/* Points Breakdown Chart */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Points Breakdown
            </Typography>
            <Box sx={{ height: 300, mt: 2 }}>
              <Doughnut data={doughnutChartData} options={doughnutChartOptions} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <Paper sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          Recent Point Activities
        </Typography>
        <Box sx={{ mt: 2 }}>
          {pointsData?.recent_activities?.map((activity, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                py: 2,
                borderBottom: index < pointsData.recent_activities.length - 1 ? '1px solid #e0e0e0' : 'none',
              }}
            >
              <Box>
                <Typography variant="body1" fontWeight="medium">
                  {activity.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(activity.date).toLocaleDateString()}
                </Typography>
              </Box>
              <Chip
                label={`+${activity.points} pts`}
                color="primary"
                size="small"
                sx={{ fontWeight: 'bold' }}
              />
            </Box>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};

export default PointsVisualization;
