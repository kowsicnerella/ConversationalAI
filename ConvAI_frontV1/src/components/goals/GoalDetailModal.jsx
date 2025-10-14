import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Stack,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  Paper
} from '@mui/material';
import {
  Close as CloseIcon,
  CheckCircle as CheckedIcon,
  RadioButtonUnchecked as UncheckedIcon,
  Flag as FlagIcon,
  Event as CalendarIcon,
  TrendingUp as ProgressIcon,
  EmojiEvents as TrophyIcon,
  Delete as DeleteIcon,
  PlayArrow as StartIcon
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import goalsService from '../../services/goalsService';
import MilestoneProgress from './MilestoneProgress';

const GoalDetailModal = ({ open, goal, onClose, onComplete, onAbandon, onUpdate }) => {
  const [goalDetail, setGoalDetail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [completionDialogOpen, setCompletionDialogOpen] = useState(false);

  useEffect(() => {
    if (open && goal) {
      loadGoalDetail();
    }
  }, [open, goal]);

  const loadGoalDetail = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await goalsService.getGoalDetail(goal.id);
      
      if (response.data.success) {
        setGoalDetail(response.data.goal);
      }
    } catch (err) {
      console.error('Error loading goal detail:', err);
      setError(err.response?.data?.error || 'Failed to load goal details');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteGoal = () => {
    setCompletionDialogOpen(true);
  };

  const confirmComplete = async () => {
    if (goalDetail) {
      await onComplete(goalDetail.id);
      setCompletionDialogOpen(false);
    }
  };

  const handleAbandonGoal = async () => {
    if (window.confirm('Are you sure you want to abandon this goal?')) {
      if (goalDetail) {
        await onAbandon(goalDetail.id);
      }
    }
  };

  const handleMilestoneComplete = async (milestoneId) => {
    try {
      await goalsService.completeMilestone(milestoneId);
      await loadGoalDetail();
      onUpdate();
    } catch (err) {
      console.error('Error completing milestone:', err);
      setError('Failed to complete milestone');
    }
  };

  if (!goal) return null;

  const displayGoal = goalDetail || goal;
  const progress = goalsService.calculateProgress(displayGoal);
  const daysRemaining = goalsService.getDaysRemaining(displayGoal);
  const isOverdue = goalsService.isOverdue(displayGoal);
  const statusInfo = goalsService.formatStatus(displayGoal.status);

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box sx={{ flex: 1 }}>
            <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 1 }}>
              <FlagIcon color="primary" />
              <Typography variant="h5" fontWeight={700}>
                {displayGoal.title || displayGoal.name}
              </Typography>
            </Stack>
            <Chip
              label={statusInfo.label}
              color={statusInfo.color}
              size="small"
              icon={<span>{statusInfo.icon}</span>}
              sx={{ fontWeight: 600 }}
            />
          </Box>
          <IconButton onClick={onClose} edge="end">
            <CloseIcon />
          </IconButton>
        </Stack>
      </DialogTitle>

      <DialogContent dividers>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
                {error}
              </Alert>
            )}

            {/* Progress Section */}
            <Paper elevation={0} sx={{ p: 3, bgcolor: 'background.default', mb: 3 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="h6" fontWeight={600}>
                  Overall Progress
                </Typography>
                <Chip
                  label={`${progress}%`}
                  color={progress === 100 ? 'success' : 'primary'}
                  sx={{ fontWeight: 700, fontSize: '1rem' }}
                />
              </Stack>
              <LinearProgress
                variant="determinate"
                value={progress}
                color={progress === 100 ? 'success' : 'primary'}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  mb: 2,
                }}
              />
              <Stack direction="row" spacing={3}>
                {displayGoal.target_date && (
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <CalendarIcon fontSize="small" color={isOverdue ? 'error' : 'action'} />
                    <Typography variant="body2" color={isOverdue ? 'error.main' : 'text.secondary'}>
                      {daysRemaining !== null ? (
                        isOverdue ? (
                          `Overdue by ${Math.abs(daysRemaining)} days`
                        ) : (
                          `${daysRemaining} days left`
                        )
                      ) : (
                        new Date(displayGoal.target_date).toLocaleDateString()
                      )}
                    </Typography>
                  </Stack>
                )}
                {displayGoal.current_value !== undefined && displayGoal.target_value && (
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <ProgressIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      {displayGoal.current_value} / {displayGoal.target_value}
                    </Typography>
                  </Stack>
                )}
              </Stack>
            </Paper>

            {/* Description */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Description
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {displayGoal.description}
              </Typography>
              {displayGoal.telugu_description && (
                <Typography variant="body2" color="text.disabled" sx={{ mt: 1, fontStyle: 'italic' }}>
                  {displayGoal.telugu_description}
                </Typography>
              )}
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Milestones */}
            {displayGoal.milestones && displayGoal.milestones.length > 0 && (
              <Box>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ mb: 2 }}>
                  Milestones ({displayGoal.milestones.filter(m => m.is_completed).length} / {displayGoal.milestones.length})
                </Typography>
                <MilestoneProgress
                  milestones={displayGoal.milestones}
                  onMilestoneComplete={handleMilestoneComplete}
                  disabled={displayGoal.status !== 'active'}
                />
              </Box>
            )}

            {/* Created Date */}
            <Box sx={{ mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="caption" color="text.disabled">
                Created on {new Date(displayGoal.created_at || Date.now()).toLocaleDateString()}
              </Typography>
              {displayGoal.completed_at && (
                <Typography variant="caption" color="text.disabled" sx={{ ml: 2 }}>
                  • Completed on {new Date(displayGoal.completed_at).toLocaleDateString()}
                </Typography>
              )}
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
          <Box>
            {displayGoal.status === 'active' && (
              <Tooltip title="Abandon this goal">
                <Button
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={handleAbandonGoal}
                >
                  Abandon
                </Button>
              </Tooltip>
            )}
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button onClick={onClose}>
              Close
            </Button>
            {displayGoal.status === 'active' && progress === 100 && (
              <Button
                variant="contained"
                color="success"
                startIcon={<TrophyIcon />}
                onClick={handleCompleteGoal}
              >
                Complete Goal
              </Button>
            )}
          </Box>
        </Box>
      </DialogActions>

      {/* Completion Confirmation Dialog */}
      <Dialog open={completionDialogOpen} onClose={() => setCompletionDialogOpen(false)}>
        <DialogTitle>
          <Stack direction="row" alignItems="center" spacing={1}>
            <TrophyIcon color="success" />
            <Typography variant="h6">Complete Goal?</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Typography>
            Congratulations! 🎉 You've achieved all milestones for this goal. 
            Completing it will generate a certificate and mark it as achieved.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompletionDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            color="success"
            onClick={confirmComplete}
            startIcon={<TrophyIcon />}
          >
            Complete & Get Certificate
          </Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

GoalDetailModal.propTypes = {
  open: PropTypes.bool.isRequired,
  goal: PropTypes.object,
  onClose: PropTypes.func.isRequired,
  onComplete: PropTypes.func.isRequired,
  onAbandon: PropTypes.func.isRequired,
  onUpdate: PropTypes.func.isRequired,
};

export default GoalDetailModal;
