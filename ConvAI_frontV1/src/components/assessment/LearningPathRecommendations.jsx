/**
 * LearningPathRecommendations Component
 * 
 * Displays personalized learning path recommendations based on assessment results.
 * Shows after assessment completion with options to:
 * - View recommended paths
 * - Create personalized path
 * - Enroll in existing paths
 * 
 * @component
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  School as PathIcon,
  AutoAwesome as PersonalizedIcon,
  TrendingUp as SkillIcon,
  AccessTime as TimeIcon,
  EmojiEvents as PriorityIcon,
  ArrowForward as EnrollIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import {
  getLearningPathRecommendations,
  createPersonalizedPath
} from '../../services/assessmentService';

const LearningPathRecommendations = ({ attemptId, onPathCreated, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPath, setSelectedPath] = useState(null);

  useEffect(() => {
    loadRecommendations();
  }, [attemptId]);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getLearningPathRecommendations(attemptId);
      
      if (response.success) {
        setRecommendations(response.recommendations);
      }
    } catch (err) {
      setError(err.message || 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePersonalizedPath = async () => {
    try {
      setCreating(true);
      setError(null);
      
      const response = await createPersonalizedPath(attemptId);
      
      if (response.success) {
        if (onPathCreated) {
          onPathCreated(response.path_id);
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to create personalized path');
    } finally {
      setCreating(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getDifficultyColor = (level) => {
    switch (level) {
      case 'beginner': return '#4caf50';
      case 'elementary': return '#2196f3';
      case 'intermediate': return '#ff9800';
      case 'advanced': return '#f44336';
      case 'expert': return '#9c27b0';
      default: return '#757575';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, textAlign: 'center' }}>
        <Typography variant="h5" fontWeight="bold" gutterBottom>
          <PathIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
          Recommended Learning Paths
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Based on your assessment results, we recommend these learning paths to improve your skills
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Create Personalized Path Option */}
      <Card sx={{ mb: 3, bgcolor: 'primary.50', border: '2px solid', borderColor: 'primary.main' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <PersonalizedIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              <Box>
                <Typography variant="h6" fontWeight="bold">
                  Create Personalized Learning Path
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  AI-generated path tailored specifically to your assessment results
                </Typography>
              </Box>
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={<PersonalizedIcon />}
              onClick={handleCreatePersonalizedPath}
              disabled={creating}
            >
              {creating ? 'Creating...' : 'Create My Path'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Recommended Paths */}
      {recommendations.length === 0 ? (
        <Alert severity="info">
          No specific path recommendations at this time. Consider creating a personalized path above!
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {recommendations.map((rec, index) => (
            <Grid item xs={12} md={6} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <Card
                  sx={{
                    height: '100%',
                    cursor: 'pointer',
                    '&:hover': {
                      boxShadow: 6,
                      transform: 'translateY(-4px)',
                      transition: 'all 0.3s ease'
                    }
                  }}
                  onClick={() => setSelectedPath(rec)}
                >
                  <CardContent>
                    {/* Priority Badge */}
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Chip
                        icon={<PriorityIcon />}
                        label={`${rec.priority.toUpperCase()} PRIORITY`}
                        color={getPriorityColor(rec.priority)}
                        size="small"
                        sx={{ fontWeight: 'bold' }}
                      />
                      <Chip
                        label={`Match: ${(rec.match_score * 100).toFixed(0)}%`}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    </Box>

                    {/* Title */}
                    <Typography variant="h6" fontWeight="bold" gutterBottom>
                      {rec.path_title}
                    </Typography>

                    {/* Description */}
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        mb: 2,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}
                    >
                      {rec.path_description}
                    </Typography>

                    {/* Metadata */}
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      <Chip
                        label={rec.difficulty_level}
                        size="small"
                        sx={{
                          bgcolor: getDifficultyColor(rec.difficulty_level),
                          color: 'white'
                        }}
                      />
                      <Chip
                        icon={<TimeIcon />}
                        label={`${rec.estimated_duration_hours} hours`}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={rec.category}
                        size="small"
                        variant="outlined"
                      />
                    </Box>

                    {/* Target Skills */}
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                        <SkillIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                        Target Skills:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {rec.target_skills.map((skill, skillIndex) => (
                          <Chip
                            key={skillIndex}
                            label={skill}
                            size="small"
                            color="primary"
                          />
                        ))}
                      </Box>
                    </Box>

                    {/* Reason */}
                    <Alert severity="info" sx={{ mb: 2 }}>
                      <Typography variant="caption">
                        <strong>Why this path:</strong> {rec.reason}
                      </Typography>
                    </Alert>

                    {/* Action Button */}
                    <Button
                      variant="contained"
                      fullWidth
                      endIcon={<EnrollIcon />}
                      onClick={(e) => {
                        e.stopPropagation();
                        // Handle enrollment
                        window.location.href = `/learning-paths/${rec.path_id}`;
                      }}
                    >
                      View & Enroll
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Path Details Dialog */}
      <Dialog
        open={!!selectedPath}
        onClose={() => setSelectedPath(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedPath && (
          <>
            <DialogTitle>
              {selectedPath.path_title}
              <Chip
                label={selectedPath.priority}
                color={getPriorityColor(selectedPath.priority)}
                size="small"
                sx={{ ml: 2 }}
              />
            </DialogTitle>
            <DialogContent>
              <Typography variant="body1" paragraph>
                {selectedPath.path_description}
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Difficulty
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {selectedPath.difficulty_level}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Duration
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {selectedPath.estimated_duration_hours} hours
                  </Typography>
                </Grid>
              </Grid>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Skills You&apos;ll Improve:
                </Typography>
                <List dense>
                  {selectedPath.target_skills.map((skill, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={`• ${skill}`} />
                    </ListItem>
                  ))}
                </List>
              </Box>

              <Alert severity="success">
                <Typography variant="body2">
                  <strong>Match Score:</strong> {(selectedPath.match_score * 100).toFixed(0)}% - 
                  This path is highly recommended for your current skill level
                </Typography>
              </Alert>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedPath(null)}>
                Close
              </Button>
              <Button
                variant="contained"
                onClick={() => {
                  window.location.href = `/learning-paths/${selectedPath.path_id}`;
                }}
              >
                Go to Path
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Close Button */}
      {onClose && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button variant="outlined" onClick={onClose}>
            Close
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default LearningPathRecommendations;
