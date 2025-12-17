// Application constants and configuration

export const API_ENDPOINTS = {
  AUTH: '/api/v1/auth',
  RAG: '/api/v1/rag',
  TRANSLATION: '/api/v1/translation',
  PERSONALIZATION: '/api/v1/personalization',
  CONTENT: '/api/v1/content',
  HEALTH: '/health',
} as const;

export const SUPPORTED_LANGUAGES = {
  ENGLISH: 'english',
  URDU: 'urdu',
} as const;

export const USER_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
} as const;

export const CONTENT_TYPES = {
  TEXT: 'text',
  CODE: 'code',
  DIAGRAM: 'diagram',
  FORMULA: 'formula',
  VIDEO: 'video',
  INTERACTIVE: 'interactive',
} as const;

export const AI_MODELS = {
  CLAUDE: 'claude-3-sonnet',
  OPENAI: 'gpt-4-turbo',
  EMBEDDING: 'text-embedding-ada-002',
} as const;

export const CACHE_KEYS = {
  USER_PROFILE: 'user_profile',
  CHAPTER_CONTENT: 'chapter_content',
  TRANSLATION: 'translation',
  PERSONALIZATION: 'personalization',
  RAG_RESPONSE: 'rag_response',
} as const;

export const ERROR_CODES = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  AI_SERVICE_ERROR: 'AI_SERVICE_ERROR',
  DATABASE_ERROR: 'DATABASE_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
  RATE_LIMIT_ERROR: 'RATE_LIMIT_ERROR',
} as const;

export const DEFAULT_CONFIG = {
  API_TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
  CACHE_TTL: 3600, // 1 hour
  MAX_CONTENT_LENGTH: 50000,
  MAX_QUERY_LENGTH: 1000,
  PAGINATION_LIMIT: 20,
} as const;

export const ROUTES = {
  HOME: '/',
  DOCS: '/docs',
  CHAPTER: '/chapter',
  PROFILE: '/profile',
  LOGIN: '/login',
  REGISTER: '/register',
} as const;