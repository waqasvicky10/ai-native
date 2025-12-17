// Abstract AI service interface and base implementation

import { AITask, AIResponse, TaskContext, AppConfig } from '../types/index';

export abstract class BaseAIService {
  protected config: AppConfig['ai'];
  protected retryAttempts: number = 3;
  protected timeout: number = 30000;

  constructor(config: AppConfig['ai']) {
    this.config = config;
  }

  abstract execute(task: AITask, context: TaskContext): Promise<AIResponse>;

  protected async withRetry<T>(
    operation: () => Promise<T>,
    attempts: number = this.retryAttempts
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      if (attempts > 1) {
        await this.delay(1000 * (this.retryAttempts - attempts + 1));
        return this.withRetry(operation, attempts - 1);
      }
      throw error;
    }
  }

  protected delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  protected generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  protected validateInput(input: any, requiredFields: string[]): void {
    for (const field of requiredFields) {
      if (!input[field]) {
        throw new Error(`Missing required field: ${field}`);
      }
    }
  }
}

export interface AIServiceFactory {
  createTranslationService(): BaseAIService;
  createPersonalizationService(): BaseAIService;
  createContentGenerationService(): BaseAIService;
  createRAGService(): BaseAIService;
}

export class DefaultAIServiceFactory implements AIServiceFactory {
  constructor(private config: AppConfig) {}

  createTranslationService(): BaseAIService {
    // Implementation will be added in translation service task
    throw new Error('Translation service not implemented yet');
  }

  createPersonalizationService(): BaseAIService {
    // Implementation will be added in personalization service task
    throw new Error('Personalization service not implemented yet');
  }

  createContentGenerationService(): BaseAIService {
    // Implementation will be added in content generation service task
    throw new Error('Content generation service not implemented yet');
  }

  createRAGService(): BaseAIService {
    // Implementation will be added in RAG service task
    throw new Error('RAG service not implemented yet');
  }
}