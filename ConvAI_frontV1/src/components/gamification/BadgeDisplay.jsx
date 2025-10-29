/**
 * BadgeDisplay Component - Phase 2 Gamification
 * Displays user's earned badges with unlock animations and progress tracking
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  LinearProgress,
  Chip,
  Tooltip,
  Zoom,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  Star as StarIcon,
  LocalFireDepartment as FireIcon,
  School as SchoolIcon,
  Speed as SpeedIcon,
  Favorite as HeartIcon,
  Close as CloseIcon,
  Lock as LockIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

const BadgeDisplay = ({ userId }) => {
  const [badges, setBadges] = useState([]);
  const [selectedBadge, setSelectedBadge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUnlockAnimation, setShowUnlockAnimation] = useState(false);

  // Badge icons mapping
  const badgeIcons = {
    streak_master: <FireIcon sx={{ fontSize: 48 }} />,
    quick_learner: <SpeedIcon sx={{ fontSize: 48 }} />,
    dedicated_student: <SchoolIcon sx={{ fontSize: 48 }} />,
    perfect_score: <StarIcon sx={{ fontSize: 48 }} />,
    champion: <TrophyIcon sx={{ fontSize: 48 }} />,
    consistency_king: <HeartIcon sx={{ fontSize: 48 }} />,
  };

  // Badge colors
  const badgeColors = {
    bronze: '#CD7F32',
    silver: '#C0C0C0',
    gold: '#FFD700',
    platinum: '#E5E4E2',
    diamond: '#B9F2FF',
  };

  useEffect(() => {
    fetchBadges();
  }, [userId]);

  const fetchBadges = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/gamification/badges', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setBadges(data.badges || []);
      }
    } catch (error) {
      console.error('Error fetching badges:', error);
      // Set mock data for demonstration
      setBadges(getMockBadges());
    } finally {
      setLoading(false);
    }
  };

  const getMockBadges = () => [
    {
      id: 1,
      name: 'Streak Master',
      description: 'Complete activities for 7 consecutive days',
      icon: 'streak_master',
      tier: 'gold',
      earned: true,
      earned_at: '2025-10-15',
      progress: 100,
      requirement: 7,
    },
    {
      id: 2,
      name: 'Quick Learner',
      description: 'Complete 10 activities in a single day',
      icon: 'quick_learner',
      tier: 'silver',
      earned: true,
      earned_at: '2025-10-12',
      progress: 100,
      requirement: 10,
    },
    {
      id: 3,
      name: 'Dedicated Student',
      description: 'Complete 100 total activities',
      icon: 'dedicated_student',
      tier: 'platinum',
      earned: false,
      progress: 65,
      requirement: 100,
    },
    {
      id: 4,
      name: 'Perfect Score',
      description: 'Achieve 100% on 5 activities',
      icon: 'perfect_score',
      tier: 'diamond',
      earned: false,
      progress: 40,
      requirement: 5,
    },
    {
      id: 5,
      name: 'Champion',
      description: 'Reach the top of the leaderboard',
      icon: 'champion',
      tier: 'gold',
      earned: false,
      progress: 0,
      requirement: 1,
    },
    {
      id: 6,
      name: 'Consistency King',
      description: 'Maintain a 30-day streak',
      icon: 'consistency_king',
      tier: 'diamond',
      earned: false,
      progress: 23,
      requirement: 30,
    },
  ];

  const handleBadgeClick = (badge) => {
    setSelectedBadge(badge);
  };

  const handleCloseDialog = () => {
    setSelectedBadge(null);
  };

  const BadgeCard = ({ badge, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      <Card
        sx={{
          height: '100%',
          cursor: 'pointer',
          position: 'relative',
          overflow: 'visible',
          transition: 'all 0.3s ease',
          background: badge.earned
            ? `linear-gradient(135deg, ${badgeColors[badge.tier]}20 0%, ${badgeColors[badge.tier]}40 100%)`
            : 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)',
          border: badge.earned ? `2px solid ${badgeColors[badge.tier]}` : '2px solid #ccc',
          '&:hover': {
            transform: 'translateY(-8px)',
            boxShadow: badge.earned ? 6 : 2,
          },
        }}
        onClick={() => handleBadgeClick(badge)}
      >
        <CardContent sx={{ textAlign: 'center', p: 3 }}>
          {/* Badge Icon */}
          <Box
            sx={{
              position: 'relative',
              display: 'inline-block',
              mb: 2,
            }}
          >
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.6 }}
            >
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: badge.earned
                    ? `linear-gradient(135deg, ${badgeColors[badge.tier]} 0%, ${badgeColors[badge.tier]}80 100%)`
                    : '#ccc',
                  color: badge.earned ? '#fff' : '#666',
                  boxShadow: badge.earned ? 4 : 1,
                  filter: badge.earned ? 'none' : 'grayscale(100%)',
                }}
              >
                {badge.earned ? badgeIcons[badge.icon] : <LockIcon sx={{ fontSize: 48 }} />}
              </Box>
            </motion.div>

            {/* Tier indicator */}
            {badge.earned && (
              <Chip
                label={badge.tier.toUpperCase()}
                size="small"
                sx={{
                  position: 'absolute',
                  top: -8,
                  right: -8,
                  backgroundColor: badgeColors[badge.tier],
                  color: '#fff',
                  fontWeight: 'bold',
                  fontSize: '0.65rem',
                }}
              />
            )}
          </Box>

          {/* Badge Name */}
          <Typography
            variant="h6"
            gutterBottom
            sx={{
              fontWeight: 'bold',
              color: badge.earned ? 'text.primary' : 'text.disabled',
            }}
          >
            {badge.name}
          </Typography>

          {/* Badge Description */}
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 2, minHeight: 40 }}
          >
            {badge.description}
          </Typography>

          {/* Progress */}
          {!badge.earned && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  Progress
                </Typography>
                <Typography variant="caption" color="text.secondary" fontWeight="bold">
                  {badge.progress}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={badge.progress}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: badgeColors[badge.tier],
                  },
                }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {Math.floor((badge.progress / 100) * badge.requirement)} / {badge.requirement}
              </Typography>
            </Box>
          )}

          {/* Earned date */}
          {badge.earned && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Earned: {new Date(badge.earned_at).toLocaleDateString()}
            </Typography>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          🏆 Your Badges
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Earn badges by completing challenges and reaching milestones
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
          <Chip
            icon={<TrophyIcon />}
            label={`${badges.filter(b => b.earned).length} / ${badges.length} Earned`}
            color="primary"
            variant="filled"
          />
          <Chip
            label={`${Math.round((badges.filter(b => b.earned).length / badges.length) * 100)}% Complete`}
            variant="outlined"
          />
        </Box>
      </Box>

      {/* Badge Grid */}
      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography>Loading badges...</Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {badges.map((badge, index) => (
            <Grid item xs={12} sm={6} md={4} key={badge.id}>
              <BadgeCard badge={badge} index={index} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Badge Detail Dialog */}
      <Dialog
        open={selectedBadge !== null}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
        TransitionComponent={Zoom}
      >
        {selectedBadge && (
          <>
            <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
              <IconButton
                onClick={handleCloseDialog}
                sx={{ position: 'absolute', right: 8, top: 8 }}
              >
                <CloseIcon />
              </IconButton>
            </DialogTitle>
            <DialogContent sx={{ textAlign: 'center', pt: 0 }}>
              {/* Large Badge Icon */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200 }}
              >
                <Box
                  sx={{
                    width: 150,
                    height: 150,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: selectedBadge.earned
                      ? `linear-gradient(135deg, ${badgeColors[selectedBadge.tier]} 0%, ${badgeColors[selectedBadge.tier]}80 100%)`
                      : '#ccc',
                    color: '#fff',
                    margin: '0 auto',
                    mb: 3,
                    boxShadow: 6,
                    filter: selectedBadge.earned ? 'none' : 'grayscale(100%)',
                  }}
                >
                  {selectedBadge.earned ? (
                    <Box sx={{ fontSize: 80 }}>{badgeIcons[selectedBadge.icon]}</Box>
                  ) : (
                    <LockIcon sx={{ fontSize: 80 }} />
                  )}
                </Box>
              </motion.div>

              {/* Badge Info */}
              <Typography variant="h4" gutterBottom fontWeight="bold">
                {selectedBadge.name}
              </Typography>
              <Chip
                label={selectedBadge.tier.toUpperCase()}
                sx={{
                  backgroundColor: badgeColors[selectedBadge.tier],
                  color: '#fff',
                  fontWeight: 'bold',
                  mb: 2,
                }}
              />
              <Typography variant="body1" color="text.secondary" paragraph>
                {selectedBadge.description}
              </Typography>

              {/* Status */}
              {selectedBadge.earned ? (
                <Box
                  sx={{
                    mt: 3,
                    p: 2,
                    backgroundColor: 'success.light',
                    borderRadius: 2,
                  }}
                >
                  <Typography variant="h6" color="success.dark" fontWeight="bold">
                    ✓ Badge Earned!
                  </Typography>
                  <Typography variant="body2" color="success.dark">
                    {new Date(selectedBadge.earned_at).toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Progress to Unlock
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={selectedBadge.progress}
                    sx={{
                      height: 12,
                      borderRadius: 6,
                      mb: 1,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: badgeColors[selectedBadge.tier],
                      },
                    }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {Math.floor((selectedBadge.progress / 100) * selectedBadge.requirement)} /{' '}
                    {selectedBadge.requirement} completed ({selectedBadge.progress}%)
                  </Typography>
                  <Typography variant="body2" color="primary" fontWeight="bold" sx={{ mt: 1 }}>
                    {selectedBadge.requirement -
                      Math.floor((selectedBadge.progress / 100) * selectedBadge.requirement)}{' '}
                    more to go!
                  </Typography>
                </Box>
              )}
            </DialogContent>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default BadgeDisplay;
