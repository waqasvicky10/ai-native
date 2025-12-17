// Core type definitions for the AI-native textbook system

export interface User {
  id: string;
  email: string;
  name?: string;
  image?: string;
  profile: UserProfile;
  preferences: UserPreferences;
  progress: LearningProgress;
  createdAt: Date;
  updatedAt: Date;
}

export interface UserProfile {
  id: string;
  backgroundLevel: 'beginner' | 'intermediate' | 'advanced';
  learningGoals: string[];
  preferredLanguage: 'english' | 'urdu';
  technicalBackground: string;
  interests: string[];
  experienceYears?: number;
}

export interface UserPreferences {
  language: 'english' | 'urdu';
  contentPersonalization: boolean;
  chatbotEnabled: boolean;
  notificationsEnabled: boolean;
  theme: 'light' | 'dark';
  autoTranslate: boolean;
}

export interface LearningProgress {
  completedChapters: string[];
  currentChapter: string;
  timeSpent: number;
  assessmentScores: Record<string, number>;
  bookmarks: Bookmark[];
  lastAccessedAt: Date;
}

export interface Bookmark {
  id: string;
  chapterId: string;
  section: string;
  note?: string;
  createdAt: Date;
}

export interface ChapterContent {
  id: string;
  title: string;
  content: string;
  metadata: ContentMetadata;
  prerequisites: string[];
  learningObjectives: string[];
  estimatedReadingTime: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

export interface ContentMetadata {
  author: string;
  lastUpdated: Date;
  version: string;
  tags: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  language: string;
  wordCount: number;
}

export interface TranslatedContent {
  originalId: string;
  translatedContent: string;
  language: string;
  qualityScore: number;
  translatedAt: Date;
  preservedTerms: string[];
  translator: 'claude' | 'openai' | 'human';
}

export interface PersonalizedContent {
  originalId: string;
  personalizedContent: string;
  userProfileId: string;
  adaptationLevel: string;
  personalizedAt: Date;
  adaptationReasons: string[];
}

// AI Service Types
export interface AITask {
  id: string;
  type: 'translation' | 'personalization' | 'content_generation' | 'rag_query';
  input: any;
  context: TaskContext;
  priority: 'low' | 'medium' | 'high';
  createdAt: Date;
}

export interface TaskContext {
  userId?: string;
  chapterId?: string;
  sessionId?: string;
  userProfile?: UserProfile;
  additionalContext?: Record<string, any>;
}

export interface AIResponse {
  taskId: string;
  result: any;
  confidence: number;
  processingTime: number;
  model: string;
  completedAt: Date;
  metadata?: Record<string, any>;
}

// RAG System Types
export interface VectorDocument {
  id: string;
  content: string;
  embedding: number[];
  metadata: {
    chapterId: string;
    section: string;
    contentType: 'text' | 'code' | 'diagram' | 'formula';
    language: string;
    difficulty: string;
    tags: string[];
  };
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    chapterId?: string;
    relevantDocuments?: string[];
    confidence?: number;
  };
}

export interface ChatContext {
  userId: string;
  chapterId: string;
  conversationHistory: ChatMessage[];
  relevantDocuments: VectorDocument[];
  sessionId: string;
}

export interface ChatResponse {
  message: string;
  confidence: number;
  sources: VectorDocument[];
  suggestedFollowUps?: string[];
  processingTime: number;
}

// Claude Subagent Types
export interface ClaudeSubagent {
  name: string;
  capabilities: string[];
  version: string;
  execute(task: AITask, context: TaskContext): Promise<AIResponse>;
}

export interface ContentGenerationAgent extends ClaudeSubagent {
  generateChapterContent(topic: string, level: string): Promise<string>;
  createInteractiveExamples(concept: string): Promise<InteractiveComponent>;
  generateAssessments(chapter: ChapterContent): Promise<Assessment[]>;
}

export interface TranslationAgent extends ClaudeSubagent {
  translateToUrdu(content: string, preserveTechnical: boolean): Promise<TranslatedContent>;
  validateTranslationQuality(original: string, translated: string): Promise<QualityScore>;
  adaptCulturalContext(content: string, targetCulture: string): Promise<AdaptedContent>;
}

export interface PersonalizationAgent extends ClaudeSubagent {
  adaptContentLevel(content: string, userLevel: string): Promise<AdaptedContent>;
  generatePersonalizedExamples(concept: string, userBackground: string): Promise<Example[]>;
  createLearningPath(userGoals: string[], currentProgress: LearningProgress): Promise<LearningPath>;
}

// Component Types
export interface InteractiveComponent {
  id: string;
  type: 'quiz' | 'simulation' | 'diagram' | 'code_editor' | 'video';
  props: Record<string, any>;
  metadata: {
    difficulty: string;
    estimatedTime: number;
    learningObjectives: string[];
  };
}

export interface Assessment {
  id: string;
  type: 'multiple_choice' | 'short_answer' | 'coding' | 'essay';
  question: string;
  options?: string[];
  correctAnswer?: string;
  explanation: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  points: number;
}

export interface Example {
  id: string;
  title: string;
  description: string;
  code?: string;
  explanation: string;
  difficulty: string;
  tags: string[];
}

export interface LearningPath {
  id: string;
  userId: string;
  chapters: string[];
  estimatedDuration: number;
  difficulty: string;
  goals: string[];
  createdAt: Date;
}

// Utility Types
export interface QualityScore {
  overall: number;
  accuracy: number;
  fluency: number;
  technicalPreservation: number;
  culturalAdaptation: number;
}

export interface AdaptedContent {
  content: string;
  adaptationLevel: string;
  changes: ContentChange[];
  metadata: {
    originalDifficulty: string;
    targetDifficulty: string;
    adaptationReasons: string[];
  };
}

export interface ContentChange {
  type: 'simplification' | 'elaboration' | 'example_addition' | 'terminology_change';
  originalText: string;
  newText: string;
  reason: string;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: Date;
  userId?: string;
  requestId?: string;
}

// Configuration Types
export interface AppConfig {
  api: {
    baseUrl: string;
    timeout: number;
    retries: number;
  };
  ai: {
    openaiApiKey: string;
    claudeApiKey: string;
    qdrantUrl: string;
    qdrantApiKey?: string;
  };
  database: {
    url: string;
    maxConnections: number;
  };
  auth: {
    secret: string;
    tokenExpiry: number;
  };
  features: {
    chatbotEnabled: boolean;
    translationEnabled: boolean;
    personalizationEnabled: boolean;
  };
}