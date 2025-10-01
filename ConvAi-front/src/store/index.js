import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Auth Store
export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      
      login: async (username, password) => {
        set({ loading: true });
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Login failed');
          }
          
          const data = await response.json();
          const { access_token, user } = data;
          
          set({
            user,
            token: access_token,
            isAuthenticated: true,
            loading: false,
          });
          
          return data;
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      register: async (userData) => {
        set({ loading: true });
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/register`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: userData.username,
              email: userData.email,
              password: userData.password,
              native_language: userData.nativeLanguage,
              target_language: userData.targetLanguage,
              learning_goals: userData.learning_goals || [],
            }),
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Registration failed');
          }
          
          const data = await response.json();
          set({ loading: false });
          return data;
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      updateProfile: async (profileData) => {
        const { user, token } = get();
        if (!user || !token) throw new Error('Not authenticated');

        set({ loading: true });
        try {
          const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/profile/${user.id}`, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify(profileData),
          });
          
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Profile update failed');
          }
          
          const data = await response.json();
          set({
            user: { ...user, ...data.user },
            loading: false,
          });
          
          return data;
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          loading: false,
        });
      },
      
      updateUser: (userData) => {
        set((state) => ({
          user: { ...state.user, ...userData },
        }));
      },
      
      setLoading: (loading) => {
        set({ loading });
      },

      initializeAuth: () => {
        const { token } = get();
        if (token) {
          set({ isAuthenticated: true });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Theme Store
export const useThemeStore = create(
  persist(
    (set) => ({
      isDark: false,
      toggleTheme: () => set((state) => ({ isDark: !state.isDark })),
      setTheme: (isDark) => set({ isDark }),
    }),
    {
      name: 'theme-storage',
    }
  )
);

// Dashboard Store
export const useDashboardStore = create((set, get) => ({
  dashboardData: null,
  learningPaths: [],
  recentActivities: [],
  badges: [],
  loading: false,
  error: null,
  
  setDashboardData: (data) => {
    set({
      dashboardData: data,
      learningPaths: data.learning_paths || [],
      recentActivities: data.recent_activities || [],
      badges: data.badges || [],
      loading: false,
      error: null,
    });
  },
  
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
  
  clearDashboard: () => {
    set({
      dashboardData: null,
      learningPaths: [],
      recentActivities: [],
      badges: [],
      loading: false,
      error: null,
    });
  },
}));

// Activity Store
export const useActivityStore = create((set, get) => ({
  currentActivity: null,
  activityHistory: [],
  completedActivities: [],
  loading: false,
  error: null,
  
  setCurrentActivity: (activity) => {
    set({ currentActivity: activity });
  },
  
  completeActivity: (activityId, score, timeSpent) => {
    const state = get();
    const completedActivity = {
      id: activityId,
      completedAt: new Date().toISOString(),
      score,
      timeSpent,
    };
    
    set({
      completedActivities: [...state.completedActivities, completedActivity],
      currentActivity: null,
    });
  },
  
  setActivityHistory: (history) => {
    set({ activityHistory: history });
  },
  
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
}));

// Gamification Store
export const useGamificationStore = create((set, get) => ({
  userBadges: [],
  achievements: [],
  leaderboard: [],
  dailyChallenge: null,
  userStats: null,
  loading: false,
  error: null,
  
  setBadges: (badges) => set({ userBadges: badges }),
  setAchievements: (achievements) => set({ achievements }),
  setLeaderboard: (leaderboard) => set({ leaderboard }),
  setDailyChallenge: (challenge) => set({ dailyChallenge: challenge }),
  setUserStats: (stats) => set({ userStats: stats }),
  
  addNewBadge: (badge) => {
    const state = get();
    set({
      userBadges: [...state.userBadges, badge],
    });
  },
  
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
}));

// Vocabulary Store
export const useVocabularyStore = create((set, get) => ({
  vocabulary: [],
  practiceWords: [],
  masteredWords: [],
  currentWord: null,
  loading: false,
  error: null,
  
  setVocabulary: (vocabulary) => {
    const practiced = vocabulary.filter(word => word.practice_count > 0);
    const mastered = vocabulary.filter(word => word.mastery_level >= 0.8);
    
    set({
      vocabulary,
      practiceWords: practiced,
      masteredWords: mastered,
    });
  },
  
  addWord: (word) => {
    const state = get();
    set({
      vocabulary: [...state.vocabulary, word],
    });
  },
  
  updateWordProgress: (wordId, progress) => {
    const state = get();
    const updatedVocabulary = state.vocabulary.map(word =>
      word.id === wordId ? { ...word, ...progress } : word
    );
    
    set({
      vocabulary: updatedVocabulary,
      practiceWords: updatedVocabulary.filter(word => word.practice_count > 0),
      masteredWords: updatedVocabulary.filter(word => word.mastery_level >= 0.8),
    });
  },
  
  setCurrentWord: (word) => set({ currentWord: word }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
}));

// Navigation Store
export const useNavigationStore = create((set) => ({
  activeRoute: '/',
  breadcrumbs: [],
  sidebarOpen: false,
  mobileMenuOpen: false,
  
  setActiveRoute: (route) => set({ activeRoute: route }),
  setBreadcrumbs: (breadcrumbs) => set({ breadcrumbs }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  toggleMobileMenu: () => set((state) => ({ mobileMenuOpen: !state.mobileMenuOpen })),
  closeMobileMenu: () => set({ mobileMenuOpen: false }),
}));