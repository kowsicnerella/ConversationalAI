import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Stack
} from '@mui/material';
import {
  Quiz as QuizIcon,
  Style as FlashcardIcon,
  Create as WriteIcon,
  RecordVoiceOver as RolePlayIcon,
  EmojiEvents as TrophyIcon,
  PlayArrow as StartIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import QuizActivity from '../../components/activities/QuizActivity';
import FlashcardActivity from '../../components/activities/FlashcardActivity';
import WritingActivity from '../../components/activities/WritingActivity';
import RolePlayActivity from '../../components/activities/RolePlayActivity';
import axiosInstance from '../../config/api';
import { API_ENDPOINTS } from '../../config/api';

const ActivitiesPage = () => {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('beginner');
  const [showActivityDialog, setShowActivityDialog] = useState(false);

  useEffect(() => {
    loadTopics();
  }, []);

  const loadTopics = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get(API_ENDPOINTS.ACTIVITIES.TOPICS);
      if (response.data.success) {
        setTopics(response.data.topics);
      }
    } catch (err) {
      console.error('Error loading topics:', err);
      setError('Failed to load topics');
    } finally {
      setLoading(false);
    }
  };

  const handleStartActivity = (activityType) => {
    setSelectedActivity(activityType);
    setShowActivityDialog(true);
  };

  const handleActivityComplete = (evaluation) => {
    console.log('Activity completed:', evaluation);
    setShowActivityDialog(false);
    setSelectedActivity(null);
    setSelectedTopic('');
    setSelectedLevel('beginner');
  };

  const handleCloseActivity = () => {
    setShowActivityDialog(false);
    setSelectedActivity(null);
  };

  const activityTypes = [
    {
      id: 'quiz',
      title: 'Quiz Challenge',
      title_telugu: 'క్విజ్ ఛాలెంజ్',
      description: 'Test your knowledge with multiple-choice questions',
      description_telugu: 'బహుళ ఎంపిక ప్రశ్నలతో మీ జ్ఞానాన్ని పరీక్షించండి',
      icon: QuizIcon,
      color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      points: '40 points',
      duration: '5-10 min'
    },
    {
      id: 'flashcard',
      title: 'Flashcard Practice',
      title_telugu: 'ఫ్లాష్‌కార్డ్ ప్రాక్టీస్',
      description: 'Learn vocabulary with interactive flashcards',
      description_telugu: 'ఇంటరాక్టివ్ ఫ్లాష్‌కార్డ్‌లతో పదజాలం నేర్చుకోండి',
      icon: FlashcardIcon,
      color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      points: '10 points',
      duration: '5-8 min'
    },
    {
      id: 'writing',
      title: 'Writing Practice',
      title_telugu: 'రాత ప్రాక్టీస్',
      description: 'Practice writing with AI-powered feedback',
      description_telugu: 'AI ఫీడ్‌బ్యాక్‌తో రాత ప్రాక్టీస్ చేయండి',
      icon: WriteIcon,
      color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      points: 'Up to 90 points',
      duration: '10-15 min'
    },
    {
      id: 'roleplay',
      title: 'Role-Play Scenarios',
      title_telugu: 'రోల్-ప్లే దృశ్యాలు',
      description: 'Practice real conversations in realistic situations',
      description_telugu: 'వాస్తవ పరిస్థితులలో నిజమైన సంభాషణలను ప్రాక్టీస్ చేయండి',
      icon: RolePlayIcon,
      color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
      points: '30-60 points',
      duration: '5-15 min'
    }
  ];

  const levels = [
    { value: 'beginner', label: 'Beginner', label_telugu: 'ప్రారంభ' },
    { value: 'intermediate', label: 'Intermediate', label_telugu: 'మధ్యస్థ' },
    { value: 'advanced', label: 'Advanced', label_telugu: 'అధునాతన' }
  ];

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Paper
        elevation={3}
        sx={{
          p: 4,
          mb: 4,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          borderRadius: 3
        }}
      >
        <Typography variant="h3" fontWeight="bold" gutterBottom>
          Learning Activities
        </Typography>
        <Typography variant="h6">
          లెర్నింగ్ యాక్టివిటీస్
        </Typography>
        <Typography variant="body1" mt={2} sx={{ opacity: 0.9 }}>
          Choose an activity to practice and improve your English skills
        </Typography>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Activity Cards */}
      <Grid container spacing={3} mb={4}>
        {activityTypes.map((activity, index) => (
          <Grid item xs={12} md={6} key={activity.id}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card
                elevation={4}
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 3,
                  transition: 'transform 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-8px)'
                  }
                }}
              >
                <Box
                  sx={{
                    background: activity.color,
                    color: 'white',
                    p: 3,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 2
                  }}
                >
                  <activity.icon sx={{ fontSize: 50 }} />
                  <Box flex={1}>
                    <Typography variant="h5" fontWeight="bold">
                      {activity.title}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      {activity.title_telugu}
                    </Typography>
                  </Box>
                </Box>

                <CardContent sx={{ flex: 1, p: 3 }}>
                  <Typography variant="body1" color="text.primary" gutterBottom>
                    {activity.description}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    {activity.description_telugu}
                  </Typography>

                  <Stack direction="row" spacing={1} mt={2}>
                    <Chip
                      icon={<TrophyIcon />}
                      label={activity.points}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                    <Chip
                      label={activity.duration}
                      size="small"
                      color="secondary"
                      variant="outlined"
                    />
                  </Stack>
                </CardContent>

                <CardActions sx={{ p: 3, pt: 0 }}>
                  <Button
                    fullWidth
                    variant="contained"
                    size="large"
                    startIcon={<StartIcon />}
                    onClick={() => handleStartActivity(activity.id)}
                    sx={{
                      background: activity.color,
                      '&:hover': {
                        opacity: 0.9
                      }
                    }}
                  >
                    Start Activity
                  </Button>
                </CardActions>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Topics Section */}
      {topics.length > 0 && (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h5" fontWeight="bold" gutterBottom>
            Available Topics
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Choose from various topics to practice
          </Typography>
          <Grid container spacing={2}>
            {topics.map((topic) => (
              <Grid item xs={6} sm={4} md={3} key={topic.id}>
                <Card
                  variant="outlined"
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      backgroundColor: '#f5f5f5',
                      transform: 'scale(1.05)'
                    }
                  }}
                >
                  <Typography variant="h4" mb={1}>
                    {topic.icon}
                  </Typography>
                  <Typography variant="body1" fontWeight="bold">
                    {topic.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {topic.name_telugu}
                  </Typography>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}

      {/* Activity Selection Dialog */}
      <Dialog
        open={showActivityDialog && !selectedTopic}
        onClose={handleCloseActivity}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, p: 2 }
        }}
      >
        <DialogTitle>
          <Typography variant="h5" fontWeight="bold">
            Configure Activity
          </Typography>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Select Topic</InputLabel>
              <Select
                value={selectedTopic}
                label="Select Topic"
                onChange={(e) => setSelectedTopic(e.target.value)}
              >
                {topics.map((topic) => (
                  <MenuItem key={topic.id} value={topic.id}>
                    {topic.icon} {topic.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Difficulty Level</InputLabel>
              <Select
                value={selectedLevel}
                label="Difficulty Level"
                onChange={(e) => setSelectedLevel(e.target.value)}
              >
                {levels.map((level) => (
                  <MenuItem key={level.value} value={level.value}>
                    {level.label} ({level.label_telugu})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Button
              fullWidth
              variant="contained"
              size="large"
              onClick={() => {
                // This will trigger rendering the activity component
              }}
              disabled={!selectedTopic}
            >
              Start Activity
            </Button>
          </Stack>
        </DialogContent>
      </Dialog>

      {/* Activity Full Screen Dialog */}
      <Dialog
        open={showActivityDialog && selectedTopic}
        onClose={handleCloseActivity}
        maxWidth="md"
        fullWidth
        fullScreen
        PaperProps={{
          sx: { backgroundColor: '#f5f5f5' }
        }}
      >
        <Box sx={{ minHeight: '100vh', py: 2 }}>
          {selectedActivity === 'quiz' && (
            <QuizActivity
              topic={selectedTopic}
              level={selectedLevel}
              onComplete={handleActivityComplete}
            />
          )}
          {selectedActivity === 'flashcard' && (
            <FlashcardActivity
              topic={selectedTopic}
              level={selectedLevel}
              onComplete={handleActivityComplete}
            />
          )}
          {selectedActivity === 'writing' && (
            <WritingActivity
              topic={selectedTopic}
              level={selectedLevel}
              onComplete={handleActivityComplete}
            />
          )}
          {selectedActivity === 'roleplay' && (
            <RolePlayActivity
              topic={selectedTopic}
              level={selectedLevel}
              onComplete={handleActivityComplete}
            />
          )}
        </Box>
      </Dialog>
    </Container>
  );
};

export default ActivitiesPage;
