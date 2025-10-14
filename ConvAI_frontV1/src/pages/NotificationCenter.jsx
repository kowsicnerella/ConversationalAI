import { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Button,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Circle as CircleIcon,
  CheckCircle as CheckCircleIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import API from '../config/api';

const NotificationCenter = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentTab, setCurrentTab] = useState(0); // 0: All, 1: Unread, 2: Read
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [unreadCount, setUnreadCount] = useState(0);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [notificationToDelete, setNotificationToDelete] = useState(null);
  const navigate = useNavigate();

  const ITEMS_PER_PAGE = 10;

  useEffect(() => {
    fetchNotifications();
  }, [currentTab, page]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError('');

      const offset = (page - 1) * ITEMS_PER_PAGE;
      let url = `/notifications/?limit=${ITEMS_PER_PAGE}&offset=${offset}`;

      if (currentTab === 1) {
        url += '&unread_only=true';
      } else if (currentTab === 2) {
        url += '&unread_only=false';
      }

      const response = await API.get(url);
      if (response.data.success) {
        const allNotifications = response.data.notifications || [];
        
        // Filter based on tab
        let filteredNotifications = allNotifications;
        if (currentTab === 1) {
          filteredNotifications = allNotifications.filter(n => !n.is_read);
        } else if (currentTab === 2) {
          filteredNotifications = allNotifications.filter(n => n.is_read);
        }

        setNotifications(filteredNotifications);
        setUnreadCount(response.data.unread_count || 0);
        
        const total = response.data.total || filteredNotifications.length;
        setTotalPages(Math.ceil(total / ITEMS_PER_PAGE));
      }
    } catch (err) {
      setError('Failed to load notifications. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
    setPage(1);
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await API.post(`/notifications/mark-read/${notificationId}`);
      fetchNotifications();
    } catch (err) {
      console.error('Failed to mark as read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      setLoading(true);
      await API.post('/notifications/mark-all-read');
      fetchNotifications();
    } catch (err) {
      setError('Failed to mark all as read. Please try again.');
      console.error(err);
    }
  };

  const handleDeleteClick = (notification) => {
    setNotificationToDelete(notification);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!notificationToDelete) return;

    try {
      await API.delete(`/notifications/${notificationToDelete.id}`);
      setDeleteDialogOpen(false);
      setNotificationToDelete(null);
      fetchNotifications();
    } catch (err) {
      setError('Failed to delete notification. Please try again.');
      console.error(err);
    }
  };

  const handleClearAll = async () => {
    try {
      setLoading(true);
      await API.delete('/notifications/clear');
      fetchNotifications();
    } catch (err) {
      setError('Failed to clear all notifications. Please try again.');
      console.error(err);
    }
  };

  const handleNotificationClick = async (notification) => {
    // Mark as read
    if (!notification.is_read) {
      await handleMarkAsRead(notification.id);
    }

    // Navigate if action URL exists
    if (notification.action_url) {
      navigate(notification.action_url);
    }
  };

  const getNotificationIcon = (type) => {
    const iconName = type?.icon || 'NotificationsActive';
    const iconMap = {
      'NotificationsActive': '🔔',
      'Whatshot': '🔥',
      'EmojiEvents': '🏆',
      'NewReleases': '🆕',
      'Lightbulb': '💡',
      'School': '📚',
      'Flag': '🚩',
    };
    return iconMap[iconName] || '🔔';
  };

  const getPriorityColor = (priority) => {
    const colorMap = {
      'urgent': 'error',
      'high': 'warning',
      'normal': 'info',
      'low': 'default',
    };
    return colorMap[priority] || 'default';
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} minutes ago`;
    if (hours < 24) return `${hours} hours ago`;
    if (days < 7) return `${days} days ago`;
    return date.toLocaleDateString() + ' at ' + date.toLocaleTimeString();
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h4" fontWeight="bold">
          Notifications
        </Typography>
        <IconButton
          color="primary"
          onClick={() => navigate('/settings/notifications')}
        >
          <SettingsIcon />
        </IconButton>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab label="All" />
          <Tab label={`Unread (${unreadCount})`} />
          <Tab label="Read" />
        </Tabs>
      </Box>

      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        {unreadCount > 0 && (
          <Button
            variant="outlined"
            startIcon={<CheckCircleIcon />}
            onClick={handleMarkAllRead}
            disabled={loading}
          >
            Mark All as Read
          </Button>
        )}
        {notifications.length > 0 && (
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleClearAll}
            disabled={loading}
          >
            Clear All
          </Button>
        )}
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : notifications.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No notifications
          </Typography>
          <Typography color="text.disabled">
            {currentTab === 1 ? "You're all caught up!" : "You don't have any notifications yet."}
          </Typography>
        </Box>
      ) : (
        <>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {notifications.map((notification) => (
              <Card
                key={notification.id}
                sx={{
                  bgcolor: notification.is_read ? 'background.paper' : 'action.hover',
                  cursor: notification.action_url ? 'pointer' : 'default',
                  '&:hover': {
                    boxShadow: 3,
                  },
                }}
                onClick={() => handleNotificationClick(notification)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                    <Avatar
                      sx={{
                        bgcolor: getPriorityColor(notification.priority) + '.light',
                      }}
                    >
                      {getNotificationIcon(notification.type)}
                    </Avatar>

                    <Box sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography variant="h6" sx={{ flexGrow: 1 }}>
                          {notification.title}
                        </Typography>
                        {!notification.is_read && (
                          <CircleIcon sx={{ fontSize: 10, color: 'primary.main' }} />
                        )}
                      </Box>

                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {notification.message}
                      </Typography>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography variant="caption" color="text.disabled">
                          {formatTimestamp(notification.created_at)}
                        </Typography>

                        {notification.type && (
                          <Chip
                            label={notification.type.display_name}
                            size="small"
                            variant="outlined"
                          />
                        )}

                        {notification.priority && notification.priority !== 'normal' && (
                          <Chip
                            label={notification.priority.toUpperCase()}
                            size="small"
                            color={getPriorityColor(notification.priority)}
                          />
                        )}
                      </Box>
                    </Box>
                  </Box>
                </CardContent>

                <CardActions sx={{ justifyContent: 'space-between' }}>
                  <Box>
                    {notification.action_text && notification.action_url && (
                      <Button size="small" color="primary">
                        {notification.action_text}
                      </Button>
                    )}
                  </Box>

                  <Box>
                    {!notification.is_read && (
                      <Button
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMarkAsRead(notification.id);
                        }}
                      >
                        Mark as Read
                      </Button>
                    )}
                    <IconButton
                      size="small"
                      color="error"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteClick(notification);
                      }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </CardActions>
              </Card>
            ))}
          </Box>

          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
              />
            </Box>
          )}
        </>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Notification</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this notification? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default NotificationCenter;
