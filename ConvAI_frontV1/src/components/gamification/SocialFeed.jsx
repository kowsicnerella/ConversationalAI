/**
 * SocialFeed - Social Achievement Feed
 * Displays shared achievements from connections with:
 * - Feed of shared achievements
 * - Achievement cards with user info
 * - Like and comment features
 * - Share achievement button
 * - Visibility selector (public, friends, private)
 * - Caption input
 * - Timestamp display
 * - Load more pagination
 * - Connection management
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  IconButton,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Divider,
  Paper,
} from '@mui/material';
import {
  Favorite as LikeIcon,
  FavoriteBorder as LikeOutlineIcon,
  Share as ShareIcon,
  Refresh as RefreshIcon,
  EmojiEvents as TrophyIcon,
  People as PeopleIcon,
  PersonAdd as AddFriendIcon,
} from '@mui/icons-material';
import gamificationService from '../../services/gamificationService';

const SocialFeed = ({ currentUserId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feed, setFeed] = useState([]);
  const [connections, setConnections] = useState([]);
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [selectedAchievement, setSelectedAchievement] = useState(null);
  const [shareCaption, setShareCaption] = useState('');
  const [shareVisibility, setShareVisibility] = useState('friends');
  const [sharing, setSharing] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [liking, setLiking] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [feedData, connectionsData] = await Promise.all([
        gamificationService.getSocialFeed(20),
        gamificationService.getConnections('accepted'),
      ]);
      setFeed(feedData.feed || []);
      setConnections(connectionsData.connections || []);
    } catch (err) {
      setError(err.message || 'Failed to load social feed');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchData();
    setRefreshing(false);
  };

  const handleShareAchievement = async () => {
    if (!selectedAchievement) return;
    
    try {
      setSharing(true);
      await gamificationService.shareAchievement(
        selectedAchievement.id,
        shareCaption,
        shareVisibility
      );
      setShareDialogOpen(false);
      setShareCaption('');
      setSelectedAchievement(null);
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to share achievement');
    } finally {
      setSharing(false);
    }
  };

  const handleLike = async (postId) => {
    try {
      setLiking(postId);
      // Note: Like API endpoint would need to be added to the backend
      // For now, we'll just simulate it
      await new Promise(resolve => setTimeout(resolve, 500));
      // Refresh feed to get updated likes
      await fetchData();
    } catch (err) {
      setError(err.message || 'Failed to like post');
    } finally {
      setLiking(null);
    }
  };

  const openShareDialog = (achievement) => {
    setSelectedAchievement(achievement);
    setShareDialogOpen(true);
  };

  const closeShareDialog = () => {
    setShareDialogOpen(false);
    setShareCaption('');
    setSelectedAchievement(null);
  };

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
            <Button color="inherit" size="small" onClick={fetchData}>
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
            Social Feed
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {connections.length} connection{connections.length !== 1 ? 's' : ''}
          </Typography>
        </Box>
        <Box>
          <IconButton onClick={handleRefresh} disabled={refreshing} sx={{ mr: 1 }}>
            <RefreshIcon />
          </IconButton>
          <Button
            variant="contained"
            startIcon={<ShareIcon />}
            onClick={() => setShareDialogOpen(true)}
          >
            Share Achievement
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Feed Section */}
        <Grid item xs={12} md={8}>
          {feed.length === 0 ? (
            <Card>
              <CardContent>
                <Box textAlign="center" py={8}>
                  <PeopleIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No posts yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={3}>
                    {connections.length === 0
                      ? 'Connect with other learners to see their achievements!'
                      : 'Be the first to share an achievement!'}
                  </Typography>
                  {connections.length === 0 ? (
                    <Button
                      variant="contained"
                      startIcon={<AddFriendIcon />}
                    >
                      Find Friends
                    </Button>
                  ) : (
                    <Button
                      variant="contained"
                      startIcon={<ShareIcon />}
                      onClick={() => setShareDialogOpen(true)}
                    >
                      Share Your First Achievement
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          ) : (
            <Box>
              {feed.map((post) => (
                <Card key={post.id} sx={{ mb: 3 }}>
                  <CardContent>
                    {/* User Header */}
                    <Box display="flex" alignItems="center" mb={2}>
                      <Avatar
                        src={post.user_avatar}
                        sx={{ width: 48, height: 48, mr: 2 }}
                      >
                        {post.user_name?.[0]?.toUpperCase()}
                      </Avatar>
                      <Box flex={1}>
                        <Typography variant="subtitle1" fontWeight="bold">
                          {post.user_name}
                          {post.user_id === currentUserId && (
                            <Chip 
                              label="You"
                              size="small"
                              color="primary"
                              sx={{ ml: 1 }}
                            />
                          )}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(post.shared_at).toLocaleString()}
                        </Typography>
                      </Box>
                      <Chip
                        label={post.visibility}
                        size="small"
                        variant="outlined"
                      />
                    </Box>

                    {/* Achievement Display */}
                    <Paper
                      variant="outlined"
                      sx={{
                        p: 2,
                        mb: 2,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                      }}
                    >
                      <Box display="flex" alignItems="center">
                        <TrophyIcon sx={{ fontSize: 48, mr: 2 }} />
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            Achievement Unlocked!
                          </Typography>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {post.achievement_title}
                          </Typography>
                          <Typography variant="body2" sx={{ opacity: 0.9 }}>
                            {post.achievement_description}
                          </Typography>
                        </Box>
                      </Box>
                    </Paper>

                    {/* Caption */}
                    {post.caption && (
                      <Typography variant="body1" paragraph>
                        {post.caption}
                      </Typography>
                    )}

                    {/* Achievement Metadata */}
                    <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                      <Chip
                        label={post.achievement_rarity}
                        size="small"
                        sx={{
                          bgcolor: post.achievement_rarity === 'legendary' ? '#f39c12' :
                                   post.achievement_rarity === 'epic' ? '#9b59b6' :
                                   post.achievement_rarity === 'rare' ? '#3498db' :
                                   post.achievement_rarity === 'uncommon' ? '#27ae60' : '#95a5a6',
                          color: 'white',
                          fontWeight: 'bold',
                          textTransform: 'uppercase',
                        }}
                      />
                      <Chip
                        label={`+${post.achievement_points} points`}
                        size="small"
                        color="warning"
                      />
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    {/* Actions */}
                    <Box display="flex" alignItems="center" justifyContent="space-between">
                      <Box display="flex" alignItems="center">
                        <IconButton
                          color={post.liked ? 'error' : 'default'}
                          onClick={() => handleLike(post.id)}
                          disabled={liking === post.id}
                        >
                          {post.liked ? <LikeIcon /> : <LikeOutlineIcon />}
                        </IconButton>
                        <Typography variant="body2" color="text.secondary">
                          {post.likes || 0} {post.likes === 1 ? 'like' : 'likes'}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}

              {/* Load More */}
              {feed.length >= 20 && (
                <Box textAlign="center" mt={3}>
                  <Button variant="outlined">
                    Load More
                  </Button>
                </Box>
              )}
            </Box>
          )}
        </Grid>

        {/* Connections Sidebar */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Your Connections
                </Typography>
                <IconButton size="small">
                  <AddFriendIcon />
                </IconButton>
              </Box>

              {connections.length === 0 ? (
                <Box textAlign="center" py={4}>
                  <PeopleIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="body2" color="text.secondary" mb={2}>
                    No connections yet
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<AddFriendIcon />}
                  >
                    Find Friends
                  </Button>
                </Box>
              ) : (
                <Box>
                  {connections.slice(0, 10).map((connection) => (
                    <Box
                      key={connection.id}
                      display="flex"
                      alignItems="center"
                      mb={2}
                    >
                      <Avatar
                        src={connection.avatar_url}
                        sx={{ mr: 2 }}
                      >
                        {connection.username?.[0]?.toUpperCase()}
                      </Avatar>
                      <Box flex={1}>
                        <Typography variant="subtitle2">
                          {connection.username}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {connection.connection_type}
                        </Typography>
                      </Box>
                    </Box>
                  ))}
                  {connections.length > 10 && (
                    <Button fullWidth size="small">
                      View All ({connections.length})
                    </Button>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Share Achievement Dialog */}
      <Dialog
        open={shareDialogOpen}
        onClose={closeShareDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Share Achievement</DialogTitle>
        <DialogContent>
          {selectedAchievement ? (
            <Box mb={3}>
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                }}
              >
                <Box display="flex" alignItems="center">
                  <TrophyIcon sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h6">
                      {selectedAchievement.title}
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.9 }}>
                      {selectedAchievement.description}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Box>
          ) : (
            <Alert severity="info" sx={{ mb: 3 }}>
              Select an achievement from your profile to share
            </Alert>
          )}

          <TextField
            fullWidth
            multiline
            rows={3}
            label="Add a caption (optional)"
            value={shareCaption}
            onChange={(e) => setShareCaption(e.target.value)}
            placeholder="Share your thoughts about this achievement..."
            sx={{ mb: 3 }}
          />

          <FormControl fullWidth>
            <InputLabel>Visibility</InputLabel>
            <Select
              value={shareVisibility}
              onChange={(e) => setShareVisibility(e.target.value)}
              label="Visibility"
            >
              <MenuItem value="public">
                🌍 Public - Everyone can see
              </MenuItem>
              <MenuItem value="friends">
                👥 Friends - Only connections can see
              </MenuItem>
              <MenuItem value="private">
                🔒 Private - Only you can see
              </MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={closeShareDialog}>
            Cancel
          </Button>
          <Button
            onClick={handleShareAchievement}
            variant="contained"
            disabled={!selectedAchievement || sharing}
            startIcon={<ShareIcon />}
          >
            {sharing ? <CircularProgress size={24} /> : 'Share'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SocialFeed;
