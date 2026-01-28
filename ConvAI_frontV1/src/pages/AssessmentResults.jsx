import { useEffect, useState } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
} from "@mui/material";
import { useNavigate, useLocation } from "react-router-dom";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import {
  TrendingUp,
  TrendingDown,
  EmojiEvents,
  ArrowForward,
  Star,
  ArrowBack,
  Home,
} from "@mui/icons-material";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const AssessmentResults = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  useEffect(() => {
    // Check if results were passed via navigation state
    if (location.state?.results) {
      setResults(location.state.results);
    } else if (location.state?.assessmentId) {
      // Fetch results if we only have assessment ID
      fetchResults(location.state.assessmentId);
    } else {
      // No data available, redirect to dashboard
      navigate("/dashboard");
    }
  }, [location, navigate]);

  const fetchResults = async (assessmentId) => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(
        API_ENDPOINTS.ASSESSMENT.RESULTS(assessmentId)
      );
      setResults(response.data.results);
    } catch (err) {
      console.error("Error fetching results:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewLearningPaths = () => {
    // Check if we came from onboarding
    const fromOnboarding = location.state?.fromOnboarding;

    if (fromOnboarding) {
      // Navigate back to onboarding with results
      navigate("/onboarding", {
        state: {
          assessmentResults: results,
          currentStep: 4, // Go to path selection step
        },
        replace: true,
      });
    } else {
      // Navigate to learning paths page
      navigate("/learning-paths", {
        state: {
          fromAssessment: true,
          proficiencyLevel: results?.overall_proficiency_level,
          assessmentResults: results,
        },
      });
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 3 }}>
          Loading Results...
        </Typography>
      </Container>
    );
  }

  if (!results) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="error">
          No assessment results found. Please complete an assessment first.
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate("/assessment")}
          sx={{ mt: 2 }}
        >
          Take Assessment
        </Button>
      </Container>
    );
  }

  // Transform skill breakdown for radar chart
  const radarData = results.skill_breakdown
    ? Object.entries(results.skill_breakdown).map(([skill, score]) => ({
        skill: skill.replace(/_/g, " ").toUpperCase(),
        score: Math.round(score),
        fullMark: 100,
      }))
    : [];

  // Determine proficiency color
  const getProficiencyColor = (level) => {
    const colors = {
      beginner: "#ef4444",
      elementary: "#f97316",
      intermediate: "#eab308",
      "upper-intermediate": "#84cc16",
      advanced: "#22c55e",
      proficient: "#10b981",
    };
    return colors[level?.toLowerCase()] || "#6366f1";
  };

  const proficiencyColor = getProficiencyColor(
    results.overall_proficiency_level
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Navigation Buttons */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBack />}
          onClick={() => navigate(-1)}
          size="small"
        >
          Back
        </Button>
        <Button
          variant="outlined"
          startIcon={<Home />}
          onClick={() => navigate('/dashboard')}
          size="small"
        >
          Dashboard
        </Button>
      </Box>

      {/* Header */}
      <Box sx={{ textAlign: "center", mb: 4 }}>
        <Typography variant="h3" fontWeight={700} gutterBottom>
          🎉 Assessment Complete!
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Here's your personalized English proficiency report
        </Typography>
      </Box>

      {/* Overall Score Card */}
      <Card
        sx={{
          mb: 4,
          background: `linear-gradient(135deg, ${proficiencyColor} 0%, ${proficiencyColor}dd 100%)`,
          color: "white",
        }}
      >
        <CardContent sx={{ p: 4, textAlign: "center" }}>
          <EmojiEvents sx={{ fontSize: 80, mb: 2 }} />
          <Typography variant="h2" fontWeight={800}>
            {Math.round(results.overall_score)}%
          </Typography>
          <Typography variant="h5" fontWeight={600} sx={{ mt: 2 }}>
            Overall Score
          </Typography>
          <Chip
            icon={<Star />}
            label={results.overall_proficiency_level?.toUpperCase() || "N/A"}
            sx={{
              mt: 2,
              backgroundColor: "rgba(255,255,255,0.2)",
              color: "white",
              fontSize: "1.1rem",
              fontWeight: 700,
              px: 2,
              py: 3,
            }}
            size="medium"
          />
          <Typography variant="body1" sx={{ mt: 2, opacity: 0.9 }}>
            You're on the right path to mastering English!
          </Typography>
        </CardContent>
      </Card>

      <Grid container spacing={4}>
        {/* Radar Chart */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                📊 Skill Breakdown
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="skill" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar
                    name="Score"
                    dataKey="score"
                    stroke={proficiencyColor}
                    fill={proficiencyColor}
                    fillOpacity={0.6}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Skill Details */}
        <Grid item xs={12} md={6}>
          <Card sx={{ height: "100%" }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                🎯 Detailed Scores
              </Typography>
              <Box sx={{ mt: 3 }}>
                {results.skill_breakdown &&
                  Object.entries(results.skill_breakdown).map(
                    ([skill, score], index) => (
                      <Box key={index} sx={{ mb: 3 }}>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            mb: 1,
                          }}
                        >
                          <Typography variant="body1" fontWeight={600}>
                            {skill.replace(/_/g, " ").toUpperCase()}
                          </Typography>
                          <Typography
                            variant="body1"
                            fontWeight={700}
                            color="primary"
                          >
                            {Math.round(score)}%
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={score}
                          sx={{
                            height: 10,
                            borderRadius: 5,
                            backgroundColor: "#e5e7eb",
                            "& .MuiLinearProgress-bar": {
                              backgroundColor: proficiencyColor,
                            },
                          }}
                        />
                      </Box>
                    )
                  )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Strengths */}
        {results.strengths && results.strengths.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                height: "100%",
                background: "linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%)",
              }}
            >
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <TrendingUp sx={{ fontSize: 32, mr: 1, color: "#059669" }} />
                  <Typography variant="h6" fontWeight={600}>
                    💪 Your Strengths
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                  {results.strengths.map((strength, index) => (
                    <Alert
                      key={index}
                      severity="success"
                      sx={{ backgroundColor: "rgba(255,255,255,0.5)" }}
                    >
                      <Typography variant="body1" fontWeight={500}>
                        {strength.english || strength}
                      </Typography>
                      {strength.telugu && (
                        <Typography
                          variant="body2"
                          sx={{ mt: 0.5, fontStyle: "italic" }}
                        >
                          {strength.telugu}
                        </Typography>
                      )}
                    </Alert>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Weaknesses */}
        {results.weaknesses && results.weaknesses.length > 0 && (
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                height: "100%",
                background: "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
              }}
            >
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <TrendingDown
                    sx={{ fontSize: 32, mr: 1, color: "#dc2626" }}
                  />
                  <Typography variant="h6" fontWeight={600}>
                    📈 Areas to Improve
                  </Typography>
                </Box>
                <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
                  {results.weaknesses.map((weakness, index) => (
                    <Alert
                      key={index}
                      severity="warning"
                      sx={{ backgroundColor: "rgba(255,255,255,0.5)" }}
                    >
                      <Typography variant="body1" fontWeight={500}>
                        {weakness.english || weakness}
                      </Typography>
                      {weakness.telugu && (
                        <Typography
                          variant="body2"
                          sx={{ mt: 0.5, fontStyle: "italic" }}
                        >
                          {weakness.telugu}
                        </Typography>
                      )}
                    </Alert>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Recommendations */}
        {results.recommendations && results.recommendations.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  💡 Personalized Recommendations
                </Typography>
                <Grid container spacing={2} sx={{ mt: 2 }}>
                  {results.recommendations.map((rec, index) => (
                    <Grid item xs={12} md={6} key={index}>
                      <Alert
                        severity="info"
                        sx={{
                          backgroundColor: "#eff6ff",
                          "& .MuiAlert-icon": {
                            color: "#3b82f6",
                          },
                        }}
                      >
                        <Typography variant="body1">
                          {rec.english || rec}
                        </Typography>
                        {rec.telugu && (
                          <Typography
                            variant="body2"
                            sx={{ mt: 1, fontStyle: "italic", opacity: 0.8 }}
                          >
                            {rec.telugu}
                          </Typography>
                        )}
                      </Alert>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Action Button */}
      <Box sx={{ textAlign: "center", mt: 4 }}>
        <Button
          variant="contained"
          size="large"
          endIcon={<ArrowForward />}
          onClick={handleViewLearningPaths}
          sx={{
            px: 6,
            py: 2,
            fontSize: "1.1rem",
            background: `linear-gradient(135deg, ${proficiencyColor} 0%, ${proficiencyColor}dd 100%)`,
            "&:hover": {
              background: `linear-gradient(135deg, ${proficiencyColor}dd 0%, ${proficiencyColor}bb 100%)`,
            },
          }}
        >
          View Personalized Learning Paths
        </Button>
      </Box>
    </Container>
  );
};

export default AssessmentResults;
