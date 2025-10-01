import { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Chip,
  LinearProgress,
  Paper,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Collapse,
  Alert,
  Tooltip,
  Fade,
} from "@mui/material";
import {
  Timer,
  Lightbulb,
  Spellcheck,
  Translate,
  VolumeUp,
  Save,
  Send,
  ExpandMore,
  ExpandLess,
  CheckCircle,
  Warning,
  Info,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";
import { activitiesAPI } from "../../services/api";

const WritingPromptActivity = ({ promptData, onComplete, onSave }) => {
  const [writingText, setWritingText] = useState("");
  const [timeLeft, setTimeLeft] = useState(promptData.timeLimit || 1800); // 30 minutes default
  const [wordCount, setWordCount] = useState(0);
  const [showHints, setShowHints] = useState(false);
  const [showRubric, setShowRubric] = useState(false);
  const [grammarFeedback, setGrammarFeedback] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);
  const [writingProgress, setWritingProgress] = useState(0);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [autoSaveStatus, setAutoSaveStatus] = useState("saved");

  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      handleAutoSubmit();
    }
  }, [timeLeft]);

  useEffect(() => {
    const words = writingText
      .trim()
      .split(/\s+/)
      .filter((word) => word.length > 0);
    setWordCount(words.length);

    const targetWords = promptData.targetWordCount || 200;
    setWritingProgress(Math.min((words.length / targetWords) * 100, 100));

    // Auto-save every 30 seconds
    setAutoSaveStatus("saving");
    const autoSaveTimer = setTimeout(() => {
      if (onSave) {
        onSave({
          text: writingText,
          wordCount: words.length,
          timeSpent: (promptData.timeLimit || 1800) - timeLeft,
        });
      }
      setAutoSaveStatus("saved");
    }, 2000);

    return () => clearTimeout(autoSaveTimer);
  }, [
    writingText,
    promptData.targetWordCount,
    promptData.timeLimit,
    timeLeft,
    onSave,
  ]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleTextChange = (event) => {
    setWritingText(event.target.value);
  };

  const analyzeGrammar = async () => {
    if (!writingText.trim()) return;

    setIsAnalyzing(true);

    try {
      // Use real API for grammar analysis
      const response = await activitiesAPI.analyzeWriting(writingText);
      if (response.success && response.data.feedback) {
        setGrammarFeedback(response.data.feedback);
        toast.success("Grammar analysis complete!");
      } else {
        toast.warning("Grammar analysis unavailable. Please try again later.");
        setGrammarFeedback([]);
      }
    } catch (error) {
      console.error("Error analyzing grammar:", error);
      toast.error("Failed to analyze grammar. Please try again.");
      setGrammarFeedback([]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const playAudio = (text) => {
    if ("speechSynthesis" in window && text.trim()) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const handleAutoSubmit = () => {
    toast.info("Time is up! Auto-submitting your work.");
    handleSubmit();
  };

  const handleSubmit = () => {
    const result = {
      text: writingText,
      wordCount,
      timeSpent: (promptData.timeLimit || 1800) - timeLeft,
      grammarFeedback,
      completion: Math.min(
        (wordCount / (promptData.targetWordCount || 200)) * 100,
        100
      ),
    };

    onComplete(result);
    setShowSubmitDialog(false);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case "error":
        return "#f44336";
      case "warning":
        return "#ff9800";
      case "info":
        return "#2196f3";
      default:
        return "#757575";
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case "error":
        return <Warning />;
      case "warning":
        return <Warning />;
      case "info":
        return <Info />;
      default:
        return <CheckCircle />;
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto" }}>
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
                {promptData.title}
              </Typography>
              <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
                <Chip
                  label={autoSaveStatus === "saving" ? "Saving..." : "Saved"}
                  color={autoSaveStatus === "saving" ? "warning" : "success"}
                  size="small"
                />
                <Chip
                  icon={<Timer />}
                  label={formatTime(timeLeft)}
                  color={timeLeft < 300 ? "error" : "primary"}
                  sx={{ fontWeight: "bold" }}
                />
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Progress: {wordCount} / {promptData.targetWordCount || 200}{" "}
                words
              </Typography>
              <LinearProgress
                variant="determinate"
                value={writingProgress}
                sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary">
                {Math.round(writingProgress)}%
              </Typography>
            </Box>

            <Box sx={{ display: "flex", gap: 1 }}>
              <Button
                size="small"
                startIcon={<Lightbulb />}
                onClick={() => setShowHints(!showHints)}
                variant={showHints ? "contained" : "outlined"}
              >
                Hints
              </Button>
              <Button
                size="small"
                startIcon={<Info />}
                onClick={() => setShowRubric(!showRubric)}
                variant={showRubric ? "contained" : "outlined"}
              >
                Rubric
              </Button>
              <Button
                size="small"
                startIcon={<Translate />}
                onClick={() => setShowTranslation(!showTranslation)}
                variant={showTranslation ? "contained" : "outlined"}
              >
                Translation
              </Button>
            </Box>
          </CardContent>
        </Card>
      </motion.div>

      <Box sx={{ display: "flex", gap: 3 }}>
        {/* Main Writing Area */}
        <Box sx={{ flex: 2 }}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {/* Prompt */}
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
                  <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                    Writing Prompt
                  </Typography>
                  <IconButton
                    onClick={() => playAudio(promptData.prompt)}
                    color="primary"
                    size="small"
                  >
                    <VolumeUp />
                  </IconButton>
                </Box>

                <Typography variant="body1" sx={{ lineHeight: 1.8, mb: 2 }}>
                  {promptData.prompt}
                </Typography>

                {promptData.context && (
                  <Paper sx={{ p: 2, bgcolor: "#f5f5f5", borderRadius: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Context:</strong> {promptData.context}
                    </Typography>
                  </Paper>
                )}
              </CardContent>
            </Card>

            {/* Writing Area */}
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
                  <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                    Your Response
                  </Typography>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Tooltip title="Analyze Grammar">
                      <IconButton
                        onClick={analyzeGrammar}
                        disabled={isAnalyzing || !writingText.trim()}
                        color="primary"
                        size="small"
                      >
                        <Spellcheck />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Listen to your writing">
                      <IconButton
                        onClick={() => playAudio(writingText)}
                        disabled={!writingText.trim()}
                        color="primary"
                        size="small"
                      >
                        <VolumeUp />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>

                <TextField
                  multiline
                  rows={15}
                  fullWidth
                  placeholder="Start writing your response here..."
                  value={writingText}
                  onChange={handleTextChange}
                  variant="outlined"
                  sx={{
                    "& .MuiOutlinedInput-root": {
                      borderRadius: 2,
                      fontSize: "1rem",
                      lineHeight: 1.6,
                    },
                  }}
                />

                {isAnalyzing && (
                  <Box sx={{ mt: 2, textAlign: "center" }}>
                    <LinearProgress sx={{ mb: 1 }} />
                    <Typography variant="body2" color="text.secondary">
                      Analyzing your writing...
                    </Typography>
                  </Box>
                )}

                {/* Grammar Feedback */}
                <AnimatePresence>
                  {grammarFeedback.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <Box sx={{ mt: 3 }}>
                        <Typography
                          variant="subtitle2"
                          sx={{ mb: 2, fontWeight: "bold" }}
                        >
                          Writing Feedback ({grammarFeedback.length})
                        </Typography>
                        {grammarFeedback.map((feedback, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                          >
                            <Alert
                              severity={feedback.severity}
                              icon={getSeverityIcon(feedback.severity)}
                              sx={{ mb: 1, borderRadius: 2 }}
                            >
                              <Typography variant="body2">
                                {feedback.message}
                              </Typography>
                              {feedback.suggestion && (
                                <Typography
                                  variant="caption"
                                  sx={{
                                    display: "block",
                                    mt: 0.5,
                                    fontStyle: "italic",
                                  }}
                                >
                                  Suggestion: {feedback.suggestion}
                                </Typography>
                              )}
                            </Alert>
                          </motion.div>
                        ))}
                      </Box>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Action Buttons */}
                <Box sx={{ display: "flex", gap: 2, mt: 3 }}>
                  <Button
                    variant="outlined"
                    startIcon={<Save />}
                    onClick={() => {
                      if (onSave) {
                        onSave({
                          text: writingText,
                          wordCount,
                          timeSpent: (promptData.timeLimit || 1800) - timeLeft,
                        });
                      }
                      toast.success("Draft saved!");
                    }}
                    sx={{ borderRadius: 2 }}
                  >
                    Save Draft
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<Send />}
                    onClick={() => setShowSubmitDialog(true)}
                    disabled={wordCount < (promptData.minWordCount || 50)}
                    sx={{ borderRadius: 2 }}
                  >
                    Submit
                  </Button>
                </Box>

                {wordCount < (promptData.minWordCount || 50) && (
                  <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                    Minimum {promptData.minWordCount || 50} words required
                  </Typography>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Box>

        {/* Sidebar */}
        <Box sx={{ flex: 1 }}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Box sx={{ position: "sticky", top: 20 }}>
              {/* Hints */}
              <Collapse in={showHints}>
                <Card sx={{ mb: 3, borderRadius: 3 }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                      Writing Hints
                    </Typography>
                    {promptData.hints?.map((hint, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <Chip
                          label={hint}
                          variant="outlined"
                          sx={{ mb: 1, mr: 1 }}
                        />
                      </motion.div>
                    ))}
                  </CardContent>
                </Card>
              </Collapse>

              {/* Rubric */}
              <Collapse in={showRubric}>
                <Card sx={{ mb: 3, borderRadius: 3 }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                      Evaluation Rubric
                    </Typography>
                    {promptData.rubric?.map((criteria, index) => (
                      <Box key={index} sx={{ mb: 2 }}>
                        <Typography
                          variant="subtitle2"
                          sx={{ fontWeight: "bold" }}
                        >
                          {criteria.category}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {criteria.description}
                        </Typography>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
              </Collapse>

              {/* Translation */}
              <Collapse in={showTranslation && promptData.translation}>
                <Card sx={{ mb: 3, borderRadius: 3 }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                      Translation
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {promptData.translation}
                    </Typography>
                  </CardContent>
                </Card>
              </Collapse>

              {/* Statistics */}
              <Card sx={{ borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Typography variant="h6" sx={{ fontWeight: "bold", mb: 2 }}>
                    Writing Statistics
                  </Typography>

                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2">Words:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                      {wordCount}
                    </Typography>
                  </Box>

                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2">Characters:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                      {writingText.length}
                    </Typography>
                  </Box>

                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      mb: 1,
                    }}
                  >
                    <Typography variant="body2">Time Remaining:</Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: "bold",
                        color: timeLeft < 300 ? "#f44336" : "inherit",
                      }}
                    >
                      {formatTime(timeLeft)}
                    </Typography>
                  </Box>

                  <Box
                    sx={{ display: "flex", justifyContent: "space-between" }}
                  >
                    <Typography variant="body2">Completion:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                      {Math.round(writingProgress)}%
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          </motion.div>
        </Box>
      </Box>

      {/* Submit Confirmation Dialog */}
      <Dialog
        open={showSubmitDialog}
        onClose={() => setShowSubmitDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Submit Writing?</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Are you ready to submit your writing? You won&apos;t be able to make
            changes after submission.
          </Typography>

          <Paper sx={{ p: 2, bgcolor: "#f5f5f5", borderRadius: 2 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Word Count:</strong> {wordCount} words
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Time Spent:</strong>{" "}
              {formatTime((promptData.timeLimit || 1800) - timeLeft)}
            </Typography>
            <Typography variant="body2">
              <strong>Completion:</strong> {Math.round(writingProgress)}%
            </Typography>
          </Paper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSubmitDialog(false)}>
            Continue Writing
          </Button>
          <Button onClick={handleSubmit} variant="contained">
            Submit Final Draft
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

WritingPromptActivity.propTypes = {
  promptData: PropTypes.shape({
    title: PropTypes.string.isRequired,
    prompt: PropTypes.string.isRequired,
    context: PropTypes.string,
    translation: PropTypes.string,
    timeLimit: PropTypes.number,
    targetWordCount: PropTypes.number,
    minWordCount: PropTypes.number,
    hints: PropTypes.arrayOf(PropTypes.string),
    rubric: PropTypes.arrayOf(
      PropTypes.shape({
        category: PropTypes.string.isRequired,
        description: PropTypes.string.isRequired,
      })
    ),
  }).isRequired,
  onComplete: PropTypes.func.isRequired,
  onSave: PropTypes.func,
};

export default WritingPromptActivity;
