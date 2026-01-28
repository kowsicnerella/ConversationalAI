import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  LinearProgress,
  Chip,
  ButtonGroup,
  Stack,
} from "@mui/material";
import {
  NavigateBefore,
  NavigateNext,
  Shuffle,
  VolumeUp,
  Star,
  StarBorder,
  CheckCircle,
  Close,
  EmojiEvents,
  Home,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import PageTransition from "../../components/common/PageTransition";
import GradientText from "../../components/common/GradientText";
import AnimatedButton from "../../components/common/AnimatedButton";
import axiosInstance, { API_ENDPOINTS } from "../../config/api";
import gamificationService from "../../services/gamificationService";
import AIGeneratingLoader from "../../components/common/AIGeneratingLoader";
import AIGeneratedBadge from "../../components/common/AIGeneratedBadge";

const FlashcardsActivity = () => {
  const { activityId } = useParams();
  const navigate = useNavigate();
  const [flashcards, setFlashcards] = useState([]);
  const [currentCard, setCurrentCard] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [knownCards, setKnownCards] = useState([]);
  const [studyComplete, setStudyComplete] = useState(false);
  const [nextActivityId, setNextActivityId] = useState(null);
  const [learningPathId, setLearningPathId] = useState(null);

  useEffect(() => {
    fetchFlashcards();
  }, [activityId]);

  const fetchFlashcards = async () => {
    try {
      const response = await axiosInstance.get(
        API_ENDPOINTS.ACTIVITIES.GENERATE.replace(":type", "flashcard"),
        {
          params: { activityId },
        }
      );
      setFlashcards(response.data.flashcards || []);
    } catch (error) {
      console.error("Error fetching flashcards:", error);
      // Mock data
      setFlashcards([
        {
          id: 1,
          word: "Hello",
          pronunciation: "హలో (halō)",
          translation: "నమస్కారం (namaskāraṁ)",
          definition: "A greeting used when meeting someone",
          example: "Hello! How are you today?",
          audioUrl: null,
        },
        {
          id: 2,
          word: "Thank you",
          pronunciation: "థ్యాంక్ యూ (thyānk yū)",
          translation: "ధన్యవాదాలు (dhanyavādālu)",
          definition: "An expression of gratitude",
          example: "Thank you for your help!",
          audioUrl: null,
        },
        {
          id: 3,
          word: "Beautiful",
          pronunciation: "బ్యూటిఫుల్ (byūṭiphul)",
          translation: "అందమైన (andamaina)",
          definition: "Pleasing to the senses or mind aesthetically",
          example: "The sunset is beautiful tonight.",
          audioUrl: null,
        },
        {
          id: 4,
          word: "Friend",
          pronunciation: "ఫ్రెండ్ (phreṇḍ)",
          translation: "స్నేహితుడు (snēhituḍu)",
          definition: "A person whom one knows and with whom one has a bond",
          example: "She is my best friend.",
          audioUrl: null,
        },
        {
          id: 5,
          word: "Learn",
          pronunciation: "లర్న్ (larn)",
          translation: "నేర్చుకొను (nērcukonu)",
          definition: "To acquire knowledge or skill by study",
          example: "I want to learn English.",
          audioUrl: null,
        },
      ]);
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

    if (studyComplete) {
      fetchNextActivity();
    }
  }, [studyComplete, activityId]);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleNext = () => {
    if (currentCard < flashcards.length - 1) {
      setCurrentCard(currentCard + 1);
      setIsFlipped(false);
    }
  };

  const handlePrevious = () => {
    if (currentCard > 0) {
      setCurrentCard(currentCard - 1);
      setIsFlipped(false);
    }
  };

  const handleShuffle = () => {
    const shuffled = [...flashcards].sort(() => Math.random() - 0.5);
    setFlashcards(shuffled);
    setCurrentCard(0);
    setIsFlipped(false);
  };

  const handleMarkKnown = async (known) => {
    const cardId = flashcards[currentCard].id;
    if (known) {
      setKnownCards([...knownCards, cardId]);
    } else {
      setKnownCards(knownCards.filter((id) => id !== cardId));
    }

    // Move to next card or complete study
    if (currentCard < flashcards.length - 1) {
      handleNext();
    } else {
      // Calculate final results
      const finalKnownCards = known 
        ? [...knownCards, cardId]
        : knownCards.filter((id) => id !== cardId);
      
      const totalCount = flashcards.length;
      const knownCount = finalKnownCards.length;
      const percentage = Math.round((knownCount / totalCount) * 100);
      
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
        
        console.log("Saving flashcard activity results:", {
          activityId,
          learningNodeId,
          score: percentage,
          knownCount,
          totalCount
        });
        
        await axiosInstance.post(
          API_ENDPOINTS.LEARNING_PATH.COMPLETE_ACTIVITY,
          {
            learning_node_id: learningNodeId,
            activity_id: activityId,
            score: percentage,
            time_spent: 0, // You can track actual time if needed
            activity_type: "flashcards",
            activity_results: {
              cardsStudied: totalCount,
              cardsKnown: knownCount,
            },
          }
        );
        
        console.log("✅ Activity results saved successfully");
      } catch (error) {
        console.error("❌ Error saving activity results:", error);
        // Continue to show completion screen even if API call fails
      }

      // Update streak after completing activity
      try {
        await gamificationService.updateStreak();
        console.log("✅ Streak updated successfully");
      } catch (error) {
        console.error("Failed to update streak:", error);
      }
      
      setStudyComplete(true);
    }
  };

  const handleSpeak = (text) => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-US";
      window.speechSynthesis.speak(utterance);
    }
  };

  const toggleBookmark = () => {
    // Placeholder for bookmark functionality
    console.log("Bookmark toggled");
  };

  if (flashcards.length === 0) {
    return (
      <AIGeneratingLoader 
        message="AI is creating your flashcards..."
        subMessage="Preparing vocabulary cards for you"
      />
    );
  }

  if (studyComplete) {
    const knownCount = knownCards.length;
    const totalCount = flashcards.length;
    const percentage = Math.round((knownCount / totalCount) * 100);

    return (
      <PageTransition>
        <Box sx={{ maxWidth: 800, margin: "0 auto" }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, type: "spring" }}
          >
            <Card sx={{ textAlign: "center", p: 4 }}>
              <EmojiEvents
                sx={{ fontSize: 80, color: "primary.main", mb: 2 }}
              />
              <GradientText variant="h4" sx={{ mb: 2, fontWeight: 700 }}>
                Study Session Complete!
              </GradientText>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                You've reviewed all {totalCount} flashcards
              </Typography>

              <Box sx={{ mt: 4, mb: 4 }}>
                <Typography variant="h2" color="primary.main" fontWeight={700}>
                  {percentage}%
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Cards marked as known: {knownCount} / {totalCount}
                </Typography>
              </Box>

              <Box sx={{ display: "flex", gap: 2, justifyContent: "center", flexWrap: "wrap" }}>
                {nextActivityId && (
                  <AnimatedButton
                    variant="contained"
                    color="success"
                    startIcon={<NavigateNext />}
                    onClick={() => {
                      // Navigate based on activity type
                      const actType = nextActivityId.type || "flashcard";
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
                  Study Again
                </AnimatedButton>
              </Box>
            </Card>
          </motion.div>
        </Box>
      </PageTransition>
    );
  }

  const card = flashcards[currentCard];
  const progress = ((currentCard + 1) / flashcards.length) * 100;
  const isCardKnown = knownCards.includes(card.id);

  return (
    <PageTransition>
      <Box sx={{ maxWidth: 900, margin: "0 auto" }}>
        {/* Header */}
        <Box
          sx={{
            mb: 4,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <Box>
            <Stack direction="row" alignItems="center" spacing={2}>
              <GradientText variant="h4" sx={{ mb: 1, fontWeight: 700 }}>
                Flashcards Study
              </GradientText>
              <AIGeneratedBadge size="medium" />
            </Stack>
            <Typography variant="body1" color="text.secondary">
              Review and memorize vocabulary
            </Typography>
          </Box>
          <IconButton onClick={handleShuffle} color="primary">
            <Shuffle />
          </IconButton>
        </Box>

        {/* Progress */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box
              sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}
            >
              <Typography variant="body1" fontWeight={600}>
                Card {currentCard + 1} of {flashcards.length}
              </Typography>
              <Chip
                label={`${knownCards.length} known`}
                color="success"
                size="small"
                icon={<CheckCircle />}
              />
            </Box>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </CardContent>
        </Card>

        {/* Flashcard */}
        <Box sx={{ mb: 3, minHeight: 400 }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={currentCard}
              initial={{ opacity: 0, rotateY: 90 }}
              animate={{ opacity: 1, rotateY: 0 }}
              exit={{ opacity: 0, rotateY: -90 }}
              transition={{ duration: 0.3 }}
              style={{ perspective: 1000 }}
            >
              <Card
                onClick={handleFlip}
                sx={{
                  height: 400,
                  cursor: "pointer",
                  position: "relative",
                  transformStyle: "preserve-3d",
                  transition: "transform 0.6s",
                  transform: isFlipped ? "rotateY(180deg)" : "rotateY(0)",
                  "&:hover": {
                    boxShadow: 6,
                  },
                }}
              >
                {/* Front */}
                <Box
                  sx={{
                    position: "absolute",
                    width: "100%",
                    height: "100%",
                    backfaceVisibility: "hidden",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    alignItems: "center",
                    p: 4,
                  }}
                >
                  <IconButton
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleBookmark();
                    }}
                    sx={{ position: "absolute", top: 16, right: 16 }}
                  >
                    {isCardKnown ? <Star color="primary" /> : <StarBorder />}
                  </IconButton>

                  <Typography
                    variant="h2"
                    fontWeight={700}
                    gutterBottom
                    color="primary.main"
                  >
                    {card.word}
                  </Typography>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    {card.pronunciation}
                  </Typography>

                  <IconButton
                    color="primary"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSpeak(card.word);
                    }}
                    sx={{ mt: 2 }}
                  >
                    <VolumeUp sx={{ fontSize: 40 }} />
                  </IconButton>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mt: 4 }}
                  >
                    Click to flip
                  </Typography>
                </Box>

                {/* Back */}
                <Box
                  sx={{
                    position: "absolute",
                    width: "100%",
                    height: "100%",
                    backfaceVisibility: "hidden",
                    transform: "rotateY(180deg)",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    p: 4,
                  }}
                >
                  <Typography
                    variant="h4"
                    fontWeight={700}
                    gutterBottom
                    color="primary.main"
                  >
                    {card.translation}
                  </Typography>
                  <Typography
                    variant="h6"
                    color="text.secondary"
                    gutterBottom
                    sx={{ mb: 3 }}
                  >
                    Telugu Translation
                  </Typography>

                  <Box sx={{ mb: 3 }}>
                    <Typography
                      variant="subtitle2"
                      color="text.secondary"
                      gutterBottom
                    >
                      Definition:
                    </Typography>
                    <Typography variant="body1">{card.definition}</Typography>
                  </Box>

                  <Box>
                    <Typography
                      variant="subtitle2"
                      color="text.secondary"
                      gutterBottom
                    >
                      Example:
                    </Typography>
                    <Typography variant="body1" fontStyle="italic">
                      &quot;{card.example}&quot;
                    </Typography>
                  </Box>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mt: 4 }}
                  >
                    Click to flip back
                  </Typography>
                </Box>
              </Card>
            </motion.div>
          </AnimatePresence>
        </Box>

        {/* Navigation */}
        <Card>
          <CardContent>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <IconButton onClick={handlePrevious} disabled={currentCard === 0}>
                <NavigateBefore />
              </IconButton>

              <ButtonGroup variant="outlined">
                <AnimatedButton
                  startIcon={<Close />}
                  onClick={() => handleMarkKnown(false)}
                  color="error"
                >
                  Still Learning
                </AnimatedButton>
                <AnimatedButton
                  startIcon={<CheckCircle />}
                  onClick={() => handleMarkKnown(true)}
                  color="success"
                >
                  I Know This
                </AnimatedButton>
              </ButtonGroup>

              <IconButton
                onClick={handleNext}
                disabled={currentCard === flashcards.length - 1}
              >
                <NavigateNext />
              </IconButton>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </PageTransition>
  );
};

export default FlashcardsActivity;
