import { useState } from "react";
import PropTypes from "prop-types";
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery,
  Divider,
  Chip,
} from "@mui/material";
import {
  Menu as MenuIcon,
  Dashboard,
  School,
  Quiz,
  Assessment,
  Chat,
  Leaderboard,
  Analytics,
  Person,
  Settings,
  Logout,
  DarkMode,
  LightMode,
  Book,
} from "@mui/icons-material";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuthStore, useThemeStore } from "../../store/index.js";
import NotificationSystem from "../notifications/NotificationSystem";

const drawerWidth = 240;
const mobileDrawerWidth = 220;

const MainLayout = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  const { user, logout } = useAuthStore();
  const { isDark, toggleTheme } = useThemeStore();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [profileMenuAnchor, setProfileMenuAnchor] = useState(null);

  const menuItems = [
    { icon: Dashboard, text: "Dashboard", path: "/dashboard" },
    { icon: School, text: "Learning Paths", path: "/learning-paths" },
    { icon: Quiz, text: "Activities", path: "/activities" },
    { icon: Assessment, text: "Assessment", path: "/assessment" },
    { icon: Book, text: "Vocabulary", path: "/vocabulary" },
    { icon: Chat, text: "AI Tutor", path: "/chat" },
    { icon: Leaderboard, text: "Leaderboard", path: "/leaderboard" },
    { icon: Analytics, text: "Analytics", path: "/analytics" },
    { icon: Settings, text: "Settings", path: "/settings" },
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleProfileMenuOpen = (event) => {
    setProfileMenuAnchor(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setProfileMenuAnchor(null);
  };

  const handleLogout = () => {
    logout();
    navigate("/");
    handleProfileMenuClose();
  };

  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Box
        sx={{
          p: { xs: 1, sm: 1.5 },
          textAlign: "center",
          borderBottom: `1px solid ${theme.palette.divider}`,
          mb: 0.5,
        }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, type: "spring" }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: "bold",
              fontSize: { xs: "1rem", sm: "1.25rem" },
              background: "linear-gradient(45deg, #2196F3, #FF9800)",
              backgroundClip: "text",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Telugu Learning
          </Typography>
        </motion.div>
      </Box>

      <Divider />

      <List
        sx={{
          flex: 1,
          py: { xs: 0.5, sm: 1 },
          px: { xs: 1, sm: 1 },
        }}
      >
        {menuItems.map((item, index) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;

          return (
            <motion.div
              key={item.path}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: index * 0.1 }}
            >
              <ListItem
                disablePadding
                sx={{
                  mb: { xs: 0.25, sm: 0.5 },
                  borderRadius: { xs: 1.5, sm: 2 },
                }}
              >
                <ListItemButton
                  onClick={() => handleNavigation(item.path)}
                  sx={{
                    borderRadius: { xs: 1.5, sm: 2 },
                    py: { xs: 1, sm: 1.5 },
                    px: { xs: 1.5, sm: 2 },
                    position: 'relative',
                    overflow: 'hidden',
                    backgroundColor: isActive
                      ? theme.palette.primary.main
                      : "transparent",
                    color: isActive
                      ? theme.palette.primary.contrastText
                      : theme.palette.text.primary,
                    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      left: 0,
                      top: 0,
                      height: '100%',
                      width: '4px',
                      background: theme.palette.primary.main,
                      opacity: isActive ? 1 : 0,
                      transition: 'opacity 0.3s ease',
                    },
                    "&:hover": {
                      backgroundColor: isActive
                        ? theme.palette.primary.dark
                        : theme.palette.action.hover,
                      transform: "translateX(8px)",
                      boxShadow: isActive 
                        ? '0 4px 12px rgba(79, 70, 229, 0.3)' 
                        : '0 2px 8px rgba(0, 0, 0, 0.1)',
                      '&::before': {
                        opacity: 1,
                      },
                    },
                    "&:active": {
                      transform: "translateX(4px)",
                    },
                  }}
                >
                  <ListItemIcon
                    sx={{
                      color: isActive
                        ? theme.palette.primary.contrastText
                        : theme.palette.text.secondary,
                      minWidth: { xs: 36, sm: 40 },
                      transition: "all 0.3s ease",
                    }}
                  >
                    <motion.div
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      whileTap={{ scale: 0.95 }}
                      transition={{ type: "spring", stiffness: 400 }}
                    >
                      <Icon sx={{ fontSize: { xs: "1.25rem", sm: "1.5rem" } }} />
                    </motion.div>
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    primaryTypographyProps={{
                      fontWeight: isActive ? 600 : 400,
                      fontSize: { xs: "0.875rem", sm: "1rem" },
                    }}
                  />
                </ListItemButton>
              </ListItem>
            </motion.div>
          );
        })}
      </List>

      <Divider />

      {user && (
        <Box
          sx={{
            p: { xs: 1.5, sm: 2 },
            borderTop: `1px solid ${theme.palette.divider}`,
            mt: 1,
          }}
        >
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              p: { xs: 1.5, sm: 2 },
              backgroundColor: theme.palette.background.default,
              borderRadius: { xs: 1.5, sm: 2 },
            }}
          >
            <Avatar
              sx={{
                width: { xs: 32, sm: 40 },
                height: { xs: 32, sm: 40 },
                mr: { xs: 1.5, sm: 2 },
                backgroundColor: theme.palette.primary.main,
                fontSize: { xs: "0.875rem", sm: "1rem" },
              }}
            >
              {user.username?.charAt(0).toUpperCase()}
            </Avatar>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography
                variant="subtitle2"
                noWrap
                sx={{ fontSize: { xs: "0.75rem", sm: "0.875rem" } }}
              >
                {user.username}
              </Typography>
              <Chip
                label="Intermediate"
                size="small"
                color="primary"
                variant="outlined"
                sx={{
                  mt: 0.5,
                  height: { xs: 20, sm: 24 },
                  fontSize: { xs: "0.625rem", sm: "0.75rem" },
                }}
              />
            </Box>
          </Box>
        </Box>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: "flex" }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          backgroundColor: theme.palette.background.paper,
          color: theme.palette.text.primary,
          boxShadow: "none",
          borderBottom: `1px solid ${theme.palette.divider}`,
          zIndex: theme.zIndex.drawer + 1,
          backdropFilter: 'blur(20px)',
          background: theme.palette.mode === 'dark' 
            ? 'rgba(15, 23, 42, 0.8)' 
            : 'rgba(255, 255, 255, 0.8)',
          transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        }}
      >
        <Toolbar
          sx={{
            minHeight: { xs: 56, sm: 64 },
            px: { xs: 2, sm: 3 },
          }}
        >
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{
                mr: { xs: 1, sm: 2 },
                display: { md: "none" },
                p: { xs: 1, sm: 1.5 },
                transition: "all 0.2s ease",
                '&:hover': {
                  background: theme.palette.action.hover,
                  transform: 'rotate(90deg)',
                },
              }}
            >
              <MenuIcon />
            </IconButton>
          </motion.div>

          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{
              flexGrow: 1,
              fontSize: { xs: "1rem", sm: "1.25rem" },
              fontWeight: { xs: 500, sm: 600 },
            }}
          >
            {menuItems.find((item) => item.path === location.pathname)?.text ||
              "Telugu Learning"}
          </Typography>

          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: { xs: 0.5, sm: 1 },
            }}
          >
            <motion.div
              whileHover={{ scale: 1.1, rotate: 180 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <IconButton
                color="inherit"
                onClick={toggleTheme}
                sx={{
                  p: { xs: 1, sm: 1.5 },
                  display: { xs: "none", sm: "flex" },
                  transition: "all 0.3s ease",
                  '&:hover': {
                    background: theme.palette.action.hover,
                    boxShadow: '0 4px 12px rgba(79, 70, 229, 0.2)',
                  },
                }}
              >
                {isDark ? <LightMode /> : <DarkMode />}
              </IconButton>
            </motion.div>

            <Box sx={{ display: { xs: "none", sm: "block" } }}>
              <NotificationSystem />
            </Box>

            {user && (
              <motion.div
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <IconButton
                  onClick={handleProfileMenuOpen}
                  sx={{
                    p: { xs: 0.5, sm: 1 },
                    ml: { xs: 0.5, sm: 1 },
                    transition: "all 0.3s ease",
                    '&:hover': {
                      boxShadow: '0 4px 12px rgba(79, 70, 229, 0.3)',
                    },
                  }}
                >
                  <Avatar
                    sx={{
                      width: { xs: 28, sm: 32 },
                      height: { xs: 28, sm: 32 },
                      backgroundColor: theme.palette.primary.main,
                      fontSize: { xs: "0.875rem", sm: "1rem" },
                      transition: "all 0.3s ease",
                      '&:hover': {
                        transform: 'scale(1.1)',
                      },
                    }}
                  >
                    {user.username?.charAt(0).toUpperCase()}
                  </Avatar>
                </IconButton>
              </motion.div>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        aria-label="navigation menu"
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: { xs: mobileDrawerWidth, sm: drawerWidth },
              borderRadius: { xs: "0 16px 16px 0", sm: "0 20px 20px 0" },
            },
          }}
        >
          {drawer}
        </Drawer>

        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={profileMenuAnchor}
        open={Boolean(profileMenuAnchor)}
        onClose={handleProfileMenuClose}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
        sx={{
          '& .MuiPaper-root': {
            borderRadius: 2,
            mt: 1,
            minWidth: 180,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
          },
        }}
        TransitionComponent={motion.div}
        TransitionProps={{
          initial: { opacity: 0, y: -10 },
          animate: { opacity: 1, y: 0 },
          exit: { opacity: 0, y: -10 },
          transition: { duration: 0.2 },
        }}
      >
        <MenuItem
          onClick={() => {
            navigate("/profile");
            handleProfileMenuClose();
          }}
          sx={{
            gap: 1,
            py: 1.5,
            transition: "all 0.2s ease",
            '&:hover': {
              background: theme.palette.action.hover,
              transform: 'translateX(4px)',
            },
          }}
        >
          <Person sx={{ fontSize: '1.25rem' }} />
          Profile
        </MenuItem>
        <MenuItem 
          onClick={handleProfileMenuClose}
          sx={{
            gap: 1,
            py: 1.5,
            transition: "all 0.2s ease",
            '&:hover': {
              background: theme.palette.action.hover,
              transform: 'translateX(4px)',
            },
          }}
        >
          <Settings sx={{ fontSize: '1.25rem' }} />
          Settings
        </MenuItem>
        <Divider sx={{ my: 0.5 }} />
        <MenuItem 
          onClick={handleLogout}
          sx={{
            gap: 1,
            py: 1.5,
            color: theme.palette.error.main,
            transition: "all 0.2s ease",
            '&:hover': {
              background: `${theme.palette.error.main}10`,
              transform: 'translateX(4px)',
            },
          }}
        >
          <Logout sx={{ fontSize: '1.25rem' }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: "100vh",
          backgroundColor: theme.palette.background.default,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }} />
        <Box
          sx={{
            flexGrow: 1,
            overflow: "auto",
            px: { xs: 2, sm: 3, md: 3, lg: 4 },
            py: { xs: 2, sm: 3 },
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              style={{
                width: "100%",
                maxWidth: "100%",
                overflow: "hidden",
              }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </Box>
      </Box>
    </Box>
  );
};

MainLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default MainLayout;
