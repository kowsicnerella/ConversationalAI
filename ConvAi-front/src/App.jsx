import React, { Suspense, lazy, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import {
  ThemeProvider,
  CssBaseline,
  CircularProgress,
  Box,
  GlobalStyles,
} from "@mui/material";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Toaster } from "react-hot-toast";

// Theme and store imports
import { lightTheme, darkTheme } from "./themes/theme";
import { useThemeStore, useAuthStore } from "./store/index.js";
import AIThemeLayout from "./components/layout/AIThemeLayout";
import { NeuralBackground } from "./components/ui/AIComponents";

import PropTypes from "prop-types";

// Layout components
import MainLayout from "./components/layout/MainLayout";

// Lazy load pages for better performance
const LandingPage = lazy(() => import("./pages/Home"));
const LoginPage = lazy(() => import("./pages/auth/Login"));
const RegisterPage = lazy(() => import("./pages/auth/Register"));
const DashboardPage = lazy(() => import("./pages/Dashboard"));
const LearningPathsPage = lazy(() => import("./pages/learning/LearningPaths"));
const LearningPathDetailPage = lazy(() =>
  import("./pages/learning/LearningPathDetail")
);
const CreateLearningPathPage = lazy(() =>
  import("./pages/learning/CreateLearningPath")
);
const ActivitiesPage = lazy(() => import("./pages/activities/Activities"));
const ActivityDetailPage = lazy(() => import("./pages/ActivityDetailPage"));
const AssessmentPage = lazy(() => import("./pages/AssessmentPage"));
const VocabularyPage = lazy(() => import("./pages/VocabularyPage"));
const ChatPage = lazy(() => import("./pages/ChatPage"));
const ProfilePage = lazy(() => import("./pages/ProfilePage"));
const LeaderboardPage = lazy(() => import("./pages/LeaderboardPage"));
const AnalyticsPage = lazy(() => import("./pages/AnalyticsPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));

// Adaptive Learning Components
const InitialAssessment = lazy(() =>
  import("./components/assessment/InitialAssessment")
);
const AssessmentResults = lazy(() =>
  import("./components/assessment/AssessmentResults")
);
const AdaptiveLearningDashboard = lazy(() =>
  import("./components/adaptive/AdaptiveLearningDashboard")
);

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

// Public Route Component (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

PublicRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

// Modern AI-themed loading component for Suspense
const SuspenseLoader = () => {
  const { isDark } = useThemeStore();

  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{
        background: isDark
          ? "linear-gradient(135deg, #0a0f23 0%, #1e293b 100%)"
          : "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <NeuralBackground opacity={0.1} />

      <motion.div
        initial={{ opacity: 0, scale: 0.8, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "24px",
        }}
      >
        <motion.div
          animate={{
            rotate: 360,
            scale: [1, 1.1, 1],
          }}
          transition={{
            rotate: { duration: 2, repeat: Infinity, ease: "linear" },
            scale: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
          }}
        >
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: "50%",
              background:
                "linear-gradient(135deg, #4f46e5 0%, #06b6d4 50%, #8b5cf6 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 40px rgba(79, 70, 229, 0.4)",
            }}
          >
            <Box
              sx={{
                width: 60,
                height: 60,
                borderRadius: "50%",
                background: isDark ? "#0a0f23" : "#ffffff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <CircularProgress
                size={40}
                thickness={3}
                sx={{
                  color: "transparent",
                  "& .MuiCircularProgress-circle": {
                    stroke: "url(#gradient)",
                  },
                }}
              />
            </Box>
          </Box>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          <Box
            component="span"
            sx={{
              fontSize: "1.25rem",
              fontWeight: 600,
              background: "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
              letterSpacing: "0.02em",
            }}
          >
            Loading AI Assistant...
          </Box>
        </motion.div>
      </motion.div>

      {/* SVG Gradient Definition */}
      <svg width="0" height="0">
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4f46e5" />
            <stop offset="50%" stopColor="#06b6d4" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
      </svg>
    </Box>
  );
};

function App() {
  const { isDark } = useThemeStore();
  const theme = isDark ? darkTheme : lightTheme;

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <GlobalStyles
          styles={(theme) => ({
            html: {
              fontSize: "16px",
              [theme.breakpoints.down("sm")]: {
                fontSize: "14px",
              },
              [theme.breakpoints.up("xl")]: {
                fontSize: "18px",
              },
            },
            body: {
              margin: 0,
              minWidth: "320px",
              minHeight: "100vh",
              background: theme.palette.background.default,
              overflow: "hidden auto",
              fontFamily: theme.typography.fontFamily,
              [theme.breakpoints.down("sm")]: {
                fontSize: "0.875rem",
              },
            },
            "#root": {
              minHeight: "100vh",
              display: "flex",
              flexDirection: "column",
              overflow: "hidden",
            },
            ".container": {
              width: "100%",
              maxWidth: "100%",
              margin: "0 auto",
              padding: "0 16px",
              [theme.breakpoints.up("sm")]: {
                maxWidth: "640px",
                padding: "0 24px",
              },
              [theme.breakpoints.up("md")]: {
                maxWidth: "768px",
                padding: "0 32px",
              },
              [theme.breakpoints.up("lg")]: {
                maxWidth: "1024px",
                padding: "0 40px",
              },
              [theme.breakpoints.up("xl")]: {
                maxWidth: "1280px",
                padding: "0 48px",
              },
              [theme.breakpoints.up("xxl")]: {
                maxWidth: "1536px",
                padding: "0 64px",
              },
            },
            // Responsive image handling
            img: {
              maxWidth: "100%",
              height: "auto",
            },
            // Prevent horizontal scroll
            "*": {
              boxSizing: "border-box",
            },
            // Touch targets for mobile
            "button, a, input, select, textarea": {
              minHeight: "44px",
              [theme.breakpoints.down("sm")]: {
                minHeight: "48px",
              },
            },
            // Scrollbar styling
            "::-webkit-scrollbar": {
              width: "8px",
              height: "8px",
            },
            "::-webkit-scrollbar-track": {
              background: theme.palette.mode === "dark" ? "#1e293b" : "#f1f5f9",
            },
            "::-webkit-scrollbar-thumb": {
              background: theme.palette.mode === "dark" ? "#475569" : "#cbd5e1",
              borderRadius: "4px",
            },
            "::-webkit-scrollbar-thumb:hover": {
              background: theme.palette.mode === "dark" ? "#64748b" : "#94a3b8",
            },
          })}
        />
        <Router>
          <AnimatePresence mode="wait">
            <Suspense fallback={<SuspenseLoader />}>
              <Routes>
                {/* Public Routes */}
                <Route
                  path="/"
                  element={
                    <PublicRoute>
                      <LandingPage />
                    </PublicRoute>
                  }
                />
                <Route
                  path="/login"
                  element={
                    <PublicRoute>
                      <LoginPage />
                    </PublicRoute>
                  }
                />
                <Route
                  path="/register"
                  element={
                    <PublicRoute>
                      <RegisterPage />
                    </PublicRoute>
                  }
                />

                {/* Adaptive Learning Routes */}
                <Route
                  path="/initial-assessment"
                  element={
                    <ProtectedRoute>
                      <InitialAssessment
                        userId={localStorage.getItem("userId")}
                      />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assessment-results"
                  element={
                    <ProtectedRoute>
                      <AssessmentResults />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/adaptive-dashboard"
                  element={
                    <ProtectedRoute>
                      <AdaptiveLearningDashboard />
                    </ProtectedRoute>
                  }
                />

                {/* Protected Routes */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <DashboardPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/learning-paths"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <LearningPathsPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/learning-paths/create"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <CreateLearningPathPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/learning-paths/:id"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <LearningPathDetailPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/activities"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <ActivitiesPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/activities/:activityType"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <ActivitiesPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/activities/:activityId"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <ActivityDetailPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/assessment"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <AssessmentPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/vocabulary"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <VocabularyPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/chat"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <ChatPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <ProfilePage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/leaderboard"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <LeaderboardPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <AnalyticsPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <MainLayout>
                        <SettingsPage />
                      </MainLayout>
                    </ProtectedRoute>
                  }
                />

                {/* Catch all route */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </AnimatePresence>
        </Router>

        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: theme.palette.background.paper,
              color: theme.palette.text.primary,
              border: `1px solid ${theme.palette.divider}`,
            },
          }}
        />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
