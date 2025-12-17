// Authentication hook
import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { AuthCredentials, SignUpData } from '../services/authService';
import { UserProfile, UserPreferences } from '../types/index';

export const useAuth = () => {
  const {
    user,
    isLoading,
    isAuthenticated,
    error,
    signIn,
    signUp,
    signOut,
    updateProfile,
    updatePreferences,
    clearError,
    initializeAuth,
  } = useAuthStore();

  // Initialize authentication on mount
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Wrapper functions with better naming
  const login = async (credentials: AuthCredentials): Promise<boolean> => {
    return await signIn(credentials);
  };

  const register = async (signUpData: SignUpData): Promise<boolean> => {
    return await signUp(signUpData);
  };

  const logout = async (): Promise<void> => {
    await signOut();
  };

  const updateUserProfile = async (profileData: Partial<UserProfile>): Promise<boolean> => {
    return await updateProfile(profileData);
  };

  const updateUserPreferences = async (preferences: Partial<UserPreferences>): Promise<boolean> => {
    return await updatePreferences(preferences);
  };

  // Computed values
  const isLoggedIn = isAuthenticated && !!user;
  const userProfile = user?.profile;
  const userPreferences = user?.preferences;

  return {
    // State
    user,
    userProfile,
    userPreferences,
    isLoading,
    isAuthenticated: isLoggedIn,
    error,

    // Actions
    login,
    register,
    logout,
    updateUserProfile,
    updateUserPreferences,
    clearError,

    // Utility functions
    hasCompletedProfile: () => {
      return !!(
        userProfile?.backgroundLevel &&
        userProfile?.learningGoals?.length &&
        userProfile?.technicalBackground
      );
    },

    isBeginnerUser: () => userProfile?.backgroundLevel === 'beginner',
    isIntermediateUser: () => userProfile?.backgroundLevel === 'intermediate',
    isAdvancedUser: () => userProfile?.backgroundLevel === 'advanced',

    preferredLanguage: userPreferences?.language || 'english',
    isChatbotEnabled: userPreferences?.chatbotEnabled ?? true,
    isPersonalizationEnabled: userPreferences?.contentPersonalization ?? true,
    isAutoTranslateEnabled: userPreferences?.autoTranslate ?? false,
  };
};