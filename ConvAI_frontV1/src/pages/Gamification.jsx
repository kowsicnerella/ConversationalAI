import { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Button,
  Stack,
  Chip,
  Card,
  CardContent,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment';
import StarIcon from '@mui/icons-material/Star';
import GroupIcon from '@mui/icons-material/Group';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import VideogameAssetIcon from '@mui/icons-material/VideogameAsset';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import HomeIcon from '@mui/icons-material/Home';

// Components
import GamificationSummary from '../components/gamification/GamificationSummary';
import DailyChallengeCard from '../components/gamification/DailyChallengeCard';
import StreakTracker from '../components/gamification/StreakTracker';
import AchievementDisplay from '../components/gamification/AchievementDisplay';
import LeaderboardPanel from '../components/gamification/LeaderboardPanel';
import MilestoneProgress from '../components/gamification/MilestoneProgress';
import SocialFeed from '../components/gamification/SocialFeed';

// Services
import gamificationService from '../services/gamificationService';

import PropTypes from 'prop-types';

// Tab Panel Component
function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`gamification-tabpanel-${index}`}
      aria-labelledby={`gamification-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  value: PropTypes.number.isRequired,
  index: PropTypes.number.isRequired,
};

/**
 * Gamification Hub - Phase 9
 * Central hub for all gamification features
 */
function Gamification() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Data States
  const [summary, setSummary] = useState(null);
  const [challenges, setChallenges] = useState([]);
  const [achievements, setAchievements] = useState([]);
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [streak, setStreak] = useState(null);
  const [milestones, setMilestones] = useState([]);
  const [socialFeed, setSocialFeed] = useState([]);

  // Fetch all gamification data
  useEffect(() => {
    const fetchGamificationData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Parallel fetch of all data
        const [summaryRes, challengesRes, achievementsRes, leaderboardRes, streakRes, milestonesRes, feedRes] = await Promise.allSettled([
          gamificationService.getGamificationSummary(),
          gamificationService.getDailyChallenges(),
          gamificationService.getAchievements(),
          gamificationService.getLeaderboard('overall', 'weekly', 50),
          gamificationService.getStreak(),
          gamificationService.getMilestones(),
          gamificationService.getSocialFeed(20),
        ]);

        // Handle responses
        if (summaryRes.status === 'fulfilled') setSummary(summaryRes.value);
        if (challengesRes.status === 'fulfilled') setChallenges(challengesRes.value.challenges || []);
        if (achievementsRes.status === 'fulfilled') setAchievements(achievementsRes.value.achievements || []);
        if (leaderboardRes.status === 'fulfilled') setLeaderboardData(leaderboardRes.value.leaderboard || []);
        if (streakRes.status === 'fulfilled') setStreak(streakRes.value);
        if (milestonesRes.status === 'fulfilled') setMilestones(milestonesRes.value.milestones || []);
        if (feedRes.status === 'fulfilled') setSocialFeed(feedRes.value.feed || []);

        // Check for errors
        const errors = [summaryRes, challengesRes, achievementsRes, leaderboardRes, streakRes, milestonesRes, feedRes]
          .filter(res => res.status === 'rejected');
        
        if (errors.length > 0) {
          console.warn('Some data failed to load:', errors);
        }
      } catch (err) {
        console.error('Error fetching gamification data:', err);
        setError(err.message || 'Failed to load gamification data');
      } finally {
        setLoading(false);
      }
    };

    fetchGamificationData();
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleChallengeComplete = async (challengeId) => {
    try {
      await gamificationService.completeChallenge(challengeId);
      // Refresh data
      const res = await gamificationService.getDailyChallenges();
      setChallenges(res.challenges || []);
    } catch (err) {
      console.error('Error completing challenge:', err);
    }
  };

  if (loading && !summary) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Navigation Buttons */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate(-1)}
          size="small"
        >
          Back
        </Button>
        <Button
          variant="outlined"
          startIcon={<HomeIcon />}
          onClick={() => navigate('/dashboard')}
          size="small"
        >
          Dashboard
        </Button>
      </Box>

      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
          <VideogameAssetIcon sx={{ fontSize: 40, color: '#667eea' }} />
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold' }}>
            Gamification Hub
          </Typography>
        </Stack>
        <Typography variant="body1" color="textSecondary">
          Track your progress, complete challenges, earn achievements, and compete on leaderboards
        </Typography>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Quick Stats Cards */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <LocalFireDepartmentIcon sx={{ fontSize: 32, color: '#ff6b6b' }} />
                  <Box>
                    <Typography color="textSecondary" variant="caption">
                      Current Streak
                    </Typography>
                    <Typography variant="h5">
                      {summary.current_streak || 0} days
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <StarIcon sx={{ fontSize: 32, color: '#ffd93d' }} />
                  <Box>
                    <Typography color="textSecondary" variant="caption">
                      Total Points
                    </Typography>
                    <Typography variant="h5">
                      {summary.total_points || 0}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <EmojiEventsIcon sx={{ fontSize: 32, color: '#95e1d3' }} />
                  <Box>
                    <Typography color="textSecondary" variant="caption">
                      Achievements
                    </Typography>
                    <Typography variant="h5">
                      {summary.unlocked_achievements || 0}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Stack direction="row" alignItems="center" spacing={2}>
                  <TrendingUpIcon sx={{ fontSize: 32, color: '#667eea' }} />
                  <Box>
                    <Typography color="textSecondary" variant="caption">
                      Rank
                    </Typography>
                    <Typography variant="h5">
                      #{summary.leaderboard_rank || 'N/A'}
                    </Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ borderRadius: 2, boxShadow: 2 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="Gamification tabs"
          sx={{
            borderBottom: '1px solid #e0e0e0',
            '& .MuiTab-root': {
              fontSize: '1rem',
              fontWeight: 500,
              color: '#666',
              '&.Mui-selected': {
                color: '#667eea',
                fontWeight: 600,
              },
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#667eea',
              height: 3,
            },
          }}
        >
          <Tab label="Overview" icon={<VideogameAssetIcon />} iconPosition="start" />
          <Tab label="Daily Challenges" icon={<EmojiEventsIcon />} iconPosition="start" />
          <Tab label="Achievements" icon={<StarIcon />} iconPosition="start" />
          <Tab label="Leaderboard" icon={<TrendingUpIcon />} iconPosition="start" />
          <Tab label="Milestones" icon={<TrendingUpIcon />} iconPosition="start" />
          <Tab label="Social" icon={<GroupIcon />} iconPosition="start" />
        </Tabs>

        {/* Tab Contents */}
        <Box sx={{ p: 3 }}>
          {/* Overview Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                  Your Gamification Summary
                </Typography>
                {summary && <GamificationSummary data={summary} />}
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                  🔥 Your Streak
                </Typography>
                {streak && <StreakTracker streak={streak} />}
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                  🎯 Latest Challenge
                </Typography>
                {challenges.length > 0 && (
                  <DailyChallengeCard
                    challenge={challenges[0]}
                    onComplete={() => handleChallengeComplete(challenges[0].id)}
                  />
                )}
              </Grid>
            </Grid>
          </TabPanel>

          {/* Daily Challenges Tab */}
          <TabPanel value={activeTab} index={1}>
            <Box>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Today&apos;s Challenges ({challenges.length})
              </Typography>
              {challenges.length === 0 ? (
                <Alert severity="info">No challenges available today. Check back later!</Alert>
              ) : (
                <Grid container spacing={2}>
                  {challenges.map((challenge) => (
                    <Grid item xs={12} sm={6} md={4} key={challenge.id}>
                      <DailyChallengeCard
                        challenge={challenge}
                        onComplete={() => handleChallengeComplete(challenge.id)}
                      />
                    </Grid>
                  ))}
                </Grid>
              )}
            </Box>
          </TabPanel>

          {/* Achievements Tab */}
          <TabPanel value={activeTab} index={2}>
            <Box>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Achievements ({achievements.length})
                </Typography>
                <Chip label={`${achievements.filter(a => a.unlocked).length} Unlocked`} color="primary" />
              </Stack>
              {achievements.length === 0 ? (
                <Alert severity="info">No achievements available yet.</Alert>
              ) : (
                <AchievementDisplay achievements={achievements} />
              )}
            </Box>
          </TabPanel>

          {/* Leaderboard Tab */}
          <TabPanel value={activeTab} index={3}>
            <Box>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Weekly Leaderboard
              </Typography>
              {leaderboardData.length === 0 ? (
                <Alert severity="info">Leaderboard data not available yet.</Alert>
              ) : (
                <LeaderboardPanel leaderboardData={leaderboardData} />
              )}
            </Box>
          </TabPanel>

          {/* Milestones Tab */}
          <TabPanel value={activeTab} index={4}>
            <Box>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Your Milestones
              </Typography>
              {milestones.length === 0 ? (
                <Alert severity="info">No milestones reached yet. Keep learning!</Alert>
              ) : (
                <MilestoneProgress milestones={milestones} />
              )}
            </Box>
          </TabPanel>

          {/* Social Tab */}
          <TabPanel value={activeTab} index={5}>
            <Box>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Community Feed
              </Typography>
              {socialFeed.length === 0 ? (
                <Alert severity="info">No social activity yet. Share your achievements!</Alert>
              ) : (
                <SocialFeed feed={socialFeed} />
              )}
            </Box>
          </TabPanel>
        </Box>
      </Paper>

      {/* Action Buttons */}
      <Stack direction="row" spacing={2} sx={{ mt: 4, justifyContent: 'center' }}>
        <Button
          variant="contained"
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            px: 4,
            py: 1.5,
          }}
          onClick={() => navigate('/activities')}
        >
          Complete Activities
        </Button>
        <Button
          variant="outlined"
          sx={{ px: 4, py: 1.5 }}
          onClick={() => navigate('/goals')}
        >
          View Goals
        </Button>
      </Stack>
    </Container>
  );
}

export default Gamification;
