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
  Tabs,
  Tab,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  List,
  ListItem,
  ListItemText,
  Switch,
  FormControlLabel,
} from "@mui/material";
import {
  Send,
  SmartToy,
  Person,
  Psychology,
  Lightbulb,
  QuestionAnswer,
  Translate,
  Search,
  History,
  Insights,
  FileDownload,
  Delete,
  Edit,
  Info,
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

const ChatEnhanced = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const [showWebSearch, setShowWebSearch] = useState(false);
  const [learningContext, setLearningContext] = useState(null);
  const [memories, setMemories] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [conversationTopic, setConversationTopic] = useState("general");
  const [showNewConversationDialog, setShowNewConversationDialog] = useState(false);
  const [newConvTitle, setNewConvTitle] = useState("");
  const [webSearchResults, setWebSearchResults] = useState([]);
  const messagesEndRef = useRef(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
    loadLearningContext();
    loadMemories();
    loadStatistics();
  }, [user]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadConversations = async () => {
    try {
      const response = await axiosInstance.get("/api/chat-v2/conversations", {
        params: { limit: 20 },
      });
      if (response.data.success) {
        setConversations(response.data.conversations);
        // Load first conversation or create default
        if (response.data.conversations.length > 0) {
          loadConversation(response.data.conversations[0].id);
        } else {
          createNewConversation();
        }
      }
    } catch (error) {
      console.error("Error loading conversations:", error);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const response = await axiosInstance.get(
        `/api/chat-v2/conversations/${conversationId}`
      );
      if (response.data.success) {
        setCurrentConversation(response.data.conversation);
        setMessages(response.data.messages || []);
        setConversationTopic(response.data.conversation.topic || "general");
      }
    } catch (error) {
      console.error("Error loading conversation:", error);
    }
  };

  const loadLearningContext = async () => {
    try {
      const response = await axiosInstance.get("/api/chat-v2/user-learning-context");
      if (response.data.success) {
        setLearningContext(response.data.context);
      }
    } catch (error) {
      console.error("Error loading learning context:", error);
    }
  };

  const loadMemories = async () => {
    try {
      const response = await axiosInstance.get("/api/chat-v2/user-memories", {
        params: { limit: 10 },
      });
      if (response.data.success) {
        setMemories(response.data.memories);
      }
    } catch (error) {
      console.error("Error loading memories:", error);
    }
  };

  const loadStatistics = async () => {
    try {
      const response = await axiosInstance.get("/api/chat-v2/learning-statistics");
      if (response.data.success) {
        setStatistics(response.data.statistics);
      }
    } catch (error) {
      console.error("Error loading statistics:", error);
    }
  };

  const loadSuggestions = async () => {
    try {
      const response = await axiosInstance.get("/api/chat-v2/personalized-suggestions");
      if (response.data.success) {
        setSuggestions(response.data.suggestions);
      }
    } catch (error) {
      console.error("Error loading suggestions:", error);
    }
  };

  const createNewConversation = async () => {
    try {
      const response = await axiosInstance.post("/api/chat-v2/conversations", {
        title: newConvTitle || `New Chat - ${new Date().toLocaleDateString()}`,
        topic: conversationTopic,
      });
      if (response.data.success) {
        const newConv = response.data.conversation;
        setConversations([newConv, ...conversations]);
        setCurrentConversation(newConv);
        setMessages([]);
        setNewConvTitle("");
        setShowNewConversationDialog(false);
      }
    } catch (error) {
      console.error("Error creating conversation:", error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !currentConversation) return;

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
      const response = await axiosInstance.post(
        `/api/chat-v2/conversations/${currentConversation.id}/messages`,
        {
          message: inputMessage,
          use_web_search: showWebSearch,
          topic: conversationTopic,
        }
      );

      setTyping(false);

      if (response.data.success) {
        const aiResponse = response.data.ai_response;
        setMessages((prev) => [...prev, {
          id: Date.now() + 1,
          role: "assistant",
          content: aiResponse.content,
          timestamp: new Date(),
          telugu_translation: aiResponse.telugu_translation,
          examples: aiResponse.examples,
        }]);

        // Update conversation
        if (response.data.conversation) {
          setCurrentConversation(response.data.conversation);
        }

        // Store web results if any
        if (response.data.web_results) {
          setWebSearchResults(response.data.web_results);
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setTyping(false);
    }
  };

  const handleSearchConversations = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await axiosInstance.post("/api/chat-v2/search-conversations", {
        query: searchQuery,
        limit: 10,
      });

      if (response.data.success) {
        setConversations(response.data.conversations);
      }
    } catch (error) {
      console.error("Error searching conversations:", error);
    }
  };

  const handleExportConversation = async () => {
    if (!currentConversation) return;

    try {
      const response = await axiosInstance.get(
        `/api/chat-v2/conversations/${currentConversation.id}/export`,
        { params: { format: "json" } }
      );

      if (response.data.success) {
        const element = document.createElement("a");
        element.setAttribute(
          "href",
          "data:text/json;charset=utf-8," +
            encodeURIComponent(JSON.stringify(response.data.data, null, 2))
        );
        element.setAttribute(
          "download",
          `conversation-${currentConversation.id}.json`
        );
        element.style.display = "none";
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
      }
    } catch (error) {
      console.error("Error exporting conversation:", error);
    }
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      const response = await axiosInstance.delete(
        `/api/chat-v2/conversations/${conversationId}`
      );

      if (response.data.success) {
        setConversations(conversations.filter((c) => c.id !== conversationId));
        if (currentConversation?.id === conversationId) {
          setCurrentConversation(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error("Error deleting conversation:", error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <PageTransition>
      <Box sx={{ display: "flex", height: "calc(100vh - 120px)", gap: 2 }}>
        {/* Left Sidebar - Conversations */}
        <Box
          sx={{
            width: 300,
            borderRight: 1,
            borderColor: "divider",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* Header */}
          <Box sx={{ p: 2, borderBottom: 1, borderColor: "divider" }}>
            <AnimatedButton
              fullWidth
              variant="contained"
              onClick={() => setShowNewConversationDialog(true)}
              sx={{ mb: 2 }}
            >
              New Chat
            </AnimatedButton>

            {/* Search Box */}
            <TextField
              fullWidth
              size="small"
              placeholder="Search conversations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearchConversations()}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: "text.secondary" }} />,
              }}
            />
          </Box>

          {/* Conversations List */}
          <Box sx={{ flex: 1, overflowY: "auto" }}>
            {conversations.map((conv) => (
              <Box
                key={conv.id}
                onClick={() => loadConversation(conv.id)}
                sx={{
                  p: 2,
                  borderBottom: 1,
                  borderColor: "divider",
                  cursor: "pointer",
                  bgcolor: currentConversation?.id === conv.id ? "action.selected" : "transparent",
                  transition: "all 0.2s",
                  "&:hover": { bgcolor: "action.hover" },
                }}
              >
                <Typography variant="body2" fontWeight={600} noWrap>
                  {conv.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {conv.topic} • {conv.message_count} messages
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>

        {/* Main Chat Area */}
        <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {/* Tabs */}
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: "divider" }}
          >
            <Tab label="Chat" />
            <Tab label="Memories" icon={<History />} />
            <Tab label="Insights" icon={<Insights />} />
            <Tab label="Web Search" icon={<Search />} />
          </Tabs>

          {/* Tab Content */}
          {activeTab === 0 && (
            <>
              {/* Messages */}
              <Paper
                elevation={0}
                sx={{
                  flex: 1,
                  p: 3,
                  overflowY: "auto",
                  bgcolor: "background.default",
                }}
              >
                {messages.length === 0 && (
                  <Box sx={{ textAlign: "center", py: 4 }}>
                    <SmartToy sx={{ fontSize: 48, color: "text.secondary", mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      Start a conversation!
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Ask me anything about English learning
                    </Typography>
                  </Box>
                )}

                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
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
                                message.role === "user"
                                  ? "white"
                                  : "text.primary",
                              borderRadius: 2,
                            }}
                          >
                            <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                              {message.content}
                            </Typography>
                            {message.telugu_translation && (
                              <Typography
                                variant="caption"
                                sx={{
                                  display: "block",
                                  mt: 1,
                                  opacity: 0.7,
                                  fontStyle: "italic",
                                }}
                              >
                                🇹🇪 {message.telugu_translation}
                              </Typography>
                            )}
                            {message.examples && message.examples.length > 0 && (
                              <Box sx={{ mt: 2 }}>
                                <Typography variant="caption" fontWeight={600}>
                                  Examples:
                                </Typography>
                                {message.examples.map((ex, i) => (
                                  <Typography
                                    key={i}
                                    variant="caption"
                                    sx={{ display: "block", opacity: 0.8 }}
                                  >
                                    • {ex}
                                  </Typography>
                                ))}
                              </Box>
                            )}
                          </Paper>
                        </Box>
                      </Box>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {typing && (
                  <Box sx={{ display: "flex", gap: 2 }}>
                    <Avatar sx={{ bgcolor: "secondary.main", width: 40, height: 40 }}>
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
                )}

                <div ref={messagesEndRef} />
              </Paper>

              {/* Input Area */}
              <Paper elevation={2} sx={{ p: 2 }}>
                <Box sx={{ display: "flex", gap: 1, mb: 2, alignItems: "center" }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={showWebSearch}
                        onChange={(e) => setShowWebSearch(e.target.checked)}
                      />
                    }
                    label="Web Search"
                  />
                </Box>

                <Box sx={{ display: "flex", gap: 1, alignItems: "flex-end" }}>
                  <TextField
                    fullWidth
                    multiline
                    maxRows={4}
                    placeholder="Type your message..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={loading || !currentConversation}
                    variant="outlined"
                  />
                  <AnimatedButton
                    variant="contained"
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || loading || !currentConversation}
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
            </>
          )}

          {/* Memories Tab */}
          {activeTab === 1 && (
            <Box sx={{ p: 3, overflowY: "auto", flex: 1 }}>
              <GradientText variant="h6" sx={{ mb: 2 }}>
                Your Learning Memories
              </GradientText>
              {memories.length > 0 ? (
                <List>
                  {memories.map((memory, index) => (
                    <ListItem key={index} sx={{ mb: 2, p: 2, bgcolor: "action.hover", borderRadius: 1 }}>
                      <ListItemText
                        primary={memory.content || "Memory"}
                        secondary={memory.timestamp}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">No memories yet</Typography>
              )}
            </Box>
          )}

          {/* Insights Tab */}
          {activeTab === 2 && (
            <Box sx={{ p: 3, overflowY: "auto", flex: 1 }}>
              <GradientText variant="h6" sx={{ mb: 2 }}>
                Learning Insights
              </GradientText>
              {statistics && (
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Card>
                      <CardContent>
                        <Typography color="text.secondary">Total Conversations</Typography>
                        <Typography variant="h4">{statistics.total_conversations}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Card>
                      <CardContent>
                        <Typography color="text.secondary">Total Messages</Typography>
                        <Typography variant="h4">{statistics.total_messages}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Card>
                      <CardContent>
                        <Typography color="text.secondary">Learning Time</Typography>
                        <Typography variant="h6">
                          {Math.round(statistics.total_learning_time_seconds / 60)} min
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Card>
                      <CardContent>
                        <Typography color="text.secondary">Most Discussed</Typography>
                        <Typography variant="h6">{statistics.most_discussed_topic}</Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              )}
            </Box>
          )}

          {/* Web Search Tab */}
          {activeTab === 3 && (
            <Box sx={{ p: 3, overflowY: "auto", flex: 1 }}>
              <GradientText variant="h6" sx={{ mb: 2 }}>
                Web Search Results
              </GradientText>
              {webSearchResults.length > 0 ? (
                webSearchResults.map((result, index) => (
                  <Card key={index} sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="subtitle1" fontWeight={600}>
                        {result.title}
                      </Typography>
                      <Typography variant="body2" sx={{ my: 1 }}>
                        {result.body}
                      </Typography>
                      <Typography
                        component="a"
                        href={result.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        variant="caption"
                        color="primary"
                        sx={{ cursor: "pointer" }}
                      >
                        Read more →
                      </Typography>
                    </CardContent>
                  </Card>
                ))
              ) : (
                <Typography color="text.secondary">
                  No search results yet. Enable web search while chatting!
                </Typography>
              )}
            </Box>
          )}
        </Box>

        {/* Right Sidebar - Actions */}
        <Box
          sx={{
            width: 280,
            borderLeft: 1,
            borderColor: "divider",
            p: 2,
            display: "flex",
            flexDirection: "column",
            gap: 2,
            overflowY: "auto",
          }}
        >
          <GradientText variant="subtitle2" sx={{ fontWeight: 700 }}>
            Quick Actions
          </GradientText>

          <AnimatedButton
            fullWidth
            variant="outlined"
            startIcon={<FileDownload />}
            onClick={handleExportConversation}
            disabled={!currentConversation}
          >
            Export
          </AnimatedButton>

          <AnimatedButton
            fullWidth
            variant="outlined"
            startIcon={<Delete />}
            onClick={() =>
              currentConversation && handleDeleteConversation(currentConversation.id)
            }
            disabled={!currentConversation}
            color="error"
          >
            Delete
          </AnimatedButton>

          <Divider />

          <Typography variant="subtitle2" fontWeight={600}>
            Learning Topics
          </Typography>

          {["Grammar", "Vocabulary", "Conversation", "Pronunciation"].map((topic) => (
            <Chip
              key={topic}
              label={topic}
              onClick={() => setConversationTopic(topic.toLowerCase())}
              variant={
                conversationTopic === topic.toLowerCase()
                  ? "filled"
                  : "outlined"
              }
            />
          ))}
        </Box>
      </Box>

      {/* New Conversation Dialog */}
      <Dialog
        open={showNewConversationDialog}
        onClose={() => setShowNewConversationDialog(false)}
      >
        <DialogTitle>Start New Conversation</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Conversation Title"
            fullWidth
            value={newConvTitle}
            onChange={(e) => setNewConvTitle(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowNewConversationDialog(false)}>Cancel</Button>
          <AnimatedButton onClick={createNewConversation} variant="contained">
            Create
          </AnimatedButton>
        </DialogActions>
      </Dialog>
    </PageTransition>
  );
};

export default ChatEnhanced;
