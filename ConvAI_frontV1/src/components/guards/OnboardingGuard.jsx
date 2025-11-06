import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import axiosInstance, { API_ENDPOINTS } from "../../config/api";
import { Box, CircularProgress } from "@mui/material";

/**
 * OnboardingGuard Component
 * Ensures users complete onboarding before accessing protected routes
 * Redirects based on user's onboarding status and learning phase
 */
const OnboardingGuard = ({ children }) => {
  const [loading, setLoading] = useState(true);
  const [userStatus, setUserStatus] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();

  useEffect(() => {
    // Only check user status if authenticated
    // This prevents unnecessary API calls that would fail with 401
    if (isAuthenticated) {
      checkUserStatus();
    } else {
      // If not authenticated, immediately stop loading
      // The ProtectedRoute will handle redirecting to login
      setLoading(false);
    }
  }, [isAuthenticated, location.pathname]);

  const checkUserStatus = async () => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.STATUS);
      const status = response.data.user_status;
      setUserStatus(status);

      // Get current path
      const currentPath = location.pathname;

      // Define public routes that don't need onboarding
      const publicRoutes = [
        "/onboarding",
        "/assessment",
        "/assessment-results",
        "/profile",
        "/settings",
      ];

      // Check if current route is public
      const isPublicRoute = publicRoutes.some((route) =>
        currentPath.startsWith(route)
      );

      // If onboarding not completed and trying to access protected route
      if (!status.onboarding_completed && !isPublicRoute) {
        const redirectPath = status.navigation.redirect_to || "/onboarding";
        
        // Don't redirect if already on the target path
        if (currentPath !== redirectPath) {
          navigate(redirectPath, { replace: true });
        }
      }
      // If onboarding completed and on onboarding page, redirect to dashboard
      else if (status.onboarding_completed && currentPath === "/onboarding") {
        navigate("/dashboard", { replace: true });
      }

      setLoading(false);
    } catch (error) {
      console.error("Error checking user status:", error);
      setLoading(false);
    }
  };

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

  // Pass userStatus to children if needed
  return children;
};

export default OnboardingGuard;
