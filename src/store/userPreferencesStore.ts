// User preferences store using Zustand
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserPreferences } from '../types/index';
import { AuthService } from '../services/authService';

interface UserPreferencesState {
  // State
  preferences: UserPreferences;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<boolean>;
  setLanguage: (language: 'english' | 'urdu') => Promise<boolean>;
  setTheme: (theme: 'light' | 'dark') => Promise<boolean>;
  togglePersonalization: () => Promise<boolean>;
  toggleChatbot: () => Promise<boolean>;
  toggleNotifications: () => Promise<boolean>;
  toggleAutoTranslate: () => Promise<boolean>;
  resetPreferences: () => void;
  clearError: () => void;
}

const defaultPreferences: UserPreferences = {
  language: 'english',
  contentPersonalization: true,
  chatbotEnabled: true,
  notificationsEnabled: true,
  theme: 'light',
  autoTranslate: false,
};

const authService = new AuthService();

export const useUserPreferencesStore = create<UserPreferencesState>()(
  persist(
    (set, get) => ({
      // Initial state
      preferences: defaultPreferences,
      isLoading: false,
      error: null,

      // Update preferences action
      updatePreferences: async (updates: Partial<UserPreferences>) => {
        set({ isLoading: true, error: null });
        
        try {
          const currentPreferences = get().preferences;
          const newPreferences = { ...currentPreferences, ...updates };
          
          const response = await authService.updatePreferences(newPreferences);
          
          if (response.success && response.data) {
            set({
              preferences: response.data,
              isLoading: false,
              error: null,
            });
            return true;
          } else {
            set({
              error: response.error || 'Failed to update preferences',
              isLoading: false,
            });
            return false;
          }
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Failed to update preferences',
            isLoading: false,
          });
          return false;
        }
      },

      // Set language
      setLanguage: async (language: 'english' | 'urdu') => {
        return get().updatePreferences({ language });
      },

      // Set theme
      setTheme: async (theme: 'light' | 'dark') => {
        return get().updatePreferences({ theme });
      },

      // Toggle personalization
      togglePersonalization: async () => {
        const currentPreferences = get().preferences;
        return get().updatePreferences({ 
          contentPersonalization: !currentPreferences.contentPersonalization 
        });
      },

      // Toggle chatbot
      toggleChatbot: async () => {
        const currentPreferences = get().preferences;
        return get().updatePreferences({ 
          chatbotEnabled: !currentPreferences.chatbotEnabled 
        });
      },

      // Toggle notifications
      toggleNotifications: async () => {
        const currentPreferences = get().preferences;
        return get().updatePreferences({ 
          notificationsEnabled: !currentPreferences.notificationsEnabled 
        });
      },

      // Toggle auto translate
      toggleAutoTranslate: async () => {
        const currentPreferences = get().preferences;
        return get().updatePreferences({ 
          autoTranslate: !currentPreferences.autoTranslate 
        });
      },

      // Reset preferences to defaults
      resetPreferences: () => {
        set({ preferences: defaultPreferences });
      },

      // Clear error
      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'user-preferences-storage',
      partialize: (state) => ({
        preferences: state.preferences,
      }),
    }
  )
);