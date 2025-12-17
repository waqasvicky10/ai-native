// Background questionnaire component for new users
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { UserProfile } from '../../types/index';

interface BackgroundQuestionnaireProps {
  onComplete: (profile: Partial<UserProfile>) => void;
  onSkip?: () => void;
  isLoading?: boolean;
}

interface FormData {
  backgroundLevel: 'beginner' | 'intermediate' | 'advanced';
  technicalBackground: string;
  experienceYears: number;
  learningGoals: string[];
  interests: string[];
  preferredLanguage: 'english' | 'urdu';
  specificInterests: string;
  currentRole: string;
  motivation: string;
}

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

export const BackgroundQuestionnaire: React.FC<BackgroundQuestionnaireProps> = ({
  onComplete,
  onSkip,
  isLoading = false,
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 4;

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      backgroundLevel: 'beginner',
      preferredLanguage: 'english',
      learningGoals: [],
      interests: [],
      experienceYears: 0,
    },
  });

  const watchedGoals = watch('learningGoals') || [];
  const watchedInterests = watch('interests') || [];

  const handleGoalToggle = (goal: string) => {
    const currentGoals = watchedGoals;
    const newGoals = currentGoals.includes(goal)
      ? currentGoals.filter(g => g !== goal)
      : [...currentGoals, goal];
    setValue('learningGoals', newGoals);
  };

  const handleInterestToggle = (interest: string) => {
    const currentInterests = watchedInterests;
    const newInterests = currentInterests.includes(interest)
      ? currentInterests.filter(i => i !== interest)
      : [...currentInterests, interest];
    setValue('interests', newInterests);
  };

  const onSubmit = (data: FormData) => {
    const profile: Partial<UserProfile> = {
      backgroundLevel: data.backgroundLevel,
      technicalBackground: data.technicalBackground,
      experienceYears: data.experienceYears,
      learningGoals: data.learningGoals,
      interests: data.interests,
      preferredLanguage: data.preferredLanguage,
    };

    onComplete(profile);
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">
                What's your current level with AI and Robotics?
              </h3>
              <div className="space-y-3">
                {[
                  { value: 'beginner', label: 'Beginner', desc: 'New to AI and robotics' },
                  { value: 'intermediate', label: 'Intermediate', desc: 'Some experience with AI or robotics' },
                  { value: 'advanced', label: 'Advanced', desc: 'Experienced in AI and/or robotics' },
                ].map((option) => (
                  <label key={option.value} className="flex items-start space-x-3 cursor-pointer">
                    <input
                      type="radio"
                      value={option.value}
                      {...register('backgroundLevel', { required: 'Please select your level' })}
                      className="mt-1"
                    />
                    <div>
                      <div className="font-medium">{option.label}</div>
                      <div className="text-sm text-gray-600">{option.desc}</div>
                    </div>
                  </label>
                ))}
              </div>
              {errors.backgroundLevel && (
                <p className="text-red-500 text-sm mt-2">{errors.backgroundLevel.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Preferred Language
              </label>
              <select
                {...register('preferredLanguage')}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value="english">English</option>
                <option value="urdu">اردو (Urdu)</option>
              </select>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                What's your technical background? *
              </label>
              <input
                type="text"
                {...register('technicalBackground', { 
                  required: 'Please describe your background' 
                })}
                placeholder="e.g., Computer Science student, Software Engineer, Researcher..."
                className="w-full p-2 border border-gray-300 rounded-md"
              />
              {errors.technicalBackground && (
                <p className="text-red-500 text-sm mt-1">{errors.technicalBackground.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Years of experience with programming/technology
              </label>
              <select
                {...register('experienceYears', { valueAsNumber: true })}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                <option value={0}>Less than 1 year</option>
                <option value={1}>1-2 years</option>
                <option value={3}>3-5 years</option>
                <option value={6}>6-10 years</option>
                <option value={11}>More than 10 years</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Current role or position
              </label>
              <input
                type="text"
                {...register('currentRole')}
                placeholder="e.g., Student, Developer, Researcher, Engineer..."
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">
                What are your learning goals? (Select all that apply)
              </h3>
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

            <div>
              <label className="block text-sm font-medium mb-2">
                What motivates you to learn about Physical AI?
              </label>
              <textarea
                {...register('motivation')}
                rows={3}
                placeholder="Tell us what excites you about this field..."
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">
                Which areas interest you most? (Select all that apply)
              </h3>
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

            <div>
              <label className="block text-sm font-medium mb-2">
                Any specific topics or applications you'd like to focus on?
              </label>
              <textarea
                {...register('specificInterests')}
                rows={3}
                placeholder="e.g., autonomous vehicles, medical robotics, industrial automation..."
                className="w-full p-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Tell us about yourself</h2>
          {onSkip && (
            <button
              type="button"
              onClick={onSkip}
              className="text-gray-500 hover:text-gray-700"
            >
              Skip for now
            </button>
          )}
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(currentStep / totalSteps) * 100}%` }}
          />
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Step {currentStep} of {totalSteps}
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        {renderStep()}

        <div className="flex justify-between mt-8">
          <button
            type="button"
            onClick={prevStep}
            disabled={currentStep === 1}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          {currentStep < totalSteps ? (
            <button
              type="button"
              onClick={nextStep}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Next
            </button>
          ) : (
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Complete Setup'}
            </button>
          )}
        </div>
      </form>
    </div>
  );
};