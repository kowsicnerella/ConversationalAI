import { useState, useEffect, useRef } from "react";
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Avatar,
  Paper,
  Chip,
  IconButton,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Tooltip,
  Divider,
} from "@mui/material";
import {
  Send,
  Mic,
  MicOff,
  VolumeUp,
  Refresh,
  Star,
  CheckCircle,
  Timer,
  Person,
  SmartToy,
  Translate,
  Lightbulb,
  PlayArrow,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "react-hot-toast";
import PropTypes from "prop-types";

const RolePlayActivity = ({ scenarioData, onComplete, onProgress }) => {
  const [messages, setMessages] = useState([]);
  const [currentInput, setCurrentInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [currentTurn, setCurrentTurn] = useState(0);
  const [score, setScore] = useState(0);
  const [showHints, setShowHints] = useState(false);
  const [showTranslation, setShowTranslation] = useState(false);
  const [timeLeft, setTimeLeft] = useState(scenarioData.timeLimit || 1200); // 20 minutes
  const [isComplete, setIsComplete] = useState(false);
  const [feedback, setFeedback] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const messagesEndRef = useRef(null);

  const currentStep = scenarioData.steps[currentTurn] || null;
  const progress = ((currentTurn + 1) / scenarioData.steps.length) * 100;

  useEffect(() => {
    // Initialize with the first AI message
    if (messages.length === 0 && scenarioData.steps.length > 0) {
      const firstStep = scenarioData.steps[0];
      if (firstStep.type === "ai") {
        addMessage(firstStep.content, "ai", firstStep.emotion);
        setCurrentTurn(1);
      }
    }
  }, [scenarioData.steps, messages.length]);

  useEffect(() => {
    if (timeLeft > 0 && !isComplete) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    } else if (timeLeft === 0) {
      handleComplete();
    }
  }, [timeLeft, isComplete]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const addMessage = (content, sender, emotion = null, rating = null) => {
    const newMessage = {
      id: Date.now(),
      content,
      sender,
      emotion,
      rating,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const handleSendMessage = () => {
    if (!currentInput.trim() || !currentStep) return;

    // Add user message
    addMessage(currentInput, "user");

    // Evaluate response
    const evaluation = evaluateResponse(currentInput, currentStep);

    // Add feedback
    setFeedback((prev) => [
      ...prev,
      {
        turn: currentTurn,
        userResponse: currentInput,
        expectedResponse: currentStep.expectedResponse,
        score: evaluation.score,
        feedback: evaluation.feedback,
      },
    ]);

    setScore((prev) => prev + evaluation.score);

    // Clear input
    setCurrentInput("");

    // Move to next turn
    const nextTurn = currentTurn + 1;
    setCurrentTurn(nextTurn);

    // Progress callback
    onProgress &&
      onProgress({
        currentTurn: nextTurn,
        totalTurns: scenarioData.steps.length,
        score,
        completion: (nextTurn / scenarioData.steps.length) * 100,
      });

    // Add AI response if available
    setTimeout(() => {
      if (nextTurn < scenarioData.steps.length) {
        const nextStep = scenarioData.steps[nextTurn];
        if (nextStep.type === "ai") {
          addMessage(nextStep.content, "ai", nextStep.emotion);
          setCurrentTurn(nextTurn + 1);
        }
      } else {
        // Scenario complete
        handleComplete();
      }
    }, 1000);
  };

  const evaluateResponse = (userResponse, step) => {
    const expectedKeywords = step.keywords || [];
    const userWords = userResponse.toLowerCase().split(" ");

    let matchedKeywords = 0;
    expectedKeywords.forEach((keyword) => {
      if (userWords.some((word) => word.includes(keyword.toLowerCase()))) {
        matchedKeywords++;
      }
    });

    const keywordScore =
      expectedKeywords.length > 0
        ? (matchedKeywords / expectedKeywords.length) * 50
        : 25;

    const lengthScore = Math.min(userResponse.length / 50, 1) * 25;
    const totalScore = Math.round(keywordScore + lengthScore);

    let feedback = "";
    if (totalScore >= 70) {
      feedback = "Excellent response! Very natural and appropriate.";
    } else if (totalScore >= 50) {
      feedback = "Good response! Consider being more specific.";
    } else if (totalScore >= 30) {
      feedback = "Decent attempt. Try to include more relevant details.";
    } else {
      feedback = "Keep practicing! Think about what the situation requires.";
    }

    return { score: totalScore, feedback };
  };

  const handleComplete = () => {
    setIsComplete(true);
    setShowResults(true);

    const totalPossibleScore =
      scenarioData.steps.filter((s) => s.type === "user").length * 75;
    const finalScore = Math.round((score / totalPossibleScore) * 100);

    onComplete({
      finalScore,
      totalTurns: scenarioData.steps.length,
      timeSpent: (scenarioData.timeLimit || 1200) - timeLeft,
      messages,
      feedback,
      completion: 100,
    });
  };

  const startRecording = () => {
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();

      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsRecording(true);
        toast.success("Listening... Speak now!");
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setCurrentInput(transcript);
        setIsRecording(false);
      };

      recognition.onerror = () => {
        setIsRecording(false);
        toast.error("Speech recognition failed. Please try again.");
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognition.start();
    } else {
      toast.error("Speech recognition not supported in this browser.");
    }
  };

  const playAudio = (text) => {
    if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.8;
      speechSynthesis.speak(utterance);
    }
  };

  const restartScenario = () => {
    setMessages([]);
    setCurrentTurn(0);
    setScore(0);
    setFeedback([]);
    setShowResults(false);
    setIsComplete(false);
    setTimeLeft(scenarioData.timeLimit || 1200);
    setCurrentInput("");
  };

  const getEmotionColor = (emotion) => {
    const emotions = {
      happy: "#4caf50",
      neutral: "#757575",
      concerned: "#ff9800",
      frustrated: "#f44336",
      excited: "#9c27b0",
      professional: "#2196f3",
    };
    return emotions[emotion] || "#757575";
  };

  const getEmotionEmoji = (emotion) => {
    const emojis = {
      happy: "😊",
      neutral: "😐",
      concerned: "😟",
      frustrated: "😤",
      excited: "🤩",
      professional: "👔",
    };
    return emojis[emotion] || "😐";
  };

  if (showResults) {
    const totalPossibleScore =
      scenarioData.steps.filter((s) => s.type === "user").length * 75;
    const finalScore = Math.round((score / totalPossibleScore) * 100);

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
            <Person sx={{ fontSize: 60, mb: 2 }} />
            <Typography variant="h3" sx={{ fontWeight: "bold", mb: 2 }}>
              Role-Play Complete!
            </Typography>

            <Typography variant="h1" sx={{ fontWeight: "bold", mb: 1 }}>
              {finalScore}%
            </Typography>

            <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
              Communication Score
            </Typography>

            <Box
              sx={{ display: "flex", justifyContent: "space-around", mb: 4 }}
            >
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                  {messages.filter((m) => m.sender === "user").length}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Your Messages
                </Typography>
              </Box>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                  {feedback.filter((f) => f.score >= 60).length}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Strong Responses
                </Typography>
              </Box>
              <Box sx={{ textAlign: "center" }}>
                <Typography variant="h4" sx={{ fontWeight: "bold" }}>
                  {formatTime((scenarioData.timeLimit || 1200) - timeLeft)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  Time Spent
                </Typography>
              </Box>
            </Box>

            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={restartScenario}
              sx={{
                bgcolor: "rgba(255,255,255,0.2)",
                "&:hover": { bgcolor: "rgba(255,255,255,0.3)" },
                borderRadius: 3,
              }}
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <Box
      sx={{
        maxWidth: 1000,
        mx: "auto",
        height: "80vh",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card sx={{ mb: 2, borderRadius: 3 }}>
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
                {scenarioData.title}
              </Typography>
              <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
                <Chip
                  icon={<Timer />}
                  label={formatTime(timeLeft)}
                  color={timeLeft < 300 ? "error" : "primary"}
                  sx={{ fontWeight: "bold" }}
                />
                <Chip
                  label={`${currentTurn}/${scenarioData.steps.length}`}
                  color="secondary"
                />
              </Box>
            </Box>

            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Progress
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
              />
              <Typography variant="body2" color="text.secondary">
                {Math.round(progress)}%
              </Typography>
            </Box>

            <Typography variant="body2" color="text.secondary">
              <strong>Scenario:</strong> {scenarioData.description}
            </Typography>
          </CardContent>
        </Card>
      </motion.div>

      {/* Chat Messages */}
      <Card
        sx={{
          flex: 1,
          borderRadius: 3,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        <Box sx={{ flex: 1, overflow: "auto", p: 3 }}>
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Box
                  sx={{
                    display: "flex",
                    justifyContent:
                      message.sender === "user" ? "flex-end" : "flex-start",
                    mb: 2,
                  }}
                >
                  <Box
                    sx={{
                      maxWidth: "70%",
                      display: "flex",
                      alignItems: "flex-start",
                      gap: 1,
                      flexDirection:
                        message.sender === "user" ? "row-reverse" : "row",
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor:
                          message.sender === "user"
                            ? "#1976d2"
                            : getEmotionColor(message.emotion),
                        width: 40,
                        height: 40,
                      }}
                    >
                      {message.sender === "user" ? <Person /> : <SmartToy />}
                    </Avatar>

                    <Paper
                      sx={{
                        p: 2,
                        borderRadius: 3,
                        bgcolor:
                          message.sender === "user" ? "#1976d2" : "#f5f5f5",
                        color:
                          message.sender === "user" ? "white" : "text.primary",
                        position: "relative",
                      }}
                    >
                      <Typography variant="body1">
                        {message.content}
                        {message.emotion && message.sender === "ai" && (
                          <span style={{ marginLeft: 8 }}>
                            {getEmotionEmoji(message.emotion)}
                          </span>
                        )}
                      </Typography>

                      {message.sender === "ai" && (
                        <IconButton
                          size="small"
                          onClick={() => playAudio(message.content)}
                          sx={{
                            position: "absolute",
                            top: 4,
                            right: 4,
                            color: "text.secondary",
                          }}
                        >
                          <VolumeUp fontSize="small" />
                        </IconButton>
                      )}
                    </Paper>
                  </Box>
                </Box>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        {currentStep && currentStep.type === "user" && !isComplete && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ p: 3, borderTop: "1px solid", borderColor: "divider" }}>
              {currentStep.hint && (
                <Paper
                  sx={{ p: 2, mb: 2, bgcolor: "#e3f2fd", borderRadius: 2 }}
                >
                  <Typography variant="body2" color="primary">
                    💡 {currentStep.hint}
                  </Typography>
                </Paper>
              )}

              <Box sx={{ display: "flex", gap: 2, alignItems: "flex-end" }}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={3}
                  placeholder={
                    currentStep.placeholder || "Type your response..."
                  }
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  variant="outlined"
                  sx={{ "& .MuiOutlinedInput-root": { borderRadius: 3 } }}
                />

                <Tooltip title={isRecording ? "Recording..." : "Voice Input"}>
                  <IconButton
                    onClick={startRecording}
                    disabled={isRecording}
                    color={isRecording ? "secondary" : "default"}
                    sx={{ mb: 1 }}
                  >
                    {isRecording ? <MicOff /> : <Mic />}
                  </IconButton>
                </Tooltip>

                <Button
                  variant="contained"
                  onClick={handleSendMessage}
                  disabled={!currentInput.trim()}
                  sx={{ borderRadius: 3, px: 3 }}
                  endIcon={<Send />}
                >
                  Send
                </Button>
              </Box>

              <Box
                sx={{ display: "flex", justifyContent: "space-between", mt: 2 }}
              >
                <Typography variant="caption" color="text.secondary">
                  Expected response length:{" "}
                  {currentStep.expectedLength || "1-2 sentences"}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Score: {score} points
                </Typography>
              </Box>
            </Box>
          </motion.div>
        )}
      </Card>

      {/* Floating Action Buttons */}
      <Box
        sx={{
          position: "fixed",
          bottom: 24,
          right: 24,
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        <Tooltip title="Show Hints">
          <Fab
            size="small"
            color="primary"
            onClick={() => setShowHints(!showHints)}
          >
            <Lightbulb />
          </Fab>
        </Tooltip>

        <Tooltip title="Translation Help">
          <Fab
            size="small"
            color="secondary"
            onClick={() => setShowTranslation(!showTranslation)}
          >
            <Translate />
          </Fab>
        </Tooltip>
      </Box>

      {/* Hints Dialog */}
      <Dialog
        open={showHints}
        onClose={() => setShowHints(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>💡 Conversation Tips</DialogTitle>
        <DialogContent>
          {scenarioData.generalHints?.map((hint, index) => (
            <Typography key={index} variant="body2" sx={{ mb: 1 }}>
              • {hint}
            </Typography>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHints(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Translation Dialog */}
      <Dialog
        open={showTranslation}
        onClose={() => setShowTranslation(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>🌐 Translation Help</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            Common phrases for this scenario:
          </Typography>
          {scenarioData.commonPhrases?.map((phrase, index) => (
            <Box key={index} sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: "bold" }}>
                {phrase.english}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {phrase.telugu}
              </Typography>
            </Box>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTranslation(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

RolePlayActivity.propTypes = {
  scenarioData: PropTypes.shape({
    title: PropTypes.string.isRequired,
    description: PropTypes.string.isRequired,
    timeLimit: PropTypes.number,
    steps: PropTypes.arrayOf(
      PropTypes.shape({
        type: PropTypes.oneOf(["user", "ai"]).isRequired,
        content: PropTypes.string,
        emotion: PropTypes.string,
        hint: PropTypes.string,
        placeholder: PropTypes.string,
        expectedResponse: PropTypes.string,
        expectedLength: PropTypes.string,
        keywords: PropTypes.arrayOf(PropTypes.string),
      })
    ).isRequired,
    generalHints: PropTypes.arrayOf(PropTypes.string),
    commonPhrases: PropTypes.arrayOf(
      PropTypes.shape({
        english: PropTypes.string.isRequired,
        telugu: PropTypes.string.isRequired,
      })
    ),
  }).isRequired,
  onComplete: PropTypes.func.isRequired,
  onProgress: PropTypes.func,
};

export default RolePlayActivity;
