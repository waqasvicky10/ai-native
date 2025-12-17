// Base class for all Claude subagents

import { ClaudeSubagent, AITask, AIResponse, TaskContext, AppConfig } from '../types/index';

export abstract class BaseClaudeSubagent implements ClaudeSubagent {
  public readonly name: string;
  public readonly capabilities: string[];
  public readonly version: string;
  
  protected config: AppConfig['ai'];
  protected maxRetries: number = 3;
  protected timeout: number = 30000;

  constructor(
    name: string,
    capabilities: string[],
    version: string,
    config: AppConfig['ai']
  ) {
    this.name = name;
    this.capabilities = capabilities;
    this.version = version;
    this.config = config;
  }

  abstract execute(task: AITask, context: TaskContext): Promise<AIResponse>;

  protected async callClaudeAPI(
    prompt: string,
    systemPrompt?: string,
    maxTokens: number = 4000
  ): Promise<string> {
    // This will be implemented when we add the actual Claude API integration
    // For now, return a placeholder
    throw new Error('Claude API integration not implemented yet');
  }

  protected async callOpenAI(
    prompt: string,
    systemPrompt?: string,
    maxTokens: number = 4000
  ): Promise<string> {
    // This will be implemented when we add the actual OpenAI API integration
    // For now, return a placeholder
    throw new Error('OpenAI API integration not implemented yet');
  }

  protected validateTask(task: AITask, requiredType: string): void {
    if (task.type !== requiredType) {
      throw new Error(`Invalid task type. Expected ${requiredType}, got ${task.type}`);
    }
  }

  protected createResponse(
    taskId: string,
    result: any,
    confidence: number,
    model: string,
    startTime: number,
    metadata?: Record<string, any>
  ): AIResponse {
    return {
      taskId,
      result,
      confidence,
      processingTime: Date.now() - startTime,
      model,
      completedAt: new Date(),
      metadata,
    };
  }

  protected async withErrorHandling<T>(
    operation: () => Promise<T>,
    taskId: string
  ): Promise<T> {
    try {
      return await operation();
    } catch (error) {
      console.error(`Error in subagent ${this.name} for task ${taskId}:`, error);
      throw new Error(`Subagent ${this.name} failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  protected extractTechnicalTerms(content: string): string[] {
    // Simple regex to find technical terms (capitalized words, acronyms, etc.)
    const technicalTermRegex = /\b[A-Z]{2,}|\b[A-Z][a-z]*(?:[A-Z][a-z]*)*\b/g;
    const matches = content.match(technicalTermRegex) || [];
    return [...new Set(matches)]; // Remove duplicates
  }

  protected preserveFormatting(originalContent: string, newContent: string): string {
    // Preserve markdown formatting, code blocks, etc.
    // This is a simplified implementation
    const codeBlockRegex = /```[\s\S]*?```/g;
    const inlineCodeRegex = /`[^`]+`/g;
    
    const codeBlocks = originalContent.match(codeBlockRegex) || [];
    const inlineCodes = originalContent.match(inlineCodeRegex) || [];
    
    let result = newContent;
    
    // This would need more sophisticated logic to properly preserve formatting
    // For now, just return the new content
    return result;
  }

  public getCapabilities(): string[] {
    return [...this.capabilities];
  }

  public getVersion(): string {
    return this.version;
  }

  public getName(): string {
    return this.name;
  }
}