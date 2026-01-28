import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { Box, CircularProgress } from "@mui/material";

// Layouts
import MainLayout from "./layouts/MainLayoutEnhanced";
import AuthLayout from "./layouts/AuthLayout";

// Guards
import OnboardingGuard from "./components/guards/OnboardingGuard";

// Debug
import Debug from "./pages/Debug";

// Pages
import LandingPage from "./pages/LandingPage";
import Login from "./pages/auth/NewLogin";
import Register from "./pages/auth/NewRegister";
import ForgotPassword from "./pages/auth/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import LearningPaths from "./pages/LearningPaths";
import LearningPathDetail from "./pages/LearningPathDetail";
import Activities from "./pages/Activities";
import ActivityDetail from "./pages/ActivityDetail";
import ActivityHistory from "./pages/ActivityHistory";
import Vocabulary from "./pages/Vocabulary";
import VocabularyMastery from "./pages/VocabularyMastery"; // Phase 5: SM-2 Vocabulary System
import ImageLearning from "./pages/ImageLearning";
import Chat from "./pages/Chat";
import ChatTutor from "./pages/ChatTutor";
import { ChatProvider } from "./context/ChatContext";
import Analytics from "./pages/Analytics";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";  // NEW Phase 2 Analytics
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import Notifications from "./pages/Notifications";
import NotificationCenter from "./pages/NotificationCenter";
import NotificationSettings from "./pages/NotificationSettings";
import Leaderboard from "./pages/Leaderboard";
import AuthTest from "./pages/AuthTest";
import Onboarding from "./pages/Onboarding";
import MasteryDashboard from "./pages/MasteryDashboard";
import InitialAssessment from "./pages/InitialAssessment";
import AssessmentResults from "./pages/AssessmentResults";
import LessonView from "./pages/LessonView";
import Goals from "./pages/Goals";
import Practice from "./pages/Practice";
import Gamification from "./pages/Gamification"; // Phase 9: Gamification Hub

// Activity Types
import QuizActivity from "./pages/activities/QuizActivity";
import FlashcardsActivity from "./pages/activities/FlashcardsActivity";
import ReadingActivity from "./pages/activities/ReadingActivity";

function App() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        }}
      >
        <CircularProgress size={60} sx={{ color: "white" }} />
      </Box>
    );
  }

  return (
    <Routes>
      {/* Debug Route - Public */}
      <Route path="/debug" element={<Debug />} />

      {/* Public Routes */}
      <Route path="/" element={<LandingPage />} />

      {/* Auth Routes */}
      <Route element={<AuthLayout />}>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />}
        />
        <Route
          path="/register"
          element={
            isAuthenticated ? <Navigate to="/dashboard" /> : <Register />
          }
        />
        <Route path="/forgot-password" element={<ForgotPassword />} />
      </Route>

      {/* Protected Routes with Onboarding Guard */}
      <Route element={<ProtectedRoute />}>
        {/* Onboarding Flow Routes - Always accessible once authenticated */}
        <Route
          path="/assessment"
          element={
            <OnboardingGuard allowedPhases={["assessment", "onboarding"]}>
              <InitialAssessment />
            </OnboardingGuard>
          }
        />
        <Route
          path="/assessment-results"
          element={
            <OnboardingGuard allowedPhases={["assessment", "onboarding"]}>
              <AssessmentResults />
            </OnboardingGuard>
          }
        />
        <Route
          path="/onboarding"
          element={
            <OnboardingGuard allowedPhases={["onboarding"]}>
              <Onboarding />
            </OnboardingGuard>
          }
        />

        {/* Protected Routes - Require completed onboarding */}
        <Route
          path="/dashboard"
          element={
            <OnboardingGuard requireOnboarding>
              <Dashboard />
            </OnboardingGuard>
          }
        />
        <Route
          path="/learning-paths"
          element={
            <OnboardingGuard requireOnboarding>
              <LearningPaths />
            </OnboardingGuard>
          }
        />
        <Route
          path="/learning-paths/:id"
          element={
            <OnboardingGuard requireOnboarding>
              <LearningPathDetail />
            </OnboardingGuard>
          }
        />
        <Route
          path="/activities"
          element={
            <OnboardingGuard requireOnboarding>
              <Activities />
            </OnboardingGuard>
          }
        />
        <Route
          path="/activities/:id"
          element={
            <OnboardingGuard requireOnboarding>
              <ActivityDetail />
            </OnboardingGuard>
          }
        />
        <Route
          path="/activities/quiz/:activityId"
          element={
            <OnboardingGuard requireOnboarding>
              <QuizActivity />
            </OnboardingGuard>
          }
        />
        <Route
          path="/activities/flashcards/:activityId"
          element={
            <OnboardingGuard requireOnboarding>
              <FlashcardsActivity />
            </OnboardingGuard>
          }
        />
        <Route
          path="/activities/reading/:activityId"
          element={
            <OnboardingGuard requireOnboarding>
              <ReadingActivity />
            </OnboardingGuard>
          }
        />
        <Route
          path="/vocabulary"
          element={
            <OnboardingGuard requireOnboarding>
              <Vocabulary />
            </OnboardingGuard>
          }
        />
        <Route
          path="/vocabulary-mastery"
          element={
            <OnboardingGuard requireOnboarding>
              <VocabularyMastery />
            </OnboardingGuard>
          }
        />
        <Route
          path="/goals"
          element={
            <OnboardingGuard requireOnboarding>
              <Goals />
            </OnboardingGuard>
          }
        />
        <Route
          path="/practice"
          element={
            <OnboardingGuard requireOnboarding>
              <Practice />
            </OnboardingGuard>
          }
        />
        <Route
          path="/image-learning"
          element={
            <OnboardingGuard requireOnboarding>
              <ImageLearning />
            </OnboardingGuard>
          }
        />
        <Route
          path="/chat"
          element={
            <OnboardingGuard requireOnboarding>
              <ChatProvider>
                <Chat />
              </ChatProvider>
            </OnboardingGuard>
          }
        />
        <Route
          path="/chat-tutor"
          element={
            <OnboardingGuard requireOnboarding>
              <ChatProvider>
                <ChatTutor />
              </ChatProvider>
            </OnboardingGuard>
          }
        />
        <Route
          path="/analytics"
          element={
            <OnboardingGuard requireOnboarding>
              <Analytics />
            </OnboardingGuard>
          }
        />
        <Route
          path="/analytics-dashboard"
          element={
            <OnboardingGuard requireOnboarding>
              <AnalyticsDashboard />
            </OnboardingGuard>
          }
        />
        <Route
          path="/activity-history"
          element={
            <OnboardingGuard requireOnboarding>
              <ActivityHistory />
            </OnboardingGuard>
          }
        />
        <Route
          path="/leaderboard"
          element={
            <OnboardingGuard requireOnboarding>
              <Leaderboard />
            </OnboardingGuard>
          }
        />
        <Route
          path="/gamification"
          element={
            <OnboardingGuard requireOnboarding>
              <Gamification />
            </OnboardingGuard>
          }
        />
        <Route
          path="/notifications"
          element={
            <OnboardingGuard requireOnboarding>
              <NotificationCenter />
            </OnboardingGuard>
          }
        />
        <Route
          path="/settings/notifications"
          element={
            <OnboardingGuard requireOnboarding>
              <NotificationSettings />
            </OnboardingGuard>
          }
        />
        <Route
          path="/profile"
          element={
            <OnboardingGuard requireOnboarding>
              <Profile />
            </OnboardingGuard>
          }
        />
        <Route
          path="/settings"
          element={
            <OnboardingGuard requireOnboarding>
              <Settings />
            </OnboardingGuard>
          }
        />
        <Route
          path="/lesson/:lessonId"
          element={
            <OnboardingGuard requireOnboarding>
              <LessonView />
            </OnboardingGuard>
          }
        />
        <Route
          path="/lesson"
          element={
            <OnboardingGuard requireOnboarding>
              <LessonView />
            </OnboardingGuard>
          }
        />
        <Route
          path="/mastery"
          element={
            <OnboardingGuard requireOnboarding>
              <MasteryDashboard />
            </OnboardingGuard>
          }
        />
        <Route
          path="/auth-test"
          element={
            <OnboardingGuard requireOnboarding>
              <AuthTest />
            </OnboardingGuard>
          }
        />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

// Protected Route Component
function ProtectedRoute() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <MainLayout />;
}

export default App;
