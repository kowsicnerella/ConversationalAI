import PropTypes from 'prop-types';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Checkbox,
  Typography,
  Box,
  Chip,
  Tooltip,
  Paper
} from '@mui/material';
import {
  CheckCircle as CheckedIcon,
  RadioButtonUnchecked as UncheckedIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const MilestoneProgress = ({ milestones, onMilestoneComplete, disabled }) => {
  const handleToggle = (milestone) => {
    if (!disabled && !milestone.is_completed && onMilestoneComplete) {
      onMilestoneComplete(milestone.id);
    }
  };

  const sortedMilestones = [...milestones].sort((a, b) => (a.order || 0) - (b.order || 0));

  return (
    <List sx={{ width: '100%' }}>
      {sortedMilestones.map((milestone, index) => (
        <motion.div
          key={milestone.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <Paper
            elevation={0}
            sx={{
              mb: 1,
              border: 1,
              borderColor: milestone.is_completed ? 'success.main' : 'divider',
              bgcolor: milestone.is_completed ? 'success.light' : 'background.paper',
              opacity: milestone.is_completed ? 0.9 : 1,
              transition: 'all 0.3s ease',
            }}
          >
            <ListItem
              button={!disabled && !milestone.is_completed}
              onClick={() => handleToggle(milestone)}
              disabled={disabled}
            >
              <ListItemIcon>
                <Checkbox
                  edge="start"
                  checked={milestone.is_completed}
                  disabled={disabled}
                  icon={<UncheckedIcon />}
                  checkedIcon={<CheckedIcon color="success" />}
                  tabIndex={-1}
                  disableRipple
                />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Typography
                    variant="body1"
                    fontWeight={milestone.is_completed ? 400 : 600}
                    sx={{
                      textDecoration: milestone.is_completed ? 'line-through' : 'none',
                      color: milestone.is_completed ? 'text.secondary' : 'text.primary',
                    }}
                  >
                    {milestone.title}
                  </Typography>
                }
                secondary={
                  <Box sx={{ mt: 0.5 }}>
                    {milestone.description && (
                      <Typography variant="body2" color="text.secondary">
                        {milestone.description}
                      </Typography>
                    )}
                    {milestone.telugu_description && (
                      <Typography variant="caption" color="text.disabled">
                        {milestone.telugu_description}
                      </Typography>
                    )}
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                {milestone.is_completed ? (
                  <Chip
                    label="Completed"
                    color="success"
                    size="small"
                    sx={{ fontWeight: 600 }}
                  />
                ) : milestone.criteria && (
                  <Tooltip title="Milestone criteria">
                    <IconButton edge="end" size="small">
                      <InfoIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                )}
              </ListItemSecondaryAction>
            </ListItem>
          </Paper>
        </motion.div>
      ))}
      
      {sortedMilestones.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.disabled">
            No milestones defined for this goal
          </Typography>
        </Box>
      )}
    </List>
  );
};

MilestoneProgress.propTypes = {
  milestones: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      description: PropTypes.string,
      telugu_description: PropTypes.string,
      is_completed: PropTypes.bool,
      order: PropTypes.number,
      criteria: PropTypes.object,
    })
  ).isRequired,
  onMilestoneComplete: PropTypes.func,
  disabled: PropTypes.bool,
};

MilestoneProgress.defaultProps = {
  disabled: false,
};

export default MilestoneProgress;
