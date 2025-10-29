/**
 * AchievementNotification Component - Phase 2 Gamification
 * Toast notification system for achievements, badges, and milestones with confetti
 */

import { useState, useEffect } from 'react';
import {
  Snackbar,
  Alert,
  Box,
  Typography,
  IconButton,
  Paper,
  Slide,
  Button,
} from '@mui/material';
import {
  Close as CloseIcon,
  Share as ShareIcon,
  EmojiEvents as TrophyIcon,
  Star as StarIcon,
  LocalFireDepartment as FireIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import Confetti from 'react-confetti';

const AchievementNotification = () => {
  const [achievements, setAchievements] = useState([]);
  const [currentAchievement, setCurrentAchievement] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);
  const [windowSize, setWindowSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    
    // Listen for achievement events
    const handleAchievement = (event) => {
      addAchievement(event.detail);
    };
    
    window.addEventListener('achievement-earned', handleAchievement);
    
    // Polling for new achievements (backend integration)
    const pollInterval = setInterval(checkForNewAchievements, 30000); // Every 30 seconds
    
    return () => {
      window.removeEventListener('achievement-earned', handleAchievement);
      clearInterval(pollInterval);
    };
  }, []);

  useEffect(() => {
    // Display achievements one by one
    if (achievements.length > 0 && !currentAchievement) {
      const nextAchievement = achievements[0];
      setCurrentAchievement(nextAchievement);
      setShowConfetti(nextAchievement.showConfetti !== false);
      
      // Auto-hide after 6 seconds
      setTimeout(() => {
        handleClose();
      }, 6000);
    }
  }, [achievements, currentAchievement]);

  const checkForNewAchievements = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/gamification/achievements/recent', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.achievements && data.achievements.length > 0) {
          data.achievements.forEach(achievement => {
            addAchievement(achievement);
          });
        }
      }
    } catch (error) {
      console.error('Error checking achievements:', error);
    }
  };

  const addAchievement = (achievement) => {
    setAchievements(prev => [...prev, achievement]);
  };

  const handleClose = () => {
    setShowConfetti(false);
    setTimeout(() => {
      setCurrentAchievement(null);
      setAchievements(prev => prev.slice(1));
    }, 300);
  };

  const handleShare = () => {
    if (currentAchievement) {
      const text = `I just earned "${currentAchievement.title}" on the Language Learning Platform! 🎉`;
      if (navigator.share) {
        navigator.share({
          title: 'Achievement Unlocked!',
          text: text,
        });
      } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(text);
        alert('Achievement copied to clipboard!');
      }
    }
  };

  const getAchievementIcon = (type) => {
    switch (type) {
      case 'badge':
        return <TrophyIcon sx={{ fontSize: 60, color: '#FFD700' }} />;
      case 'level':
        return <TrendingUpIcon sx={{ fontSize: 60, color: '#4CAF50' }} />;
      case 'streak':
        return <FireIcon sx={{ fontSize: 60, color: '#FF5722' }} />;
      case 'milestone':
        return <StarIcon sx={{ fontSize: 60, color: '#9C27B0' }} />;
      default:
        return <TrophyIcon sx={{ fontSize: 60, color: '#2196F3' }} />;
    }
  };

  const getAchievementColor = (type) => {
    switch (type) {
      case 'badge':
        return { bg: '#FFF9C4', border: '#FFD700', text: '#F57F17' };
      case 'level':
        return { bg: '#E8F5E9', border: '#4CAF50', text: '#1B5E20' };
      case 'streak':
        return { bg: '#FFEBEE', border: '#FF5722', text: '#B71C1C' };
      case 'milestone':
        return { bg: '#F3E5F5', border: '#9C27B0', text: '#4A148C' };
      default:
        return { bg: '#E3F2FD', border: '#2196F3', text: '#0D47A1' };
    }
  };

  if (!currentAchievement) {
    return null;
  }

  const colors = getAchievementColor(currentAchievement.type);

  return (
    <>
      {/* Confetti */}
      <AnimatePresence>
        {showConfetti && (
          <Confetti
            width={windowSize.width}
            height={windowSize.height}
            recycle={false}
            numberOfPieces={300}
            gravity={0.2}
            colors={[colors.border, '#FFD700', '#FFA500', '#FF69B4', '#00CED1']}
          />
        )}
      </AnimatePresence>

      {/* Notification */}
      <Snackbar
        open={!!currentAchievement}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
        TransitionComponent={Slide}
        sx={{ mt: 8 }}
      >
        <motion.div
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 400, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 200, damping: 25 }}
        >
          <Paper
            elevation={8}
            sx={{
              width: 400,
              overflow: 'hidden',
              position: 'relative',
              background: `linear-gradient(135deg, ${colors.bg} 0%, white 100%)`,
              border: `3px solid ${colors.border}`,
              borderRadius: 2,
            }}
          >
            {/* Header with sparkle animation */}
            <Box
              sx={{
                background: `linear-gradient(135deg, ${colors.border} 0%, ${colors.border}dd 100%)`,
                color: 'white',
                p: 2,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <motion.div
                animate={{
                  rotate: [0, 360],
                  scale: [1, 1.2, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  repeatDelay: 1,
                }}
                style={{
                  position: 'absolute',
                  top: -10,
                  right: -10,
                  fontSize: 60,
                  opacity: 0.2,
                }}
              >
                ✨
              </motion.div>
              
              <Typography variant="h6" fontWeight="bold" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                🎉 Achievement Unlocked!
              </Typography>
              
              <IconButton
                onClick={handleClose}
                sx={{
                  position: 'absolute',
                  right: 8,
                  top: 8,
                  color: 'white',
                }}
                size="small"
              >
                <CloseIcon />
              </IconButton>
            </Box>

            {/* Content */}
            <Box sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                {/* Icon with pulse animation */}
                <motion.div
                  animate={{
                    scale: [1, 1.1, 1],
                  }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    repeatType: 'reverse',
                  }}
                >
                  <Box
                    sx={{
                      width: 80,
                      height: 80,
                      borderRadius: '50%',
                      background: `linear-gradient(135deg, ${colors.border}40 0%, ${colors.border}20 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: `0 4px 20px ${colors.border}40`,
                    }}
                  >
                    {getAchievementIcon(currentAchievement.type)}
                  </Box>
                </motion.div>

                {/* Text */}
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="h6"
                    fontWeight="bold"
                    sx={{ color: colors.text, mb: 0.5 }}
                  >
                    {currentAchievement.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {currentAchievement.description}
                  </Typography>
                  
                  {/* Reward */}
                  {currentAchievement.reward && (
                    <Box
                      sx={{
                        mt: 1,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 0.5,
                        backgroundColor: colors.border + '20',
                        px: 1.5,
                        py: 0.5,
                        borderRadius: 1,
                      }}
                    >
                      <StarIcon sx={{ fontSize: 16, color: colors.border }} />
                      <Typography
                        variant="caption"
                        fontWeight="bold"
                        sx={{ color: colors.text }}
                      >
                        {currentAchievement.reward}
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Box>

              {/* Share Button */}
              <Button
                variant="outlined"
                startIcon={<ShareIcon />}
                onClick={handleShare}
                fullWidth
                sx={{
                  mt: 2,
                  borderColor: colors.border,
                  color: colors.text,
                  '&:hover': {
                    borderColor: colors.border,
                    backgroundColor: colors.bg,
                  },
                }}
              >
                Share Achievement
              </Button>
            </Box>
          </Paper>
        </motion.div>
      </Snackbar>
    </>
  );
};

// Helper function to trigger achievement from anywhere in the app
export const triggerAchievement = (achievement) => {
  const event = new CustomEvent('achievement-earned', { detail: achievement });
  window.dispatchEvent(event);
};

// Example achievement object structure:
// {
//   type: 'badge' | 'level' | 'streak' | 'milestone',
//   title: 'Streak Master!',
//   description: 'You completed activities for 7 consecutive days',
//   reward: '+100 XP',
//   showConfetti: true
// }

export default AchievementNotification;
