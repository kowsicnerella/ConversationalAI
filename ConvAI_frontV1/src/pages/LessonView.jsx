import { useState, useEffect, useRef } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Chip,
  Alert,
  CircularProgress,
} from "@mui/material";
import { useParams, useNavigate } from "react-router-dom";
import {
  AccessTime,
  CheckCircle,
  ArrowBack,
  TrendingUp,
} from "@mui/icons-material";
import axiosInstance, { API_ENDPOINTS } from "../config/api";
import LessonReview from "../components/LessonReview";
import MilestoneModal from "../components/MilestoneModal";

// Activity type components
import QuizActivity from "./activities/QuizActivity";
import FlashcardsActivity from "./activities/FlashcardsActivity";
import ReadingActivity from "./activities/ReadingActivity";

const LessonView = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const completingLessonRef = useRef(false);
  const [lesson, setLesson] = useState(null);
  const [activity, setActivity] = useState(null);
  const [lessonReview, setLessonReview] = useState(null);
  const [nextLesson, setNextLesson] = useState(null);
  const [milestone, setMilestone] = useState(null);
  const [showReview, setShowReview] = useState(false);
  const [showMilestone, setShowMilestone] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [activityScore, setActivityScore] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (lessonId) {
      fetchLesson();
    } else {
      // No lesson ID provided, fetch next lesson
      fetchNextLesson();
    }
  }, [lessonId]);

  const fetchLesson = async () => {
    try {
      setLoading(true);
      setError("");

      // Fetch lesson details
      const response = await axiosInstance.get(
        API_ENDPOINTS.COURSES.PATH_DETAIL(lessonId)
      );

      setLesson(response.data.lesson || response.data);
      setActivity(response.data.activity || response.data.lesson?.activity);
      setStartTime(Date.now());
    } catch (err) {
      console.error("Error fetching lesson:", err);
      setError("Failed to load lesson. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchNextLesson = async () => {
    try {
      setLoading(true);
      setError("");

      // Fetch next recommended lesson
      const response = await axiosInstance.get(API_ENDPOINTS.LESSON.NEXT);

      if (response.data.next_lesson) {
        setLesson(response.data.next_lesson);
        setActivity(response.data.next_lesson.activity);
        setStartTime(Date.now());
      } else {
        setError("No lessons available. Please check your learning path.");
      }
    } catch (err) {
      console.error("Error fetching next lesson:", err);
      setError("Failed to load next lesson. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleActivityComplete = async (score, results) => {
    if (completingLessonRef.current) {
      console.log("handleActivityComplete already in progress - ignoring duplicate call");
      return;
    }

    try {
      completingLessonRef.current = true;
      setSubmitting(true);
      setActivityScore(score);

      const timeSpent = Math.floor((Date.now() - startTime) / 1000); // seconds

      // Call lesson completion endpoint
      const response = await axiosInstance.post(API_ENDPOINTS.LESSON.COMPLETE, {
        lesson_id: lesson.id,
        activity_id: activity.id,
        score: score,
        time_spent: timeSpent,
        activity_type: activity.activity_type || activity.type,
        activity_results: results,
      });

      // Extract response data
      const { lesson_review, next_lesson, milestone_achieved } = response.data;

      setLessonReview(lesson_review);
      setNextLesson(next_lesson);

      if (milestone_achieved) {
        setMilestone(milestone_achieved);
        setShowMilestone(true);
      }

      // Show review
      setShowReview(true);
    } catch (err) {
      console.error("Error completing lesson:", err);
      setError("Failed to save lesson progress. Please try again.");
    } finally {
      setSubmitting(false);
      completingLessonRef.current = false;
    }
  };

  const handleContinueToNext = () => {
    if (nextLesson) {
      // Navigate to next lesson
      navigate(`/lesson/${nextLesson.id}`, { replace: true });
      // Reset state
      setShowReview(false);
      setLessonReview(null);
      setActivityScore(null);
      setLesson(null);
      setActivity(null);
      // Fetch next lesson
      fetchLesson();
    } else {
      // No more lessons, go to dashboard
      navigate("/dashboard");
    }
  };

  const renderActivity = () => {
    if (!activity) {
      return (
        <Alert severity="warning">
          No activity found for this lesson. Please contact support.
        </Alert>
      );
    }

    const activityType = (
      activity.activity_type ||
      activity.type ||
      ""
    ).toLowerCase();

    // Map activity type to component
    switch (activityType) {
      case "quiz":
      case "multiple_choice":
        return (
          <QuizActivity
            activityId={activity.id}
            onComplete={handleActivityComplete}
            embedded={true}
          />
        );

      case "flashcards":
      case "flashcard":
        return (
          <FlashcardsActivity
            activityId={activity.id}
            onComplete={handleActivityComplete}
            embedded={true}
          />
        );

      case "reading":
      case "reading_comprehension":
        return (
          <ReadingActivity
            activityId={activity.id}
            onComplete={handleActivityComplete}
            embedded={true}
          />
        );

      case "writing":
      case "writing_prompt":
        return (
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body1" fontWeight={600}>
              Writing Activity Coming Soon
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Writing activities are under development. For now, please continue
              to the next lesson.
            </Typography>
            <Button
              variant="contained"
              onClick={() => handleActivityComplete(100, { status: "skipped" })}
              sx={{ mt: 2 }}
              disabled={submitting}
            >
              Continue to Next Lesson
            </Button>
          </Alert>
        );

      case "roleplay":
      case "role_play":
        return (
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body1" fontWeight={600}>
              Role Play Activity Coming Soon
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Role play activities are under development. For now, please
              continue to the next lesson.
            </Typography>
            <Button
              variant="contained"
              onClick={() => handleActivityComplete(100, { status: "skipped" })}
              sx={{ mt: 2 }}
              disabled={submitting}
            >
              Continue to Next Lesson
            </Button>
          </Alert>
        );

      default:
        return (
          <Alert severity="error">
            <Typography variant="body1" fontWeight={600}>
              Unknown Activity Type: {activityType}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              This activity type is not supported yet. Please try another lesson
              or contact support.
            </Typography>
            <Button
              variant="outlined"
              onClick={() => navigate("/dashboard")}
              sx={{ mt: 2 }}
            >
              Back to Dashboard
            </Button>
          </Alert>
        );
    }
  };

  // Get motivational message based on score
  const getMotivationalMessage = (score) => {
    if (score >= 90) {
      return {
        english: "Outstanding work! You're mastering English beautifully! 🌟",
        telugu:
          "అద్భుతమైన పని! మీరు ఇంగ్లీష్‌ను అద్భుతంగా నేర్చుకుంటున్నారు! 🌟",
      };
    } else if (score >= 75) {
      return {
        english: "Great job! You're making excellent progress! 🎯",
        telugu: "మంచి పని! మీరు అద్భుతమైన పురోగతి చేస్తున్నారు! 🎯",
      };
    } else if (score >= 60) {
      return {
        english: "Good effort! Keep practicing and you'll improve! 💪",
        telugu: "మంచి ప్రయత్నం! సాధన కొనసాగించండి మరియు మీరు మెరుగుపడతారు! 💪",
      };
    } else if (score >= 50) {
      return {
        english: "You're learning! Let's review the areas that need work. 📚",
        telugu:
          "మీరు నేర్చుకుంటున్నారు! పని అవసరమైన ప్రాంతాలను సమీక్షిస్తాము. 📚",
      };
    } else {
      return {
        english: "Don't give up! Every expert was once a beginner. 🌱",
        telugu: "వదులుకోవద్దు! ప్రతి నిపుణుడు ఒకప్పుడు ప్రారంభకుడే. 🌱",
      };
    }
  };

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: "center" }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 3 }}>
          Loading Lesson...
        </Typography>
      </Container>
    );
  }

  if (error && !lesson) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="error">{error}</Alert>
        <Box sx={{ display: "flex", gap: 2, mt: 3 }}>
          <Button
            variant="outlined"
            startIcon={<ArrowBack />}
            onClick={() => navigate("/dashboard")}
          >
            Back to Dashboard
          </Button>
          <Button
            variant="contained"
            onClick={lessonId ? fetchLesson : fetchNextLesson}
          >
            Retry
          </Button>
        </Box>
      </Container>
    );
  }

  // Show lesson review after completion
  if (showReview && lessonReview) {
    const motivationalMsg = getMotivationalMessage(activityScore);

    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LessonReview
          review={lessonReview}
          motivationalMessage={motivationalMsg.english}
          teluguMotivationalMessage={motivationalMsg.telugu}
          onContinue={handleContinueToNext}
        />

        {/* Milestone Modal */}
        {showMilestone && milestone && (
          <MilestoneModal
            open={showMilestone}
            onClose={() => setShowMilestone(false)}
            milestone={milestone}
          />
        )}
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate("/dashboard")}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>

        <Card
          sx={{
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
          }}
        >
          <CardContent>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "flex-start",
              }}
            >
              <Box sx={{ flex: 1 }}>
                <Typography variant="h4" fontWeight={700} gutterBottom>
                  {lesson?.title || "Current Lesson"}
                </Typography>
                {lesson?.title_telugu && (
                  <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
                    {lesson.title_telugu}
                  </Typography>
                )}
                <Typography variant="body1" sx={{ opacity: 0.95 }}>
                  {lesson?.description || "Complete this lesson to continue"}
                </Typography>
              </Box>

              <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
                {lesson?.difficulty_level && (
                  <Chip
                    label={lesson.difficulty_level}
                    sx={{
                      backgroundColor: "rgba(255,255,255,0.2)",
                      color: "white",
                    }}
                  />
                )}
                {lesson?.estimated_time && (
                  <Chip
                    icon={<AccessTime sx={{ color: "white !important" }} />}
                    label={`${lesson.estimated_time} min`}
                    sx={{
                      backgroundColor: "rgba(255,255,255,0.2)",
                      color: "white",
                    }}
                  />
                )}
              </Box>
            </Box>

            {/* Progress in learning path */}
            {lesson?.learning_path_progress && (
              <Box sx={{ mt: 3 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mb: 1,
                  }}
                >
                  <Typography variant="body2">
                    Lesson {lesson.learning_path_progress.current_lesson} of{" "}
                    {lesson.learning_path_progress.total_lessons}
                  </Typography>
                  <Typography variant="body2">
                    {lesson.learning_path_progress.completion_percentage}%
                    Complete
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={lesson.learning_path_progress.completion_percentage}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: "rgba(255,255,255,0.3)",
                    "& .MuiLinearProgress-bar": {
                      backgroundColor: "white",
                    },
                  }}
                />
              </Box>
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}

      {/* Activity Content */}
      <Box sx={{ mb: 4 }}>
        {submitting ? (
          <Card>
            <CardContent sx={{ textAlign: "center", py: 6 }}>
              <CircularProgress size={60} />
              <Typography variant="h6" sx={{ mt: 3 }}>
                Processing Your Results...
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Our AI is analyzing your performance and preparing personalized
                feedback
              </Typography>
            </CardContent>
          </Card>
        ) : (
          renderActivity()
        )}
      </Box>

      {/* Learning Tips */}
      {!submitting && (
        <Alert severity="info" icon={<TrendingUp />}>
          <Typography variant="body2">
            <strong>Pro Tip:</strong> Take your time and focus on understanding
            rather than speed. You&apos;ll receive personalized AI feedback
            after completing this lesson!
          </Typography>
        </Alert>
      )}
    </Container>
  );
};

export default LessonView;
