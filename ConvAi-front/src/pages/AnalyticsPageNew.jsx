import { useState } from "react";
import {
  Box,
  Typography,
  Grid,
  CardContent,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  LinearProgress,
  Switch,
  FormControlLabel,
  Button,
  Container,
  useTheme,
  alpha,
} from "@mui/material";
import {
  AccessTime,
  EmojiEvents,
  Psychology,
  Assessment,
  Insights,
  Download,
  Refresh,
  AutoAwesome,
  BarChart as BarChartIcon,
  ShowChart,
  DataUsage,
} from "@mui/icons-material";
import {
  Line,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ComposedChart,
} from "recharts";
import { motion } from "framer-motion";

import {
  GlassCard,
  GradientText,
  FloatingElement,
  NeuralBackground,
  AnimatedCounter,
} from "../components/ui/AIComponents";

// Enhanced mock data for AI analytics
const weeklyProgressData = [
  {
    day: "Mon",
    studyTime: 45,
    activities: 8,
    score: 85,
    streak: 1,
    aiInsights: 12,
  },
  {
    day: "Tue",
    studyTime: 60,
    activities: 12,
    score: 92,
    streak: 2,
    aiInsights: 15,
  },
  {
    day: "Wed",
    studyTime: 38,
    activities: 6,
    score: 78,
    streak: 3,
    aiInsights: 9,
  },
  {
    day: "Thu",
    studyTime: 75,
    activities: 15,
    score: 88,
    streak: 4,
    aiInsights: 18,
  },
  {
    day: "Fri",
    studyTime: 52,
    activities: 10,
    score: 91,
    streak: 5,
    aiInsights: 14,
  },
  {
    day: "Sat",
    studyTime: 90,
    activities: 18,
    score: 95,
    streak: 6,
    aiInsights: 22,
  },
  {
    day: "Sun",
    studyTime: 35,
    activities: 7,
    score: 82,
    streak: 7,
    aiInsights: 11,
  },
];

const skillRadarData = [
  { skill: "Speaking", current: 85, target: 95, aiPrediction: 88 },
  { skill: "Listening", current: 92, target: 95, aiPrediction: 94 },
  { skill: "Reading", current: 78, target: 90, aiPrediction: 82 },
  { skill: "Writing", current: 88, target: 95, aiPrediction: 91 },
  { skill: "Grammar", current: 82, target: 90, aiPrediction: 85 },
  { skill: "Vocabulary", current: 90, target: 95, aiPrediction: 93 },
];

const activityBreakdownData = [
  {
    name: "AI Conversations",
    value: 35,
    color: "#4f46e5",
    time: 280,
    efficiency: 92,
  },
  {
    name: "Smart Flashcards",
    value: 25,
    color: "#06b6d4",
    time: 200,
    efficiency: 88,
  },
  {
    name: "Adaptive Reading",
    value: 20,
    color: "#8b5cf6",
    time: 160,
    efficiency: 85,
  },
  {
    name: "AI Writing Coach",
    value: 12,
    color: "#10b981",
    time: 96,
    efficiency: 90,
  },
  {
    name: "Voice Analysis",
    value: 8,
    color: "#f59e0b",
    time: 64,
    efficiency: 87,
  },
];

const aiInsightsData = [
  {
    insight: "Peak learning time",
    value: "8-10 PM",
    trend: "optimal",
    color: "#10b981",
  },
  {
    insight: "Strongest skill",
    value: "Listening",
    trend: "excellent",
    color: "#06b6d4",
  },
  {
    insight: "Focus area",
    value: "Reading speed",
    trend: "improving",
    color: "#8b5cf6",
  },
  {
    insight: "Next milestone",
    value: "Level 5",
    trend: "achievable",
    color: "#f59e0b",
  },
];

const TabPanel = ({ children, value, index, ...other }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`analytics-tabpanel-${index}`}
    aria-labelledby={`analytics-tab-${index}`}
    {...other}
  >
    {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
  </div>
);

// Define PropTypes for the TabPanel component
TabPanel.propTypes = {
  children: {},
  value: {},
  index: {},
};

const AnalyticsPage = () => {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState("week");
  const [isLoading, setIsLoading] = useState(false);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1500);
  };

  const calculateTotalStudyTime = () => {
    return weeklyProgressData.reduce((total, day) => total + day.studyTime, 0);
  };

  const calculateAverageScore = () => {
    const total = weeklyProgressData.reduce((sum, day) => sum + day.score, 0);
    return Math.round(total / weeklyProgressData.length);
  };

  const getCurrentStreak = () => {
    return Math.max(...weeklyProgressData.map((day) => day.streak));
  };

  const getTotalAIInsights = () => {
    return weeklyProgressData.reduce((total, day) => total + day.aiInsights, 0);
  };

  // Enhanced stat cards data with AI theming
  const statCards = [
    {
      title: "AI Learning Time",
      value: calculateTotalStudyTime(),
      suffix: " mins",
      icon: <AccessTime />,
      trend: "+12%",
      color: theme.palette.primary.main,
      description: "Smart time tracking",
      bgGradient: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
    },
    {
      title: "Performance Score",
      value: calculateAverageScore(),
      suffix: "%",
      icon: <Assessment />,
      trend: "+8%",
      color: theme.palette.success.main,
      description: "AI-analyzed progress",
      bgGradient: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
    },
    {
      title: "Learning Streak",
      value: getCurrentStreak(),
      suffix: " days",
      icon: <EmojiEvents />,
      trend: "+2",
      color: theme.palette.warning.main,
      description: "Consistency milestone",
      bgGradient: "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
    },
    {
      title: "AI Insights",
      value: getTotalAIInsights(),
      suffix: "",
      icon: <Psychology />,
      trend: "+15",
      color: theme.palette.secondary.main,
      description: "Smart recommendations",
      bgGradient: "linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)",
    },
  ];

  return (
    <Box sx={{ position: "relative", minHeight: "100vh" }}>
      <NeuralBackground opacity={0.05} />

      <Container maxWidth="xl" sx={{ py: 4, position: "relative", zIndex: 1 }}>
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header Section */}
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 4,
            }}
          >
            <Box>
              <GradientText variant="h3" gradient="primary" sx={{ mb: 1 }}>
                AI Learning Analytics
                <AutoAwesome
                  sx={{ ml: 1, fontSize: "0.8em", verticalAlign: "middle" }}
                />
              </GradientText>
              <Typography
                variant="h6"
                color="text.secondary"
                sx={{ fontWeight: 400 }}
              >
                Discover insights, track progress, and optimize your AI-powered
                learning journey
              </Typography>
            </Box>
            <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Time Range</InputLabel>
                <Select
                  value={timeRange}
                  label="Time Range"
                  onChange={(e) => setTimeRange(e.target.value)}
                >
                  <MenuItem value="week">This Week</MenuItem>
                  <MenuItem value="month">This Month</MenuItem>
                  <MenuItem value="quarter">This Quarter</MenuItem>
                  <MenuItem value="year">This Year</MenuItem>
                </Select>
              </FormControl>
              <IconButton
                onClick={handleRefresh}
                disabled={isLoading}
                sx={{
                  background:
                    "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                  color: "white",
                  "&:hover": {
                    background:
                      "linear-gradient(135deg, #4338ca 0%, #6d28d9 100%)",
                  },
                }}
              >
                <Refresh />
              </IconButton>
              <Button
                startIcon={<Download />}
                variant="outlined"
                sx={{
                  borderColor: theme.palette.primary.main,
                  color: theme.palette.primary.main,
                }}
              >
                Export
              </Button>
            </Box>
          </Box>

          {/* AI-Enhanced Stats Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {statCards.map((stat, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <FloatingElement delay={index * 0.1} amplitude={6}>
                  <GlassCard
                    sx={{
                      height: "100%",
                      background: alpha(stat.color, 0.1),
                      border: `1px solid ${alpha(stat.color, 0.3)}`,
                      position: "relative",
                      overflow: "hidden",
                    }}
                    glow={true}
                    hover={true}
                  >
                    <CardContent sx={{ p: 3 }}>
                      {/* Background gradient overlay */}
                      <Box
                        sx={{
                          position: "absolute",
                          top: 0,
                          right: 0,
                          width: "80px",
                          height: "80px",
                          background: stat.bgGradient,
                          borderRadius: "50%",
                          opacity: 0.1,
                          transform: "translate(30px, -30px)",
                        }}
                      />

                      <Box
                        sx={{ display: "flex", alignItems: "center", mb: 2 }}
                      >
                        <Box
                          sx={{
                            p: 1.5,
                            borderRadius: 3,
                            background: stat.bgGradient,
                            color: "white",
                            display: "flex",
                            alignItems: "center",
                            boxShadow: `0 8px 16px ${alpha(stat.color, 0.3)}`,
                          }}
                        >
                          {stat.icon}
                        </Box>
                        <Box sx={{ ml: "auto" }}>
                          <Chip
                            label={stat.trend}
                            size="small"
                            sx={{
                              background: alpha(
                                theme.palette.success.main,
                                0.1
                              ),
                              color: theme.palette.success.main,
                              border: `1px solid ${alpha(
                                theme.palette.success.main,
                                0.3
                              )}`,
                              fontWeight: 600,
                            }}
                          />
                        </Box>
                      </Box>

                      <Box
                        sx={{ display: "flex", alignItems: "baseline", mb: 1 }}
                      >
                        <AnimatedCounter
                          to={stat.value}
                          duration={1.5}
                          suffix={stat.suffix}
                          sx={{
                            fontSize: "2.5rem",
                            fontWeight: 800,
                            background: stat.bgGradient,
                            WebkitBackgroundClip: "text",
                            WebkitTextFillColor: "transparent",
                            backgroundClip: "text",
                          }}
                        />
                      </Box>

                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 600, mb: 0.5 }}
                      >
                        {stat.title}
                      </Typography>

                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ opacity: 0.8 }}
                      >
                        {stat.description}
                      </Typography>
                    </CardContent>
                  </GlassCard>
                </FloatingElement>
              </Grid>
            ))}
          </Grid>

          {/* AI-Enhanced Analytics Tabs */}
          <GlassCard sx={{ mb: 4, overflow: "visible" }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
              sx={{
                "& .MuiTabs-indicator": {
                  display: "none",
                },
                p: 1,
              }}
            >
              <Tab
                label="AI Overview"
                icon={<ShowChart />}
                sx={{
                  borderRadius: 2,
                  mx: 0.5,
                  minHeight: 60,
                  "&.Mui-selected": {
                    background:
                      "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                    color: "white",
                  },
                }}
              />
              <Tab
                label="Skills Analysis"
                icon={<Psychology />}
                sx={{
                  borderRadius: 2,
                  mx: 0.5,
                  minHeight: 60,
                  "&.Mui-selected": {
                    background:
                      "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                    color: "white",
                  },
                }}
              />
              <Tab
                label="Learning Patterns"
                icon={<BarChartIcon />}
                sx={{
                  borderRadius: 2,
                  mx: 0.5,
                  minHeight: 60,
                  "&.Mui-selected": {
                    background:
                      "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                    color: "white",
                  },
                }}
              />
              <Tab
                label="Performance Insights"
                icon={<DataUsage />}
                sx={{
                  borderRadius: 2,
                  mx: 0.5,
                  minHeight: 60,
                  "&.Mui-selected": {
                    background:
                      "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                    color: "white",
                  },
                }}
              />
            </Tabs>

            {/* AI Overview Tab */}
            <TabPanel value={tabValue} index={0}>
              <Grid container spacing={4}>
                {/* AI-Enhanced Weekly Progress Chart */}
                <Grid item xs={12} lg={8}>
                  <GlassCard hover={true} glow={true}>
                    <CardContent sx={{ p: 3 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          mb: 3,
                        }}
                      >
                        <GradientText variant="h6" gradient="secondary">
                          Weekly AI Learning Progress
                        </GradientText>
                        <FormControlLabel
                          control={
                            <Switch
                              defaultChecked
                              sx={{
                                "& .MuiSwitch-switchBase.Mui-checked": {
                                  color: theme.palette.primary.main,
                                },
                              }}
                            />
                          }
                          label="Show AI predictions"
                        />
                      </Box>
                      <ResponsiveContainer width="100%" height={350}>
                        <ComposedChart data={weeklyProgressData}>
                          <CartesianGrid
                            strokeDasharray="3 3"
                            stroke={alpha(theme.palette.text.secondary, 0.2)}
                          />
                          <XAxis
                            dataKey="day"
                            stroke={theme.palette.text.secondary}
                            fontSize={12}
                          />
                          <YAxis
                            yAxisId="left"
                            stroke={theme.palette.text.secondary}
                            fontSize={12}
                          />
                          <YAxis
                            yAxisId="right"
                            orientation="right"
                            stroke={theme.palette.text.secondary}
                            fontSize={12}
                          />
                          <RechartsTooltip
                            contentStyle={{
                              background: alpha(
                                theme.palette.background.paper,
                                0.9
                              ),
                              border: `1px solid ${alpha(
                                theme.palette.primary.main,
                                0.3
                              )}`,
                              borderRadius: "12px",
                              backdropFilter: "blur(10px)",
                            }}
                          />
                          <Legend />
                          <Bar
                            yAxisId="left"
                            dataKey="studyTime"
                            fill="url(#gradient1)"
                            name="Study Time (min)"
                          />
                          <Line
                            yAxisId="right"
                            type="monotone"
                            dataKey="score"
                            stroke="#4f46e5"
                            strokeWidth={3}
                            name="Score (%)"
                          />
                          <Line
                            yAxisId="right"
                            type="monotone"
                            dataKey="aiInsights"
                            stroke="#06b6d4"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            name="AI Insights"
                          />
                          <defs>
                            <linearGradient
                              id="gradient1"
                              x1="0"
                              y1="0"
                              x2="0"
                              y2="1"
                            >
                              <stop
                                offset="5%"
                                stopColor="#4f46e5"
                                stopOpacity={0.8}
                              />
                              <stop
                                offset="95%"
                                stopColor="#4f46e5"
                                stopOpacity={0.2}
                              />
                            </linearGradient>
                          </defs>
                        </ComposedChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </GlassCard>
                </Grid>

                {/* AI Activity Breakdown */}
                <Grid item xs={12} lg={4}>
                  <GlassCard sx={{ height: "100%" }} hover={true} glow={true}>
                    <CardContent sx={{ p: 3 }}>
                      <GradientText
                        variant="h6"
                        gradient="accent"
                        sx={{ mb: 3 }}
                      >
                        AI Activity Breakdown
                      </GradientText>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={activityBreakdownData}
                            cx="50%"
                            cy="50%"
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                            label={({ name, percent }) =>
                              `${name} ${(percent * 100).toFixed(0)}%`
                            }
                          >
                            {activityBreakdownData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <RechartsTooltip
                            contentStyle={{
                              background: alpha(
                                theme.palette.background.paper,
                                0.9
                              ),
                              border: `1px solid ${alpha(
                                theme.palette.primary.main,
                                0.3
                              )}`,
                              borderRadius: "12px",
                              backdropFilter: "blur(10px)",
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </GlassCard>
                </Grid>
              </Grid>

              {/* AI Insights Grid */}
              <Grid container spacing={3} sx={{ mt: 2 }}>
                {aiInsightsData.map((insight, index) => (
                  <Grid item xs={12} sm={6} md={3} key={index}>
                    <FloatingElement delay={index * 0.2} amplitude={4}>
                      <GlassCard
                        sx={{
                          textAlign: "center",
                          background: alpha(insight.color, 0.1),
                          border: `1px solid ${alpha(insight.color, 0.3)}`,
                        }}
                        hover={true}
                      >
                        <CardContent sx={{ p: 2 }}>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ mb: 1, display: "block" }}
                          >
                            {insight.insight}
                          </Typography>
                          <Typography
                            variant="h5"
                            sx={{ fontWeight: 700, mb: 1 }}
                          >
                            {insight.value}
                          </Typography>
                          <Chip
                            label={insight.trend}
                            size="small"
                            sx={{
                              background: alpha(insight.color, 0.2),
                              color: insight.color,
                              fontWeight: 600,
                            }}
                          />
                        </CardContent>
                      </GlassCard>
                    </FloatingElement>
                  </Grid>
                ))}
              </Grid>
            </TabPanel>

            {/* Skills Analysis Tab */}
            <TabPanel value={tabValue} index={1}>
              <Grid container spacing={4}>
                <Grid item xs={12} lg={6}>
                  <GlassCard hover={true} glow={true}>
                    <CardContent sx={{ p: 3 }}>
                      <GradientText
                        variant="h6"
                        gradient="primary"
                        sx={{ mb: 3 }}
                      >
                        AI Skills Radar Analysis
                      </GradientText>
                      <ResponsiveContainer width="100%" height={400}>
                        <RadarChart data={skillRadarData}>
                          <PolarGrid
                            stroke={alpha(theme.palette.text.secondary, 0.3)}
                          />
                          <PolarAngleAxis
                            dataKey="skill"
                            tick={{
                              fontSize: 12,
                              fill: theme.palette.text.secondary,
                            }}
                          />
                          <PolarRadiusAxis
                            angle={90}
                            domain={[0, 100]}
                            tick={{
                              fontSize: 10,
                              fill: theme.palette.text.secondary,
                            }}
                          />
                          <Radar
                            name="Current Level"
                            dataKey="current"
                            stroke="#4f46e5"
                            fill="#4f46e5"
                            fillOpacity={0.3}
                            strokeWidth={2}
                          />
                          <Radar
                            name="AI Prediction"
                            dataKey="aiPrediction"
                            stroke="#06b6d4"
                            fill="transparent"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                          />
                          <Radar
                            name="Target"
                            dataKey="target"
                            stroke="#10b981"
                            fill="transparent"
                            strokeWidth={1}
                            strokeDasharray="2 2"
                          />
                          <Legend />
                        </RadarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </GlassCard>
                </Grid>

                <Grid item xs={12} lg={6}>
                  <GlassCard hover={true} glow={true}>
                    <CardContent sx={{ p: 3 }}>
                      <GradientText
                        variant="h6"
                        gradient="secondary"
                        sx={{ mb: 3 }}
                      >
                        Skill Progress Timeline
                      </GradientText>
                      <Box
                        sx={{
                          height: 400,
                          display: "flex",
                          flexDirection: "column",
                          gap: 2,
                        }}
                      >
                        {skillRadarData.map((skill, index) => (
                          <Box key={skill.skill} sx={{ mb: 2 }}>
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
                                color="text.secondary"
                              >
                                {skill.current}%
                              </Typography>
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={skill.current}
                              sx={{
                                height: 8,
                                borderRadius: 4,
                                background: alpha(
                                  theme.palette.primary.main,
                                  0.1
                                ),
                                "& .MuiLinearProgress-bar": {
                                  background: `linear-gradient(90deg, ${
                                    activityBreakdownData[
                                      index % activityBreakdownData.length
                                    ].color
                                  } 0%, ${theme.palette.primary.main} 100%)`,
                                  borderRadius: 4,
                                },
                              }}
                            />
                          </Box>
                        ))}
                      </Box>
                    </CardContent>
                  </GlassCard>
                </Grid>
              </Grid>
            </TabPanel>

            {/* Additional tabs content can be added here */}
            <TabPanel value={tabValue} index={2}>
              <GlassCard>
                <CardContent sx={{ p: 4, textAlign: "center" }}>
                  <Psychology
                    sx={{
                      fontSize: 64,
                      color: theme.palette.primary.main,
                      mb: 2,
                    }}
                  />
                  <GradientText variant="h5" gradient="primary" sx={{ mb: 2 }}>
                    Learning Patterns Analysis
                  </GradientText>
                  <Typography variant="body1" color="text.secondary">
                    Advanced AI pattern recognition coming soon...
                  </Typography>
                </CardContent>
              </GlassCard>
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
              <GlassCard>
                <CardContent sx={{ p: 4, textAlign: "center" }}>
                  <Insights
                    sx={{
                      fontSize: 64,
                      color: theme.palette.secondary.main,
                      mb: 2,
                    }}
                  />
                  <GradientText
                    variant="h5"
                    gradient="secondary"
                    sx={{ mb: 2 }}
                  >
                    Performance Insights
                  </GradientText>
                  <Typography variant="body1" color="text.secondary">
                    Deep performance analytics and recommendations coming
                    soon...
                  </Typography>
                </CardContent>
              </GlassCard>
            </TabPanel>
          </GlassCard>
        </motion.div>
      </Container>
    </Box>
  );
};

export default AnalyticsPage;
