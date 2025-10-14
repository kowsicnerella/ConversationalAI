import PropTypes from 'prop-types';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  LinearProgress,
  Chip,
  Stack,
  Box,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Flag as FlagIcon,
  CheckCircle as CompletedIcon,
  PlayArrow as ActiveIcon,
  Pause as PausedIcon,
  Cancel as AbandonedIcon,
  TrendingUp as ProgressIcon,
  Event as CalendarIcon,
  MoreVert as MoreIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import goalsService from '../../services/goalsService';

const GoalCard = ({ goal, onClick }) => {
  const progress = goalsService.calculateProgress(goal);
  const daysRemaining = goalsService.getDaysRemaining(goal);
  const isOverdue = goalsService.isOverdue(goal);
  const statusInfo = goalsService.formatStatus(goal.status);

  const getStatusIcon = () => {
    switch (goal.status) {
      case 'active':
        return <ActiveIcon fontSize="small" />;
      case 'completed':
        return <CompletedIcon fontSize="small" />;
      case 'paused':
        return <PausedIcon fontSize="small" />;
      case 'abandoned':
        return <AbandonedIcon fontSize="small" />;
      default:
        return <FlagIcon fontSize="small" />;
    }
  };

  const getProgressColor = () => {
    if (goal.status === 'completed') return 'success';
    if (isOverdue) return 'error';
    if (progress >= 75) return 'success';
    if (progress >= 50) return 'primary';
    if (progress >= 25) return 'warning';
    return 'error';
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        sx={{
          height: '100%',
          cursor: 'pointer',
          position: 'relative',
          overflow: 'visible',
          background: goal.status === 'completed' 
            ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(129, 199, 132, 0.05) 100%)'
            : 'background.paper',
          border: goal.status === 'active' ? '2px solid' : '1px solid',
          borderColor: goal.status === 'active' ? 'primary.main' : 'divider',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: 6,
            borderColor: 'primary.main',
          },
        }}
        onClick={onClick}
      >
        <CardContent>
          {/* Status Chip */}
          <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
            <Chip
              icon={getStatusIcon()}
              label={statusInfo.label}
              color={statusInfo.color}
              size="small"
              sx={{ fontWeight: 600 }}
            />
            <Tooltip title="More options">
              <IconButton size="small" onClick={(e) => { e.stopPropagation(); }}>
                <MoreIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Stack>

          {/* Goal Title */}
          <Typography variant="h6" fontWeight={700} gutterBottom sx={{ mb: 1 }}>
            {goal.title || goal.name}
          </Typography>

          {/* Goal Description */}
          <Typography 
            variant="body2" 
            color="text.secondary" 
            sx={{ 
              mb: 2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
            }}
          >
            {goal.description}
          </Typography>

          {/* Progress Bar */}
          <Box sx={{ mb: 2 }}>
            <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                Progress
              </Typography>
              <Typography variant="caption" fontWeight={700} color={`${getProgressColor()}.main`}>
                {progress}%
              </Typography>
            </Stack>
            <LinearProgress
              variant="determinate"
              value={progress}
              color={getProgressColor()}
              sx={{
                height: 8,
                borderRadius: 4,
                bgcolor: 'action.hover',
              }}
            />
          </Box>

          {/* Milestones */}
          {goal.milestones && goal.milestones.length > 0 && (
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 1 }}>
              <ProgressIcon fontSize="small" color="action" />
              <Typography variant="caption" color="text.secondary">
                {goal.milestones.filter(m => m.is_completed).length} / {goal.milestones.length} milestones
              </Typography>
            </Stack>
          )}

          {/* Target Date & Days Remaining */}
          {goal.target_date && (
            <Stack direction="row" alignItems="center" spacing={1}>
              <CalendarIcon fontSize="small" color={isOverdue ? 'error' : 'action'} />
              <Typography 
                variant="caption" 
                color={isOverdue ? 'error.main' : 'text.secondary'}
                fontWeight={isOverdue ? 600 : 400}
              >
                {daysRemaining !== null ? (
                  isOverdue ? (
                    `Overdue by ${Math.abs(daysRemaining)} days`
                  ) : (
                    `${daysRemaining} days remaining`
                  )
                ) : (
                  new Date(goal.target_date).toLocaleDateString()
                )}
              </Typography>
            </Stack>
          )}

          {/* Goal Type Badge */}
          {goal.is_custom && (
            <Chip
              label="Custom"
              size="small"
              variant="outlined"
              sx={{ mt: 1, fontSize: '0.7rem' }}
            />
          )}
        </CardContent>

        {/* Completion Badge for Completed Goals */}
        {goal.status === 'completed' && (
          <Box
            sx={{
              position: 'absolute',
              top: -12,
              right: -12,
              bgcolor: 'success.main',
              color: 'white',
              borderRadius: '50%',
              width: 48,
              height: 48,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 3,
              border: '3px solid',
              borderColor: 'background.paper',
            }}
          >
            <CompletedIcon />
          </Box>
        )}
      </Card>
    </motion.div>
  );
};

GoalCard.propTypes = {
  goal: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string,
    name: PropTypes.string,
    description: PropTypes.string,
    status: PropTypes.string.isRequired,
    target_date: PropTypes.string,
    current_value: PropTypes.number,
    target_value: PropTypes.number,
    is_custom: PropTypes.bool,
    milestones: PropTypes.arrayOf(PropTypes.shape({
      is_completed: PropTypes.bool,
    })),
  }).isRequired,
  onClick: PropTypes.func.isRequired,
};

export default GoalCard;
