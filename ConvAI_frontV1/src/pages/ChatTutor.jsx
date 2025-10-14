import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Divider,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Alert,
  Tooltip,
  Menu,
  MenuItem,
  Card,
  CardContent,
  Collapse,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Menu as MenuIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Summarize as SummarizeIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import API from '../config/api';

const ChatTutor = () => {
  // State
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [error, setError] = useState('');
  const [renameDialogOpen, setRenameDialogOpen] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [expandedMessages, setExpandedMessages] = useState({});
  const [summary, setSummary] = useState('');
  const [loadingSummary, setLoadingSummary] = useState(false);
  
  const messagesEndRef = useRef(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await API.get('/chat-tutor/conversations');
      setConversations(response.data.conversations || []);
      
      // Auto-select first conversation
      if (response.data.conversations?.length > 0 && !currentConversation) {
        loadConversation(response.data.conversations[0].id);
      }
    } catch (err) {
      setError('Failed to load conversations: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      setLoading(true);
      setError('');
      const response = await API.get(`/chat-tutor/conversations/${conversationId}`);
      setCurrentConversation(response.data.conversation);
      setMessages(response.data.messages || []);
      setDrawerOpen(false);
    } catch (err) {
      setError('Failed to load conversation: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const createNewConversation = async () => {
    try {
      setLoading(true);
      const response = await API.post('/chat-tutor/conversations', {
        topic: 'General'
      });
      
      setConversations([response.data.conversation, ...conversations]);
      setCurrentConversation(response.data.conversation);
      setMessages([]);
      setDrawerOpen(false);
      setError('');
    } catch (err) {
      setError('Failed to create conversation: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || sending) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');

    try {
      setSending(true);
      setError('');

      // If no conversation, create one and send message in one request
      if (!currentConversation) {
        const response = await API.post('/chat-tutor/quick-chat', {
          message: userMessage
        });
        
        setCurrentConversation(response.data.conversation);
        setMessages([response.data.user_message, response.data.ai_response]);
        setConversations([response.data.conversation, ...conversations]);
      } else {
        // Send message to existing conversation
        const response = await API.post(
          `/chat-tutor/conversations/${currentConversation.id}/messages`,
          { message: userMessage }
        );
        
        setMessages([...messages, response.data.user_message, response.data.ai_response]);
        setCurrentConversation(response.data.conversation);
      }
    } catch (err) {
      setError('Failed to send message: ' + (err.response?.data?.error || err.message));
    } finally {
      setSending(false);
    }
  };

  const clearConversation = async () => {
    if (!currentConversation) return;
    
    if (!window.confirm('Clear all messages in this conversation?')) return;

    try {
      await API.delete(`/chat-tutor/conversations/${currentConversation.id}/clear`);
      setMessages([]);
      setError('');
      handleMenuClose();
    } catch (err) {
      setError('Failed to clear conversation: ' + (err.response?.data?.error || err.message));
    }
  };

  const deleteConversation = async () => {
    if (!currentConversation) return;
    
    if (!window.confirm('Delete this conversation permanently?')) return;

    try {
      await API.delete(`/chat-tutor/conversations/${currentConversation.id}`);
      setConversations(conversations.filter(c => c.id !== currentConversation.id));
      setCurrentConversation(null);
      setMessages([]);
      setError('');
      handleMenuClose();
    } catch (err) {
      setError('Failed to delete conversation: ' + (err.response?.data?.error || err.message));
    }
  };

  const renameConversation = async () => {
    if (!currentConversation || !newTitle.trim()) return;

    try {
      const response = await API.put(`/chat-tutor/conversations/${currentConversation.id}`, {
        title: newTitle.trim()
      });
      
      setCurrentConversation(response.data.conversation);
      setConversations(conversations.map(c => 
        c.id === currentConversation.id ? response.data.conversation : c
      ));
      setRenameDialogOpen(false);
      setNewTitle('');
      setError('');
    } catch (err) {
      setError('Failed to rename conversation: ' + (err.response?.data?.error || err.message));
    }
  };

  const loadSummary = async () => {
    if (!currentConversation) return;

    try {
      setLoadingSummary(true);
      const response = await API.get(`/chat-tutor/conversations/${currentConversation.id}/summary`);
      setSummary(response.data.summary);
    } catch (err) {
      setError('Failed to load summary: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleMenuClick = (event) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
  };

  const toggleMessageExpand = (messageId) => {
    setExpandedMessages(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Render message with formatting
  const renderMessage = (message) => {
    const isUser = message.role === 'user';
    const isExpanded = expandedMessages[message.id];

    return (
      <motion.div
        key={message.id}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Box
          sx={{
            display: 'flex',
            justifyContent: isUser ? 'flex-end' : 'flex-start',
            mb: 2,
          }}
        >
          {!isUser && (
            <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>
              <BotIcon />
            </Avatar>
          )}
          
          <Box sx={{ maxWidth: '75%' }}>
            <Paper
              elevation={2}
              sx={{
                p: 2,
                bgcolor: isUser ? 'primary.main' : 'grey.100',
                color: isUser ? 'white' : 'text.primary',
              }}
            >
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {message.content}
              </Typography>

              {/* Telugu Translation */}
              {!isUser && message.telugu_translation && (
                <Box sx={{ mt: 1.5 }}>
                  <Chip
                    label="తెలుగు"
                    size="small"
                    color="primary"
                    variant="outlined"
                    sx={{ mb: 0.5 }}
                  />
                  <Typography variant="body2" color="primary.dark">
                    {message.telugu_translation}
                  </Typography>
                </Box>
              )}

              {/* Grammar Explanation */}
              {!isUser && message.grammar_explanation && (
                <Card sx={{ mt: 1.5, bgcolor: 'info.light' }}>
                  <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Typography variant="caption" fontWeight="bold" color="info.dark">
                      📖 Grammar Note:
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {message.grammar_explanation}
                    </Typography>
                  </CardContent>
                </Card>
              )}

              {/* Examples */}
              {!isUser && message.examples && message.examples.length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" fontWeight="bold" color="success.dark">
                    💡 Examples:
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => toggleMessageExpand(message.id)}
                    sx={{ ml: 0.5 }}
                  >
                    {isExpanded ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
                  </IconButton>
                  
                  <Collapse in={isExpanded}>
                    <List dense sx={{ mt: 0.5 }}>
                      {message.examples.map((example, idx) => (
                        <ListItem key={idx} disableGutters>
                          <Typography variant="body2">• {example}</Typography>
                        </ListItem>
                      ))}
                    </List>
                  </Collapse>
                </Box>
              )}

              {/* Correction */}
              {!isUser && message.correction && (
                <Alert severity="warning" sx={{ mt: 1.5, py: 0 }}>
                  <Typography variant="body2">
                    {message.correction}
                  </Typography>
                </Alert>
              )}

              <Typography
                variant="caption"
                sx={{ display: 'block', mt: 1, opacity: 0.7 }}
              >
                {new Date(message.created_at).toLocaleTimeString()}
              </Typography>
            </Paper>
          </Box>

          {isUser && (
            <Avatar sx={{ bgcolor: 'secondary.main', ml: 1 }}>
              <PersonIcon />
            </Avatar>
          )}
        </Box>
      </motion.div>
    );
  };

  return (
    <Box sx={{ display: 'flex', height: 'calc(100vh - 64px)', overflow: 'hidden' }}>
      {/* Sidebar Drawer */}
      <Drawer
        anchor="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{ '& .MuiDrawer-paper': { width: 300, mt: '64px' } }}
      >
        <Box sx={{ p: 2 }}>
          <Button
            variant="contained"
            fullWidth
            startIcon={<AddIcon />}
            onClick={createNewConversation}
            disabled={loading}
          >
            New Conversation
          </Button>
        </Box>
        
        <Divider />
        
        <List>
          {conversations.map(conv => (
            <ListItemButton
              key={conv.id}
              selected={currentConversation?.id === conv.id}
              onClick={() => loadConversation(conv.id)}
            >
              <ListItemText
                primary={conv.title}
                secondary={`${conv.message_count} messages`}
              />
            </ListItemButton>
          ))}
        </List>
      </Drawer>

      {/* Main Chat Area */}
      <Container maxWidth="lg" sx={{ display: 'flex', flexDirection: 'column', height: '100%', py: 2 }}>
        {/* Header */}
        <Paper elevation={2} sx={{ p: 2, mb: 2, display: 'flex', alignItems: 'center' }}>
          <IconButton onClick={() => setDrawerOpen(true)} sx={{ mr: 2 }}>
            <MenuIcon />
          </IconButton>
          
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6">
              {currentConversation?.title || 'Chat with AI Tutor'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Ask questions about English grammar, vocabulary, and more!
            </Typography>
          </Box>

          {currentConversation && (
            <>
              <Tooltip title="Summary">
                <IconButton onClick={loadSummary} disabled={loadingSummary}>
                  <SummarizeIcon />
                </IconButton>
              </Tooltip>
              <IconButton onClick={handleMenuClick}>
                <EditIcon />
              </IconButton>
              <Menu
                anchorEl={menuAnchor}
                open={Boolean(menuAnchor)}
                onClose={handleMenuClose}
              >
                <MenuItem onClick={() => { setRenameDialogOpen(true); handleMenuClose(); }}>
                  <EditIcon fontSize="small" sx={{ mr: 1 }} />
                  Rename
                </MenuItem>
                <MenuItem onClick={clearConversation}>
                  <ClearIcon fontSize="small" sx={{ mr: 1 }} />
                  Clear Messages
                </MenuItem>
                <MenuItem onClick={deleteConversation} sx={{ color: 'error.main' }}>
                  <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
                  Delete Conversation
                </MenuItem>
              </Menu>
            </>
          )}
        </Paper>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" onClose={() => setError('')} sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Summary Alert */}
        {summary && (
          <Alert severity="info" onClose={() => setSummary('')} sx={{ mb: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold">Conversation Summary:</Typography>
            <Typography variant="body2">{summary}</Typography>
          </Alert>
        )}

        {/* Messages Area */}
        <Paper
          elevation={1}
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            p: 3,
            mb: 2,
            bgcolor: 'grey.50',
          }}
        >
          {loading && messages.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <CircularProgress />
            </Box>
          ) : messages.length === 0 ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
              <BotIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Start a conversation!
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ask me anything about English - grammar, vocabulary, pronunciation, or usage.
              </Typography>
            </Box>
          ) : (
            <AnimatePresence>
              {messages.map(renderMessage)}
              {sending && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 1 }}>
                    <BotIcon />
                  </Avatar>
                  <Paper elevation={2} sx={{ p: 2, bgcolor: 'grey.100' }}>
                    <CircularProgress size={20} />
                    <Typography variant="caption" sx={{ ml: 1 }}>
                      Thinking...
                    </Typography>
                  </Paper>
                </Box>
              )}
            </AnimatePresence>
          )}
          <div ref={messagesEndRef} />
        </Paper>

        {/* Input Area */}
        <Paper elevation={3} sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              placeholder="Ask a question... (e.g., 'What is the difference between go and went?')"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={sending}
            />
            <IconButton
              color="primary"
              onClick={sendMessage}
              disabled={!inputMessage.trim() || sending}
              sx={{
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' },
                '&:disabled': { bgcolor: 'grey.300' },
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Container>

      {/* Rename Dialog */}
      <Dialog open={renameDialogOpen} onClose={() => setRenameDialogOpen(false)}>
        <DialogTitle>Rename Conversation</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="New Title"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') renameConversation();
            }}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRenameDialogOpen(false)}>Cancel</Button>
          <Button onClick={renameConversation} variant="contained" disabled={!newTitle.trim()}>
            Rename
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatTutor;
