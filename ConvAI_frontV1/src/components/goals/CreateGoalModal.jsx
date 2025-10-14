import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Grid,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  Stack
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  School as SchoolIcon,
  Timer as TimerIcon,
  MenuBook as BookIcon,
  Flag as FlagIcon,
  Add as AddIcon
} from '@mui/icons-material';
import goalsService from '../../services/goalsService';

const CreateGoalModal = ({ open, onClose, onGoalCreated }) => {
  const [mode, setMode] = useState('template'); // 'template' or 'custom'
  const [availableGoals, setAvailableGoals] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Custom goal fields
  const [customTitle, setCustomTitle] = useState('');
  const [customDescription, setCustomDescription] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [targetValue, setTargetValue] = useState('');

  useEffect(() => {
    if (open && mode === 'template') {
      loadAvailableGoals();
    }
  }, [open, mode]);

  const loadAvailableGoals = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await goalsService.getAvailableGoals();
      
      if (response.data.success) {
        setAvailableGoals(response.data.available_goals || []);
      }
    } catch (err) {
      console.error('Error loading available goals:', err);
      setError(err.response?.data?.error || 'Failed to load goal templates');
    } finally {
      setLoading(false);
    }
  };

  const handleModeChange = (event) => {
    setMode(event.target.value);
    setSelectedTemplate(null);
    setError('');
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
  };

  const handleCreate = async () => {
    try {
      setSubmitting(true);
      setError('');

      let goalData;

      if (mode === 'template') {
        if (!selectedTemplate) {
          setError('Please select a goal template');
          return;
        }

        goalData = {
          goal_type_id: selectedTemplate.id,
          target_date: targetDate || undefined,
        };
      } else {
        // Custom goal
        if (!customTitle || !customDescription) {
          setError('Please provide title and description');
          return;
        }

        goalData = {
          is_custom: true,
          title: customTitle,
          description: customDescription,
          criteria: {
            target_value: parseInt(targetValue) || 100,
            metric: 'completion'
          },
          target_date: targetDate || undefined,
        };
      }

      const response = await goalsService.createGoal(goalData);

      if (response.data.success) {
        onGoalCreated();
        handleClose();
      }
    } catch (err) {
      console.error('Error creating goal:', err);
      setError(err.response?.data?.error || 'Failed to create goal');
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setMode('template');
    setSelectedTemplate(null);
    setCustomTitle('');
    setCustomDescription('');
    setTargetDate('');
    setTargetValue('');
    setError('');
    onClose();
  };

  const getGoalIcon = (iconName) => {
    const icons = {
      trophy: TrophyIcon,
      school: SchoolIcon,
      timer: TimerIcon,
      book: BookIcon,
      flag: FlagIcon,
    };
    const Icon = icons[iconName] || TrophyIcon;
    return <Icon />;
  };

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="md" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' }
      }}
    >
      <DialogTitle>
        <Stack direction="row" alignItems="center" spacing={2}>
          <AddIcon color="primary" />
          <Typography variant="h5" fontWeight={700}>
            Create New Goal
          </Typography>
        </Stack>
      </DialogTitle>

      <DialogContent dividers>
        {/* Mode Selection */}
        <FormControl component="fieldset" sx={{ mb: 3 }}>
          <FormLabel component="legend">Goal Type</FormLabel>
          <RadioGroup row value={mode} onChange={handleModeChange}>
            <FormControlLabel 
              value="template" 
              control={<Radio />} 
              label="Choose from Templates" 
            />
            <FormControlLabel 
              value="custom" 
              control={<Radio />} 
              label="Create Custom Goal" 
            />
          </RadioGroup>
        </FormControl>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Template Mode */}
        {mode === 'template' && (
          <Box>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Grid container spacing={2}>
                {availableGoals.map((template) => (
                  <Grid item xs={12} sm={6} key={template.id}>
                    <Card
                      sx={{
                        border: selectedTemplate?.id === template.id ? 2 : 1,
                        borderColor: selectedTemplate?.id === template.id ? 'primary.main' : 'divider',
                        transition: 'all 0.2s',
                      }}
                    >
                      <CardActionArea onClick={() => handleTemplateSelect(template)}>
                        <CardContent>
                          <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 1 }}>
                            <Box sx={{ color: 'primary.main' }}>
                              {getGoalIcon(template.icon)}
                            </Box>
                            <Typography variant="h6" fontWeight={600}>
                              {template.name}
                            </Typography>
                          </Stack>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                            {template.description}
                          </Typography>
                          {template.telugu_description && (
                            <Typography variant="caption" color="text.disabled">
                              {template.telugu_description}
                            </Typography>
                          )}
                          <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                            <Chip 
                              label={template.difficulty || 'Intermediate'} 
                              size="small" 
                              color="primary" 
                              variant="outlined" 
                            />
                            {template.estimated_time && (
                              <Chip 
                                label={template.estimated_time} 
                                size="small" 
                                variant="outlined" 
                              />
                            )}
                          </Stack>
                        </CardContent>
                      </CardActionArea>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        )}

        {/* Custom Mode */}
        {mode === 'custom' && (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Goal Title"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                placeholder="e.g., Master 500 Telugu Words"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={customDescription}
                onChange={(e) => setCustomDescription(e.target.value)}
                placeholder="Describe what you want to achieve..."
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Target Value (optional)"
                value={targetValue}
                onChange={(e) => setTargetValue(e.target.value)}
                placeholder="100"
                helperText="Numeric goal (e.g., 500 for words)"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Target Date (optional)"
                value={targetDate}
                onChange={(e) => setTargetDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                inputProps={{ min: getTodayDate() }}
              />
            </Grid>
          </Grid>
        )}

        {/* Target Date for Template Mode */}
        {mode === 'template' && selectedTemplate && (
          <Box sx={{ mt: 3 }}>
            <TextField
              fullWidth
              type="date"
              label="Target Date (optional)"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              inputProps={{ min: getTodayDate() }}
              helperText="Set a deadline for your goal"
            />
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose} disabled={submitting}>
          Cancel
        </Button>
        <Button
          variant="contained"
          onClick={handleCreate}
          disabled={submitting || (mode === 'template' && !selectedTemplate)}
          startIcon={submitting ? <CircularProgress size={16} /> : <AddIcon />}
        >
          {submitting ? 'Creating...' : 'Create Goal'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

CreateGoalModal.propTypes = {
  open: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onGoalCreated: PropTypes.func.isRequired,
};

export default CreateGoalModal;
