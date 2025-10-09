import { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Chip,
  Tabs,
  Tab,
  Badge,
  Button,
  Menu,
  MenuItem,
  Divider,
} from "@mui/material";
import {
  Notifications as NotificationsIcon,
  MoreVert,
  CheckCircle,
  EmojiEvents,
  School,
  LocalFireDepartment,
  TrendingUp,
  Star,
  Delete,
  DoneAll,
  FilterList,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import PageTransition from "../components/common/PageTransition";
import GradientText from "../components/common/GradientText";
import HoverCard from "../components/common/HoverCard";

const Notifications = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: "achievement",
      icon: <EmojiEvents sx={{ color: "#FFD700" }} />,
      title: "New Achievement Unlocked!",
      message: 'You earned the "7 Day Streak" achievement',
      time: "2 hours ago",
      read: false,
    },
    {
      id: 2,
      type: "streak",
      icon: <LocalFireDepartment sx={{ color: "#FF6B6B" }} />,
      title: "Streak Alert",
      message: "Keep it up! You are on a 15-day learning streak",
      time: "5 hours ago",
      read: false,
    },
    {
      id: 3,
      type: "activity",
      icon: <School sx={{ color: "#667eea" }} />,
      title: "New Activity Available",
      message: "Check out the new reading comprehension activity",
      time: "1 day ago",
      read: false,
    },
    {
      id: 4,
      type: "level",
      icon: <TrendingUp sx={{ color: "#43e97b" }} />,
      title: "Level Up!",
      message: "Congratulations! You reached Level 10",
      time: "2 days ago",
      read: true,
    },
    {
      id: 5,
      type: "achievement",
      icon: <Star sx={{ color: "#f093fb" }} />,
      title: "Perfect Score!",
      message: "You scored 100% on English Vocabulary Quiz",
      time: "3 days ago",
      read: true,
    },
    {
      id: 6,
      type: "activity",
      icon: <School sx={{ color: "#667eea" }} />,
      title: "New Learning Path",
      message: "Business English path is now available",
      time: "4 days ago",
      read: true,
    },
    {
      id: 7,
      type: "streak",
      icon: <LocalFireDepartment sx={{ color: "#FF6B6B" }} />,
      title: "Streak Reminder",
      message: "Don't forget to practice today to maintain your streak!",
      time: "5 days ago",
      read: true,
    },
  ]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleMenuOpen = (event, notification) => {
    setAnchorEl(event.currentTarget);
    setSelectedNotification(notification);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedNotification(null);
  };

  const handleMarkAsRead = (notificationId) => {
    setNotifications(
      notifications.map((n) =>
        n.id === notificationId ? { ...n, read: true } : n
      )
    );
    handleMenuClose();
  };

  const handleDelete = (notificationId) => {
    setNotifications(notifications.filter((n) => n.id !== notificationId));
    handleMenuClose();
  };

  const handleMarkAllAsRead = () => {
    setNotifications(notifications.map((n) => ({ ...n, read: true })));
  };

  const handleClearAll = () => {
    setNotifications([]);
  };

  const getFilteredNotifications = () => {
    if (activeTab === 0) return notifications;
    if (activeTab === 1) return notifications.filter((n) => !n.read);
    if (activeTab === 2)
      return notifications.filter((n) => n.type === "achievement");
    if (activeTab === 3)
      return notifications.filter((n) => n.type === "activity");
    return notifications;
  };

  const filteredNotifications = getFilteredNotifications();
  const unreadCount = notifications.filter((n) => !n.read).length;

  const getNotificationColor = (type) => {
    switch (type) {
      case "achievement":
        return "#FFD700";
      case "streak":
        return "#FF6B6B";
      case "activity":
        return "#667eea";
      case "level":
        return "#43e97b";
      default:
        return "#667eea";
    }
  };

  return (
    <PageTransition>
      <Box>
        {/* Header */}
        <Box
          sx={{
            mb: 4,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 2,
          }}
        >
          <Box>
            <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}>
              <GradientText variant="h4" sx={{ fontWeight: 700 }}>
                Notifications
              </GradientText>
              {unreadCount > 0 && (
                <Badge badgeContent={unreadCount} color="error">
                  <NotificationsIcon color="primary" />
                </Badge>
              )}
            </Box>
            <Typography variant="body1" color="text.secondary">
              Stay updated with your learning progress
            </Typography>
          </Box>
          <Box sx={{ display: "flex", gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<DoneAll />}
              onClick={handleMarkAllAsRead}
              disabled={unreadCount === 0}
            >
              Mark All Read
            </Button>
            <Button
              variant="outlined"
              size="small"
              color="error"
              startIcon={<Delete />}
              onClick={handleClearAll}
              disabled={notifications.length === 0}
            >
              Clear All
            </Button>
          </Box>
        </Box>

        {/* Filter Tabs */}
        <Card sx={{ mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="All" icon={<FilterList />} iconPosition="start" />
            <Tab
              label={`Unread (${unreadCount})`}
              icon={<NotificationsIcon />}
              iconPosition="start"
            />
            <Tab
              label="Achievements"
              icon={<EmojiEvents />}
              iconPosition="start"
            />
            <Tab label="Activities" icon={<School />} iconPosition="start" />
          </Tabs>
        </Card>

        {/* Notifications List */}
        <Box>
          {filteredNotifications.length === 0 ? (
            <Card>
              <CardContent sx={{ textAlign: "center", py: 6 }}>
                <NotificationsIcon
                  sx={{ fontSize: 60, color: "text.secondary", mb: 2 }}
                />
                <Typography variant="h6" color="text.secondary">
                  No notifications
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  You are all caught up!
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <AnimatePresence>
              {filteredNotifications.map((notification, index) => (
                <motion.div
                  key={notification.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <HoverCard sx={{ mb: 2 }}>
                    <CardContent>
                      <Box sx={{ display: "flex", gap: 2 }}>
                        {/* Icon */}
                        <Box
                          sx={{
                            width: 48,
                            height: 48,
                            borderRadius: "50%",
                            bgcolor: notification.read
                              ? "grey.200"
                              : `${getNotificationColor(notification.type)}20`,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                          }}
                        >
                          {notification.icon}
                        </Box>

                        {/* Content */}
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "flex-start",
                              justifyContent: "space-between",
                              gap: 1,
                            }}
                          >
                            <Box sx={{ flex: 1 }}>
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 1,
                                  mb: 0.5,
                                }}
                              >
                                <Typography
                                  variant="h6"
                                  fontWeight={notification.read ? 400 : 700}
                                  sx={{ fontSize: "1rem" }}
                                >
                                  {notification.title}
                                </Typography>
                                {!notification.read && (
                                  <Box
                                    sx={{
                                      width: 8,
                                      height: 8,
                                      borderRadius: "50%",
                                      bgcolor: "primary.main",
                                    }}
                                  />
                                )}
                              </Box>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{
                                  mb: 1,
                                  overflow: "hidden",
                                  textOverflow: "ellipsis",
                                }}
                              >
                                {notification.message}
                              </Typography>
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 1,
                                }}
                              >
                                <Chip
                                  label={notification.time}
                                  size="small"
                                  variant="outlined"
                                  sx={{ fontSize: "0.7rem", height: 24 }}
                                />
                                <Chip
                                  label={notification.type}
                                  size="small"
                                  sx={{
                                    fontSize: "0.7rem",
                                    height: 24,
                                    bgcolor: `${getNotificationColor(
                                      notification.type
                                    )}20`,
                                    color: getNotificationColor(
                                      notification.type
                                    ),
                                    fontWeight: 600,
                                  }}
                                />
                              </Box>
                            </Box>

                            {/* Actions */}
                            <IconButton
                              size="small"
                              onClick={(e) => handleMenuOpen(e, notification)}
                            >
                              <MoreVert />
                            </IconButton>
                          </Box>
                        </Box>
                      </Box>
                    </CardContent>
                  </HoverCard>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </Box>

        {/* Context Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          {selectedNotification && !selectedNotification.read && (
            <MenuItem onClick={() => handleMarkAsRead(selectedNotification.id)}>
              <CheckCircle sx={{ mr: 1, fontSize: 20 }} />
              Mark as Read
            </MenuItem>
          )}
          <MenuItem
            onClick={() =>
              selectedNotification && handleDelete(selectedNotification.id)
            }
            sx={{ color: "error.main" }}
          >
            <Delete sx={{ mr: 1, fontSize: 20 }} />
            Delete
          </MenuItem>
        </Menu>
      </Box>
    </PageTransition>
  );
};

export default Notifications;
