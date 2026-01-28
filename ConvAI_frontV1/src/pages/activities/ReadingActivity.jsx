import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  Chip,
  Divider,
  LinearProgress,
  Stack,
} from "@mui/material";
import {
  AccessTime,
  MenuBook,
  CheckCircle,
  Cancel,
  EmojiEvents,
  Home,
  NavigateNext,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import PageTransition from "../../components/common/PageTransition";
import GradientText from "../../components/common/GradientText";
import AnimatedButton from "../../components/common/AnimatedButton";
import axiosInstance, { API_ENDPOINTS } from "../../config/api";
import gamificationService from "../../services/gamificationService";
import AIGeneratingLoader from "../../components/common/AIGeneratingLoader";
import AIGeneratedBadge from "../../components/common/AIGeneratedBadge";

const ReadingActivity = () => {
  const { activityId } = useParams();
  const navigate = useNavigate();
  const [reading, setReading] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(null);
  const [nextActivityId, setNextActivityId] = useState(null);
  const [learningPathId, setLearningPathId] = useState(null);

  useEffect(() => {
    fetchReading();
  }, [activityId]);

  const fetchReading = async () => {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.ACTIVITIES.GENERATE.replace(":type", "reading"),
        {
          params: { activityId },
        }
      );
      setReading(response.data);
    } catch (error) {
      console.error("Error fetching reading:", error);
      // Mock data
      setReading({
        id: activityId,
        title: "The Power of Communication",
        level: "Intermediate",
        estimatedTime: 15,
        passage: `Communication is one of the most essential skills in human interaction. It allows us to express our thoughts, share our feelings, and connect with others on a deeper level. Effective communication involves not just speaking, but also active listening and understanding non-verbal cues.

In today's globalized world, the ability to communicate across cultures has become increasingly important. Learning a new language opens doors to new opportunities, friendships, and experiences. It helps us appreciate different perspectives and builds bridges between diverse communities.

Studies have shown that learning a second language can improve cognitive abilities, enhance memory, and even delay the onset of dementia. Language learning exercises the brain and promotes mental flexibility. Moreover, bilingual individuals often demonstrate better problem-solving skills and creative thinking.

However, language learning is not without its challenges. It requires dedication, practice, and patience. Many learners struggle with pronunciation, grammar rules, and vocabulary retention. The key to success lies in consistent practice, immersion, and maintaining a positive attitude despite setbacks.

Technology has revolutionized language learning in recent years. Mobile apps, online courses, and language exchange platforms have made learning more accessible than ever before. These tools provide interactive exercises, immediate feedback, and opportunities to practice with native speakers from around the world.`,
        questions: [
          {
            id: 1,
            question:
              "What is described as one of the most essential skills in human interaction?",
            options: [
              "Writing",
              "Communication",
              "Technology",
              "Problem-solving",
            ],
            correctAnswer: 1,
            explanation:
              'The passage clearly states that "Communication is one of the most essential skills in human interaction."',
          },
          {
            id: 2,
            question:
              "According to the passage, what does effective communication involve besides speaking?",
            options: [
              "Writing and reading",
              "Active listening and understanding non-verbal cues",
              "Using technology",
              "Learning multiple languages",
            ],
            correctAnswer: 1,
            explanation:
              'The text mentions that effective communication involves "not just speaking, but also active listening and understanding non-verbal cues."',
          },
          {
            id: 3,
            question:
              "What benefit of learning a second language is mentioned in the passage?",
            options: [
              "It guarantees a better job",
              "It makes travel easier",
              "It can improve cognitive abilities and enhance memory",
              "It is less expensive than other hobbies",
            ],
            correctAnswer: 2,
            explanation:
              'The passage states that "learning a second language can improve cognitive abilities, enhance memory, and even delay the onset of dementia."',
          },
          {
            id: 4,
            question:
              "What is identified as key to success in language learning?",
            options: [
              "Native talent",
              "Expensive courses",
              "Consistent practice, immersion, and a positive attitude",
              "Perfect grammar from the start",
            ],
            correctAnswer: 2,
            explanation:
              'The text explicitly mentions that "The key to success lies in consistent practice, immersion, and maintaining a positive attitude despite setbacks."',
          },
          {
            id: 5,
            question:
              "How has technology affected language learning according to the passage?",
            options: [
              "It has made it more difficult",
              "It has had no significant impact",
              "It has made learning more accessible",
              "It has replaced traditional methods entirely",
            ],
            correctAnswer: 2,
            explanation:
              'The passage states that technology "has made learning more accessible than ever before" through various digital tools and platforms.',
          },
        ],
      });
    }
  };

  // Fetch learning path and next activity
  useEffect(() => {
    const fetchNextActivity = async () => {
      try {
        // Try to get learning path ID from localStorage (set when navigating from LearningPathDetail)
        const pathIdFromStorage = localStorage.getItem("currentLearningPathId");
        if (pathIdFromStorage) {
          setLearningPathId(pathIdFromStorage);
          const pathResponse = await axiosInstance.get(
            API_ENDPOINTS.COURSES.PATH_DETAIL(pathIdFromStorage)
          );
          const activities = pathResponse.data.learning_path.activities;
          const currentIndex = activities.findIndex(
            (a) => a.id === parseInt(activityId)
          );
          
          if (currentIndex !== -1 && currentIndex < activities.length - 1) {
            setNextActivityId(activities[currentIndex + 1]);
          }
        }
      } catch (error) {
        console.error("Error fetching next activity:", error);
      }
    };

    if (submitted) {
      fetchNextActivity();
    }
  }, [submitted, activityId]);

  const handleAnswerChange = (questionId, answerIndex) => {
    if (!submitted) {
      setAnswers({ ...answers, [questionId]: answerIndex });
    }
  };

  const handleSubmit = async () => {
    let correct = 0;
    reading.questions.forEach((question) => {
      if (answers[question.id] === question.correctAnswer) {
        correct++;
      }
    });
    const percentage = Math.round((correct / reading.questions.length) * 100);
    
    // Save results to backend
    try {
      // Get activity data from sessionStorage to extract learning_node_id
      const activityData = JSON.parse(sessionStorage.getItem('currentActivity') || '{}');
      
      // Use multiple fallbacks to find learning_node_id
      let learningNodeId = activityData.nodeId;
      
      // If nodeId is not available, try to construct one from available data
      if (!learningNodeId) {
        // Try to use _node_info if available
        const nodeInfo = activityData._node_info;
        if (nodeInfo) {
          learningNodeId = nodeInfo.id 
            || nodeInfo.node_id 
            || `node_${activityData.nodeName?.replace(/\s+/g, '_').toLowerCase() || 'unknown'}`;
        }
      }
      
      // Final fallback: use activity ID as a reference
      if (!learningNodeId) {
        learningNodeId = `node_from_activity_${activityId}`;
        console.warn("⚠️ Using fallback learning_node_id:", learningNodeId);
      }
      
      console.log("Saving reading activity results:", {
        activityId,
        learningNodeId,
        score: percentage,
        correct,
        total: reading.questions.length
      });
      
      await axiosInstance.post(
        API_ENDPOINTS.LEARNING_PATH.COMPLETE_ACTIVITY,
        {
          learning_node_id: learningNodeId,
          activity_id: activityId,
          score: percentage,
          time_spent: 0, // You can track actual time if needed
          activity_type: "reading",
          activity_results: {
            correctAnswers: correct,
            totalQuestions: reading.questions.length,
          },
        }
      );
      
      console.log("✅ Reading activity results saved successfully");
    } catch (error) {
      console.error("❌ Error saving reading activity results:", error);
      // Continue to show results even if API call fails
    }

    // Update streak after completing activity
    try {
      await gamificationService.updateStreak();
      console.log("✅ Streak updated successfully");
    } catch (error) {
      console.error("Failed to update streak:", error);
    }
    
    setScore({ correct, total: reading.questions.length, percentage });
    setSubmitted(true);
  };

  if (!reading) {
    return (
      <AIGeneratingLoader 
        message="AI is preparing your reading passage..."
        subMessage="Creating a personalized reading exercise for you"
      />
    );
  }

  const allQuestionsAnswered = reading.questions.every(
    (q) => answers[q.id] !== undefined
  );

  return (
    <PageTransition>
      <Box sx={{ maxWidth: 1000, margin: "0 auto" }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Stack direction="row" alignItems="center" spacing={2}>
            <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
              {reading.title}
            </GradientText>
            <AIGeneratedBadge size="medium" />
          </Stack>
          <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
            <Chip icon={<MenuBook />} label={reading.level} color="primary" />
            <Chip
              icon={<AccessTime />}
              label={`${reading.estimatedTime} min read`}
            />
          </Box>
        </Box>

        {/* Reading Passage */}
        <Card sx={{ mb: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Reading Passage
            </Typography>
            <Divider sx={{ mb: 3 }} />
            <Typography
              variant="body1"
              sx={{
                lineHeight: 2,
                textAlign: "justify",
                fontSize: "1.1rem",
                whiteSpace: "pre-line",
              }}
            >
              {reading.passage}
            </Typography>
          </CardContent>
        </Card>

        {/* Questions */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Comprehension Questions
          </Typography>
          {reading.questions.map((question, index) => (
            <motion.div
              key={question.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom fontWeight={600}>
                    {index + 1}. {question.question}
                  </Typography>

                  <RadioGroup
                    value={answers[question.id] ?? ""}
                    onChange={(e) =>
                      handleAnswerChange(question.id, Number(e.target.value))
                    }
                  >
                    {question.options.map((option, optionIndex) => (
                      <Card
                        key={optionIndex}
                        sx={{
                          mb: 1,
                          cursor: submitted ? "default" : "pointer",
                          border: 2,
                          borderColor:
                            submitted && optionIndex === question.correctAnswer
                              ? "success.main"
                              : submitted &&
                                optionIndex === answers[question.id] &&
                                optionIndex !== question.correctAnswer
                              ? "error.main"
                              : answers[question.id] === optionIndex
                              ? "primary.main"
                              : "transparent",
                          bgcolor:
                            submitted && optionIndex === question.correctAnswer
                              ? "success.light"
                              : submitted &&
                                optionIndex === answers[question.id] &&
                                optionIndex !== question.correctAnswer
                              ? "error.light"
                              : "background.paper",
                        }}
                        onClick={() =>
                          handleAnswerChange(question.id, optionIndex)
                        }
                      >
                        <CardContent
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            py: 1.5,
                          }}
                        >
                          <FormControlLabel
                            value={optionIndex}
                            control={<Radio disabled={submitted} />}
                            label={option}
                            sx={{ flex: 1, m: 0 }}
                          />
                          {submitted &&
                            optionIndex === question.correctAnswer && (
                              <CheckCircle color="success" />
                            )}
                          {submitted &&
                            optionIndex === answers[question.id] &&
                            optionIndex !== question.correctAnswer && (
                              <Cancel color="error" />
                            )}
                        </CardContent>
                      </Card>
                    ))}
                  </RadioGroup>

                  {submitted && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      transition={{ duration: 0.3 }}
                    >
                      <Box
                        sx={{
                          mt: 2,
                          p: 2,
                          bgcolor:
                            answers[question.id] === question.correctAnswer
                              ? "success.light"
                              : "error.light",
                          borderRadius: 2,
                        }}
                      >
                        <Typography
                          variant="body2"
                          fontWeight={600}
                          gutterBottom
                        >
                          {answers[question.id] === question.correctAnswer
                            ? "✓ Correct!"
                            : "✗ Incorrect"}
                        </Typography>
                        <Typography variant="body2">
                          {question.explanation}
                        </Typography>
                      </Box>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </Box>

        {/* Submit/Results Section */}
        {!submitted ? (
          <Card sx={{ position: "sticky", bottom: 16 }}>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <Typography variant="body1">
                  {Object.keys(answers).length} / {reading.questions.length}{" "}
                  questions answered
                </Typography>
                <AnimatedButton
                  variant="contained"
                  size="large"
                  onClick={handleSubmit}
                  disabled={!allQuestionsAnswered}
                >
                  Submit Answers
                </AnimatedButton>
              </Box>
              <LinearProgress
                variant="determinate"
                value={
                  (Object.keys(answers).length / reading.questions.length) * 100
                }
                sx={{ mt: 2, height: 6, borderRadius: 3 }}
              />
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent sx={{ textAlign: "center", p: 4 }}>
              <EmojiEvents
                sx={{ fontSize: 60, color: "primary.main", mb: 2 }}
              />
              <GradientText variant="h4" fontWeight={700} gutterBottom>
                Activity Complete!
              </GradientText>
              <Typography
                variant="h2"
                color="primary.main"
                fontWeight={700}
                gutterBottom
              >
                {score.percentage}%
              </Typography>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                You got {score.correct} out of {score.total} questions correct
              </Typography>

              <Box
                sx={{
                  display: "flex",
                  gap: 2,
                  justifyContent: "center",
                  mt: 3,
                  flexWrap: "wrap",
                }}
              >
                {nextActivityId && (
                  <AnimatedButton
                    variant="contained"
                    color="success"
                    startIcon={<NavigateNext />}
                    onClick={() => {
                      // Navigate based on activity type
                      const actType = nextActivityId.type || "reading";
                      const typeStr = String(actType).toLowerCase();
                      if (typeStr === "flashcard" || typeStr === "flashcards") {
                        navigate(`/activities/flashcards/${nextActivityId.id}`);
                      } else if (typeStr === "quiz") {
                        navigate(`/activities/quiz/${nextActivityId.id}`);
                      } else if (typeStr === "reading") {
                        navigate(`/activities/reading/${nextActivityId.id}`);
                      } else {
                        navigate(`/activities/${nextActivityId.id}`);
                      }
                    }}
                  >
                    Next Activity
                  </AnimatedButton>
                )}
                <AnimatedButton
                  variant="contained"
                  startIcon={<Home />}
                  onClick={() => navigate("/dashboard")}
                >
                  Back to Dashboard
                </AnimatedButton>
                <AnimatedButton
                  variant="outlined"
                  onClick={() => window.location.reload()}
                >
                  Try Again
                </AnimatedButton>
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>
    </PageTransition>
  );
};

export default ReadingActivity;
