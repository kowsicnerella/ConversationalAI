import { useState } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  IconButton,
  Chip,
  LinearProgress,
  Paper,
  Container,
  useTheme,
  useMediaQuery,
  Stack,
} from "@mui/material";
import {
  Flip,
  VolumeUp,
  CheckCircle,
  Cancel,
  Refresh,
  NavigateNext,
  NavigateBefore,
  Bookmark,
  BookmarkBorder,
  SwipeLeft,
  SwipeRight,
} from "@mui/icons-material";
import {
  motion,
  useMotionValue,
  useTransform,
  AnimatePresence,
} from "framer-motion";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";
import { vocabularyAPI } from "../../services/api";

const FlashcardActivity = ({ flashcards, onComplete, onProgress }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down("sm"));
  const isTablet = useMediaQuery(theme.breakpoints.down("md"));

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [knownCards, setKnownCards] = useState(new Set());
  const [unknownCards, setUnknownCards] = useState(new Set());
  const [bookmarkedCards, setBookmarkedCards] = useState(new Set());
  const [showResults, setShowResults] = useState(false);

  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-25, 25]);
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0]);

  const currentCard = flashcards[currentIndex];
  const progress = ((currentIndex + 1) / flashcards.length) * 100;

  const handleDragEnd = (event, info) => {
    const threshold = isMobile ? 80 : 120;

    if (info.offset.x > threshold) {
      handleMarkAsKnown();
    } else if (info.offset.x < -threshold) {
      handleMarkAsUnknown();
    } else {
      x.set(0);
    }
  };

  const handleMarkAsKnown = async () => {
    const newKnownCards = new Set(knownCards);
    newKnownCards.add(currentCard.id);
    setKnownCards(newKnownCards);

    if (currentCard.vocabularyId) {
      try {
        await vocabularyAPI.logPracticeResult(currentCard.vocabularyId, {
          is_correct: true,
          practice_type: "flashcard",
        });
      } catch (error) {
        console.error("Failed to log practice result:", error);
      }
    }

    toast.success("✓ Marked as known!");
    goToNextCard();
  };

  const handleMarkAsUnknown = async () => {
    const newUnknownCards = new Set(unknownCards);
    newUnknownCards.add(currentCard.id);
    setUnknownCards(newUnknownCards);

    if (currentCard.vocabularyId) {
      try {
        await vocabularyAPI.logPracticeResult(currentCard.vocabularyId, {
          is_correct: false,
          practice_type: "flashcard",
        });
      } catch (error) {
        console.error("Failed to log practice result:", error);
      }
    }

    toast.error("📚 Marked for review");
    goToNextCard();
  };

  const goToNextCard = () => {
    x.set(0);
    setIsFlipped(false);

    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      onProgress?.({
        current: currentIndex + 2,
        total: flashcards.length,
        known: knownCards.size,
        unknown: unknownCards.size,
      });
    } else {
      setShowResults(true);
      onComplete({
        totalCards: flashcards.length,
        knownCards: knownCards.size,
        unknownCards: unknownCards.size,
        bookmarkedCards: bookmarkedCards.size,
        accuracy: Math.round((knownCards.size / flashcards.length) * 100),
      });
    }
  };

  const goToPreviousCard = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setIsFlipped(false);
      x.set(0);
    }
  };

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleBookmark = () => {
    const newBookmarkedCards = new Set(bookmarkedCards);
    if (bookmarkedCards.has(currentCard.id)) {
      newBookmarkedCards.delete(currentCard.id);
      toast.success("Removed from bookmarks");
    } else {
      newBookmarkedCards.add(currentCard.id);
      toast.success("Added to bookmarks");
    }
    setBookmarkedCards(newBookmarkedCards);
  };

  const playAudio = (text, language = "en") => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = language === "telugu" ? "te-IN" : "en-US";
      utterance.rate = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const resetActivity = () => {
    setCurrentIndex(0);
    setIsFlipped(false);
    setKnownCards(new Set());
    setUnknownCards(new Set());
    setShowResults(false);
    x.set(0);
  };

  // Results Screen
  if (showResults) {
    const accuracy = Math.round((knownCards.size / flashcards.length) * 100);
    const isPerfect = accuracy === 100;
    const isGood = accuracy >= 80;

    return (
      <Container maxWidth="sm" sx={{ py: { xs: 2, sm: 4 } }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card
            className="hover-lift"
            sx={{
              borderRadius: { xs: 3, sm: 4 },
              background: isPerfect
                ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                : isGood
                ? "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
                : "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
              color: "white",
              overflow: "hidden",
              boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
            }}
          >
            <CardContent sx={{ p: { xs: 3, sm: 5 }, textAlign: "center" }}>
              {/* Confetti Animation */}
              {isPerfect && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: [0, 1.2, 1] }}
                  transition={{ duration: 0.6 }}
                >
                  <Typography variant="h2" sx={{ mb: 2 }}>
                    🎉
                  </Typography>
                </motion.div>
              )}

              <Typography
                variant={isMobile ? "h4" : "h3"}
                sx={{ fontWeight: 800, mb: 2 }}
              >
                {isPerfect
                  ? "Perfect Score!"
                  : isGood
                  ? "Great Job!"
                  : "Well Done!"}
              </Typography>

              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
              >
                <Typography
                  variant={isMobile ? "h1" : "h1"}
                  sx={{
                    fontWeight: 900,
                    mb: 1,
                    fontSize: { xs: "3rem", sm: "4rem", md: "5rem" },
                  }}
                >
                  {accuracy}%
                </Typography>
              </motion.div>

              <Typography
                variant={isMobile ? "h6" : "h5"}
                sx={{ mb: 4, opacity: 0.95, fontWeight: 500 }}
              >
                Accuracy Score
              </Typography>

              {/* Stats Grid */}
              <Stack
                direction={{ xs: "column", sm: "row" }}
                spacing={{ xs: 2, sm: 3 }}
                justifyContent="center"
                sx={{ mb: 4 }}
              >
                <Box
                  className="hover-scale"
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    background: "rgba(255,255,255,0.15)",
                    backdropFilter: "blur(10px)",
                  }}
                >
                  <Typography
                    variant="h4"
                    sx={{ fontWeight: 700, color: "#4caf50" }}
                  >
                    {knownCards.size}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Known
                  </Typography>
                </Box>

                <Box
                  className="hover-scale"
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    background: "rgba(255,255,255,0.15)",
                    backdropFilter: "blur(10px)",
                  }}
                >
                  <Typography
                    variant="h4"
                    sx={{ fontWeight: 700, color: "#ff5252" }}
                  >
                    {unknownCards.size}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Review Needed
                  </Typography>
                </Box>

                <Box
                  className="hover-scale"
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    background: "rgba(255,255,255,0.15)",
                    backdropFilter: "blur(10px)",
                  }}
                >
                  <Typography
                    variant="h4"
                    sx={{ fontWeight: 700, color: "#ffa726" }}
                  >
                    {bookmarkedCards.size}
                  </Typography>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>
                    Bookmarked
                  </Typography>
                </Box>
              </Stack>

              <Button
                variant="contained"
                size="large"
                startIcon={<Refresh />}
                onClick={resetActivity}
                fullWidth={isMobile}
                sx={{
                  bgcolor: "rgba(255,255,255,0.25)",
                  color: "white",
                  fontWeight: 600,
                  py: 1.5,
                  px: 4,
                  borderRadius: 3,
                  "&:hover": {
                    bgcolor: "rgba(255,255,255,0.35)",
                    transform: "translateY(-2px)",
                  },
                  transition: "all 0.3s ease",
                }}
              >
                Study Again
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </Container>
    );
  }

  // Main Flashcard UI
  return (
    <Container
      maxWidth="md"
      sx={{
        py: { xs: 2, sm: 3, md: 4 },
        px: { xs: 2, sm: 3 },
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Progress Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Paper
          elevation={0}
          className="glass-card"
          sx={{
            p: { xs: 2, sm: 3 },
            mb: { xs: 2, sm: 3 },
            borderRadius: { xs: 2, sm: 3 },
            background:
              theme.palette.mode === "dark"
                ? "rgba(30, 41, 59, 0.6)"
                : "rgba(255, 255, 255, 0.8)",
            backdropFilter: "blur(20px)",
          }}
        >
          <Stack
            direction={{ xs: "column", sm: "row" }}
            justifyContent="space-between"
            alignItems={{ xs: "flex-start", sm: "center" }}
            spacing={2}
            sx={{ mb: 2 }}
          >
            <Typography
              variant={isMobile ? "h6" : "h5"}
              sx={{ fontWeight: 700 }}
            >
              Flashcards Study
            </Typography>
            <Chip
              label={`${currentIndex + 1} / ${flashcards.length}`}
              color="primary"
              sx={{
                fontWeight: 700,
                fontSize: { xs: "0.875rem", sm: "1rem" },
                px: 2,
              }}
            />
          </Stack>

          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: { xs: 6, sm: 8 },
              borderRadius: 4,
              mb: 2,
              bgcolor:
                theme.palette.mode === "dark"
                  ? "rgba(255,255,255,0.1)"
                  : "rgba(0,0,0,0.05)",
            }}
          />

          <Stack
            direction="row"
            justifyContent="space-between"
            flexWrap="wrap"
            gap={1}
          >
            <Chip
              size="small"
              label={`Known: ${knownCards.size}`}
              color="success"
              variant="outlined"
            />
            <Chip
              size="small"
              label={`Review: ${unknownCards.size}`}
              color="error"
              variant="outlined"
            />
            <Chip
              size="small"
              label={`Bookmarks: ${bookmarkedCards.size}`}
              color="warning"
              variant="outlined"
            />
          </Stack>
        </Paper>
      </motion.div>

      {/* Flashcard Container */}
      <Box
        sx={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          position: "relative",
          minHeight: { xs: 400, sm: 450, md: 500 },
          mb: { xs: 2, sm: 3 },
        }}
      >
        <AnimatePresence mode="wait">
          <motion.div
            key={currentIndex}
            drag="x"
            dragConstraints={{ left: 0, right: 0 }}
            style={{
              x,
              rotate,
              opacity,
              width: "100%",
              maxWidth: isTablet ? "100%" : 500,
              cursor: "grab",
            }}
            onDragEnd={handleDragEnd}
            whileTap={{ scale: 0.98, cursor: "grabbing" }}
            animate={{ scale: 1 }}
            initial={{ scale: 0.9, opacity: 0 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card
              className="hover-lift"
              sx={{
                aspectRatio: isMobile ? "3/4" : "4/3",
                borderRadius: { xs: 3, sm: 4 },
                overflow: "hidden",
                position: "relative",
                boxShadow: "0 25px 50px rgba(0,0,0,0.15)",
                background: theme.palette.background.paper,
              }}
            >
              <motion.div
                animate={{ rotateY: isFlipped ? 180 : 0 }}
                transition={{
                  duration: 0.6,
                  type: "spring",
                  stiffness: 120,
                  damping: 15,
                }}
                style={{
                  width: "100%",
                  height: "100%",
                  position: "relative",
                  transformStyle: "preserve-3d",
                }}
              >
                {/* Front of Card */}
                <CardContent
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    alignItems: "center",
                    textAlign: "center",
                    backfaceVisibility: "hidden",
                    p: { xs: 3, sm: 4 },
                    background:
                      "linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)",
                    position: "absolute",
                    width: "100%",
                  }}
                >
                  <Typography
                    variant={isMobile ? "h4" : "h3"}
                    sx={{
                      fontWeight: 800,
                      mb: 3,
                      color: "#1976d2",
                      wordBreak: "break-word",
                    }}
                  >
                    {currentCard.front}
                  </Typography>

                  {currentCard.frontImage && (
                    <Box
                      sx={{
                        mb: 3,
                        width: "100%",
                        maxHeight: { xs: 120, sm: 180 },
                        display: "flex",
                        justifyContent: "center",
                      }}
                    >
                      <img
                        src={currentCard.frontImage}
                        alt="Front"
                        style={{
                          maxWidth: "100%",
                          maxHeight: "100%",
                          borderRadius: 12,
                          objectFit: "contain",
                        }}
                      />
                    </Box>
                  )}

                  <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        playAudio(currentCard.front, currentCard.frontLanguage);
                      }}
                      color="primary"
                      className="hover-scale"
                      sx={{
                        bgcolor: "rgba(25, 118, 210, 0.1)",
                        "&:hover": { bgcolor: "rgba(25, 118, 210, 0.2)" },
                      }}
                    >
                      <VolumeUp />
                    </IconButton>
                    <IconButton
                      onClick={(e) => {
                        e.stopPropagation();
                        handleBookmark();
                      }}
                      color={
                        bookmarkedCards.has(currentCard.id)
                          ? "warning"
                          : "default"
                      }
                      className="hover-scale"
                      sx={{
                        bgcolor: bookmarkedCards.has(currentCard.id)
                          ? "rgba(255, 167, 38, 0.1)"
                          : "rgba(0,0,0,0.05)",
                      }}
                    >
                      {bookmarkedCards.has(currentCard.id) ? (
                        <Bookmark />
                      ) : (
                        <BookmarkBorder />
                      )}
                    </IconButton>
                  </Stack>

                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{
                      mt: "auto",
                      fontSize: { xs: "0.75rem", sm: "0.875rem" },
                    }}
                  >
                    {isMobile ? "Tap to flip" : "Click to flip or drag to mark"}
                  </Typography>
                </CardContent>

                {/* Back of Card */}
                <CardContent
                  sx={{
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    alignItems: "center",
                    textAlign: "center",
                    backfaceVisibility: "hidden",
                    transform: "rotateY(180deg)",
                    p: { xs: 3, sm: 4 },
                    background:
                      "linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)",
                    position: "absolute",
                    width: "100%",
                  }}
                >
                  <Typography
                    variant={isMobile ? "h4" : "h3"}
                    sx={{
                      fontWeight: 800,
                      mb: 3,
                      color: "#7b1fa2",
                      wordBreak: "break-word",
                    }}
                  >
                    {currentCard.back}
                  </Typography>

                  {currentCard.backImage && (
                    <Box
                      sx={{
                        mb: 3,
                        width: "100%",
                        maxHeight: { xs: 120, sm: 180 },
                        display: "flex",
                        justifyContent: "center",
                      }}
                    >
                      <img
                        src={currentCard.backImage}
                        alt="Back"
                        style={{
                          maxWidth: "100%",
                          maxHeight: "100%",
                          borderRadius: 12,
                          objectFit: "contain",
                        }}
                      />
                    </Box>
                  )}

                  {currentCard.example && (
                    <Typography
                      variant="body1"
                      sx={{
                        mb: 3,
                        fontStyle: "italic",
                        opacity: 0.85,
                        px: 2,
                        fontSize: { xs: "0.875rem", sm: "1rem" },
                      }}
                    >
                      &quot;{currentCard.example}&quot;
                    </Typography>
                  )}

                  <IconButton
                    onClick={(e) => {
                      e.stopPropagation();
                      playAudio(currentCard.back, currentCard.backLanguage);
                    }}
                    color="primary"
                    className="hover-scale"
                    sx={{
                      bgcolor: "rgba(123, 31, 162, 0.1)",
                      "&:hover": { bgcolor: "rgba(123, 31, 162, 0.2)" },
                    }}
                  >
                    <VolumeUp />
                  </IconButton>
                </CardContent>
              </motion.div>

              {/* Flip Button */}
              <IconButton
                onClick={handleFlip}
                className="hover-scale"
                sx={{
                  position: "absolute",
                  top: { xs: 12, sm: 16 },
                  right: { xs: 12, sm: 16 },
                  zIndex: 10,
                  bgcolor: theme.palette.primary.main,
                  color: "white",
                  width: { xs: 40, sm: 48 },
                  height: { xs: 40, sm: 48 },
                  "&:hover": {
                    bgcolor: theme.palette.primary.dark,
                    transform: "rotate(180deg) scale(1.1)",
                  },
                  transition: "all 0.3s ease",
                }}
              >
                <Flip />
              </IconButton>
            </Card>
          </motion.div>
        </AnimatePresence>

        {/* Swipe Indicators - Desktop Only */}
        {!isMobile && (
          <>
            <Box
              sx={{
                position: "absolute",
                left: { md: -80, lg: -100 },
                top: "50%",
                transform: "translateY(-50%)",
                opacity: 0.4,
                pointerEvents: "none",
              }}
            >
              <motion.div
                animate={{ x: [-10, 0, -10] }}
                transition={{ repeat: Infinity, duration: 2 }}
              >
                <Stack alignItems="center" spacing={1}>
                  <SwipeLeft fontSize="large" color="error" />
                  <Chip
                    icon={<Cancel />}
                    label="Unknown"
                    color="error"
                    size="small"
                  />
                </Stack>
              </motion.div>
            </Box>

            <Box
              sx={{
                position: "absolute",
                right: { md: -80, lg: -100 },
                top: "50%",
                transform: "translateY(-50%)",
                opacity: 0.4,
                pointerEvents: "none",
              }}
            >
              <motion.div
                animate={{ x: [10, 0, 10] }}
                transition={{ repeat: Infinity, duration: 2 }}
              >
                <Stack alignItems="center" spacing={1}>
                  <SwipeRight fontSize="large" color="success" />
                  <Chip
                    icon={<CheckCircle />}
                    label="Known"
                    color="success"
                    size="small"
                  />
                </Stack>
              </motion.div>
            </Box>
          </>
        )}
      </Box>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Stack spacing={2}>
          {/* Mark Buttons */}
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Cancel />}
              onClick={handleMarkAsUnknown}
              fullWidth
              size={isMobile ? "medium" : "large"}
              className="hover-lift"
              sx={{
                borderRadius: 3,
                py: { xs: 1.5, sm: 2 },
                borderWidth: 2,
                fontWeight: 600,
                "&:hover": {
                  borderWidth: 2,
                },
              }}
            >
              Need Review
            </Button>
            <Button
              variant="contained"
              color="success"
              startIcon={<CheckCircle />}
              onClick={handleMarkAsKnown}
              fullWidth
              size={isMobile ? "medium" : "large"}
              className="hover-lift"
              sx={{
                borderRadius: 3,
                py: { xs: 1.5, sm: 2 },
                fontWeight: 600,
                boxShadow: "0 4px 12px rgba(76, 175, 80, 0.3)",
              }}
            >
              I Know This
            </Button>
          </Stack>

          {/* Navigation */}
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
          >
            <IconButton
              onClick={goToPreviousCard}
              disabled={currentIndex === 0}
              size={isMobile ? "medium" : "large"}
              className="hover-scale"
              sx={{
                bgcolor:
                  currentIndex === 0
                    ? "transparent"
                    : theme.palette.action.hover,
                "&:hover": {
                  bgcolor: theme.palette.action.selected,
                },
              }}
            >
              <NavigateBefore />
            </IconButton>

            {!isMobile && (
              <Typography
                variant="body2"
                color="text.secondary"
                align="center"
                sx={{ fontSize: { xs: "0.75rem", sm: "0.875rem" } }}
              >
                Swipe or use buttons to mark cards
              </Typography>
            )}

            <IconButton
              onClick={goToNextCard}
              disabled={currentIndex === flashcards.length - 1}
              size={isMobile ? "medium" : "large"}
              className="hover-scale"
              sx={{
                bgcolor:
                  currentIndex === flashcards.length - 1
                    ? "transparent"
                    : theme.palette.action.hover,
                "&:hover": {
                  bgcolor: theme.palette.action.selected,
                },
              }}
            >
              <NavigateNext />
            </IconButton>
          </Stack>
        </Stack>
      </motion.div>
    </Container>
  );
};

FlashcardActivity.propTypes = {
  flashcards: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      front: PropTypes.string.isRequired,
      back: PropTypes.string.isRequired,
      frontImage: PropTypes.string,
      backImage: PropTypes.string,
      example: PropTypes.string,
      frontLanguage: PropTypes.string,
      backLanguage: PropTypes.string,
      vocabularyId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    })
  ).isRequired,
  onComplete: PropTypes.func.isRequired,
  onProgress: PropTypes.func,
};

export default FlashcardActivity;
