/**
 * LeaderboardPanel - Rankings Display
 * Shows leaderboard with:
 * - Category selector (9 categories)
 * - Time period selector (daily, weekly, monthly, all-time)
 * - Rankings table with rank, user, score, stats
 * - User's rank highlight
 * - Rank change indicators
 * - Pagination support
 * - User avatar display
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Avatar,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Alert,
  CircularProgress,
  IconButton,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as NoChangeIcon,
  EmojiEvents as TrophyIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import gamificationService from '../../services/gamificationService';

// Category config
const categories = [
  { value: 'overall', label: 'Overall', icon: '🏆' },
  { value: 'vocabulary', label: 'Vocabulary', icon: '📚' },
  { value: 'grammar', label: 'Grammar', icon: '✏️' },
  { value: 'reading', label: 'Reading', icon: '📖' },
  { value: 'writing', label: 'Writing', icon: '✍️' },
  { value: 'listening', label: 'Listening', icon: '👂' },
  { value: 'speaking', label: 'Speaking', icon: '🗣️' },
  { value: 'study_time', label: 'Study Time', icon: '⏱️' },
  { value: 'activity_count', label: 'Activities', icon: '🎯' },
  { value: 'streak', label: 'Streak', icon: '🔥' },
];

// Time period config
const timePeriods = [
  { value: 'daily', label: 'Today' },
  { value: 'weekly', label: 'This Week' },
  { value: 'monthly', label: 'This Month' },
  { value: 'all_time', label: 'All Time' },
];

// Medal colors for top 3
const medalColors = {
  1: '#FFD700', // Gold
  2: '#C0C0C0', // Silver
  3: '#CD7F32', // Bronze
};

const LeaderboardPanel = ({ currentUserId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [userRank, setUserRank] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('overall');
  const [selectedTimePeriod, setSelectedTimePeriod] = useState(1); // Index for Tabs
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchLeaderboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategory, selectedTimePeriod]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const timePeriod = timePeriods[selectedTimePeriod].value;
      const data = await gamificationService.getLeaderboard(selectedCategory, timePeriod, 100);
      setLeaderboard(data.leaderboard || []);
      setUserRank(data.user_rank || null);
      setStats(data.stats || null);
    } catch (err) {
      setError(err.message || 'Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchLeaderboard();
    setRefreshing(false);
  };

  const getRankIcon = (rank) => {
    if (rank <= 3) {
      return (
        <TrophyIcon 
          sx={{ 
            color: medalColors[rank],
            fontSize: 28
          }} 
        />
      );
    }
    return <Typography variant="h6">#{rank}</Typography>;
  };

  const getRankChangeIcon = (change) => {
    if (!change || change === 0) {
      return <NoChangeIcon sx={{ color: 'text.secondary', fontSize: 16 }} />;
    }
    if (change > 0) {
      return (
        <Box display="flex" alignItems="center" color="success.main">
          <TrendingUpIcon sx={{ fontSize: 16 }} />
          <Typography variant="caption">+{change}</Typography>
        </Box>
      );
    }
    return (
      <Box display="flex" alignItems="center" color="error.main">
        <TrendingDownIcon sx={{ fontSize: 16 }} />
        <Typography variant="caption">{change}</Typography>
      </Box>
    );
  };

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error" action={
            <Button color="inherit" size="small" onClick={fetchLeaderboard}>
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
        <Typography variant="h4" component="h1">
          Leaderboard
        </Typography>
        <IconButton onClick={handleRefresh} disabled={refreshing}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* User Rank Card */}
      {userRank && (
        <Card sx={{ mb: 3, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <Box display="flex" alignItems="center">
                  <Box mr={2}>
                    {getRankIcon(userRank.rank)}
                  </Box>
                  <Box>
                    <Typography variant="h5" fontWeight="bold">
                      Rank #{userRank.rank}
                    </Typography>
                    <Typography variant="body2">
                      Your Position
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  <Typography variant="h5" fontWeight="bold">
                    {userRank.score}
                  </Typography>
                  <Typography variant="body2">
                    Score
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center">
                  {stats && stats.percentile && (
                    <>
                      <Typography variant="h5" fontWeight="bold">
                        Top {stats.percentile}%
                      </Typography>
                      <Typography variant="body2">
                        Of All Users
                      </Typography>
                    </>
                  )}
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  label="Category"
                >
                  {categories.map((cat) => (
                    <MenuItem key={cat.value} value={cat.value}>
                      {cat.icon} {cat.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <Tabs
                value={selectedTimePeriod}
                onChange={(e, newValue) => setSelectedTimePeriod(newValue)}
                variant="fullWidth"
              >
                {timePeriods.map((period, index) => (
                  <Tab key={period.value} label={period.label} value={index} />
                ))}
              </Tabs>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Leaderboard Table */}
      <Card>
        <CardContent>
          {loading ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell align="center" width="80">Rank</TableCell>
                    <TableCell>User</TableCell>
                    <TableCell align="center">Score</TableCell>
                    <TableCell align="center">Change</TableCell>
                    <TableCell align="center">Stats</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {leaderboard.map((entry) => (
                    <TableRow
                      key={entry.user_id}
                      sx={{
                        bgcolor: entry.user_id === currentUserId ? 'action.selected' : 'inherit',
                        '&:hover': {
                          bgcolor: 'action.hover',
                        },
                      }}
                    >
                      {/* Rank */}
                      <TableCell align="center">
                        <Box display="flex" justifyContent="center" alignItems="center">
                          {getRankIcon(entry.rank)}
                        </Box>
                      </TableCell>

                      {/* User */}
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <Avatar 
                            src={entry.avatar_url}
                            sx={{ mr: 2 }}
                          >
                            {entry.username?.[0]?.toUpperCase()}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {entry.username}
                              {entry.user_id === currentUserId && (
                                <Chip 
                                  label="You"
                                  size="small"
                                  color="primary"
                                  sx={{ ml: 1 }}
                                />
                              )}
                            </Typography>
                            {entry.level && (
                              <Typography variant="caption" color="text.secondary">
                                Level {entry.level}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </TableCell>

                      {/* Score */}
                      <TableCell align="center">
                        <Typography variant="h6" fontWeight="bold">
                          {entry.score?.toLocaleString()}
                        </Typography>
                      </TableCell>

                      {/* Change */}
                      <TableCell align="center">
                        {getRankChangeIcon(entry.rank_change)}
                      </TableCell>

                      {/* Stats */}
                      <TableCell align="center">
                        {entry.stats && (
                          <Box>
                            {entry.stats.activities && (
                              <Typography variant="caption" display="block">
                                🎯 {entry.stats.activities} activities
                              </Typography>
                            )}
                            {entry.stats.streak && (
                              <Typography variant="caption" display="block">
                                🔥 {entry.stats.streak} day streak
                              </Typography>
                            )}
                            {entry.stats.study_time && (
                              <Typography variant="caption" display="block">
                                ⏱️ {Math.round(entry.stats.study_time / 60)}h studied
                              </Typography>
                            )}
                          </Box>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}

                  {leaderboard.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 8 }}>
                        <TrophyIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary">
                          No rankings yet
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Be the first to earn points and claim the top spot!
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Stats Summary */}
          {stats && (
            <Box mt={3} p={2} bgcolor="action.hover" borderRadius={1}>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    Total Players
                  </Typography>
                  <Typography variant="h6">
                    {stats.total_users?.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    Average Score
                  </Typography>
                  <Typography variant="h6">
                    {Math.round(stats.average_score || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    Top Score
                  </Typography>
                  <Typography variant="h6">
                    {stats.top_score?.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption" color="text.secondary">
                    Your Percentile
                  </Typography>
                  <Typography variant="h6" color="primary">
                    Top {stats.percentile}%
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default LeaderboardPanel;
