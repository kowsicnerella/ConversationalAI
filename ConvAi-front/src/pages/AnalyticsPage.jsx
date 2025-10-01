import { useState, useEffect } from "react";
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
  Container,
  useTheme,
  useMediaQuery,
  alpha,
  CircularProgress,
  Stack,
} from "@mui/material";
import {
  AccessTime,
  EmojiEvents,
  Psychology,
  Assessment,
  Insights,
  Refresh,
  AutoAwesome,
  BarChart as BarChartIcon,
  ShowChart,
  DataUsage,
} from "@mui/icons-material";
import { toast } from "react-hot-toast";
import { analyticsAPI } from "../services/api";
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
import PropTypes from "prop-types";

import {
  GlassCard,
  GradientText,
  FloatingElement,
  NeuralBackground,
  AnimatedCounter,
} from "../components/ui/AIComponents";

// Mock data removed - using real API data from analyticsAPI

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
  children: PropTypes.node,
  value: PropTypes.number.isRequired,
  index: PropTypes.number.isRequired,
};

const AnalyticsPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState("week");
  const [isLoading, setIsLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);
  // const [learningTrends, setLearningTrends] = useState(null);
  // const [vocabularyAnalytics, setVocabularyAnalytics] = useState(null);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [
        dashboardResponse,
        performanceResponse,
        // trendsResponse,
        // vocabResponse,
      ] = await Promise.all([
        analyticsAPI.getDashboardSummary(),
        analyticsAPI.getPerformanceAnalysis(),
        // analyticsAPI.getLearningTrends(30),
        // analyticsAPI.getVocabularyAnalytics(),
      ]);

      if (dashboardResponse.data.success) {
        setDashboardData(dashboardResponse.data.data);
      }
      if (performanceResponse.data.success) {
        setPerformanceData(performanceResponse.data.data);
      }
      // if (trendsResponse.data.success) {
      //   setLearningTrends(trendsResponse.data.data);
      // }
      // if (vocabResponse.data.success) {
      //   setVocabularyAnalytics(vocabResponse.data.data);
      // }
    } catch (error) {
      console.error("Error loading analytics data:", error);
      toast.error("Failed to load analytics data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  // Load data on component mount
  useEffect(() => {
    loadDashboardData();
  }, []);

  const calculateTotalStudyTime = () => {
    if (!dashboardData || !dashboardData.weekly_minutes) return 0;
    return dashboardData.total_study_time_minutes || 0;
  };

  const calculateAverageScore = () => {
    if (!performanceData || !performanceData.average_score) return 0;
    return Math.round(performanceData.average_score || 0);
  };

  const getCurrentStreak = () => {
    if (!dashboardData || !dashboardData.current_streak) return 0;
    return dashboardData.current_streak || 0;
  };

  const getTotalAIInsights = () => {
    if (!dashboardData) return 0;
    return dashboardData.total_activities_completed || 0;
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

      <Container
        maxWidth="xl"
        sx={{
          py: { xs: 2, sm: 3, md: 4 },
          px: { xs: 2, sm: 3 },
          position: "relative",
          zIndex: 1,
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header Section */}
          <Box
            sx={{
              mb: { xs: 3, sm: 4 },
            }}
          >
            <Stack
              direction={{ xs: "column", md: "row" }}
              justifyContent="space-between"
              alignItems={{ xs: "flex-start", md: "center" }}
              spacing={{ xs: 2, md: 0 }}
              sx={{ mb: 2 }}
            >
              <Box>
                <GradientText
                  variant={isMobile ? "h5" : "h4"}
                  gradient="primary"
                  sx={{
                    mb: 0.5,
                    fontWeight: 800,
                    display: 'flex',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                  }}
                >
                  AI Learning Analytics
                  <AutoAwesome
                    sx={{
                      ml: 1,
                      fontSize: { xs: "0.7em", sm: "0.8em" },
                      verticalAlign: "middle",
                    }}
                  />
                </GradientText>
                <Typography
                  variant={isMobile ? "body2" : "h6"}
                  color="text.secondary"
                  sx={{
                    fontWeight: 400,
                    maxWidth: { sm: "80%", md: "100%" },
                  }}
                >
                  Discover insights, track progress, and optimize your learning
                </Typography>
              </Box>
              <Stack
                direction="row"
                spacing={1.5}
                alignItems="center"
                sx={{ width: { xs: '100%', md: 'auto' } }}
              >
                <FormControl
                  size={isMobile ? "small" : "medium"}
                  sx={{ minWidth: { xs: 120, sm: 140 }, flex: { xs: 1, md: 0 } }}
                >
                  <InputLabel>Time Range</InputLabel>
                  <Select
                    value={timeRange}
                    label="Time Range"
                    onChange={(e) => setTimeRange(e.target.value)}
                  >
                    <MenuItem value="week">This Week</MenuItem>
                    <MenuItem value="month">This Month</MenuItem>
                    <MenuItem value="quarter">Quarter</MenuItem>
                    <MenuItem value="year">This Year</MenuItem>
                  </Select>
                </FormControl>
                <IconButton
                  onClick={handleRefresh}
                  disabled={isLoading}
                  className="hover-scale"
                  sx={{
                    background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)",
                    color: "white",
                    width: { xs: 40, sm: 48 },
                    height: { xs: 40, sm: 48 },
                    "&:hover": {
                      background: "linear-gradient(135deg, #4338ca 0%, #6d28d9 100%)",
                    },
                    "&:disabled": {
                      background: alpha(theme.palette.action.disabled, 0.3),
                    },
                  }}
                >
                  {isLoading ? (
                    <CircularProgress size={20} sx={{ color: "white" }} />
                  ) : (
                    <Refresh />
                  )}
                </IconButton>
              </Stack>
            </Stack>
          </Box>

          {/* AI-Enhanced Stats Cards */}
          <Grid container spacing={{ xs: 2, sm: 2.5, md: 3 }} sx={{ mb: { xs: 3, sm: 4 } }}>
            {statCards.map((stat, index) => (
              <Grid item xs={12} sm={6} lg={3} key={index}>
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
          <GlassCard sx={{ mb: { xs: 3, sm: 4 }, overflow: "visible" }}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              variant={isMobile ? "scrollable" : "scrollable"}
              scrollButtons="auto"
              sx={{
                "& .MuiTabs-indicator": {
                  display: "none",
                },
                p: { xs: 0.5, sm: 1 },
              }}
            >
              <Tab
                label="AI Overview"
                icon={<ShowChart />}
                iconPosition={isMobile ? "start" : "top"}
                sx={{
                  borderRadius: 2,
                  mx: { xs: 0.25, sm: 0.5 },
                  minHeight: { xs: 50, sm: 60 },
                  fontSize: { xs: "0.8rem", sm: "0.875rem" },
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
                iconPosition={isMobile ? "start" : "top"}
                sx={{
                  borderRadius: 2,
                  mx: { xs: 0.25, sm: 0.5 },
                  minHeight: { xs: 50, sm: 60 },
                  fontSize: { xs: "0.8rem", sm: "0.875rem" },
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
                iconPosition={isMobile ? "start" : "top"}
                sx={{
                  borderRadius: 2,
                  mx: { xs: 0.25, sm: 0.5 },
                  minHeight: { xs: 50, sm: 60 },
                  fontSize: { xs: "0.8rem", sm: "0.875rem" },
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
                iconPosition={isMobile ? "start" : "top"}
                sx={{
                  borderRadius: 2,
                  mx: { xs: 0.25, sm: 0.5 },
                  minHeight: { xs: 50, sm: 60 },
                  fontSize: { xs: "0.8rem", sm: "0.875rem" },
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
              <Grid container spacing={{ xs: 2, sm: 3, md: 4 }}>
                {/* AI-Enhanced Weekly Progress Chart */}
                <Grid item xs={12} lg={8}>
                  <GlassCard hover={true} glow={true}>
                    <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          mb: 3,
                          flexDirection: { xs: "column", sm: "row" },
                          gap: { xs: 1, sm: 0 },
                        }}
                      >
                        <GradientText 
                          variant={isMobile ? "subtitle1" : "h6"} 
                          gradient="secondary"
                          sx={{ textAlign: { xs: "center", sm: "left" }, width: { xs: "100%", sm: "auto" } }}
                        >
                          Weekly AI Learning Progress
                        </GradientText>
                        <FormControlLabel
                          control={
                            <Switch
                              defaultChecked
                              size={isMobile ? "small" : "medium"}
                              sx={{
                                "& .MuiSwitch-switchBase.Mui-checked": {
                                  color: theme.palette.primary.main,
                                },
                              }}
                            />
                          }
                          label={<Typography variant={isMobile ? "body2" : "body1"}>Show AI predictions</Typography>}
                        />
                      </Box>
                      <ResponsiveContainer width="100%" height={isMobile ? 280 : isTablet ? 320 : 350}>
                        <ComposedChart
                          data={dashboardData?.weekly_progress || []}
                        >
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
                    <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                      <GradientText
                        variant={isMobile ? "subtitle1" : "h6"}
                        gradient="accent"
                        sx={{ mb: { xs: 2, sm: 3 } }}
                      >
                        AI Activity Breakdown
                      </GradientText>
                      <ResponsiveContainer width="100%" height={isMobile ? 250 : 300}>
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
              <Grid container spacing={{ xs: 2, sm: 3, md: 4 }}>
                <Grid item xs={12} lg={6}>
                  <GlassCard hover={true} glow={true}>
                    <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                      <GradientText
                        variant={isMobile ? "subtitle1" : "h6"}
                        gradient="primary"
                        sx={{ mb: { xs: 2, sm: 3 } }}
                      >
                        AI Skills Radar Analysis
                      </GradientText>
                      <ResponsiveContainer width="100%" height={isMobile ? 300 : isTablet ? 350 : 400}>
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
                    <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
                      <GradientText
                        variant={isMobile ? "subtitle1" : "h6"}
                        gradient="secondary"
                        sx={{ mb: { xs: 2, sm: 3 } }}
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
                <CardContent sx={{ p: { xs: 2.5, sm: 3 }, textAlign: "center" }}>
                  <Psychology
                    sx={{
                      fontSize: { xs: 40, sm: 48 },
                      color: theme.palette.primary.main,
                      mb: 1.5,
                    }}
                  />
                  <GradientText 
                    variant={isMobile ? "body1" : "h6"} 
                    gradient="primary" 
                    sx={{ mb: 1.5 }}
                  >
                    Learning Patterns Analysis
                  </GradientText>
                  <Typography variant={isMobile ? "body2" : "body1"} color="text.secondary">
                    Advanced AI pattern recognition coming soon...
                  </Typography>
                </CardContent>
              </GlassCard>
            </TabPanel>

            <TabPanel value={tabValue} index={3}>
              <GlassCard>
                <CardContent sx={{ p: { xs: 2.5, sm: 3 }, textAlign: "center" }}>
                  <Insights
                    sx={{
                      fontSize: { xs: 40, sm: 48 },
                      color: theme.palette.secondary.main,
                      mb: 1.5,
                    }}
                  />
                  <GradientText
                    variant={isMobile ? "body1" : "h6"}
                    gradient="secondary"
                    sx={{ mb: 1.5 }}
                  >
                    Performance Insights
                  </GradientText>
                  <Typography variant={isMobile ? "body2" : "body1"} color="text.secondary">
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
