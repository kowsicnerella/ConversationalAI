import PropTypes from "prop-types";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Divider,
  Alert,
  Button,
  Grid,
} from "@mui/material";
import {
  TrendingUp,
  TrendingDown,
  Remove,
  CheckCircle,
  Warning,
  ArrowForward,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import GradientText from "./common/GradientText";

const LessonReview = ({
  review,
  motivationalMessage,
  teluguMotivationalMessage,
  onContinue,
}) => {
  if (!review) return null;

  const getPerformanceColor = (score) => {
    if (score >= 90) return "success";
    if (score >= 75) return "primary";
    if (score >= 60) return "warning";
    return "error";
  };

  const getPerformanceLabel = (score) => {
    if (score >= 90) return "Excellent";
    if (score >= 75) return "Good";
    if (score >= 60) return "Satisfactory";
    return "Needs Improvement";
  };

  const getDifficultyIcon = (adjustment) => {
    if (adjustment === "increase") return <TrendingUp />;
    if (adjustment === "decrease") return <TrendingDown />;
    return <Remove />;
  };

  const performanceColor = getPerformanceColor(review.performance_score);
  const performanceLabel = getPerformanceLabel(review.performance_score);

  return (
    <Box>
      {/* Header with Score */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card
          sx={{
            mb: 3,
            borderRadius: 3,
            background: `linear-gradient(135deg, ${
              performanceColor === "success"
                ? "#4CAF50"
                : performanceColor === "primary"
                ? "#2196F3"
                : performanceColor === "warning"
                ? "#FF9800"
                : "#F44336"
            }15 0%, ${
              performanceColor === "success"
                ? "#4CAF50"
                : performanceColor === "primary"
                ? "#2196F3"
                : performanceColor === "warning"
                ? "#FF9800"
                : "#F44336"
            }30 100%)`,
          }}
        >
          <CardContent sx={{ textAlign: "center", py: 4 }}>
            <GradientText variant="h3" sx={{ mb: 1, fontWeight: 700 }}>
              {review.performance_score}%
            </GradientText>
            <Chip
              label={performanceLabel}
              color={performanceColor}
              size="large"
              sx={{ fontSize: "1rem", fontWeight: 600 }}
            />
            <Typography variant="h6" color="text.secondary" sx={{ mt: 2 }}>
              Lesson Complete!
            </Typography>
          </CardContent>
        </Card>
      </motion.div>

      {/* Motivational Message */}
      {motivationalMessage && (
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Alert
            icon={<CheckCircle />}
            severity="info"
            sx={{ mb: 3, borderRadius: 2 }}
          >
            <Typography variant="body1" fontWeight={500}>
              {motivationalMessage}
            </Typography>
            {teluguMotivationalMessage && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {teluguMotivationalMessage}
              </Typography>
            )}
          </Alert>
        </motion.div>
      )}

      {/* Strengths & Weaknesses */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card sx={{ borderRadius: 3, height: "100%" }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <CheckCircle color="success" sx={{ mr: 1 }} />
                  <Typography variant="h6" fontWeight={600}>
                    Strengths
                  </Typography>
                </Box>
                {review.strengths && review.strengths.length > 0 ? (
                  review.strengths.map((strength, index) => (
                    <Box key={index} mb={1.5}>
                      <Typography variant="body2" color="text.primary">
                        ✓ {strength}
                      </Typography>
                    </Box>
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Keep practicing to identify your strengths!
                  </Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card sx={{ borderRadius: 3, height: "100%" }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Warning color="warning" sx={{ mr: 1 }} />
                  <Typography variant="h6" fontWeight={600}>
                    Areas to Improve
                  </Typography>
                </Box>
                {review.weaknesses && review.weaknesses.length > 0 ? (
                  review.weaknesses.map((weakness, index) => (
                    <Box key={index} mb={1.5}>
                      <Typography variant="body2" color="text.primary">
                        • {weakness}
                      </Typography>
                    </Box>
                  ))
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    Great job! No major areas of concern.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Detailed Feedback */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Card sx={{ mb: 3, borderRadius: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Detailed Feedback
            </Typography>
            <Typography variant="body1" paragraph sx={{ mt: 2 }}>
              {review.feedback_english}
            </Typography>
            {review.feedback_telugu && (
              <>
                <Divider sx={{ my: 2 }} />
                <Typography variant="body1" color="text.secondary">
                  {review.feedback_telugu}
                </Typography>
              </>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Focus Areas */}
      {review.focus_areas && review.focus_areas.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card sx={{ mb: 3, borderRadius: 3 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Focus Areas for Next Lesson
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1} mt={2}>
                {review.focus_areas.map((area, index) => (
                  <Chip
                    key={index}
                    label={area}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Difficulty Adjustment */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <Card sx={{ mb: 3, borderRadius: 3 }}>
          <CardContent>
            <Box
              display="flex"
              alignItems="center"
              justifyContent="space-between"
            >
              <Box>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Difficulty Adjustment
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {review.difficulty_adjustment === "increase"
                    ? "Great performance! Next lesson will be more challenging."
                    : review.difficulty_adjustment === "decrease"
                    ? "Let's review fundamentals. Next lesson will reinforce basics."
                    : "You're doing well. Difficulty will remain the same."}
                </Typography>
              </Box>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  color:
                    review.difficulty_adjustment === "increase"
                      ? "success.main"
                      : review.difficulty_adjustment === "decrease"
                      ? "warning.main"
                      : "info.main",
                }}
              >
                {getDifficultyIcon(review.difficulty_adjustment)}
              </Box>
            </Box>
          </CardContent>
        </Card>
      </motion.div>

      {/* Next Lesson Preview */}
      {review.next_lesson_recommendation && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <Card
            sx={{
              borderRadius: 3,
              background:
                "linear-gradient(135deg, #667eea15 0%, #764ba230 100%)",
            }}
          >
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Up Next 🎯
              </Typography>
              <Typography variant="body1" paragraph sx={{ mt: 2 }}>
                <strong>Topic:</strong>{" "}
                {review.next_lesson_recommendation.topic_focus ||
                  "Adaptive Content"}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {review.next_lesson_recommendation.reasoning ||
                  "Personalized content based on your performance"}
              </Typography>
              {review.next_lesson_recommendation.telugu_reasoning && (
                <Typography variant="body2" color="text.secondary">
                  {review.next_lesson_recommendation.telugu_reasoning}
                </Typography>
              )}

              {onContinue && (
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  endIcon={<ArrowForward />}
                  onClick={onContinue}
                  sx={{
                    mt: 3,
                    py: 1.5,
                    borderRadius: 2,
                    background: "linear-gradient(45deg, #667eea, #764ba2)",
                  }}
                >
                  Continue to Next Lesson
                </Button>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </Box>
  );
};

LessonReview.propTypes = {
  review: PropTypes.shape({
    performance_score: PropTypes.number,
    strengths: PropTypes.arrayOf(PropTypes.string),
    weaknesses: PropTypes.arrayOf(PropTypes.string),
    feedback_english: PropTypes.string,
    feedback_telugu: PropTypes.string,
    focus_areas: PropTypes.arrayOf(PropTypes.string),
    difficulty_adjustment: PropTypes.string,
    next_lesson_recommendation: PropTypes.shape({
      topic_focus: PropTypes.string,
      reasoning: PropTypes.string,
      telugu_reasoning: PropTypes.string,
    }),
  }),
  motivationalMessage: PropTypes.string,
  teluguMotivationalMessage: PropTypes.string,
  onContinue: PropTypes.func,
};

export default LessonReview;
