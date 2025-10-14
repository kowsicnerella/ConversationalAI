import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  Tab,
  Tabs,
  Alert,
  CircularProgress,
  Chip,
  Stack,
  Fab,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  EmojiEvents as TrophyIcon,
  Flag as FlagIcon,
  CheckCircle as CompletedIcon,
  PlayArrow as ActiveIcon,
  Pause as PausedIcon,
  Cancel as AbandonedIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import PageTransition from '../components/common/PageTransition';
import GradientText from '../components/common/GradientText';
import GoalCard from '../components/goals/GoalCard';
import CreateGoalModal from '../components/goals/CreateGoalModal';
import GoalDetailModal from '../components/goals/GoalDetailModal';
import CertificateGallery from '../components/goals/CertificateGallery';
import goalsService from '../services/goalsService';

const Goals = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [goals, setGoals] = useState([]);
  const [activeGoals, setActiveGoals] = useState([]);
  const [completedGoals, setCompletedGoals] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);

  useEffect(() => {
    loadGoals();
    loadCertificates();
  }, []);

  const loadGoals = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await goalsService.getMyGoals();
      
      if (response.data.success) {
        setGoals(response.data.goals);
        setActiveGoals(response.data.active_goals);
        setCompletedGoals(response.data.completed_goals);
      }
    } catch (err) {
      console.error('Error loading goals:', err);
      setError(err.response?.data?.error || 'Failed to load goals');
    } finally {
      setLoading(false);
    }
  };

  const loadCertificates = async () => {
    try {
      const response = await goalsService.getCertificates();
      
      if (response.data.success) {
        setCertificates(response.data.certificates || []);
      }
    } catch (err) {
      console.error('Error loading certificates:', err);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleCreateGoal = () => {
    setCreateModalOpen(true);
  };

  const handleGoalCreated = () => {
    setCreateModalOpen(false);
    loadGoals();
  };

  const handleGoalClick = (goal) => {
    setSelectedGoal(goal);
    setDetailModalOpen(true);
  };

  const handleGoalUpdated = () => {
    loadGoals();
    setDetailModalOpen(false);
    setSelectedGoal(null);
  };

  const handleCompleteGoal = async (goalId) => {
    try {
      const response = await goalsService.completeGoal(goalId);
      
      if (response.data.success) {
        await loadGoals();
        await loadCertificates();
        setDetailModalOpen(false);
      }
    } catch (err) {
      console.error('Error completing goal:', err);
      setError(err.response?.data?.error || 'Failed to complete goal');
    }
  };

  const handleAbandonGoal = async (goalId) => {
    try {
      const response = await goalsService.abandonGoal(goalId);
      
      if (response.data.success) {
        await loadGoals();
        setDetailModalOpen(false);
      }
    } catch (err) {
      console.error('Error abandoning goal:', err);
      setError(err.response?.data?.error || 'Failed to abandon goal');
    }
  };

  const getGoalsByStatus = (status) => {
    return goals.filter(goal => goal.status === status);
  };

  const renderGoalsGrid = (goalsToDisplay) => {
    if (goalsToDisplay.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <FlagIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No goals found
          </Typography>
          <Typography variant="body2" color="text.disabled" sx={{ mb: 3 }}>
            {activeTab === 0 ? 'Create your first goal to start your learning journey!' : 'Complete some goals to see them here'}
          </Typography>
          {activeTab === 0 && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreateGoal}
            >
              Create Goal
            </Button>
          )}
        </Box>
      );
    }

    return (
      <Grid container spacing={3}>
        {goalsToDisplay.map((goal) => (
          <Grid item xs={12} md={6} lg={4} key={goal.id}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <GoalCard
                goal={goal}
                onClick={() => handleGoalClick(goal)}
              />
            </motion.div>
          </Grid>
        ))}
      </Grid>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <PageTransition>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <TrophyIcon sx={{ fontSize: 40, color: 'primary.main' }} />
              <GradientText variant="h3" sx={{ fontWeight: 700 }}>
                Your Goals
              </GradientText>
            </Box>
            <Button
              variant="contained"
              size="large"
              startIcon={<AddIcon />}
              onClick={handleCreateGoal}
              sx={{
                background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                boxShadow: '0 3px 5px 2px rgba(102, 126, 234, .3)',
              }}
            >
              New Goal
            </Button>
          </Stack>

          {/* Stats Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6} md={3}>
              <Card>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <ActiveIcon color="primary" />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {activeGoals.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Goals
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <CompletedIcon color="success" />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {completedGoals.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Completed
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <TrophyIcon color="warning" />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {certificates.length}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Certificates
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <FlagIcon color="error" />
                    <Box>
                      <Typography variant="h4" fontWeight={700}>
                        {Math.round(
                          (completedGoals.length / Math.max(goals.length, 1)) * 100
                        )}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Success Rate
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}
        </Box>

        {/* Tabs */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab 
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <span>Active Goals</span>
                  <Chip label={activeGoals.length} size="small" color="primary" />
                </Stack>
              }
            />
            <Tab 
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <span>Completed</span>
                  <Chip label={completedGoals.length} size="small" color="success" />
                </Stack>
              }
            />
            <Tab 
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <span>All Goals</span>
                  <Chip label={goals.length} size="small" />
                </Stack>
              }
            />
            <Tab 
              label={
                <Stack direction="row" spacing={1} alignItems="center">
                  <span>Certificates</span>
                  <Chip label={certificates.length} size="small" color="warning" />
                </Stack>
              }
            />
          </Tabs>
        </Box>

        {/* Tab Content */}
        <Box>
          {activeTab === 0 && renderGoalsGrid(activeGoals)}
          {activeTab === 1 && renderGoalsGrid(completedGoals)}
          {activeTab === 2 && renderGoalsGrid(goals)}
          {activeTab === 3 && (
            <CertificateGallery certificates={certificates} />
          )}
        </Box>

        {/* Modals */}
        <CreateGoalModal
          open={createModalOpen}
          onClose={() => setCreateModalOpen(false)}
          onGoalCreated={handleGoalCreated}
        />

        <GoalDetailModal
          open={detailModalOpen}
          goal={selectedGoal}
          onClose={() => {
            setDetailModalOpen(false);
            setSelectedGoal(null);
          }}
          onComplete={handleCompleteGoal}
          onAbandon={handleAbandonGoal}
          onUpdate={handleGoalUpdated}
        />

        {/* Floating Action Button for Mobile */}
        <Tooltip title="Create New Goal" placement="left">
          <Fab
            color="primary"
            sx={{
              position: 'fixed',
              bottom: 24,
              right: 24,
              display: { xs: 'flex', md: 'none' },
            }}
            onClick={handleCreateGoal}
          >
            <AddIcon />
          </Fab>
        </Tooltip>
      </Container>
    </PageTransition>
  );
};

export default Goals;
