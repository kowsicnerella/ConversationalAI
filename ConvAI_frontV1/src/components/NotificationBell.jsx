import { useState, useEffect } from 'react';
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  Circle as CircleIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import API from '../config/api';

const NotificationBell = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotifications();
    // Poll for new notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await API.get('/notifications/?limit=5&offset=0');
      if (response.data.success) {
        setNotifications(response.data.notifications || []);
        setUnreadCount(response.data.unread_count || 0);
      }
    } catch (err) {
      console.error('Failed to fetch notifications:', err);
    }
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = async (notification) => {
    try {
      // Mark as read
      if (!notification.is_read) {
        await API.post(`/notifications/mark-read/${notification.id}`);
        fetchNotifications(); // Refresh
      }

      // Navigate to action URL if exists
      if (notification.action_url) {
        navigate(notification.action_url);
      }

      handleClose();
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      setLoading(true);
      await API.post('/notifications/mark-all-read');
      fetchNotifications();
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewAll = () => {
    navigate('/notifications');
    handleClose();
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
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const open = Boolean(anchorEl);

  return (
    <>
      <IconButton
        color="inherit"
        onClick={handleClick}
        sx={{ ml: 1 }}
      >
        <Badge badgeContent={unreadCount} color="error">
          {unreadCount > 0 ? <NotificationsActiveIcon /> : <NotificationsIcon />}
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: 360,
            maxHeight: 500,
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <Box sx={{ px: 2, py: 1.5, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Notifications</Typography>
          {unreadCount > 0 && (
            <Button
              size="small"
              onClick={handleMarkAllRead}
              disabled={loading}
            >
              Mark all read
            </Button>
          )}
        </Box>
        
        <Divider />

        {notifications.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <NotificationsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
            <Typography color="text.secondary">
              No notifications yet
            </Typography>
          </Box>
        ) : (
          <List sx={{ p: 0 }}>
            {notifications.map((notification, index) => (
              <Box key={notification.id}>
                <ListItem
                  button
                  onClick={() => handleNotificationClick(notification)}
                  sx={{
                    bgcolor: notification.is_read ? 'transparent' : 'action.hover',
                    '&:hover': {
                      bgcolor: 'action.selected',
                    },
                  }}
                >
                  <ListItemAvatar>
                    <Avatar
                      sx={{
                        bgcolor: getPriorityColor(notification.priority) + '.light',
                      }}
                    >
                      {getNotificationIcon(notification.type)}
                    </Avatar>
                  </ListItemAvatar>
                  
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle2" sx={{ flexGrow: 1 }}>
                          {notification.title}
                        </Typography>
                        {!notification.is_read && (
                          <CircleIcon sx={{ fontSize: 8, color: 'primary.main' }} />
                        )}
                      </Box>
                    }
                    secondary={
                      <>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                          }}
                        >
                          {notification.message}
                        </Typography>
                        <Typography variant="caption" color="text.disabled">
                          {formatTimestamp(notification.created_at)}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                {index < notifications.length - 1 && <Divider />}
              </Box>
            ))}
          </List>
        )}

        {notifications.length > 0 && (
          <>
            <Divider />
            <Box sx={{ p: 1 }}>
              <Button
                fullWidth
                size="small"
                onClick={handleViewAll}
              >
                View All Notifications
              </Button>
            </Box>
          </>
        )}
      </Menu>
    </>
  );
};

export default NotificationBell;
