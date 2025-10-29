/**
 * LevelProgressBar Component - Phase 2 Gamification
 * Displays user's current level, XP progress, and level-up animations
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Paper,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Star as StarIcon,
  Whatshot as FireIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import Confetti from 'react-confetti';

const LevelProgressBar = ({ showFull = false }) => {
  const [levelData, setLevelData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showLevelUpAnimation, setShowLevelUpAnimation] = useState(false);
  const [windowSize, setWindowSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    fetchLevelData();
  }, []);

  const fetchLevelData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/gamification/level', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setLevelData(data);
        
        // Check if user just leveled up
        if (data.just_leveled_up) {
          setShowLevelUpAnimation(true);
          setTimeout(() => setShowLevelUpAnimation(false), 5000);
        }
      }
    } catch (error) {
      console.error('Error fetching level:', error);
      // Set mock data for demonstration
      setLevelData(getMockLevelData());
    } finally {
      setLoading(false);
    }
  };

  const getMockLevelData = () => ({
    current_level: 12,
    current_xp: 2450,
    xp_for_next_level: 3000,
    xp_for_current_level: 2000,
    total_xp: 24500,
    level_name: 'Intermediate Scholar',
    next_level_name: 'Advanced Learner',
    xp_rate: '+15 XP/activity avg',
    estimated_time_to_next: '~5 days',
    just_leveled_up: false,
  });

  const calculateProgress = () => {
    if (!levelData) return 0;
    const xpInCurrentLevel = levelData.current_xp - levelData.xp_for_current_level;
    const xpNeededForLevel = levelData.xp_for_next_level - levelData.xp_for_current_level;
    return (xpInCurrentLevel / xpNeededForLevel) * 100;
  };

  const getLevelColor = (level) => {
    if (level >= 20) return '#9c27b0'; // Purple - Master
    if (level >= 15) return '#f44336'; // Red - Expert
    if (level >= 10) return '#ff9800'; // Orange - Advanced
    if (level >= 5) return '#2196f3'; // Blue - Intermediate
    return '#4caf50'; // Green - Beginner
  };

  const getLevelBadge = (level) => {
    if (level >= 20) return '🏆';
    if (level >= 15) return '💎';
    if (level >= 10) return '⭐';
    if (level >= 5) return '📚';
    return '🌱';
  };

  if (loading) {
    return null;
  }

  const progress = calculateProgress();
  const levelColor = getLevelColor(levelData.current_level);
  const xpRemaining = levelData.xp_for_next_level - levelData.current_xp;

  // Compact version (for header/navbar)
  if (!showFull) {
    return (
      <Tooltip
        title={
          <Box sx={{ p: 1 }}>
            <Typography variant="body2" fontWeight="bold">
              {levelData.level_name}
            </Typography>
            <Typography variant="caption">
              {levelData.current_xp} / {levelData.xp_for_next_level} XP
            </Typography>
            <Typography variant="caption" display="block">
              {xpRemaining} XP to Level {levelData.current_level + 1}
            </Typography>
          </Box>
        }
        arrow
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            cursor: 'pointer',
            '&:hover': { opacity: 0.8 },
          }}
        >
          <Chip
            label={`Lv ${levelData.current_level}`}
            size="small"
            sx={{
              backgroundColor: levelColor,
              color: 'white',
              fontWeight: 'bold',
            }}
          />
          <Box sx={{ width: 100 }}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: `${levelColor}30`,
                '& .MuiLinearProgress-bar': {
                  backgroundColor: levelColor,
                  borderRadius: 4,
                },
              }}
            />
          </Box>
        </Box>
      </Tooltip>
    );
  }

  // Full version (for dashboard/profile)
  return (
    <Box>
      {/* Level Up Animation */}
      <AnimatePresence>
        {showLevelUpAnimation && (
          <>
            <Confetti
              width={windowSize.width}
              height={windowSize.height}
              recycle={false}
              numberOfPieces={500}
              gravity={0.3}
            />
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 200 }}
              style={{
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                zIndex: 9999,
              }}
            >
              <Paper
                elevation={24}
                sx={{
                  p: 4,
                  textAlign: 'center',
                  background: `linear-gradient(135deg, ${levelColor} 0%, ${levelColor}dd 100%)`,
                  color: 'white',
                  borderRadius: 4,
                }}
              >
                <Typography variant="h2" fontWeight="bold" gutterBottom>
                  🎉 LEVEL UP! 🎉
                </Typography>
                <Typography variant="h3" fontWeight="bold">
                  Level {levelData.current_level}
                </Typography>
                <Typography variant="h5" sx={{ mt: 2 }}>
                  {levelData.level_name}
                </Typography>
              </Paper>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Level Display */}
      <Paper
        sx={{
          p: 3,
          background: `linear-gradient(135deg, ${levelColor}15 0%, ${levelColor}05 100%)`,
          border: `2px solid ${levelColor}40`,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {/* Level Badge */}
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ repeat: Infinity, duration: 2, repeatDelay: 3 }}
            >
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${levelColor} 0%, ${levelColor}cc 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexDirection: 'column',
                  color: 'white',
                  boxShadow: 4,
                }}
              >
                <Typography variant="h3" fontWeight="bold">
                  {levelData.current_level}
                </Typography>
                <Typography variant="caption" sx={{ fontSize: 20 }}>
                  {getLevelBadge(levelData.current_level)}
                </Typography>
              </Box>
            </motion.div>

            {/* Level Info */}
            <Box>
              <Typography variant="h5" fontWeight="bold" gutterBottom>
                {levelData.level_name}
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <Chip
                  icon={<StarIcon />}
                  label={`${levelData.total_xp.toLocaleString()} Total XP`}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  icon={<TrendingUpIcon />}
                  label={levelData.xp_rate}
                  size="small"
                  color="success"
                  variant="outlined"
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                Next: {levelData.next_level_name} (Level {levelData.current_level + 1})
              </Typography>
            </Box>
          </Box>

          {/* Estimated time */}
          <Chip
            icon={<FireIcon />}
            label={levelData.estimated_time_to_next}
            sx={{
              backgroundColor: levelColor,
              color: 'white',
              fontWeight: 'bold',
            }}
          />
        </Box>

        {/* Progress Bar */}
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" fontWeight="medium">
              Level {levelData.current_level} Progress
            </Typography>
            <Typography variant="body2" fontWeight="bold" sx={{ color: levelColor }}>
              {Math.round(progress)}%
            </Typography>
          </Box>

          {/* Animated Progress Bar */}
          <Box sx={{ position: 'relative' }}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{
                height: 20,
                borderRadius: 10,
                backgroundColor: '#e0e0e0',
                overflow: 'visible',
                '& .MuiLinearProgress-bar': {
                  background: `linear-gradient(90deg, ${levelColor} 0%, ${levelColor}dd 100%)`,
                  borderRadius: 10,
                  boxShadow: `0 0 10px ${levelColor}60`,
                },
              }}
            />
            {/* XP Text on Progress Bar */}
            <Typography
              variant="caption"
              fontWeight="bold"
              sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                color: progress > 50 ? 'white' : 'text.primary',
                zIndex: 1,
              }}
            >
              {levelData.current_xp.toLocaleString()} / {levelData.xp_for_next_level.toLocaleString()} XP
            </Typography>
          </Box>

          {/* XP Remaining */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {xpRemaining.toLocaleString()} XP to next level
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {levelData.xp_for_current_level.toLocaleString()} XP this level
            </Typography>
          </Box>
        </Box>

        {/* Motivational Message */}
        <Box
          sx={{
            mt: 3,
            p: 2,
            backgroundColor: `${levelColor}10`,
            borderRadius: 2,
            borderLeft: `4px solid ${levelColor}`,
          }}
        >
          <Typography variant="body2" fontWeight="medium">
            {progress < 25 && "🚀 You're just getting started! Keep learning to level up!"}
            {progress >= 25 && progress < 50 && "💪 Great progress! You're a quarter of the way there!"}
            {progress >= 50 && progress < 75 && "🔥 Halfway to the next level! Keep up the momentum!"}
            {progress >= 75 && progress < 90 && "⭐ Almost there! Just a little more to reach the next level!"}
            {progress >= 90 && "🎯 So close! One more push to level up!"}
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default LevelProgressBar;
