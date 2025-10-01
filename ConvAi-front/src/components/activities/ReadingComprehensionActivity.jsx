import { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Chip,
  LinearProgress,
  Paper,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
} from "@mui/material";
import {
  ExpandMore,
  Timer,
  Lightbulb,
  VolumeUp,
  Translate,
  CheckCircle,
  PlayArrow,
  Refresh,
  MenuBook,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";

const ReadingComprehensionActivity = ({
  comprehensionData,
  onComplete,
  onNext,
}) => {
  // Removed unused currentSection state
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [timeLeft, setTimeLeft] = useState(comprehensionData.timeLimit || 1200); // 20 minutes default
  const [highlightedWords, setHighlightedWords] = useState(new Set());
  const [showTranslation, setShowTranslation] = useState(false);
  const [readingProgress, setReadingProgress] = useState(0);
  const [showHints, setShowHints] = useState({});
  const [score, setScore] = useState(0);

  useEffect(() => {
    if (timeLeft > 0 && !showResults) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0) {
      handleComplete();
    }
  }, [timeLeft, showResults, handleComplete]);

  useEffect(() => {
    // Simulate reading progress based on scroll or time
    const progressInterval = setInterval(() => {
      if (readingProgress < 100 && !showResults) {
        setReadingProgress((prev) => Math.min(prev + 0.5, 100));
      }
    }, 1000);

    return () => clearInterval(progressInterval);
  }, [readingProgress, showResults]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleWordClick = (word, index) => {
    const wordKey = `${word}-${index}`;
    const newHighlighted = new Set(highlightedWords);

    if (highlightedWords.has(wordKey)) {
      newHighlighted.delete(wordKey);
      toast.success("Word unhighlighted");
    } else {
      newHighlighted.add(wordKey);
      toast.success("Word highlighted");
    }

    setHighlightedWords(newHighlighted);
  };

  const handleAnswerSelect = (questionIndex, answer) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: answer,
    });
  };

  const handleComplete = useCallback(() => {
    const totalQuestions = comprehensionData.questions.length;
    const correctAnswers = Object.entries(selectedAnswers).filter(
      ([questionIndex, answer]) =>
        answer === comprehensionData.questions[questionIndex].correctAnswer
    ).length;

    const finalScore = Math.round((correctAnswers / totalQuestions) * 100);
    setScore(finalScore);
    setShowResults(true);

    onComplete({
      score: finalScore,
      correctAnswers,
      totalQuestions,
      timeSpent: (comprehensionData.timeLimit || 1200) - timeLeft,
      highlightedWords: Array.from(highlightedWords),
      readingProgress,
      answers: selectedAnswers,
    });
  }, [
    comprehensionData,
    selectedAnswers,
    timeLeft,
    highlightedWords,
    readingProgress,
    onComplete,
  ]);

  const playAudio = (text) => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const toggleHint = (questionIndex) => {
    setShowHints({
      ...showHints,
      [questionIndex]: !showHints[questionIndex],
    });
  };

  const renderHighlightableText = (text) => {
    const words = text.split(/(\s+)/);
    return words.map((word, index) => {
      const wordKey = `${word.trim()}-${index}`;
      const isHighlighted = highlightedWords.has(wordKey);

      if (word.trim() === "") return word;

      return (
        <motion.span
          key={index}
          onClick={() => handleWordClick(word.trim(), index)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          style={{
            cursor: "pointer",
            backgroundColor: isHighlighted ? "#ffeb3b" : "transparent",
            padding: "2px 1px",
            borderRadius: "3px",
            transition: "background-color 0.3s ease",
          }}
        >
          {word}
        </motion.span>
      );
    });
  };

  if (showResults) {
    const totalQuestions = comprehensionData.questions.length;
    const correctAnswers = Object.entries(selectedAnswers).filter(
      ([questionIndex, answer]) =>
        answer === comprehensionData.questions[questionIndex].correctAnswer
    ).length;

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Card
          sx={{
            maxWidth: 800,
            mx: "auto",
            borderRadius: 4,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            color: "white",
            overflow: "hidden",
          }}
        >
          <CardContent sx={{ p: 4, textAlign: "center" }}>
            <MenuBook sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
              Reading Complete!
            </Typography>

            <Typography variant="h1" sx={{ fontWeight: "bold", mb: 1 }}>
              {score}%
            </Typography>

            <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
              {correctAnswers} out of {totalQuestions} correct
            </Typography>

            <Box
              sx={{ display: "flex", justifyContent: "space-around", mb: 4 }}
            >
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                  {readingProgress}%
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Reading Progress
                </Typography>
              </Box>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                  {highlightedWords.size}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Words Highlighted
                </Typography>
              </Box>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                  {formatTime((comprehensionData.timeLimit || 1200) - timeLeft)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Time Spent
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: "flex", gap: 2, justifyContent: "center" }}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={() => window.location.reload()}
                sx={{
                  bgcolor: "rgba(255,255,255,0.2)",
                  "&:hover": { bgcolor: "rgba(255,255,255,0.3)" },
                  borderRadius: 3,
                }}
              >
                Read Again
              </Button>
              {onNext && (
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={onNext}
                  sx={{
                    bgcolor: "#4caf50",
                    "&:hover": { bgcolor: "#45a049" },
                    borderRadius: 3,
                  }}
                >
                  Next Activity
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <Box sx={{ maxWidth: 1000, mx: "auto" }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card sx={{ mb: 3, borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="h5" sx={{ fontWeight: "bold" }}>
                {comprehensionData.title}
              </Typography>
              <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
                <Chip
                  icon={<Timer />}
                  label={formatTime(timeLeft)}
                  color={timeLeft < 300 ? "error" : "primary"}
                  sx={{ fontWeight: "bold" }}
                />
                <IconButton
                  onClick={() => playAudio(comprehensionData.title)}
                  color="primary"
                >
                  <VolumeUp />
                </IconButton>
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Reading Progress
              </Typography>
              <LinearProgress
                variant="determinate"
                value={readingProgress}
                sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary">
                {Math.round(readingProgress)}%
              </Typography>
            </Box>

            <Typography variant="body2" color="text.secondary">
              Click on words to highlight them for review
            </Typography>
          </CardContent>
        </Card>
      </motion.div>

      <Box sx={{ display: "flex", gap: 3 }}>
        {/* Reading Passage */}
        <Box sx={{ flex: 2 }}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ mb: 3, borderRadius: 3 }}>
              <CardContent sx={{ p: 4 }}>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 3,
                  }}
                >
                  <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                    Reading Passage
                  </Typography>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Tooltip title="Listen to passage">
                      <IconButton
                        onClick={() => playAudio(comprehensionData.passage)}
                        color="primary"
                        size="small"
                      >
                        <VolumeUp />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Show translation">
                      <IconButton
                        onClick={() => setShowTranslation(!showTranslation)}
                        color={showTranslation ? "primary" : "default"}
                        size="small"
                      >
                        <Translate />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>

                <Typography
                  variant="body1"
                  sx={{
                    lineHeight: 2,
                    fontSize: "1.1rem",
                    textAlign: "justify",
                    userSelect: "none",
                  }}
                >
                  {renderHighlightableText(comprehensionData.passage)}
                </Typography>

                {showTranslation && comprehensionData.translation && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Divider sx={{ my: 3 }} />
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ fontStyle: "italic", lineHeight: 1.8 }}
                    >
                      {comprehensionData.translation}
                    </Typography>
                  </motion.div>
                )}

                {highlightedWords.size > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>
                      Highlighted Words ({highlightedWords.size}):
                    </Typography>
                    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                      {Array.from(highlightedWords).map((wordKey, index) => {
                        const word = wordKey.split("-")[0];
                        return (
                          <Chip
                            key={index}
                            label={word}
                            size="small"
                            onDelete={() => {
                              const newHighlighted = new Set(highlightedWords);
                              newHighlighted.delete(wordKey);
                              setHighlightedWords(newHighlighted);
                            }}
                            sx={{ bgcolor: "#ffeb3b", color: "#000" }}
                          />
                        );
                      })}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Box>

        {/* Questions */}
        <Box sx={{ flex: 1 }}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card sx={{ borderRadius: 3, position: "sticky", top: 20 }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: "bold", mb: 3 }}>
                  Comprehension Questions
                </Typography>

                <Box sx={{ maxHeight: 600, overflow: "auto" }}>
                  {comprehensionData.questions.map((question, index) => (
                    <Accordion key={index} sx={{ mb: 2, borderRadius: 2 }}>
                      <AccordionSummary expandIcon={<ExpandMore />}>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 2,
                            width: "100%",
                          }}
                        >
                          <Typography
                            variant="body2"
                            sx={{ fontWeight: "bold" }}
                          >
                            Q{index + 1}
                          </Typography>
                          {selectedAnswers[index] && (
                            <CheckCircle
                              sx={{ color: "#4caf50", fontSize: 16 }}
                            />
                          )}
                          {question.hint && (
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleHint(index);
                              }}
                            >
                              <Lightbulb />
                            </IconButton>
                          )}
                        </Box>
                      </AccordionSummary>

                      <AccordionDetails>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {question.question}
                        </Typography>

                        {showHints[index] && question.hint && (
                          <Paper
                            sx={{
                              p: 2,
                              mb: 2,
                              bgcolor: "#e3f2fd",
                              borderRadius: 2,
                            }}
                          >
                            <Typography variant="body2" color="primary">
                              💡 {question.hint}
                            </Typography>
                          </Paper>
                        )}

                        <FormControl component="fieldset" fullWidth>
                          <RadioGroup
                            value={selectedAnswers[index] || ""}
                            onChange={(e) =>
                              handleAnswerSelect(index, e.target.value)
                            }
                          >
                            {question.options.map((option, optionIndex) => (
                              <FormControlLabel
                                key={optionIndex}
                                value={option}
                                control={<Radio size="small" />}
                                label={
                                  <Typography variant="body2">
                                    {option}
                                  </Typography>
                                }
                                sx={{ mb: 1 }}
                              />
                            ))}
                          </RadioGroup>
                        </FormControl>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>

                <Button
                  variant="contained"
                  fullWidth
                  onClick={handleComplete}
                  disabled={
                    Object.keys(selectedAnswers).length <
                    comprehensionData.questions.length
                  }
                  sx={{ mt: 3, borderRadius: 2 }}
                >
                  Submit Answers
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        </Box>
      </Box>
    </Box>
  );
};

ReadingComprehensionActivity.propTypes = {
  comprehensionData: PropTypes.shape({
    title: PropTypes.string.isRequired,
    passage: PropTypes.string.isRequired,
    translation: PropTypes.string,
    timeLimit: PropTypes.number,
    questions: PropTypes.arrayOf(
      PropTypes.shape({
        question: PropTypes.string.isRequired,
        options: PropTypes.arrayOf(PropTypes.string).isRequired,
        correctAnswer: PropTypes.string.isRequired,
        hint: PropTypes.string,
      })
    ).isRequired,
  }).isRequired,
  onComplete: PropTypes.func.isRequired,
  onNext: PropTypes.func,
};

export default ReadingComprehensionActivity;
