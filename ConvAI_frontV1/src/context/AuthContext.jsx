import { createContext, useState, useContext, useEffect } from "react";
import axiosInstance, { API_ENDPOINTS } from "../config/api";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userStatus, setUserStatus] = useState(null);

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem("access_token");
    const savedUser = localStorage.getItem("user");

    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
        setIsAuthenticated(true);
        // Fetch fresh status after setting authenticated
        fetchUserStatus();
      } catch (error) {
        console.error("Error parsing saved user:", error);
        logout();
      }
    }
    setLoading(false);
  }, []);

  const fetchUserStatus = async () => {
    try {
      const response = await axiosInstance.get(API_ENDPOINTS.USER.STATUS);
      const status = response.data.user_status;
      setUserStatus(status);
      
      // Update user object with latest onboarding fields
      if (user) {
        const updatedUser = {
          ...user,
          onboarding_completed: status.onboarding_completed,
          needs_initial_assessment: status.needs_initial_assessment,
          current_learning_phase: status.current_learning_phase,
          initial_assessment_id: status.initial_assessment_id,
        };
        setUser(updatedUser);
        localStorage.setItem("user", JSON.stringify(updatedUser));
      }
      
      return status;
    } catch (error) {
      console.error("Error fetching user status:", error);
      return null;
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axiosInstance.post(API_ENDPOINTS.AUTH.LOGIN, {
        username,
        password,
      });

      const { access_token, user: userData } = response.data;

      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(userData));

      setUser(userData);
      setIsAuthenticated(true);

      // Fetch fresh status after login
      await fetchUserStatus();

      return { success: true, user: userData };
    } catch (error) {
      console.error("Login error:", error);
      return {
        success: false,
        error: error.response?.data?.message || "Login failed",
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axiosInstance.post(
        API_ENDPOINTS.AUTH.REGISTER,
        userData
      );

      const { access_token, user: newUser, assessment } = response.data;

      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user", JSON.stringify(newUser));

      setUser(newUser);
      setIsAuthenticated(true);

      // Fetch fresh status after registration
      await fetchUserStatus();

      // Return assessment data if available so it can be passed to onboarding
      return { 
        success: true, 
        user: newUser,
        assessment: assessment || null // Include assessment questions from registration
      };
    } catch (error) {
      console.error("Registration error:", error);
      return {
        success: false,
        error: error.response?.data?.message || "Registration failed",
      };
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateUser = (updatedData) => {
    const updatedUser = { ...user, ...updatedData };
    setUser(updatedUser);
    localStorage.setItem("user", JSON.stringify(updatedUser));
  };

  const getOnboardingRedirectPath = (userData) => {
    // Determine where to redirect based on onboarding status
    if (!userData) return "/login";

    // If onboarding is complete, go to dashboard
    if (userData.onboarding_completed) {
      return "/dashboard";
    }

    // Check current learning phase
    const phase = userData.current_learning_phase;

    if (phase === "onboarding" || userData.needs_initial_assessment) {
      return "/onboarding";
    }

    if (phase === "assessment") {
      return "/assessment";
    }

    if (phase === "learning" || phase === "mastery") {
      return "/dashboard";
    }

    // Default to onboarding if unclear
    return "/onboarding";
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    userStatus,
    login,
    register,
    logout,
    updateUser,
    fetchUserStatus,
    getOnboardingRedirectPath,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
