import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Chip,
  Grid,
  Avatar,
  Divider,
  CircularProgress,
  Button,
} from '@mui/material';
import { Psychology, Lightbulb, TrendingUp, School } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useChat } from '../../context/ChatContext';

// eslint-disable-next-line react/prop-types
const MemoryInsights = ({ conversationId: _conversationId }) => {
  const { searchMemories, learningContext, loadLearningContext } = useChat();
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadLearningContext();
  }, [loadLearningContext]);

  const loadInsights = async () => {
    setLoading(true);
    if (learningContext?.recent_topics && learningContext.recent_topics.length > 0) {
      const topicQuery = learningContext.recent_topics[0];
      const results = await searchMemories(topicQuery, 3);
      setInsights(results || []);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (learningContext) {
      loadInsights();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [learningContext]);

  if (!learningContext) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress size={24} />
      </Box>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <Card
        sx={{
          bgcolor: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          borderRadius: 2,
        }}
      >
        <CardHeader
          avatar={
            <Avatar sx={{ bgcolor: '#6366f1' }}>
              <Psychology />
            </Avatar>
          }
          title="Learning Insights"
          titleTypographyProps={{ variant: 'subtitle1', fontWeight: 'bold' }}
        />
        <Divider />
        <CardContent>
          {/* Recent Topics */}
          {learningContext.recent_topics && learningContext.recent_topics.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <School sx={{ mr: 1, color: '#6366f1' }} fontSize="small" />
                <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#888' }}>
                  Recent Topics
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {learningContext.recent_topics.map((topic, idx) => (
                  <Chip
                    key={idx}
                    label={topic}
                    size="small"
                    sx={{
                      bgcolor: '#6366f1',
                      color: '#fff',
                      fontSize: '0.8rem',
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Conversation Count */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TrendingUp sx={{ mr: 1, color: '#6366f1' }} fontSize="small" />
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#888' }}>
                Conversation Count
              </Typography>
            </Box>
            <Typography variant="h6" sx={{ color: '#fff', fontWeight: 'bold' }}>
              {learningContext.conversation_count || 0}
            </Typography>
          </Box>

          {/* Related Memories */}
          {insights.length > 0 && (
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Lightbulb sx={{ mr: 1, color: '#6366f1' }} fontSize="small" />
                <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#888' }}>
                  Related Memories
                </Typography>
              </Box>
              <Grid container spacing={1}>
                {insights.map((insight, idx) => (
                  <Grid item xs={12} key={idx}>
                    <Box
                      sx={{
                        p: 1.5,
                        bgcolor: 'rgba(99, 102, 241, 0.1)',
                        borderLeft: '3px solid #6366f1',
                        borderRadius: 1,
                      }}
                    >
                      <Typography variant="caption" sx={{ color: '#ccc' }}>
                        {typeof insight === 'string' ? insight : insight.content || JSON.stringify(insight)}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Refresh Button */}
          <Button
            size="small"
            fullWidth
            onClick={loadInsights}
            disabled={loading}
            sx={{
              mt: 2,
              color: '#6366f1',
              textTransform: 'none',
              '&:hover': { bgcolor: 'rgba(99, 102, 241, 0.1)' },
            }}
          >
            {loading ? 'Loading...' : 'Refresh Insights'}
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default MemoryInsights;
