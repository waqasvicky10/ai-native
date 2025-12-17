// Authentication store using Zustand
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, UserProfile, UserPreferences } from '../types/index';
import { AuthService, AuthCredentials, SignUpData } from '../services/authService';

interface AuthState {
  // State
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  
  // Actions
  signIn: (credentials: AuthCredentials) => Promise<boolean>;
  signUp: (signUpData: SignUpData) => Promise<boolean>;
  signOut: () => Promise<void>;
  updateProfile: (profileData: Partial<UserProfile>) => Promise<boolean>;
  updatePreferences: (preferences: Partial<UserPreferences>) => Promise<boolean>;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
}

const authService = new AuthService();

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,

      // Sign in action
      signIn: async (credentials: AuthCredentials) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authService.signIn(credentials);
          
          if (response.success && response.data) {
            set({
              user: response.data.user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({
              error: response.error || 'Sign in failed',
              isLoading: false,
              isAuthenticated: false,
            });
            return false;
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Sign in failed',
            isLoading: false,
            isAuthenticated: false,
          });
          return false;
        }
      },

      // Sign up action
      signUp: async (signUpData: SignUpData) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await authService.signUp(signUpData);
          
          if (response.success && response.data) {
            set({
              user: response.data.user,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({
              error: response.error || 'Sign up failed',
              isLoading: false,
              isAuthenticated: false,
            });
            return false;
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Sign up failed',
            isLoading: false,
            isAuthenticated: false,
          });
          return false;
        }
      },

      // Sign out action
      signOut: async () => {
        set({ isLoading: true });
        
        try {
          await authService.signOut();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          // Even if sign out fails, clear local state
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: error instanceof Error ? error.message : 'Sign out failed',
          });
        }
      },

      // Update profile action
      updateProfile: async (profileData: Partial<UserProfile>) => {
        const { user } = get();
        if (!user) return false;

        set({ isLoading: true, error: null });
        
        try {
          const response = await authService.updateProfile(profileData);
          
          if (response.success && response.data) {
            set({
              user: {
                ...user,
                profile: response.data,
              },
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({
              error: response.error || 'Profile update failed',
              isLoading: false,
            });
            return false;
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Profile update failed',
            isLoading: false,
          });
          return false;
        }
      },

      // Update preferences action
      updatePreferences: async (preferences: Partial<UserPreferences>) => {
        const { user } = get();
        if (!user) return false;

        set({ isLoading: true, error: null });
        
        try {
          const response = await authService.updatePreferences(preferences);
          
          if (response.success && response.data) {
            set({
              user: {
                ...user,
                preferences: response.data,
              },
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({
              error: response.error || 'Preferences update failed',
              isLoading: false,
            });
            return false;
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Preferences update failed',
            isLoading: false,
          });
          return false;
        }
      },

      // Clear error action
      clearError: () => {
        set({ error: null });
      },

      // Initialize authentication on app start
      initializeAuth: async () => {
        if (!authService.isAuthenticated()) {
          return;
        }

        set({ isLoading: true });
        
        try {
          const response = await authService.getCurrentUser();
          
          if (response.success && response.data) {
            set({
              user: response.data,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
          } else {
            // Token might be expired, clear auth state
            set({
              user: null,
              isAuthenticated: false,
              isLoading: false,
              error: null,
            });
          }
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);