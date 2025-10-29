import { useState, useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import gamificationService from "../services/gamificationService";
import NotificationBell from "../components/NotificationBell";
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  useMediaQuery,
  CircularProgress,
  Badge,
} from "@mui/material";
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  Quiz as QuizIcon,
  Book as BookIcon,
  Chat as ChatIcon,
  Analytics as AnalyticsIcon,
  Leaderboard as LeaderboardIcon,
  AccountCircle,
  Settings as SettingsIcon,
  Logout,
  Brightness4,
  Brightness7,
  Close as CloseIcon,
  EmojiEvents as GoalsIcon,
  Psychology as PracticeIcon,
  VideogameAsset as GamificationIcon,
  LocalFireDepartment as FireIcon,
} from "@mui/icons-material";

const drawerWidth = 260;

const menuItems = [
  { text: "Dashboard", icon: <DashboardIcon />, path: "/dashboard" },
  { text: "Learning Paths", icon: <SchoolIcon />, path: "/learning-paths" },
  { text: "Activities", icon: <QuizIcon />, path: "/activities" },
  { text: "Vocabulary", icon: <BookIcon />, path: "/vocabulary" },
  { text: "Goals", icon: <GoalsIcon />, path: "/goals" },
  { text: "Practice", icon: <PracticeIcon />, path: "/practice" },
  { text: "AI Chat", icon: <ChatIcon />, path: "/chat" },
  { text: "Analytics", icon: <AnalyticsIcon />, path: "/analytics" },
  { text: "Gamification", icon: <GamificationIcon />, path: "/gamification" },
  { text: "Leaderboard", icon: <LeaderboardIcon />, path: "/leaderboard" },
];

const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { mode, toggleTheme } = useTheme();
  const isMobile = useMediaQuery("(max-width:900px)");

  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showNavbar, setShowNavbar] = useState(true);
  const [streak, setStreak] = useState(null);
  const { userStatus } = useAuth(); // Get userStatus from AuthContext instead of duplicating

  useEffect(() => {
    fetchStreakData();
  }, [location.pathname]);

  // Update navbar visibility when userStatus changes from AuthContext
  useEffect(() => {
    if (userStatus) {
      setShowNavbar(userStatus.navigation?.show_navbar ?? true);
      setLoading(false);
    }
  }, [userStatus]);

  const fetchStreakData = async () => {
    try {
      const data = await gamificationService.getStreak();
      setStreak(data.streak);
    } catch (err) {
      console.error('Failed to fetch streak:', err);
    }
  };

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
    handleClose();
  };

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Logo */}
      <Box sx={{ p: 3, textAlign: "center" }}>
        <Typography
          variant="h5"
          sx={{
            fontWeight: 800,
            background: "linear-gradient(90deg, #0ea5e9 0%, #d946ef 100%)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          Telugu Learn
        </Typography>
        <Typography variant="caption" color="text.secondary">
          English Learning Platform
        </Typography>
      </Box>

      <Divider />

      {/* Navigation Menu */}
      <List sx={{ flexGrow: 1, px: 1.5 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (isMobile) setMobileOpen(false);
              }}
              sx={{
                borderRadius: 2,
                "&.Mui-selected": {
                  background:
                    "linear-gradient(90deg, rgba(14, 165, 233, 0.1) 0%, rgba(217, 70, 239, 0.1) 100%)",
                  color: mode === "dark" ? "#0ea5e9" : "#1976d2",
                  fontWeight: 600,
                  "& .MuiListItemIcon-root": {
                    color: mode === "dark" ? "#0ea5e9" : "#1976d2",
                  },
                  "&:hover": {
                    background:
                      "linear-gradient(90deg, rgba(14, 165, 233, 0.15) 0%, rgba(217, 70, 239, 0.15) 100%)",
                  },
                },
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 40,
                  color: location.pathname === item.path ? "inherit" : "text.secondary",
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

      {/* User Profile Section */}
      <Box sx={{ p: 2 }}>
        <ListItem disablePadding>
          <ListItemButton
            onClick={() => {
              navigate("/profile");
              if (isMobile) setMobileOpen(false);
            }}
            sx={{ borderRadius: 2 }}
          >
            <ListItemIcon>
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  bgcolor: "primary.main",
                  fontSize: "0.875rem",
                }}
              >
                {user?.username?.charAt(0).toUpperCase() || "U"}
              </Avatar>
            </ListItemIcon>
            <ListItemText
              primary={user?.username || "User"}
              secondary={`${userStatus?.profile?.points || 0} points`}
              primaryTypographyProps={{ variant: "body2", fontWeight: 600 }}
              secondaryTypographyProps={{ variant: "caption" }}
            />
          </ListItemButton>
        </ListItem>
      </Box>
    </Box>
  );

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // If navbar should not be shown (during onboarding), render without layout
  if (!showNavbar) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          bgcolor: "background.default",
        }}
      >
        <Outlet />
      </Box>
    );
  }

  // Normal layout with navbar
  return (
    <Box sx={{ display: "flex" }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          bgcolor: "background.paper",
          color: "text.primary",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: "none" } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {menuItems.find((item) => item.path === location.pathname)?.text || "Dashboard"}
          </Typography>

          {/* Streak Badge */}
          {streak && (
            <IconButton
              onClick={() => navigate("/gamification")}
              title="View your gamification"
              sx={{
                mr: 1,
                background: streak.current_streak > 0 ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : undefined,
                color: streak.current_streak > 0 ? "white" : "inherit",
                transition: "all 0.2s",
                "&:hover": {
                  transform: "scale(1.1)",
                },
              }}
            >
              <Badge badgeContent={streak.current_streak} color="error">
                <FireIcon />
              </Badge>
            </IconButton>
          )}

          {/* Notification Bell */}
          <NotificationBell />

          {/* Theme Toggle */}
          <IconButton onClick={toggleTheme} color="inherit">
            {mode === "dark" ? <Brightness7 /> : <Brightness4 />}
          </IconButton>

          {/* User Menu */}
          <IconButton onClick={handleMenu} color="inherit">
            <Avatar
              sx={{
                width: 32,
                height: 32,
                bgcolor: "primary.main",
                fontSize: "0.875rem",
              }}
            >
              {user?.username?.charAt(0).toUpperCase() || "U"}
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            onClick={handleClose}
          >
            <MenuItem onClick={() => navigate("/profile")}>
              <AccountCircle sx={{ mr: 1 }} /> Profile
            </MenuItem>
            <MenuItem onClick={() => navigate("/settings")}>
              <SettingsIcon sx={{ mr: 1 }} /> Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <Logout sx={{ mr: 1 }} /> Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
              bgcolor: "background.paper",
            },
          }}
        >
          <Box sx={{ display: "flex", justifyContent: "flex-end", p: 1 }}>
            <IconButton onClick={handleDrawerToggle}>
              <CloseIcon />
            </IconButton>
          </Box>
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
              bgcolor: "background.paper",
              borderRight: "1px solid",
              borderColor: "divider",
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: "100vh",
          bgcolor: "background.default",
        }}
      >
        <Toolbar /> {/* Spacer for AppBar */}
        <Outlet />
      </Box>
    </Box>
  );
};

export default MainLayout;
