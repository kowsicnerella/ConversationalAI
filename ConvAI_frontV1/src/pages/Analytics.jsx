import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  ToggleButtonGroup,
  ToggleButton,
  Tabs,
  Tab,
  Chip,
} from "@mui/material";
import {
  TrendingUp,
  School,
  EmojiEvents,
  LocalFireDepartment,
  CalendarToday,
} from "@mui/icons-material";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { motion } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import StatCard from "../components/common/StatCard";

const Analytics = () => {
  const { t } = useTranslation();
  const [timeRange, setTimeRange] = useState("week");
  const [activeTab, setActiveTab] = useState(0);

  // Mock data for charts
  const weeklyProgressData = [
    { day: "Mon", points: 120, activities: 5, time: 45 },
    { day: "Tue", points: 180, activities: 7, time: 60 },
    { day: "Wed", points: 150, activities: 6, time: 50 },
    { day: "Thu", points: 200, activities: 8, time: 75 },
    { day: "Fri", points: 170, activities: 6, time: 55 },
    { day: "Sat", points: 220, activities: 9, time: 80 },
    { day: "Sun", points: 190, activities: 7, time: 65 },
  ];

  const skillProgressData = [
    { skill: "Reading", progress: 85 },
    { skill: "Writing", progress: 70 },
    { skill: "Listening", progress: 78 },
    { skill: "Speaking", progress: 65 },
    { skill: "Grammar", progress: 82 },
    { skill: "Vocabulary", progress: 90 },
  ];

  const activityDistribution = [
    { name: "Quiz", value: 35, color: "#667eea" },
    { name: "Flashcards", value: 25, color: "#764ba2" },
    { name: "Reading", value: 20, color: "#f093fb" },
    { name: "Writing", value: 12, color: "#4facfe" },
    { name: "Chat", value: 8, color: "#43e97b" },
  ];

  const monthlyData = [
    { month: "Jan", points: 1200, activities: 45 },
    { month: "Feb", points: 1400, activities: 52 },
    { month: "Mar", points: 1800, activities: 68 },
    { month: "Apr", points: 2100, activities: 75 },
    { month: "May", points: 2400, activities: 82 },
    { month: "Jun", points: 2800, activities: 95 },
  ];

  const levelProgress = [
    { level: "Beginner", completion: 100 },
    { level: "Elementary", completion: 85 },
    { level: "Intermediate", completion: 60 },
    { level: "Advanced", completion: 35 },
    { level: "Proficient", completion: 10 },
  ];

  const stats = [
    {
      title: "Total Points",
      value: "12,450",
      icon: <EmojiEvents />,
      color: "primary",
      change: "+15%",
    },
    {
      title: "Activities Completed",
      value: "248",
      icon: <School />,
      color: "success",
      change: "+22",
    },
    {
      title: "Current Streak",
      value: "15 days",
      icon: <LocalFireDepartment />,
      color: "warning",
      change: "Best: 23",
    },
    {
      title: "Study Time",
      value: "42h",
      icon: <TrendingUp />,
      color: "info",
      change: "+8h this week",
    },
  ];

  const handleTimeRangeChange = (event, newRange) => {
    if (newRange !== null) {
      setTimeRange(newRange);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <PageTransition>
      <Box>
        {/* Header */}
        <Box
          sx={{
            mb: 4,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 2,
          }}
        >
          <Box>
            <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
              Analytics Dashboard
            </GradientText>
            <Typography variant="body1" color="text.secondary">
              Track your learning progress and insights
            </Typography>
          </Box>
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={handleTimeRangeChange}
            size="small"
          >
            <ToggleButton value="week">Week</ToggleButton>
            <ToggleButton value="month">Month</ToggleButton>
            <ToggleButton value="year">Year</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <StatCard {...stat} />
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* Chart Tabs */}
        <Card sx={{ mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
          >
            <Tab
              label="Progress Over Time"
              icon={<TrendingUp />}
              iconPosition="start"
            />
            <Tab
              label="Activity Distribution"
              icon={<CalendarToday />}
              iconPosition="start"
            />
            <Tab
              label="Skill Analysis"
              icon={<School />}
              iconPosition="start"
            />
          </Tabs>
        </Card>

        {/* Chart Content */}
        {activeTab === 0 && (
          <Grid container spacing={3}>
            {/* Weekly Progress Line Chart */}
            <Grid item xs={12} lg={8}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Weekly Progress
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={weeklyProgressData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="points"
                          stroke="#667eea"
                          strokeWidth={3}
                        />
                        <Line
                          type="monotone"
                          dataKey="activities"
                          stroke="#764ba2"
                          strokeWidth={3}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Monthly Overview */}
            <Grid item xs={12} lg={4}>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <Card sx={{ height: "100%" }}>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Monthly Overview
                    </Typography>
                    <ResponsiveContainer width="100%" height={270}>
                      <BarChart data={monthlyData.slice(-4)}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Bar
                          dataKey="points"
                          fill="#667eea"
                          radius={[8, 8, 0, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Study Time Chart */}
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Study Time Analysis
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={weeklyProgressData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis
                          label={{
                            value: "Minutes",
                            angle: -90,
                            position: "insideLeft",
                          }}
                        />
                        <Tooltip />
                        <Bar
                          dataKey="time"
                          fill="#43e97b"
                          radius={[8, 8, 0, 0]}
                        >
                          {weeklyProgressData.map((entry, index) => (
                            <Cell
                              key={`cell-${index}`}
                              fill={`hsl(${140 + index * 10}, 70%, 50%)`}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        )}

        {activeTab === 1 && (
          <Grid container spacing={3}>
            {/* Activity Distribution Pie Chart */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Activity Distribution
                    </Typography>
                    <ResponsiveContainer width="100%" height={350}>
                      <PieChart>
                        <Pie
                          data={activityDistribution}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) =>
                            `${name}: ${(percent * 100).toFixed(0)}%`
                          }
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {activityDistribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Activity Breakdown */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Activity Breakdown
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {activityDistribution.map((activity, index) => (
                        <Box key={index} sx={{ mb: 3 }}>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              mb: 1,
                            }}
                          >
                            <Typography variant="body2" fontWeight={600}>
                              {activity.name}
                            </Typography>
                            <Chip
                              label={`${activity.value}%`}
                              size="small"
                              sx={{ bgcolor: activity.color, color: "white" }}
                            />
                          </Box>
                          <Box
                            sx={{
                              height: 8,
                              bgcolor: "grey.200",
                              borderRadius: 4,
                              overflow: "hidden",
                            }}
                          >
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${activity.value}%` }}
                              transition={{ duration: 1, delay: index * 0.1 }}
                              style={{
                                height: "100%",
                                background: activity.color,
                              }}
                            />
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Level Progress */}
            <Grid item xs={12}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Learning Path Progress
                    </Typography>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={levelProgress} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" domain={[0, 100]} />
                        <YAxis dataKey="level" type="category" />
                        <Tooltip />
                        <Bar
                          dataKey="completion"
                          fill="#f093fb"
                          radius={[0, 8, 8, 0]}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        )}

        {activeTab === 2 && (
          <Grid container spacing={3}>
            {/* Skill Radar Chart */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Skill Proficiency
                    </Typography>
                    <ResponsiveContainer width="100%" height={350}>
                      <RadarChart data={skillProgressData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="skill" />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                        <Radar
                          name="Progress"
                          dataKey="progress"
                          stroke="#667eea"
                          fill="#667eea"
                          fillOpacity={0.6}
                        />
                        <Tooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>

            {/* Skill Progress Bars */}
            <Grid item xs={12} md={6}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.1 }}
              >
                <Card>
                  <CardContent>
                    <Typography variant="h6" fontWeight={600} gutterBottom>
                      Detailed Skill Progress
                    </Typography>
                    <Box sx={{ mt: 3 }}>
                      {skillProgressData.map((skill, index) => (
                        <Box key={index} sx={{ mb: 3 }}>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              mb: 1,
                            }}
                          >
                            <Typography variant="body2" fontWeight={600}>
                              {skill.skill}
                            </Typography>
                            <Typography
                              variant="body2"
                              color="primary.main"
                              fontWeight={700}
                            >
                              {skill.progress}%
                            </Typography>
                          </Box>
                          <Box
                            sx={{
                              height: 10,
                              bgcolor: "grey.200",
                              borderRadius: 5,
                              overflow: "hidden",
                            }}
                          >
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${skill.progress}%` }}
                              transition={{ duration: 1, delay: index * 0.1 }}
                              style={{
                                height: "100%",
                                background:
                                  "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
                              }}
                            />
                          </Box>
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          </Grid>
        )}
      </Box>
    </PageTransition>
  );
};

export default Analytics;
