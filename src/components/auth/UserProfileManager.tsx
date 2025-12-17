// User profile management component
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../hooks/useAuth';
import { UserProfile, UserPreferences } from '../../types/index';
import { useUserPreferencesStore } from '../../store/userPreferencesStore';

interface ProfileFormData {
  backgroundLevel: 'beginner' | 'intermediate' | 'advanced';
  technicalBackground: string;
  experienceYears: number;
  learningGoals: string[];
  interests: string[];
  preferredLanguage: 'english' | 'urdu';
}

interface PreferencesFormData {
  language: 'english' | 'urdu';
  contentPersonalization: boolean;
  chatbotEnabled: boolean;
  notificationsEnabled: boolean;
  theme: 'light' | 'dark';
  autoTranslate: boolean;
}

export const UserProfileManager: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences'>('profile');
  const { user, updateUserProfile, isLoading: authLoading } = useAuth();
  const { 
    preferences, 
    updatePreferences, 
    isLoading: preferencesLoading 
  } = useUserPreferencesStore();

  const profileForm = useForm<ProfileFormData>({
    defaultValues: {
      backgroundLevel: user?.profile?.backgroundLevel || 'beginner',
      technicalBackground: user?.profile?.technicalBackground || '',
      experienceYears: user?.profile?.experienceYears || 0,
      learningGoals: user?.profile?.learningGoals || [],
      interests: user?.profile?.interests || [],
      preferredLanguage: user?.profile?.preferredLanguage || 'english',
    },
  });

  const preferencesForm = useForm<PreferencesFormData>({
    defaultValues: preferences,
  });

  // Update forms when user data changes
  useEffect(() => {
    if (user?.profile) {
      profileForm.reset({
        backgroundLevel: user.profile.backgroundLevel,
        technicalBackground: user.profile.technicalBackground,
        experienceYears: user.profile.experienceYears,
        learningGoals: user.profile.learningGoals,
        interests: user.profile.interests,
        preferredLanguage: user.profile.preferredLanguage,
      });
    }
  }, [user?.profile, profileForm]);

  useEffect(() => {
    preferencesForm.reset(preferences);
  }, [preferences, preferencesForm]);

  const onProfileSubmit = async (data: ProfileFormData) => {
    const success = await updateUserProfile(data);
    if (success) {
      // Show success message
      console.log('Profile updated successfully');
    }
  };

  const onPreferencesSubmit = async (data: PreferencesFormData) => {
    const success = await updatePreferences(data);
    if (success) {
      // Show success message
      console.log('Preferences updated successfully');
    }
  };

  const LEARNING_GOALS = [
    'Understand AI fundamentals',
    'Learn robotics programming',
    'Build physical AI systems',
    'Career advancement',
    'Academic research',
    'Personal projects',
    'Industry applications',
    'Teaching others',
  ];

  const INTEREST_AREAS = [
    'Machine Learning',
    'Computer Vision',
    'Natural Language Processing',
    'Robotics Hardware',
    'Control Systems',
    'Sensor Integration',
    'Human-Robot Interaction',
    'Autonomous Systems',
  ];

  const watchedGoals = profileForm.watch('learningGoals') || [];
  const watchedInterests = profileForm.watch('interests') || [];

  const handleGoalToggle = (goal: string) => {
    const currentGoals = watchedGoals;
    const newGoals = currentGoals.includes(goal)
      ? currentGoals.filter(g => g !== goal)
      : [...currentGoals, goal];
    profileForm.setValue('learningGoals', newGoals);
  };

  const handleInterestToggle = (interest: string) => {
    const currentInterests = watchedInterests;
    const newInterests = currentInterests.includes(interest)
      ? currentInterests.filter(i => i !== interest)
      : [...currentInterests, interest];
    profileForm.setValue('interests', newInterests);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Profile Settings</h1>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('profile')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'profile'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Profile Information
          </button>
          <button
            onClick={() => setActiveTab('preferences')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'preferences'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Preferences
          </button>
        </nav>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Learning Profile</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Experience Level
                </label>
                <select
                  {...profileForm.register('backgroundLevel')}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Years of Experience
                </label>
                <select
                  {...profileForm.register('experienceYears', { valueAsNumber: true })}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value={0}>Less than 1 year</option>
                  <option value={1}>1-2 years</option>
                  <option value={3}>3-5 years</option>
                  <option value={6}>6-10 years</option>
                  <option value={11}>More than 10 years</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium mb-2">
                Technical Background
              </label>
              <input
                type="text"
                {...profileForm.register('technicalBackground')}
                placeholder="e.g., Computer Science student, Software Engineer..."
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium mb-2">
                Learning Goals
              </label>
              <div className="grid grid-cols-2 gap-3">
                {LEARNING_GOALS.map((goal) => (
                  <label key={goal} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={watchedGoals.includes(goal)}
                      onChange={() => handleGoalToggle(goal)}
                    />
                    <span className="text-sm">{goal}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium mb-2">
                Areas of Interest
              </label>
              <div className="grid grid-cols-2 gap-3">
                {INTEREST_AREAS.map((interest) => (
                  <label key={interest} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={watchedInterests.includes(interest)}
                      onChange={() => handleInterestToggle(interest)}
                    />
                    <span className="text-sm">{interest}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={authLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {authLoading ? 'Saving...' : 'Save Profile'}
            </button>
          </div>
        </form>
      )}

      {/* Preferences Tab */}
      {activeTab === 'preferences' && (
        <form onSubmit={preferencesForm.handleSubmit(onPreferencesSubmit)} className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Application Preferences</h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Preferred Language
                </label>
                <select
                  {...preferencesForm.register('language')}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="english">English</option>
                  <option value="urdu">اردو (Urdu)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Theme
                </label>
                <select
                  {...preferencesForm.register('theme')}
                  className="w-full p-2 border border-gray-300 rounded-md"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-medium">Feature Settings</h3>
                
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    {...preferencesForm.register('contentPersonalization')}
                  />
                  <div>
                    <div className="font-medium">Content Personalization</div>
                    <div className="text-sm text-gray-600">
                      Adapt content based on your learning level and interests
                    </div>
                  </div>
                </label>

                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    {...preferencesForm.register('chatbotEnabled')}
                  />
                  <div>
                    <div className="font-medium">AI Chatbot</div>
                    <div className="text-sm text-gray-600">
                      Enable the AI assistant for questions and help
                    </div>
                  </div>
                </label>

                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    {...preferencesForm.register('autoTranslate')}
                  />
                  <div>
                    <div className="font-medium">Auto-translate</div>
                    <div className="text-sm text-gray-600">
                      Automatically translate content to your preferred language
                    </div>
                  </div>
                </label>

                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    {...preferencesForm.register('notificationsEnabled')}
                  />
                  <div>
                    <div className="font-medium">Notifications</div>
                    <div className="text-sm text-gray-600">
                      Receive updates about new content and progress
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={preferencesLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {preferencesLoading ? 'Saving...' : 'Save Preferences'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};