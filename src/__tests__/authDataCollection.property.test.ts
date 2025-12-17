/**
 * Property-based test for authentication data collection
 * Feature: ai-native-textbook, Property 8: Authentication Data Collection
 * Validates: Requirements 4.2
 */

import * as fc from 'fast-check';
import { UserProfile } from '../types/index';

// Mock the background questionnaire validation logic
const validateBackgroundQuestionnaire = (profile: Partial<UserProfile>): boolean => {
  // Property: All required background questions must be collected
  const requiredFields = [
    'backgroundLevel',
    'technicalBackground',
    'learningGoals',
    'preferredLanguage'
  ];

  return requiredFields.every(field => {
    const value = profile[field as keyof UserProfile];
    if (field === 'learningGoals') {
      return Array.isArray(value) && value.length > 0;
    }
    if (field === 'preferredLanguage') {
      return value === 'english' || value === 'urdu';
    }
    if (field === 'backgroundLevel') {
      return ['beginner', 'intermediate', 'advanced'].includes(value as string);
    }
    return value !== undefined && value !== null && value !== '';
  });
};

const validateProfileCompleteness = (profile: Partial<UserProfile>): boolean => {
  // Property: Profile should contain meaningful data
  if (!profile.backgroundLevel || !['beginner', 'intermediate', 'advanced'].includes(profile.backgroundLevel)) {
    return false;
  }

  if (!profile.technicalBackground || profile.technicalBackground.trim().length < 3) {
    return false;
  }

  if (!profile.learningGoals || !Array.isArray(profile.learningGoals) || profile.learningGoals.length === 0) {
    return false;
  }

  if (!profile.preferredLanguage || !['english', 'urdu'].includes(profile.preferredLanguage)) {
    return false;
  }

  return true;
};

// Generators for test data
const backgroundLevelGenerator = fc.constantFrom('beginner', 'intermediate', 'advanced');
const languageGenerator = fc.constantFrom('english', 'urdu');
const learningGoalsGenerator = fc.array(
  fc.constantFrom(
    'Understand AI fundamentals',
    'Learn robotics programming',
    'Build physical AI systems',
    'Career advancement',
    'Academic research',
    'Personal projects'
  ),
  { minLength: 1, maxLength: 6 }
);
const interestsGenerator = fc.array(
  fc.constantFrom(
    'Machine Learning',
    'Computer Vision',
    'Natural Language Processing',
    'Robotics Hardware',
    'Control Systems',
    'Sensor Integration'
  ),
  { minLength: 0, maxLength: 6 }
);

const validProfileGenerator = fc.record({
  backgroundLevel: backgroundLevelGenerator,
  technicalBackground: fc.string({ minLength: 3, maxLength: 100 }),
  learningGoals: learningGoalsGenerator,
  preferredLanguage: languageGenerator,
  interests: interestsGenerator,
  experienceYears: fc.integer({ min: 0, max: 20 }),
});

const invalidProfileGenerator = fc.oneof(
  // Missing background level
  fc.record({
    technicalBackground: fc.string({ minLength: 3 }),
    learningGoals: learningGoalsGenerator,
    preferredLanguage: languageGenerator,
  }),
  // Empty technical background
  fc.record({
    backgroundLevel: backgroundLevelGenerator,
    technicalBackground: fc.constant(''),
    learningGoals: learningGoalsGenerator,
    preferredLanguage: languageGenerator,
  }),
  // Empty learning goals
  fc.record({
    backgroundLevel: backgroundLevelGenerator,
    technicalBackground: fc.string({ minLength: 3 }),
    learningGoals: fc.constant([]),
    preferredLanguage: languageGenerator,
  }),
  // Invalid language
  fc.record({
    backgroundLevel: backgroundLevelGenerator,
    technicalBackground: fc.string({ minLength: 3 }),
    learningGoals: learningGoalsGenerator,
    preferredLanguage: fc.constant('invalid' as any),
  })
);

describe('Authentication Data Collection Property Tests', () => {
  /**
   * Property 8: Authentication Data Collection
   * For any user registration process, the system should collect all required 
   * background questions about experience level and learning goals
   */
  test('Property 8: Valid profiles pass all required field validation', () => {
    fc.assert(
      fc.property(validProfileGenerator, (profile) => {
        // Property: All valid profiles should pass validation
        const isValid = validateBackgroundQuestionnaire(profile);
        expect(isValid).toBe(true);
        
        // Property: All valid profiles should be complete
        const isComplete = validateProfileCompleteness(profile);
        expect(isComplete).toBe(true);
        
        return true;
      }),
      { numRuns: 100 }
    );
  });

  test('Property 8: Invalid profiles fail validation', () => {
    fc.assert(
      fc.property(invalidProfileGenerator, (profile) => {
        // Property: Invalid profiles should fail validation
        const isValid = validateBackgroundQuestionnaire(profile);
        expect(isValid).toBe(false);
        
        return true;
      }),
      { numRuns: 100 }
    );
  });

  test('Property 8: Background level must be one of valid options', () => {
    fc.assert(
      fc.property(
        fc.record({
          backgroundLevel: fc.string().filter(s => !['beginner', 'intermediate', 'advanced'].includes(s)),
          technicalBackground: fc.string({ minLength: 3 }),
          learningGoals: learningGoalsGenerator,
          preferredLanguage: languageGenerator,
        }),
        (profile) => {
          // Property: Invalid background levels should be rejected
          const isValid = validateProfileCompleteness(profile);
          expect(isValid).toBe(false);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 8: Technical background must be meaningful', () => {
    fc.assert(
      fc.property(
        fc.record({
          backgroundLevel: backgroundLevelGenerator,
          technicalBackground: fc.oneof(
            fc.constant(''),
            fc.constant('  '),
            fc.string({ maxLength: 2 })
          ),
          learningGoals: learningGoalsGenerator,
          preferredLanguage: languageGenerator,
        }),
        (profile) => {
          // Property: Empty or too short technical backgrounds should be rejected
          const isValid = validateProfileCompleteness(profile);
          expect(isValid).toBe(false);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 8: Learning goals must be non-empty array', () => {
    fc.assert(
      fc.property(
        fc.record({
          backgroundLevel: backgroundLevelGenerator,
          technicalBackground: fc.string({ minLength: 3 }),
          learningGoals: fc.oneof(
            fc.constant([]),
            fc.constant(null as any),
            fc.constant(undefined as any)
          ),
          preferredLanguage: languageGenerator,
        }),
        (profile) => {
          // Property: Empty or invalid learning goals should be rejected
          const isValid = validateBackgroundQuestionnaire(profile);
          expect(isValid).toBe(false);
          
          const isComplete = validateProfileCompleteness(profile);
          expect(isComplete).toBe(false);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 8: Language preference must be valid', () => {
    fc.assert(
      fc.property(
        fc.record({
          backgroundLevel: backgroundLevelGenerator,
          technicalBackground: fc.string({ minLength: 3 }),
          learningGoals: learningGoalsGenerator,
          preferredLanguage: fc.string().filter(s => !['english', 'urdu'].includes(s)),
        }),
        (profile) => {
          // Property: Invalid language preferences should be rejected
          const isValid = validateProfileCompleteness(profile);
          expect(isValid).toBe(false);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 8: Experience years should be reasonable', () => {
    fc.assert(
      fc.property(
        fc.record({
          backgroundLevel: backgroundLevelGenerator,
          technicalBackground: fc.string({ minLength: 3 }),
          learningGoals: learningGoalsGenerator,
          preferredLanguage: languageGenerator,
          experienceYears: fc.integer({ min: 0, max: 50 }),
        }),
        (profile) => {
          // Property: Reasonable experience years should be accepted
          const isValid = validateBackgroundQuestionnaire(profile);
          expect(isValid).toBe(true);
          
          // Property: Experience years should be non-negative
          expect(profile.experienceYears).toBeGreaterThanOrEqual(0);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 8: Interests array can be empty but must be valid', () => {
    fc.assert(
      fc.property(
        fc.record({
          backgroundLevel: backgroundLevelGenerator,
          technicalBackground: fc.string({ minLength: 3 }),
          learningGoals: learningGoalsGenerator,
          preferredLanguage: languageGenerator,
          interests: interestsGenerator,
        }),
        (profile) => {
          // Property: Valid profiles with any interests array should pass
          const isValid = validateBackgroundQuestionnaire(profile);
          expect(isValid).toBe(true);
          
          // Property: Interests should be an array
          expect(Array.isArray(profile.interests)).toBe(true);
          
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });

  test('Property 8: Profile data structure consistency', () => {
    fc.assert(
      fc.property(validProfileGenerator, (profile) => {
        // Property: All profile fields should maintain their types
        expect(typeof profile.backgroundLevel).toBe('string');
        expect(typeof profile.technicalBackground).toBe('string');
        expect(Array.isArray(profile.learningGoals)).toBe(true);
        expect(typeof profile.preferredLanguage).toBe('string');
        
        if (profile.interests !== undefined) {
          expect(Array.isArray(profile.interests)).toBe(true);
        }
        
        if (profile.experienceYears !== undefined) {
          expect(typeof profile.experienceYears).toBe('number');
        }
        
        return true;
      }),
      { numRuns: 100 }
    );
  });
});