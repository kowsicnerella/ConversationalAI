import { useState, useRef, useEffect } from "react";
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  Avatar,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  useTheme,
  CircularProgress,
  Menu,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Switch,
  FormControlLabel,
} from "@mui/material";
import {
  Send,
  Mic,
  MicOff,
  VolumeUp,
  Settings,
  History,
  Clear,
  SmartToy,
  Person,
  Download,
  Share,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useAuthStore } from "../store/index.js";
import { toast } from "react-hot-toast";
import { chatAPI } from "../services/api";

const ChatPage = () => {
  const theme = useTheme();
  const user = useAuthStore((state) => state.user);
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "bot",
      content:
        "Hello! I'm your AI Telugu-English tutor. How can I help you learn today?",
      timestamp: new Date(),
      category: "greeting",
    },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [language, setLanguage] = useState("en");
  const [chatMode, setChatMode] = useState("tutor");
  const [quickPrompts] = useState([
    { text: "Help me practice pronunciation", category: "pronunciation" },
    { text: "Explain Telugu grammar", category: "grammar" },
    { text: "Quiz me on vocabulary", category: "vocabulary" },
    { text: "Practice conversation", category: "conversation" },
    { text: "Translate this sentence", category: "translation" },
  ]);

  const messagesEndRef = useRef(null);
  const speechRecognition = useRef(null);
  const speechSynthesis = useRef(null);
  const [contextMenu, setContextMenu] = useState(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize speech services
    if ("webkitSpeechRecognition" in window) {
      speechRecognition.current = new window.webkitSpeechRecognition();
      speechRecognition.current.continuous = false;
      speechRecognition.current.interimResults = false;
      speechRecognition.current.lang = language === "te" ? "te-IN" : "en-US";

      speechRecognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputMessage(transcript);
        setIsRecording(false);
      };

      speechRecognition.current.onerror = () => {
        setIsRecording(false);
        toast.error("Speech recognition error. Please try again.");
      };
    }

    if ("speechSynthesis" in window) {
      speechSynthesis.current = window.speechSynthesis;
    }
  }, [language]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: "user",
      content: inputMessage,
      timestamp: new Date(),
      category: "user",
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageText = inputMessage;
    setInputMessage("");
    setIsTyping(true);

    try {
      let response;

      if (conversationId) {
        // Continue existing conversation
        response = await chatAPI.sendMessage(
          messageText,
          conversationId,
          chatMode === "tutor" ? "learning_chat" : "conversation"
        );
      } else {
        // Start new conversation with quick chat
        response = await chatAPI.quickChat(
          messageText,
          chatMode === "tutor" ? "tutoring" : "conversation"
        );
      }

      const botMessage = {
        id: messages.length + 2,
        type: "bot",
        content:
          response.data.ai_response?.text ||
          response.data.response ||
          "I'm here to help you learn!",
        timestamp: new Date(),
        category: response.data.ai_response?.category || "response",
        suggestions: response.data.ai_response?.suggested_practice
          ? [response.data.ai_response.suggested_practice]
          : [],
        translations: response.data.ai_response?.translations || [],
      };

      setMessages((prev) => [...prev, botMessage]);

      // Set conversation ID if this was the first message
      if (!conversationId && response.data.conversation_id) {
        setConversationId(response.data.conversation_id);
      }

      if (autoSpeak && speechEnabled) {
        speakMessage(botMessage.content);
      }
    } catch (error) {
      console.error("Failed to send message:", error);

      // Fallback to mock response
      const botResponse = generateBotResponse(messageText);
      const botMessage = {
        id: messages.length + 2,
        type: "bot",
        content: botResponse.content,
        timestamp: new Date(),
        category: botResponse.category,
        suggestions: botResponse.suggestions,
      };

      setMessages((prev) => [...prev, botMessage]);
      toast.error("Failed to get AI response, using offline mode");
    } finally {
      setIsTyping(false);
    }
  };

  const generateBotResponse = (userInput) => {
    const input = userInput.toLowerCase();

    if (input.includes("pronunciation") || input.includes("pronounce")) {
      return {
        content:
          "Let's work on pronunciation! Try saying 'Namaskaram' (నమస్కారం) - it means 'Hello' in Telugu. I'll listen and help you perfect it.",
        category: "pronunciation",
        suggestions: ["నమస్కారం", "dhanyavaadamulu", "ela unnaaru"],
      };
    }

    if (input.includes("grammar") || input.includes("rules")) {
      return {
        content:
          "Telugu grammar is fascinating! Let's start with basic sentence structure: Subject + Object + Verb. For example: 'Nenu pustakam chaduvutunanu' (I am reading a book).",
        category: "grammar",
        suggestions: [
          "Show more examples",
          "Explain verb conjugation",
          "Practice sentence building",
        ],
      };
    }

    if (input.includes("vocabulary") || input.includes("words")) {
      return {
        content:
          "Great! Let's expand your vocabulary. Here are some useful Telugu words:\n• Pustakam (పుస్తకం) - Book\n• Vidyalayam (విద్యాలయం) - School\n• Mitrudu (మిత్రుడు) - Friend\n\nWhich topic would you like to focus on?",
        category: "vocabulary",
        suggestions: [
          "Family words",
          "Food items",
          "Daily activities",
          "Numbers",
        ],
      };
    }

    if (input.includes("translate")) {
      return {
        content:
          "I'd be happy to help with translation! Please share the sentence you'd like me to translate between Telugu and English.",
        category: "translation",
        suggestions: [
          "Telugu to English",
          "English to Telugu",
          "Common phrases",
        ],
      };
    }

    return {
      content:
        "That's a great question! I'm here to help you learn Telugu and English. Would you like to practice pronunciation, learn new vocabulary, work on grammar, or have a conversation?",
      category: "general",
      suggestions: [
        "Practice pronunciation",
        "Learn vocabulary",
        "Study grammar",
        "Practice conversation",
      ],
    };
  };

  const speakMessage = (text) => {
    if (!speechSynthesis.current || !speechEnabled) return;

    setIsSpeaking(true);
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === "te" ? "te-IN" : "en-US";
    utterance.rate = 0.8;

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    speechSynthesis.current.speak(utterance);
  };

  const startRecording = () => {
    if (!speechRecognition.current) {
      toast.error("Speech recognition not supported in this browser");
      return;
    }

    setIsRecording(true);
    speechRecognition.current.start();
  };

  const stopRecording = () => {
    if (speechRecognition.current) {
      speechRecognition.current.stop();
    }
    setIsRecording(false);
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        type: "bot",
        content: "Chat cleared! How can I help you learn today?",
        timestamp: new Date(),
        category: "greeting",
      },
    ]);
    toast.success("Chat cleared");
  };

  const exportChat = () => {
    const chatData = messages.map((msg) => ({
      type: msg.type,
      content: msg.content,
      timestamp: msg.timestamp.toISOString(),
    }));

    const dataStr = JSON.stringify(chatData, null, 2);
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

    const exportFileDefaultName = `chat-history-${
      new Date().toISOString().split("T")[0]
    }.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
    linkElement.click();

    toast.success("Chat history exported");
  };

  const handleQuickPrompt = (prompt) => {
    setInputMessage(prompt.text);
  };

  const handleContextMenu = (event, message) => {
    event.preventDefault();
    setContextMenu({
      mouseX: event.clientX + 2,
      mouseY: event.clientY - 6,
      message,
    });
  };

  const handleCloseContextMenu = () => {
    setContextMenu(null);
  };

  const copyMessage = () => {
    navigator.clipboard.writeText(contextMenu.message.content);
    toast.success("Message copied to clipboard");
    handleCloseContextMenu();
  };

  const speakContextMessage = () => {
    speakMessage(contextMenu.message.content);
    handleCloseContextMenu();
  };

  return (
    <Container
      maxWidth="lg"
      sx={{ py: 3, height: "100vh", display: "flex", flexDirection: "column" }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ height: "100%", display: "flex", flexDirection: "column" }}
      >
        {/* Header */}
        <Paper
          sx={{
            p: 2,
            mb: 2,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
              <SmartToy />
            </Avatar>
            <Box>
              <Typography variant="h5" fontWeight="bold">
                AI Telugu Tutor
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {chatMode === "tutor"
                  ? "Personalized Learning Assistant"
                  : "Conversation Partner"}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: "flex", gap: 1 }}>
            <Tooltip title="Chat Settings">
              <IconButton onClick={() => setSettingsOpen(true)}>
                <Settings />
              </IconButton>
            </Tooltip>
            <Tooltip title="Chat History">
              <IconButton onClick={() => setHistoryOpen(true)}>
                <History />
              </IconButton>
            </Tooltip>
            <Tooltip title="Clear Chat">
              <IconButton onClick={clearChat}>
                <Clear />
              </IconButton>
            </Tooltip>
            <Tooltip title="Export Chat">
              <IconButton onClick={exportChat}>
                <Download />
              </IconButton>
            </Tooltip>
          </Box>
        </Paper>

        {/* Quick Prompts */}
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Quick Prompts:
          </Typography>
          <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
            {quickPrompts.map((prompt, index) => (
              <Chip
                key={index}
                label={prompt.text}
                onClick={() => handleQuickPrompt(prompt)}
                variant="outlined"
                size="small"
                sx={{ cursor: "pointer" }}
              />
            ))}
          </Box>
        </Paper>

        {/* Messages Area */}
        <Paper
          sx={{
            flex: 1,
            p: 2,
            overflow: "hidden",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <List sx={{ flex: 1, overflow: "auto", py: 0 }}>
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <ListItem
                    sx={{
                      display: "flex",
                      flexDirection:
                        message.type === "user" ? "row-reverse" : "row",
                      alignItems: "flex-start",
                      gap: 2,
                      mb: 2,
                    }}
                    onContextMenu={(e) => handleContextMenu(e, message)}
                  >
                    <Avatar
                      sx={{
                        bgcolor:
                          message.type === "user"
                            ? theme.palette.secondary.main
                            : theme.palette.primary.main,
                      }}
                    >
                      {message.type === "user" ? <Person /> : <SmartToy />}
                    </Avatar>

                    <Box
                      sx={{
                        maxWidth: "70%",
                        bgcolor:
                          message.type === "user"
                            ? theme.palette.secondary.light
                            : theme.palette.grey[100],
                        p: 2,
                        borderRadius: 2,
                        position: "relative",
                      }}
                    >
                      <Typography
                        variant="body1"
                        sx={{ whiteSpace: "pre-wrap" }}
                      >
                        {message.content}
                      </Typography>

                      {message.suggestions && (
                        <Box
                          sx={{
                            mt: 2,
                            display: "flex",
                            gap: 1,
                            flexWrap: "wrap",
                          }}
                        >
                          {message.suggestions.map((suggestion, index) => (
                            <Chip
                              key={index}
                              label={suggestion}
                              size="small"
                              variant="outlined"
                              onClick={() => setInputMessage(suggestion)}
                              sx={{ cursor: "pointer" }}
                            />
                          ))}
                        </Box>
                      )}

                      <Typography
                        variant="caption"
                        color="text.secondary"
                        sx={{ display: "block", mt: 1 }}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Box>
                  </ListItem>
                </motion.div>
              ))}
            </AnimatePresence>

            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <ListItem
                  sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}
                >
                  <Avatar sx={{ bgcolor: theme.palette.primary.main }}>
                    <SmartToy />
                  </Avatar>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <CircularProgress size={16} />
                    <Typography variant="body2" color="text.secondary">
                      AI is typing...
                    </Typography>
                  </Box>
                </ListItem>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </List>
        </Paper>

        {/* Input Area */}
        <Paper sx={{ p: 2, mt: 2 }}>
          <Box sx={{ display: "flex", gap: 1, alignItems: "flex-end" }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message or use voice input..."
              onKeyPress={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              disabled={isRecording}
            />

            <Tooltip
              title={isRecording ? "Stop Recording" : "Start Voice Input"}
            >
              <IconButton
                onClick={isRecording ? stopRecording : startRecording}
                color={isRecording ? "error" : "default"}
                disabled={!speechEnabled}
              >
                {isRecording ? <MicOff /> : <Mic />}
              </IconButton>
            </Tooltip>

            <Tooltip title="Send Message">
              <IconButton
                onClick={handleSendMessage}
                color="primary"
                disabled={!inputMessage.trim() || isRecording}
              >
                <Send />
              </IconButton>
            </Tooltip>
          </Box>
        </Paper>
      </motion.div>

      {/* Context Menu */}
      <Menu
        open={Boolean(contextMenu)}
        onClose={handleCloseContextMenu}
        anchorReference="anchorPosition"
        anchorPosition={
          contextMenu
            ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
            : undefined
        }
      >
        <MenuItem onClick={copyMessage}>
          <Share sx={{ mr: 1 }} />
          Copy Message
        </MenuItem>
        <MenuItem onClick={speakContextMessage}>
          <VolumeUp sx={{ mr: 1 }} />
          Speak Message
        </MenuItem>
      </Menu>

      {/* Settings Dialog */}
      <Dialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Chat Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 3, mt: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={speechEnabled}
                  onChange={(e) => setSpeechEnabled(e.target.checked)}
                />
              }
              label="Enable Speech Recognition"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={autoSpeak}
                  onChange={(e) => setAutoSpeak(e.target.checked)}
                />
              }
              label="Auto-speak AI Responses"
            />

            <FormControl fullWidth>
              <InputLabel>Language</InputLabel>
              <Select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                label="Language"
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="te">Telugu</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Chat Mode</InputLabel>
              <Select
                value={chatMode}
                onChange={(e) => setChatMode(e.target.value)}
                label="Chat Mode"
              >
                <MenuItem value="tutor">AI Tutor</MenuItem>
                <MenuItem value="conversation">Conversation Partner</MenuItem>
                <MenuItem value="translator">Translation Assistant</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* History Dialog */}
      <Dialog
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Conversation History</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Your recent conversations and learning progress
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body1">
              Chat history feature will be implemented with user sessions and
              persistent storage.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ChatPage;
