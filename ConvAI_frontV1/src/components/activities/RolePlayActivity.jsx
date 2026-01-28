import { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Chip,
  Alert,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Avatar
} from '@mui/material';
import {
  RecordVoiceOver as RolePlayIcon,
  Send as SendIcon,
  Close as CloseIcon,
  CheckCircle as CompleteIcon,
  Person as UserIcon,
  SmartToy as AiIcon,
  EmojiEvents as TrophyIcon,
  TipsAndUpdates as TipIcon,
  Check as CheckIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axiosInstance from '../config/api';
import { API_ENDPOINTS } from '../config/api';
import AIGeneratingLoader from '../common/AIGeneratingLoader';
import AIGeneratedBadge from '../common/AIGeneratedBadge';

const RolePlayActivity = ({ topic, level, onComplete }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [scenarioData, setScenarioData] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [userMessage, setUserMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [showEvaluation, setShowEvaluation] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [error, setError] = useState('');
  const [showGrammarFeedback, setShowGrammarFeedback] = useState(null);
  
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadScenario = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.GENERATE_ROLEPLAY, {
        topic: topic || 'restaurant',
        level: level || 'beginner'
      });

      if (response.data.success) {
        setScenarioData(response.data.scenario_data);
        setSessionId(response.data.session_id);
        
        // Add AI's initial line to conversation
        if (response.data.scenario_data.initial_line) {
          setConversationHistory([{
            role: 'ai',
            content: response.data.scenario_data.initial_line,
            timestamp: new Date().toISOString()
          }]);
        }
      } else {
        setError('Failed to load role-play scenario. Please try again.');
      }
    } catch (err) {
      console.error('Error loading scenario:', err);
      setError(err.response?.data?.message || 'Failed to load scenario.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScenario();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topic, level]);

  useEffect(() => {
    scrollToBottom();
  }, [conversationHistory]);

  const handleSendMessage = async () => {
    if (!userMessage.trim() || sending) return;

    try {
      setSending(true);
      setError('');

      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.CONVERSATION, {
        session_id: sessionId,
        scenario_data: scenarioData,
        conversation_history: conversationHistory,
        user_message: userMessage
      });

      if (response.data.success) {
        setConversationHistory(response.data.conversation_history);
        
        // Show grammar feedback if errors found
        const grammarCorrection = response.data.response_data.grammar_correction;
        if (grammarCorrection?.has_errors) {
          setShowGrammarFeedback(grammarCorrection);
        }

        setUserMessage('');
      } else {
        setError('Failed to get AI response. Please try again.');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.response?.data?.message || 'Failed to send message.');
    } finally {
      setSending(false);
    }
  };

  const handleCompleteScenario = async () => {
    try {
      setSending(true);
      setError('');

      const response = await axiosInstance.post(API_ENDPOINTS.ACTIVITIES.COMPLETE_ROLEPLAY, {
        session_id: sessionId,
        scenario_data: scenarioData,
        conversation_history: conversationHistory
      });

      if (response.data.success) {
        setEvaluation(response.data.evaluation);
        setShowEvaluation(true);
      } else {
        setError('Failed to complete scenario. Please try again.');
      }
    } catch (err) {
      console.error('Error completing scenario:', err);
      setError(err.response?.data?.message || 'Failed to complete scenario.');
    } finally {
      setSending(false);
    }
  };

  const handleFinish = () => {
    if (onComplete) {
      onComplete();
    } else {
      navigate('/activities');
    }
  };

  if (loading) {
    return (
      <AIGeneratingLoader 
        message="AI is creating your role-play scenario..."
        subMessage="Setting up your conversation practice"
      />
    );
  }

  if (!scenarioData) {
    return (
      <Alert severity="error" sx={{ m: 3 }}>
        Failed to load scenario. Please try again.
      </Alert>
    );
  }

  const userMessageCount = conversationHistory.filter(m => m.role === 'user').length;

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', p: 3 }}>
      {/* Scenario Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 3,
            mb: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}
        >
          <Stack direction="row" alignItems="center" spacing={2} mb={2}>
            <RolePlayIcon sx={{ fontSize: 40 }} />
            <Box>
              <Stack direction="row" alignItems="center" spacing={1}>
                <Typography variant="h4" fontWeight="bold">
                  {scenarioData.title}
                </Typography>
                <AIGeneratedBadge size="small" />
              </Stack>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {scenarioData.title_telugu}
              </Typography>
            </Box>
            <Chip label={scenarioData.level} color="secondary" sx={{ ml: 'auto' }} />
          </Stack>

          <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.3)' }} />

          <Stack spacing={1}>
            <Box>
              <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>Setting:</Typography>
              <Typography variant="body1">{scenarioData.setting}</Typography>
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {scenarioData.setting_telugu}
              </Typography>
            </Box>

            <Stack direction="row" spacing={3}>
              <Box>
                <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>Your Role:</Typography>
                <Chip 
                  label={scenarioData.user_role} 
                  size="small" 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}
                />
                <Typography variant="caption" display="block" sx={{ opacity: 0.7 }}>
                  {scenarioData.user_role_telugu}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>AI Role:</Typography>
                <Chip 
                  label={scenarioData.ai_role} 
                  size="small" 
                  sx={{ bgcolor: 'rgba(255,255,255,0.2)' }}
                />
                <Typography variant="caption" display="block" sx={{ opacity: 0.7 }}>
                  {scenarioData.ai_role_telugu}
                </Typography>
              </Box>
            </Stack>

            <Box>
              <Typography variant="subtitle2" sx={{ opacity: 0.8 }}>🎯 Your Goal:</Typography>
              <Typography variant="body1" fontWeight="bold">
                {scenarioData.user_goal}
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {scenarioData.user_goal_telugu}
              </Typography>
            </Box>
          </Stack>
        </Paper>
      </motion.div>

      {/* Chat Interface */}
      <Paper elevation={2} sx={{ mb: 2 }}>
        <Box
          ref={chatContainerRef}
          sx={{
            height: 400,
            overflowY: 'auto',
            p: 2,
            bgcolor: '#f5f5f5'
          }}
        >
          {conversationHistory.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: message.role === 'user' ? 20 : -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                  mb: 2
                }}
              >
                {message.role === 'ai' && (
                  <Avatar sx={{ bgcolor: '#764ba2', mr: 1 }}>
                    <AiIcon />
                  </Avatar>
                )}
                
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    maxWidth: '70%',
                    bgcolor: message.role === 'user' ? '#667eea' : 'white',
                    color: message.role === 'user' ? 'white' : 'text.primary'
                  }}
                >
                  <Typography variant="body1">{message.content}</Typography>
                  <Typography 
                    variant="caption" 
                    sx={{ 
                      opacity: 0.7, 
                      display: 'block', 
                      mt: 0.5 
                    }}
                  >
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </Typography>
                </Paper>

                {message.role === 'user' && (
                  <Avatar sx={{ bgcolor: '#667eea', ml: 1 }}>
                    <UserIcon />
                  </Avatar>
                )}
              </Box>
            </motion.div>
          ))}
          <div ref={messagesEndRef} />
        </Box>

        {/* Message Input */}
        <Box sx={{ p: 2, bgcolor: 'background.paper', borderTop: 1, borderColor: 'divider' }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          <Stack direction="row" spacing={1}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Type your response here... (Press Enter to send)"
              variant="outlined"
              disabled={sending}
            />
            <Button
              variant="contained"
              onClick={handleSendMessage}
              disabled={!userMessage.trim() || sending}
              sx={{
                minWidth: 100,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              }}
              startIcon={sending ? <CircularProgress size={20} /> : <SendIcon />}
            >
              Send
            </Button>
          </Stack>

          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              💬 {userMessageCount} message{userMessageCount !== 1 ? 's' : ''} sent
            </Typography>

            <Button
              variant="outlined"
              color="success"
              onClick={handleCompleteScenario}
              disabled={sending || userMessageCount < 3}
              startIcon={<CompleteIcon />}
            >
              Complete Scenario
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Suggested Responses (shown initially) */}
      {userMessageCount === 0 && scenarioData.suggested_responses && (
        <Paper elevation={2} sx={{ p: 2, bgcolor: '#fffbf0' }}>
          <Stack direction="row" alignItems="center" spacing={1} mb={1}>
            <TipIcon color="warning" />
            <Typography variant="subtitle2" color="warning.main">
              Suggested Responses to Start:
            </Typography>
          </Stack>
          {scenarioData.suggested_responses.map((suggestion, index) => (
            <Button
              key={index}
              variant="outlined"
              size="small"
              sx={{ mr: 1, mb: 1 }}
              onClick={() => setUserMessage(suggestion)}
            >
              {suggestion}
            </Button>
          ))}
        </Paper>
      )}

      {/* Grammar Feedback Dialog */}
      <Dialog
        open={showGrammarFeedback !== null}
        onClose={() => setShowGrammarFeedback(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">Grammar Feedback</Typography>
            <IconButton onClick={() => setShowGrammarFeedback(null)}>
              <CloseIcon />
            </IconButton>
          </Stack>
        </DialogTitle>
        <DialogContent>
          {showGrammarFeedback && (
            <>
              <Paper sx={{ p: 2, mb: 2, bgcolor: '#f0fff4' }}>
                <Typography variant="subtitle2" color="success.main" gutterBottom>
                  ✓ Corrected Version:
                </Typography>
                <Typography>{showGrammarFeedback.corrected_version}</Typography>
              </Paper>

              {showGrammarFeedback.errors && showGrammarFeedback.errors.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    ⚠️ Corrections:
                  </Typography>
                  {showGrammarFeedback.errors.map((error, index) => (
                    <Paper key={index} sx={{ p: 2, mb: 1 }}>
                      <Stack direction="row" spacing={1} alignItems="center" mb={1}>
                        <Typography 
                          variant="body2" 
                          sx={{ textDecoration: 'line-through', color: 'error.main' }}
                        >
                          {error.original}
                        </Typography>
                        <Typography variant="body2">→</Typography>
                        <Typography 
                          variant="body2" 
                          sx={{ color: 'success.main', fontWeight: 'bold' }}
                        >
                          {error.correction}
                        </Typography>
                      </Stack>
                      <Typography variant="body2" color="text.secondary">
                        {error.explanation}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {error.explanation_telugu}
                      </Typography>
                    </Paper>
                  ))}
                </Box>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowGrammarFeedback(null)}>Got it</Button>
        </DialogActions>
      </Dialog>

      {/* Evaluation Dialog */}
      <Dialog
        open={showEvaluation}
        onClose={() => {}}
        maxWidth="md"
        fullWidth
        disableEscapeKeyDown
      >
        <DialogTitle>
          <Typography variant="h5" fontWeight="bold" align="center">
            🎉 Scenario Complete!
          </Typography>
        </DialogTitle>
        <DialogContent>
          {evaluation && (
            <Stack spacing={3}>
              {/* Score Card */}
              <Paper
                sx={{
                  p: 3,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  textAlign: 'center'
                }}
              >
                <Typography variant="h3" fontWeight="bold">
                  {evaluation.overall_score}%
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  Overall Score
                </Typography>
                <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.3)' }} />
                <Stack direction="row" spacing={3} justifyContent="center">
                  <Box>
                    <Typography variant="h5">{evaluation.grammar_score}%</Typography>
                    <Typography variant="caption">Grammar</Typography>
                  </Box>
                  <Box>
                    <Typography variant="h5">{evaluation.fluency_score}%</Typography>
                    <Typography variant="caption">Fluency</Typography>
                  </Box>
                  <Box>
                    <Typography variant="h5">{evaluation.num_turns}</Typography>
                    <Typography variant="caption">Turns</Typography>
                  </Box>
                </Stack>
                <Divider sx={{ my: 2, borderColor: 'rgba(255,255,255,0.3)' }} />
                <Stack direction="row" alignItems="center" justifyContent="center" spacing={1}>
                  <TrophyIcon sx={{ fontSize: 40 }} />
                  <Typography variant="h4" fontWeight="bold">
                    {evaluation.points_earned} Points Earned!
                  </Typography>
                </Stack>
              </Paper>

              {/* Goal Achievement */}
              <Paper sx={{ p: 2, bgcolor: evaluation.goal_achieved ? '#f0fff4' : '#fff3e0' }}>
                <Stack direction="row" alignItems="center" spacing={1}>
                  {evaluation.goal_achieved ? (
                    <CheckIcon color="success" />
                  ) : (
                    <ErrorIcon color="warning" />
                  )}
                  <Typography variant="subtitle1" fontWeight="bold">
                    Goal {evaluation.goal_achieved ? 'Achieved' : 'Partially Achieved'}
                  </Typography>
                </Stack>
                <Typography variant="body2" color="text.secondary">
                  Conversation Quality: {evaluation.conversation_quality}
                </Typography>
              </Paper>

              {/* Strengths */}
              <Box>
                <Typography variant="h6" gutterBottom color="success.main">
                  💪 Strengths
                </Typography>
                <List dense>
                  {evaluation.strengths?.map((strength, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={`• ${strength}`} />
                    </ListItem>
                  ))}
                </List>
              </Box>

              {/* Improvements */}
              <Box>
                <Typography variant="h6" gutterBottom color="primary">
                  📈 Areas to Improve
                </Typography>
                <List dense>
                  {evaluation.improvements?.map((improvement, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={`• ${improvement}`} />
                    </ListItem>
                  ))}
                </List>
              </Box>

              {/* Encouragement */}
              <Paper sx={{ p: 2, bgcolor: '#f0f7ff' }}>
                <Typography variant="body1" gutterBottom>
                  {evaluation.encouragement}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {evaluation.encouragement_telugu}
                </Typography>
              </Paper>

              {/* Vocabulary Used */}
              {evaluation.vocabulary_used && evaluation.vocabulary_used.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    📚 Vocabulary You Used:
                  </Typography>
                  <Box>
                    {evaluation.vocabulary_used.map((word, index) => (
                      <Chip key={index} label={word} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                    ))}
                  </Box>
                </Box>
              )}
            </Stack>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleFinish} variant="contained" size="large" fullWidth>
            Finish
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

RolePlayActivity.propTypes = {
  topic: PropTypes.string,
  level: PropTypes.string,
  onComplete: PropTypes.func
};

export default RolePlayActivity;
