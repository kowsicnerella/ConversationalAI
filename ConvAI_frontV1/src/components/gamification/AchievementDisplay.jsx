/**
 * AchievementDisplay - Achievement Gallery
 * Shows all 52 achievements with:
 * - Category filters (Activity, Streak, Study Time, Skill, Level, Social, Secret)
 * - Rarity filters (Common, Uncommon, Rare, Epic, Legendary)
 * - Locked/unlocked toggle
 * - Achievement cards with icon, title, description
 * - Progress bars for locked achievements
 * - Showcase toggle for unlocked
 * - Secret achievement "???" display
 * - Unlock notification modal
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Alert,
  CircularProgress,
  IconButton,
  ToggleButtonGroup,
  ToggleButton,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  Badge,
  Tooltip,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  Lock as LockIcon,
  LockOpen as UnlockIcon,
  Star as StarIcon,
  Visibility as ShowcaseIcon,
  VisibilityOff as HideIcon,
  Refresh as RefreshIcon,
  HelpOutline as SecretIcon,
} from '@mui/icons-material';
import gamificationService from '../../services/gamificationService';

// Category config
const categories = [
  { value: 'all', label: 'All', icon: '🎯' },
  { value: 'activity', label: 'Activity', icon: '🎯' },
  { value: 'streak', label: 'Streak', icon: '🔥' },
  { value: 'study_time', label: 'Study Time', icon: '⏱️' },
  { value: 'skill', label: 'Skill', icon: '📚' },
  { value: 'level', label: 'Level', icon: '🎓' },
  { value: 'social', label: 'Social', icon: '👥' },
  { value: 'secret', label: 'Secret', icon: '❓' },
];

// Rarity config
const rarityColors = {
  common: '#95a5a6',
  uncommon: '#27ae60',
  rare: '#3498db',
  epic: '#9b59b6',
  legendary: '#f39c12',
  secret: '#e74c3c',
};

const rarityGradients = {
  common: 'linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%)',
  uncommon: 'linear-gradient(135deg, #27ae60 0%, #229954 100%)',
  rare: 'linear-gradient(135deg, #3498db 0%, #2980b9 100%)',
  epic: 'linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%)',
  legendary: 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)',
  secret: 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
};

const AchievementDisplay = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showLocked, setShowLocked] = useState('all');
  const [selectedAchievement, setSelectedAchievement] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [togglingShowcase, setTogglingShowcase] = useState(null);

  useEffect(() => {
    fetchAchievements();
  }, [selectedCategory]);

  const fetchAchievements = async () => {
    try {
      setLoading(true);
      setError(null);
      const category = selectedCategory === 'all' ? null : selectedCategory;
      const data = await gamificationService.getAchievements(category);
      setAchievements(data.achievements || []);
    } catch (err) {
      setError(err.message || 'Failed to load achievements');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAchievements();
    setRefreshing(false);
  };

  const handleToggleShowcase = async (achievementId) => {
    try {
      setTogglingShowcase(achievementId);
      await gamificationService.toggleAchievementShowcase(achievementId);
      await fetchAchievements();
    } catch (err) {
      setError(err.message || 'Failed to toggle showcase');
    } finally {
      setTogglingShowcase(null);
    }
  };

  const filteredAchievements = achievements.filter(achievement => {
    if (showLocked === 'unlocked' && !achievement.is_unlocked) return false;
    if (showLocked === 'locked' && achievement.is_unlocked) return false;
    return true;
  });

  const unlockedCount = achievements.filter(a => a.is_unlocked).length;
  const totalPoints = achievements
    .filter(a => a.is_unlocked)
    .reduce((sum, a) => sum + (a.points || 0), 0);

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error" action={
            <Button color="inherit" size="small" onClick={fetchAchievements}>
              Retry
            </Button>
          }>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Achievements
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {unlockedCount} / {achievements.length} unlocked • {totalPoints} points earned
          </Typography>
        </Box>
        <IconButton onClick={handleRefresh} disabled={refreshing}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Progress Bar */}
      <Box mb={4}>
        <Box display="flex" justifyContent="space-between" mb={1}>
          <Typography variant="body2" fontWeight="bold">
            Overall Progress
          </Typography>
          <Typography variant="body2" color="primary" fontWeight="bold">
            {Math.round((unlockedCount / achievements.length) * 100)}%
          </Typography>
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={(unlockedCount / achievements.length) * 100}
          sx={{ height: 12, borderRadius: 6 }}
        />
      </Box>

      {/* Category Filters */}
      <Box mb={3}>
        <Typography variant="subtitle2" gutterBottom>
          Category
        </Typography>
        <Box display="flex" flexWrap="wrap" gap={1}>
          {categories.map((cat) => (
            <Chip
              key={cat.value}
              label={`${cat.icon} ${cat.label}`}
              onClick={() => setSelectedCategory(cat.value)}
              color={selectedCategory === cat.value ? 'primary' : 'default'}
              variant={selectedCategory === cat.value ? 'filled' : 'outlined'}
            />
          ))}
        </Box>
      </Box>

      {/* Lock Filter */}
      <Box mb={3}>
        <ToggleButtonGroup
          value={showLocked}
          exclusive
          onChange={(e, newValue) => newValue && setShowLocked(newValue)}
          size="small"
        >
          <ToggleButton value="all">
            All ({achievements.length})
          </ToggleButton>
          <ToggleButton value="unlocked">
            Unlocked ({unlockedCount})
          </ToggleButton>
          <ToggleButton value="locked">
            Locked ({achievements.length - unlockedCount})
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Achievements Grid */}
      <Grid container spacing={3}>
        {filteredAchievements.map((achievement) => (
          <Grid item xs={12} sm={6} md={4} key={achievement.id}>
            <Card
              sx={{
                height: '100%',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6,
                },
                border: achievement.is_unlocked ? 2 : 1,
                borderColor: achievement.is_unlocked 
                  ? rarityColors[achievement.rarity] 
                  : 'divider',
                position: 'relative',
                overflow: 'visible',
              }}
              onClick={() => setSelectedAchievement(achievement)}
            >
              {achievement.is_unlocked && achievement.in_showcase && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: -8,
                    right: -8,
                    zIndex: 1,
                  }}
                >
                  <Badge
                    badgeContent={<StarIcon sx={{ fontSize: 16 }} />}
                    color="warning"
                  />
                </Box>
              )}

              <CardContent>
                {/* Icon & Rarity */}
                <Box textAlign="center" mb={2}>
                  <Box
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 80,
                      height: 80,
                      borderRadius: '50%',
                      background: achievement.is_unlocked
                        ? rarityGradients[achievement.rarity]
                        : 'linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%)',
                      color: 'white',
                      fontSize: 40,
                      mb: 1,
                    }}
                  >
                    {achievement.is_unlocked || !achievement.is_secret ? (
                      achievement.icon || <TrophyIcon sx={{ fontSize: 40 }} />
                    ) : (
                      <SecretIcon sx={{ fontSize: 40 }} />
                    )}
                  </Box>
                  <Chip
                    label={achievement.rarity}
                    size="small"
                    sx={{
                      bgcolor: rarityColors[achievement.rarity],
                      color: 'white',
                      fontWeight: 'bold',
                      textTransform: 'uppercase',
                    }}
                  />
                </Box>

                {/* Title & Description */}
                <Typography variant="h6" align="center" gutterBottom>
                  {achievement.is_unlocked || !achievement.is_secret
                    ? achievement.title
                    : '??? Secret Achievement ???'}
                </Typography>
                <Typography 
                  variant="body2" 
                  color="text.secondary" 
                  align="center"
                  sx={{ minHeight: 40, mb: 2 }}
                >
                  {achievement.is_unlocked || !achievement.is_secret
                    ? achievement.description
                    : 'Complete the secret criteria to unlock this achievement!'}
                </Typography>

                {/* Status */}
                {achievement.is_unlocked ? (
                  <Box>
                    <Box display="flex" justifyContent="center" alignItems="center" mb={1}>
                      <UnlockIcon sx={{ fontSize: 16, mr: 0.5, color: 'success.main' }} />
                      <Typography variant="caption" color="success.main" fontWeight="bold">
                        UNLOCKED
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" align="center" mb={1}>
                      +{achievement.points} points
                    </Typography>
                    {achievement.unlocked_at && (
                      <Typography variant="caption" color="text.secondary" align="center" display="block" mb={2}>
                        {new Date(achievement.unlocked_at).toLocaleDateString()}
                      </Typography>
                    )}
                    <Button
                      fullWidth
                      size="small"
                      variant={achievement.in_showcase ? 'contained' : 'outlined'}
                      startIcon={achievement.in_showcase ? <ShowcaseIcon /> : <HideIcon />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleShowcase(achievement.id);
                      }}
                      disabled={togglingShowcase === achievement.id}
                    >
                      {achievement.in_showcase ? 'In Showcase' : 'Add to Showcase'}
                    </Button>
                  </Box>
                ) : (
                  <Box>
                    <Box display="flex" justifyContent="center" alignItems="center" mb={2}>
                      <LockIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                      <Typography variant="caption" color="text.secondary" fontWeight="bold">
                        LOCKED
                      </Typography>
                    </Box>
                    {achievement.progress !== undefined && achievement.progress !== null && (
                      <Box mb={1}>
                        <Box display="flex" justifyContent="space-between" mb={0.5}>
                          <Typography variant="caption">
                            Progress
                          </Typography>
                          <Typography variant="caption" color="primary">
                            {Math.round(achievement.progress)}%
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={achievement.progress}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    )}
                    <Typography variant="body2" color="text.secondary" align="center">
                      {achievement.points} points
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Empty State */}
      {filteredAchievements.length === 0 && (
        <Box textAlign="center" py={8}>
          <TrophyIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No achievements found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try changing your filters
          </Typography>
        </Box>
      )}

      {/* Achievement Detail Dialog */}
      <Dialog 
        open={Boolean(selectedAchievement)} 
        onClose={() => setSelectedAchievement(null)}
        maxWidth="sm"
        fullWidth
      >
        {selectedAchievement && (
          <>
            <DialogTitle>
              <Box textAlign="center">
                <Box
                  sx={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 100,
                    height: 100,
                    borderRadius: '50%',
                    background: selectedAchievement.is_unlocked
                      ? rarityGradients[selectedAchievement.rarity]
                      : 'linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%)',
                    color: 'white',
                    fontSize: 50,
                    mb: 2,
                  }}
                >
                  {selectedAchievement.is_unlocked || !selectedAchievement.is_secret ? (
                    selectedAchievement.icon || <TrophyIcon sx={{ fontSize: 50 }} />
                  ) : (
                    <SecretIcon sx={{ fontSize: 50 }} />
                  )}
                </Box>
                <Typography variant="h5" gutterBottom>
                  {selectedAchievement.is_unlocked || !selectedAchievement.is_secret
                    ? selectedAchievement.title
                    : '??? Secret Achievement ???'}
                </Typography>
                <Chip
                  label={selectedAchievement.rarity}
                  sx={{
                    bgcolor: rarityColors[selectedAchievement.rarity],
                    color: 'white',
                    fontWeight: 'bold',
                    textTransform: 'uppercase',
                  }}
                />
              </Box>
            </DialogTitle>
            <DialogContent>
              <Typography variant="body1" paragraph>
                {selectedAchievement.is_unlocked || !selectedAchievement.is_secret
                  ? selectedAchievement.description
                  : 'This is a secret achievement. Complete the hidden criteria to unlock it!'}
              </Typography>

              {selectedAchievement.is_unlocked ? (
                <Box>
                  <Alert severity="success" icon={<UnlockIcon />} sx={{ mb: 2 }}>
                    Achievement Unlocked! +{selectedAchievement.points} points
                  </Alert>
                  {selectedAchievement.unlocked_at && (
                    <Typography variant="body2" color="text.secondary">
                      Unlocked on {new Date(selectedAchievement.unlocked_at).toLocaleDateString()}
                    </Typography>
                  )}
                  {selectedAchievement.is_repeatable && (
                    <Chip 
                      label="Repeatable Achievement"
                      size="small"
                      color="info"
                      sx={{ mt: 1 }}
                    />
                  )}
                </Box>
              ) : (
                <Box>
                  <Alert severity="info" icon={<LockIcon />}>
                    Complete the requirements to unlock this achievement
                  </Alert>
                  {selectedAchievement.progress !== undefined && (
                    <Box mt={2}>
                      <Typography variant="body2" gutterBottom>
                        Your Progress: {Math.round(selectedAchievement.progress)}%
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={selectedAchievement.progress}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  )}
                </Box>
              )}
            </DialogContent>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default AchievementDisplay;
