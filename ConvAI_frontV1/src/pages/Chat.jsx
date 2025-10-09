import { useState, useEffect, useRef } from "react";
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Grid,
  Card,
  CardContent,
} from "@mui/material";
import {
  Send,
  SmartToy,
  Person,
  Psychology,
  Lightbulb,
  QuestionAnswer,
  Translate,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import AnimatedButton from "../components/common/AnimatedButton";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const suggestedPrompts = [
  "Help me practice basic greetings",
  'Explain the difference between "your" and "you\'re"',
  'Give me a sentence with "accomplish"',
  "How do I introduce myself in English?",
];

const Chat = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Load chat history or show welcome message
    setMessages([
      {
        id: 1,
        role: "assistant",
        content: `Hello ${user?.username}! I'm your AI English learning assistant. How can I help you today?`,
        timestamp: new Date(),
      },
    ]);
  }, [user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSend = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setTyping(true);

    try {
      const response = await axiosInstance.post(API_ENDPOINTS.CHAT.MESSAGE, {
        message: inputMessage,
      });

      setTyping(false);
      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.data.response || response.data.message,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      setTyping(false);
      // Mock response for demo
      setTimeout(() => {
        const mockResponse = {
          id: Date.now() + 1,
          role: "assistant",
          content: `That's a great question! Let me help you with that. "${inputMessage}" - I can provide you with examples, explanations, and practice exercises for this topic.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, mockResponse]);
      }, 1000);
    }
  };

  const handlePromptClick = (prompt) => {
    setInputMessage(prompt);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <PageTransition>
      <Box
        sx={{
          height: "calc(100vh - 120px)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}>
            <Box
              sx={{
                width: 50,
                height: 50,
                borderRadius: "50%",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <SmartToy sx={{ color: "white", fontSize: 28 }} />
            </Box>
            <Box>
              <GradientText variant="h5" sx={{ fontWeight: 700 }}>
                AI Learning Assistant
              </GradientText>
              <Typography variant="body2" color="text.secondary">
                Ask me anything about English language learning
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Quick Actions */}
        {messages.length === 1 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
              Quick Start Suggestions:
            </Typography>
            <Grid container spacing={2}>
              {[
                {
                  icon: <Psychology />,
                  title: "Grammar Help",
                  color: "#0ea5e9",
                },
                {
                  icon: <Lightbulb />,
                  title: "Practice Tips",
                  color: "#f59e0b",
                },
                {
                  icon: <QuestionAnswer />,
                  title: "Conversation",
                  color: "#22c55e",
                },
                { icon: <Translate />, title: "Translation", color: "#d946ef" },
              ].map((action, index) => (
                <Grid item xs={6} sm={3} key={index}>
                  <Card
                    sx={{
                      cursor: "pointer",
                      transition: "all 0.3s",
                      "&:hover": {
                        transform: "translateY(-4px)",
                        boxShadow: 4,
                      },
                    }}
                    onClick={() => handlePromptClick(suggestedPrompts[index])}
                  >
                    <CardContent sx={{ textAlign: "center", p: 2 }}>
                      <Box sx={{ color: action.color, mb: 1 }}>
                        {action.icon}
                      </Box>
                      <Typography variant="body2" fontWeight={600}>
                        {action.title}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Suggested Prompts */}
        {messages.length === 1 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Try asking:
            </Typography>
            <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
              {suggestedPrompts.map((prompt, index) => (
                <Chip
                  key={index}
                  label={prompt}
                  onClick={() => handlePromptClick(prompt)}
                  sx={{ cursor: "pointer" }}
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Messages Container */}
        <Paper
          elevation={0}
          sx={{
            flex: 1,
            p: 3,
            overflowY: "auto",
            bgcolor: "background.default",
            border: 1,
            borderColor: "divider",
            borderRadius: 2,
            mb: 2,
          }}
        >
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Box
                  sx={{
                    display: "flex",
                    justifyContent:
                      message.role === "user" ? "flex-end" : "flex-start",
                    mb: 3,
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      gap: 2,
                      maxWidth: "70%",
                      flexDirection:
                        message.role === "user" ? "row-reverse" : "row",
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor:
                          message.role === "user"
                            ? "primary.main"
                            : "secondary.main",
                        width: 40,
                        height: 40,
                      }}
                    >
                      {message.role === "user" ? <Person /> : <SmartToy />}
                    </Avatar>
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        bgcolor:
                          message.role === "user"
                            ? "primary.main"
                            : "background.paper",
                        color:
                          message.role === "user" ? "white" : "text.primary",
                        borderRadius: 2,
                      }}
                    >
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: "pre-wrap" }}
                      >
                        {message.content}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{
                          display: "block",
                          mt: 1,
                          opacity: 0.7,
                        }}
                      >
                        {message.timestamp.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </Typography>
                    </Paper>
                  </Box>
                </Box>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          {typing && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
                <Avatar
                  sx={{ bgcolor: "secondary.main", width: 40, height: 40 }}
                >
                  <SmartToy />
                </Avatar>
                <Paper
                  elevation={1}
                  sx={{ p: 2, bgcolor: "background.paper", borderRadius: 2 }}
                >
                  <Box sx={{ display: "flex", gap: 0.5 }}>
                    {[0, 1, 2].map((dot) => (
                      <motion.div
                        key={dot}
                        animate={{ y: [0, -8, 0] }}
                        transition={{
                          duration: 0.6,
                          repeat: Infinity,
                          delay: dot * 0.2,
                        }}
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          backgroundColor: "#999",
                        }}
                      />
                    ))}
                  </Box>
                </Paper>
              </Box>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </Paper>

        {/* Input Area */}
        <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
          <Box sx={{ display: "flex", gap: 1, alignItems: "flex-end" }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Type your message..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              variant="outlined"
            />
            <AnimatedButton
              variant="contained"
              onClick={handleSend}
              disabled={!inputMessage.trim() || loading}
              sx={{ minWidth: 56, height: 56 }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                <Send />
              )}
            </AnimatedButton>
          </Box>
        </Paper>
      </Box>
    </PageTransition>
  );
};

export default Chat;
