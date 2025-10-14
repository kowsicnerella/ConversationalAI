import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import { Box, CircularProgress } from "@mui/material";

// Layouts
import MainLayout from "./layouts/MainLayout";
import AuthLayout from "./layouts/AuthLayout";

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
import Vocabulary from "./pages/Vocabulary";
import ImageLearning from "./pages/ImageLearning";
import Chat from "./pages/Chat";
import ChatTutor from "./pages/ChatTutor";
import Analytics from "./pages/Analytics";
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

      {/* Protected Routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/onboarding" element={<Onboarding />} />
        <Route path="/mastery" element={<MasteryDashboard />} />
        <Route path="/assessment" element={<InitialAssessment />} />
        <Route path="/assessment-results" element={<AssessmentResults />} />
        <Route path="/lesson/:lessonId" element={<LessonView />} />
        <Route path="/lesson" element={<LessonView />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/learning-paths" element={<LearningPaths />} />
        <Route path="/learning-paths/:id" element={<LearningPathDetail />} />
        <Route path="/activities" element={<Activities />} />
        <Route path="/activities/:id" element={<ActivityDetail />} />
        <Route path="/activities/quiz/:activityId" element={<QuizActivity />} />
        <Route
          path="/activities/flashcards/:activityId"
          element={<FlashcardsActivity />}
        />
        <Route
          path="/activities/reading/:activityId"
          element={<ReadingActivity />}
        />
        <Route path="/vocabulary" element={<Vocabulary />} />
        <Route path="/goals" element={<Goals />} />
        <Route path="/practice" element={<Practice />} />
        <Route path="/image-learning" element={<ImageLearning />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/chat-tutor" element={<ChatTutor />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/notifications" element={<NotificationCenter />} />
        <Route path="/settings/notifications" element={<NotificationSettings />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/auth-test" element={<AuthTest />} />
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
