import { useState, useEffect } from "react";
import {
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Typography,
  Box,
  Divider,
  Button,
} from "@mui/material";
import {
  Notifications as NotificationsIcon,
  Close,
  EmojiEvents,
  School,
  Psychology,
  Star,
  AccessTime,
  MarkEmailRead,
  Clear,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { useTheme } from "@mui/material/styles";
import { toast } from "react-hot-toast";

// Mock notification data
const mockNotifications = [
  {
    id: 1,
    type: "achievement",
    title: "Achievement Unlocked!",
    message: "You completed 7-day learning streak!",
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    read: false,
    icon: EmojiEvents,
    color: "#f59e0b",
  },
  {
    id: 2,
    type: "lesson",
    title: "New Lesson Available",
    message: "Advanced Telugu Grammar is now available",
    timestamp: new Date(Date.now() - 30 * 60 * 1000),
    read: false,
    icon: School,
    color: "#4f46e5",
  },
  {
    id: 3,
    type: "ai_insight",
    title: "Learning Insight",
    message:
      "You learn best between 9-11 AM. Schedule more sessions during this time!",
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    read: true,
    icon: Psychology,
    color: "#8b5cf6",
  },
  {
    id: 4,
    type: "reminder",
    title: "Practice Reminder",
    message: "Don't forget your daily practice session!",
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
    read: true,
    icon: AccessTime,
    color: "#06b6d4",
  },
];

const NotificationSystem = () => {
  const [notifications, setNotifications] = useState(mockNotifications);
  const [anchorEl, setAnchorEl] = useState(null);
  const theme = useTheme();
  const open = Boolean(anchorEl);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const markAsRead = (id) => {
    setNotifications((prev) =>
      prev.map((notification) =>
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) =>
      prev.map((notification) => ({ ...notification, read: true }))
    );
  };

  const removeNotification = (id) => {
    setNotifications((prev) =>
      prev.filter((notification) => notification.id !== id)
    );
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.95) {
        const newNotification = {
          id: Date.now(),
          type: "achievement",
          title: "Great Progress!",
          message: "You answered 10 questions correctly in a row!",
          timestamp: new Date(),
          read: false,
          icon: Star,
          color: "#8b5cf6",
        };

        setNotifications((prev) => {
          const IconComponent = newNotification.icon;

          toast.custom(
            (t) => (
              <motion.div
                initial={{ opacity: 0, y: -50, scale: 0.9 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -50, scale: 0.9 }}
                style={{
                  maxWidth: "28rem",
                  width: "100%",
                  background:
                    theme.palette.mode === "dark"
                      ? "rgba(30, 41, 59, 0.9)"
                      : "rgba(255, 255, 255, 0.9)",
                  boxShadow:
                    "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                  borderRadius: "16px",
                  pointerEvents: "auto",
                  display: "flex",
                  backdropFilter: "blur(20px)",
                  border: `1px solid ${newNotification.color}40`,
                }}
              >
                <Box
                  sx={{
                    display: "flex",
                    p: 2,
                    alignItems: "center",
                    width: "100%",
                  }}
                >
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 2,
                      background: `${newNotification.color}20`,
                      color: newNotification.color,
                      mr: 2,
                    }}
                  >
                    <IconComponent sx={{ fontSize: 24 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography
                      variant="subtitle2"
                      sx={{ fontWeight: 600, mb: 0.5 }}
                    >
                      {newNotification.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {newNotification.message}
                    </Typography>
                  </Box>
                  <IconButton
                    size="small"
                    onClick={() => toast.dismiss(t.id)}
                    sx={{ ml: 1 }}
                  >
                    <Close sx={{ fontSize: 18 }} />
                  </IconButton>
                </Box>
              </motion.div>
            ),
            {
              duration: 5000,
              position: "top-right",
            }
          );

          return [newNotification, ...prev];
        });
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [theme.palette.mode]);

  return (
    <>
      <IconButton
        onClick={handleClick}
        sx={{
          position: "relative",
          color: theme.palette.text.primary,
          "&:hover": {
            background: `${theme.palette.primary.main}15`,
          },
        }}
      >
        <Badge
          badgeContent={unreadCount}
          color="error"
          sx={{
            "& .MuiBadge-badge": {
              background: "linear-gradient(135deg, #ff6b6b, #ee5a24)",
              fontWeight: 600,
              fontSize: "0.75rem",
            },
          }}
        >
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: {
            width: {
              xs: "90vw",
              sm: "400px",
              md: "450px",
            },
            maxWidth: "450px",
            maxHeight: "500px",
            background:
              theme.palette.mode === "dark"
                ? "rgba(30, 41, 59, 0.95)"
                : "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(20px)",
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: "16px",
            boxShadow:
              "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
            mt: 1,
            "& .MuiList-root": {
              padding: 0,
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <Box
          sx={{
            p: 2,
            borderBottom: `1px solid ${theme.palette.divider}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            background:
              theme.palette.mode === "dark"
                ? "rgba(55, 65, 81, 0.5)"
                : "rgba(248, 250, 252, 0.8)",
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Notifications
          </Typography>
          {unreadCount > 0 && (
            <Button
              size="small"
              onClick={markAllAsRead}
              sx={{
                textTransform: "none",
                fontSize: "0.8rem",
                color: theme.palette.primary.main,
                "&:hover": {
                  background: `${theme.palette.primary.main}10`,
                },
              }}
            >
              Mark all read
            </Button>
          )}
        </Box>

        <Box sx={{ maxHeight: "350px", overflowY: "auto" }}>
          {notifications.length === 0 ? (
            <Box
              sx={{
                p: 4,
                textAlign: "center",
                color: theme.palette.text.secondary,
              }}
            >
              <NotificationsIcon sx={{ fontSize: 48, mb: 2, opacity: 0.3 }} />
              <Typography variant="body2">No notifications yet</Typography>
            </Box>
          ) : (
            notifications.map((notification, index) => {
              const IconComponent = notification.icon;
              return (
                <motion.div
                  key={notification.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <MenuItem
                    onClick={() => markAsRead(notification.id)}
                    sx={{
                      p: 0,
                      "&:hover": {
                        background: `${theme.palette.primary.main}08`,
                      },
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        p: 2,
                        width: "100%",
                        alignItems: "flex-start",
                        position: "relative",
                        background: notification.read
                          ? "transparent"
                          : `${notification.color}08`,
                      }}
                    >
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: 2,
                          background: `${notification.color}20`,
                          color: notification.color,
                          mr: 2,
                          flexShrink: 0,
                        }}
                      >
                        <IconComponent sx={{ fontSize: 20 }} />
                      </Box>

                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                          variant="subtitle2"
                          sx={{
                            fontWeight: notification.read ? 400 : 600,
                            mb: 0.5,
                            color: notification.read
                              ? theme.palette.text.secondary
                              : theme.palette.text.primary,
                          }}
                        >
                          {notification.title}
                        </Typography>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            mb: 1,
                            display: "-webkit-box",
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: "vertical",
                            overflow: "hidden",
                          }}
                        >
                          {notification.message}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ fontSize: "0.75rem" }}
                        >
                          {getTimeAgo(notification.timestamp)}
                        </Typography>
                      </Box>

                      {!notification.read && (
                        <Box
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: "50%",
                            background: notification.color,
                            position: "absolute",
                            top: 16,
                            right: 8,
                          }}
                        />
                      )}

                      <IconButton
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeNotification(notification.id);
                        }}
                        sx={{
                          position: "absolute",
                          top: 8,
                          right: 8,
                          opacity: 0,
                          transition: "opacity 0.2s",
                          ".MuiMenuItem-root:hover &": {
                            opacity: 1,
                          },
                        }}
                      >
                        <Clear sx={{ fontSize: 16 }} />
                      </IconButton>
                    </Box>
                  </MenuItem>
                  {index < notifications.length - 1 && (
                    <Divider sx={{ opacity: 0.3 }} />
                  )}
                </motion.div>
              );
            })
          )}
        </Box>

        {notifications.length > 0 && (
          <Box
            sx={{
              p: 2,
              borderTop: `1px solid ${theme.palette.divider}`,
              textAlign: "center",
              background:
                theme.palette.mode === "dark"
                  ? "rgba(55, 65, 81, 0.5)"
                  : "rgba(248, 250, 252, 0.8)",
            }}
          >
            <Button
              size="small"
              startIcon={<MarkEmailRead />}
              onClick={() => setNotifications([])}
              sx={{
                textTransform: "none",
                color: theme.palette.text.secondary,
                "&:hover": {
                  background: `${theme.palette.primary.main}10`,
                  color: theme.palette.primary.main,
                },
              }}
            >
              Clear all notifications
            </Button>
          </Box>
        )}
      </Menu>
    </>
  );
};

export default NotificationSystem;
