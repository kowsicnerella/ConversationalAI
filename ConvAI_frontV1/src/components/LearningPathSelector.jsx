import { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Grid,
  LinearProgress,
  Alert,
  CircularProgress,
} from "@mui/material";
import {
  Star,
  TrendingUp,
  AccessTime,
  CheckCircle,
  School,
} from "@mui/icons-material";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const LearningPathSelector = ({ assessmentResults, onPathSelected }) => {
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(null);
  const [recommendedPaths, setRecommendedPaths] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchRecommendedPaths();
  }, []);

  const fetchRecommendedPaths = async () => {
    try {
      setLoading(true);
      setError("");

      // Fetch personalized recommendations
      const response = await axiosInstance.post(
        API_ENDPOINTS.LEARNING_PATHS.PERSONALIZED_RECOMMENDATION,
        {
          assessment_results: assessmentResults,
        }
      );

      setRecommendedPaths(response.data.recommended_paths || []);
    } catch (err) {
      console.error("Error fetching learning paths:", err);
      setError(
        "Failed to load learning paths. Please try again or contact support."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (path) => {
    try {
      setEnrolling(path.id);
      setError("");

      // Enroll in the selected learning path
      const response = await axiosInstance.post(
        API_ENDPOINTS.COURSES.ENROLL_PATH(path.id)
      );

      // Notify parent component
      if (onPathSelected) {
        onPathSelected(path, response.data);
      }
    } catch (err) {
      console.error("Error enrolling in path:", err);
      setError(`Failed to enroll in ${path.title}. Please try again.`);
      setEnrolling(null);
    }
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      beginner: "#10b981",
      elementary: "#84cc16",
      intermediate: "#eab308",
      "upper-intermediate": "#f97316",
      advanced: "#ef4444",
    };
    return colors[difficulty?.toLowerCase()] || "#6366f1";
  };

  const getMatchScoreColor = (score) => {
    if (score >= 90) return "success";
    if (score >= 75) return "primary";
    if (score >= 60) return "warning";
    return "default";
  };

  if (loading) {
    return (
      <Box sx={{ textAlign: "center", py: 6 }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 3 }}>
          Finding Your Perfect Learning Path...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Analyzing your assessment results...
        </Typography>
      </Box>
    );
  }

  if (error && recommendedPaths.length === 0) {
    return (
      <Box sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
        <Button
          variant="contained"
          onClick={fetchRecommendedPaths}
          sx={{ mt: 2 }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: "center" }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          🎯 Your Personalized Learning Paths
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Based on your assessment, we have found the best paths for you
        </Typography>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ fontStyle: "italic", mt: 1 }}
        >
          మీ పరీక్ష ఆధారంగా, మేము మీకు ఉత్తమ మార్గాలను కనుగొన్నాము
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* Learning Paths Grid */}
      <Grid container spacing={3}>
        {recommendedPaths.map((path, index) => {
          const isRecommended = index === 0; // First path is most recommended
          const isEnrolling = enrolling === path.id;
          const matchScore = path.match_score || 0;

          return (
            <Grid item xs={12} md={6} key={path.id}>
              <Card
                sx={{
                  height: "100%",
                  position: "relative",
                  border: isRecommended ? 3 : 1,
                  borderColor: isRecommended ? "primary.main" : "divider",
                  background: isRecommended
                    ? "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)"
                    : "transparent",
                  transition: "all 0.3s ease",
                  "&:hover": {
                    transform: "translateY(-4px)",
                    boxShadow: 6,
                  },
                }}
              >
                {isRecommended && (
                  <Chip
                    icon={<Star />}
                    label="RECOMMENDED FOR YOU"
                    color="primary"
                    sx={{
                      position: "absolute",
                      top: 16,
                      right: 16,
                      fontWeight: 700,
                      zIndex: 1,
                    }}
                  />
                )}

                <CardContent sx={{ p: 3 }}>
                  {/* Path Title */}
                  <Typography
                    variant="h5"
                    fontWeight={700}
                    gutterBottom
                    sx={{ mt: isRecommended ? 2 : 0 }}
                  >
                    {path.title}
                  </Typography>

                  {/* Telugu Title */}
                  {path.title_telugu && (
                    <Typography
                      variant="body1"
                      color="text.secondary"
                      sx={{ fontStyle: "italic", mb: 2 }}
                    >
                      {path.title_telugu}
                    </Typography>
                  )}

                  {/* Match Score */}
                  <Box sx={{ mb: 2 }}>
                    <Box
                      sx={{
                        display: "flex",
                        justifyContent: "space-between",
                        mb: 1,
                      }}
                    >
                      <Typography variant="body2" fontWeight={600}>
                        Match Score
                      </Typography>
                      <Typography
                        variant="body2"
                        fontWeight={700}
                        color={getMatchScoreColor(matchScore)}
                      >
                        {matchScore}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={matchScore}
                      color={getMatchScoreColor(matchScore)}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  {/* Description */}
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {path.description || "No description available"}
                  </Typography>

                  {/* Metadata Chips */}
                  <Box
                    sx={{ display: "flex", gap: 1, flexWrap: "wrap", mb: 2 }}
                  >
                    {/* Difficulty */}
                    <Chip
                      label={path.difficulty_level || "Intermediate"}
                      size="small"
                      sx={{
                        backgroundColor: getDifficultyColor(
                          path.difficulty_level
                        ),
                        color: "white",
                        fontWeight: 600,
                      }}
                    />

                    {/* Duration */}
                    {path.estimated_duration && (
                      <Chip
                        icon={<AccessTime sx={{ fontSize: 16 }} />}
                        label={path.estimated_duration}
                        size="small"
                        variant="outlined"
                      />
                    )}

                    {/* Lesson Count */}
                    {path.total_lessons && (
                      <Chip
                        icon={<School sx={{ fontSize: 16 }} />}
                        label={`${path.total_lessons} Lessons`}
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>

                  {/* Skill Focus Tags */}
                  {path.skill_focus && path.skill_focus.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="caption"
                        fontWeight={600}
                        color="text.secondary"
                        gutterBottom
                      >
                        FOCUS AREAS:
                      </Typography>
                      <Box
                        sx={{
                          display: "flex",
                          gap: 0.5,
                          flexWrap: "wrap",
                          mt: 1,
                        }}
                      >
                        {path.skill_focus.map((skill, idx) => (
                          <Chip
                            key={idx}
                            label={skill}
                            size="small"
                            icon={<TrendingUp sx={{ fontSize: 14 }} />}
                            sx={{ fontSize: "0.75rem" }}
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* Benefits List */}
                  {path.benefits && path.benefits.length > 0 && (
                    <Box sx={{ mb: 3 }}>
                      <Typography
                        variant="caption"
                        fontWeight={600}
                        color="text.secondary"
                        gutterBottom
                      >
                        WHAT YOU&apos;LL LEARN:
                      </Typography>
                      <Box sx={{ mt: 1 }}>
                        {path.benefits.slice(0, 3).map((benefit, idx) => (
                          <Box
                            key={idx}
                            sx={{
                              display: "flex",
                              alignItems: "flex-start",
                              mb: 0.5,
                            }}
                          >
                            <CheckCircle
                              sx={{
                                fontSize: 16,
                                color: "success.main",
                                mr: 1,
                                mt: 0.3,
                              }}
                            />
                            <Typography variant="body2">{benefit}</Typography>
                          </Box>
                        ))}
                      </Box>
                    </Box>
                  )}

                  {/* Enroll Button */}
                  <Button
                    variant={isRecommended ? "contained" : "outlined"}
                    color="primary"
                    fullWidth
                    size="large"
                    disabled={isEnrolling}
                    onClick={() => handleEnroll(path)}
                    sx={{
                      mt: 2,
                      fontWeight: 700,
                      ...(isRecommended && {
                        background:
                          "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      }),
                    }}
                  >
                    {isEnrolling ? (
                      <>
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                        Enrolling...
                      </>
                    ) : (
                      <>
                        {isRecommended ? "Start This Path" : "Select This Path"}
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* No Paths Available */}
      {recommendedPaths.length === 0 && !loading && (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body1" fontWeight={600}>
            No personalized paths available yet
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>
            Please complete your initial assessment first, or contact support if
            you believe this is an error.
          </Typography>
        </Alert>
      )}

      {/* Help Text */}
      <Alert severity="info" sx={{ mt: 4 }}>
        <Typography variant="body2">
          💡 <strong>Tip:</strong> We recommend starting with the path marked
          &quot;RECOMMENDED FOR YOU&quot; as it best matches your current skill
          level and learning goals. You can switch paths anytime from your
          dashboard.
        </Typography>
      </Alert>
    </Box>
  );
};

export default LearningPathSelector;
