import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Tooltip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Star,
  LocalFireDepartment,
  EmojiEvents,
  Schedule,
  AutoStories,
  CheckCircle,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { vocabularyService } from '../../services/vocabularyService';

/**
 * VocabularyStats Component
 * Displays comprehensive vocabulary mastery statistics
 */
const VocabularyStats = ({ compact = false }) => {
  const [stats, setStats] = useState(null);
  const [reinforcementStats, setReinforcementStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const [vocabStats, reinforcement] = await Promise.all([
        vocabularyService.getVocabularyStats(),
        vocabularyService.getReinforcementStats(30),
      ]);
      setStats(vocabStats);
      setReinforcementStats(reinforcement);
    } catch (err) {
      console.error('Error loading stats:', err);
      setError('Failed to load vocabulary statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!stats) {
    return <Alert severity="info">No vocabulary statistics available yet.</Alert>;
  }

  const masteryData = [
    {
      label: 'New',
      count: stats.mastery_breakdown?.new || 0,
      color: '#64B5F6',
      icon: <Star />,
    },
    {
      label: 'Learning',
      count: stats.mastery_breakdown?.learning || 0,
      color: '#FFB74D',
      icon: <AutoStories />,
    },
    {
      label: 'Familiar',
      count: stats.mastery_breakdown?.familiar || 0,
      color: '#81C784',
      icon: <TrendingUp />,
    },
    {
      label: 'Mastered',
      count: stats.mastery_breakdown?.mastered || 0,
      color: '#4CAF50',
      icon: <CheckCircle />,
    },
  ];

  const totalWords = masteryData.reduce((sum, item) => sum + item.count, 0);

  const StatCard = ({ icon, label, value, subtitle, color = 'primary.main', progress }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 48,
                height: 48,
                borderRadius: 2,
                bgcolor: `${color}15`,
                color: color,
                mr: 2,
              }}
            >
              {icon}
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {label}
              </Typography>
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {value}
              </Typography>
            </Box>
          </Box>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
          {progress !== undefined && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  height: 6,
                  borderRadius: 1,
                  bgcolor: `${color}15`,
                  '& .MuiLinearProgress-bar': {
                    bgcolor: color,
                  },
                }}
              />
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  if (compact) {
    return (
      <Grid container spacing={2}>
        <Grid item xs={6} sm={3}>
          <StatCard
            icon={<AutoStories />}
            label="Total Words"
            value={totalWords}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            icon={<CheckCircle />}
            label="Mastered"
            value={stats.mastery_breakdown?.mastered || 0}
            color="success.main"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            icon={<LocalFireDepartment />}
            label="Review Streak"
            value={`${stats.current_streak || 0}d`}
            color="warning.main"
          />
        </Grid>
        <Grid item xs={6} sm={3}>
          <StatCard
            icon={<Schedule />}
            label="Due Today"
            value={stats.words_due_today || 0}
            color="error.main"
          />
        </Grid>
      </Grid>
    );
  }

  return (
    <Box>
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<AutoStories />}
            label="Total Vocabulary"
            value={totalWords}
            subtitle="Words in your library"
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<CheckCircle />}
            label="Mastered Words"
            value={stats.mastery_breakdown?.mastered || 0}
            subtitle={`${((stats.mastery_breakdown?.mastered || 0) / totalWords * 100).toFixed(1)}% mastery rate`}
            color="success.main"
            progress={(stats.mastery_breakdown?.mastered || 0) / totalWords * 100}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<LocalFireDepartment />}
            label="Review Streak"
            value={`${stats.current_streak || 0} days`}
            subtitle={`Best: ${stats.longest_streak || 0} days`}
            color="warning.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<Schedule />}
            label="Due Today"
            value={stats.words_due_today || 0}
            subtitle={`${stats.words_due_this_week || 0} this week`}
            color="error.main"
          />
        </Grid>
      </Grid>

      {/* Mastery Breakdown */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            Mastery Distribution
          </Typography>
          <Grid container spacing={3}>
            {masteryData.map((item) => (
              <Grid item xs={6} sm={3} key={item.label}>
                <Box sx={{ textAlign: 'center' }}>
                  <Box
                    sx={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 64,
                      height: 64,
                      borderRadius: '50%',
                      bgcolor: `${item.color}15`,
                      color: item.color,
                      mb: 1,
                    }}
                  >
                    {item.icon}
                  </Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: item.color }}>
                    {item.count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.label}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {totalWords > 0 ? `${((item.count / totalWords) * 100).toFixed(1)}%` : '0%'}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>

          {/* Visual Progress Bar */}
          <Box sx={{ mt: 4 }}>
            <Box sx={{ display: 'flex', height: 24, borderRadius: 1, overflow: 'hidden' }}>
              {masteryData.map((item) => {
                const percentage = totalWords > 0 ? (item.count / totalWords) * 100 : 0;
                if (percentage === 0) return null;
                return (
                  <Tooltip key={item.label} title={`${item.label}: ${item.count} words`}>
                    <Box
                      sx={{
                        width: `${percentage}%`,
                        bgcolor: item.color,
                        transition: 'width 0.3s ease',
                      }}
                    />
                  </Tooltip>
                );
              })}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Activity Reinforcement Stats */}
      {reinforcementStats && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Activity Reinforcement (Last 30 Days)
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary.main" sx={{ fontWeight: 700 }}>
                    {reinforcementStats.total_exposures || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Exposures
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Words seen in activities
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success.main" sx={{ fontWeight: 700 }}>
                    {reinforcementStats.production_uses || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Production Uses
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Words used correctly
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main" sx={{ fontWeight: 700 }}>
                    {reinforcementStats.activities_with_vocab || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Activities
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    With vocabulary
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main" sx={{ fontWeight: 700 }}>
                    {reinforcementStats.top_reinforced_words?.length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Top Words
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Most practiced
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            {/* Top Reinforced Words */}
            {reinforcementStats.top_reinforced_words?.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                  Most Reinforced Words
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {reinforcementStats.top_reinforced_words.slice(0, 10).map((word, idx) => (
                    <Chip
                      key={idx}
                      label={`${word.word} (${word.total_count})`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Performance Insights */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            Performance Insights
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingUp color="success" />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Average Accuracy
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {stats.average_accuracy ? `${(stats.average_accuracy * 100).toFixed(1)}%` : 'N/A'}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <EmojiEvents color="warning" />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Total Reviews
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    {stats.total_reviews || 0}
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default VocabularyStats;
