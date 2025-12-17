// User progress tracking service
import { LearningProgress, Bookmark, ApiResponse } from '../types/index';

export interface ProgressUpdate {
  chapterId: string;
  timeSpent: number;
  completed?: boolean;
  assessmentScore?: number;
}

export interface BookmarkData {
  chapterId: string;
  section: string;
  note?: string;
}

export class UserProgressService {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.apiKey = process.env.NEXT_PUBLIC_API_KEY;
  }

  async getProgress(userId: string): Promise<ApiResponse<LearningProgress>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/progress/${userId}`, {
        headers: {
          ...this.getAuthHeaders(),
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Failed to get progress',
          timestamp: new Date(),
        };
      }

      return {
        success: true,
        data,
        timestamp: new Date(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date(),
      };
    }
  }

  async updateProgress(userId: string, update: ProgressUpdate): Promise<ApiResponse<LearningProgress>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/progress/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
        body: JSON.stringify(update),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Failed to update progress',
          timestamp: new Date(),
        };
      }

      return {
        success: true,
        data,
        timestamp: new Date(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date(),
      };
    }
  }

  async markChapterComplete(userId: string, chapterId: string): Promise<ApiResponse<LearningProgress>> {
    return this.updateProgress(userId, {
      chapterId,
      timeSpent: 0,
      completed: true,
    });
  }

  async addBookmark(userId: string, bookmarkData: BookmarkData): Promise<ApiResponse<Bookmark>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/progress/${userId}/bookmarks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...this.getAuthHeaders(),
        },
        body: JSON.stringify(bookmarkData),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Failed to add bookmark',
          timestamp: new Date(),
        };
      }

      return {
        success: true,
        data,
        timestamp: new Date(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date(),
      };
    }
  }

  async removeBookmark(userId: string, bookmarkId: string): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/progress/${userId}/bookmarks/${bookmarkId}`, {
        method: 'DELETE',
        headers: {
          ...this.getAuthHeaders(),
        },
      });

      if (!response.ok) {
        const data = await response.json();
        return {
          success: false,
          error: data.message || 'Failed to remove bookmark',
          timestamp: new Date(),
        };
      }

      return {
        success: true,
        timestamp: new Date(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date(),
      };
    }
  }

  async getBookmarks(userId: string): Promise<ApiResponse<Bookmark[]>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/progress/${userId}/bookmarks`, {
        headers: {
          ...this.getAuthHeaders(),
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Failed to get bookmarks',
          timestamp: new Date(),
        };
      }

      return {
        success: true,
        data,
        timestamp: new Date(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date(),
      };
    }
  }

  async recordAssessmentScore(
    userId: string, 
    chapterId: string, 
    score: number
  ): Promise<ApiResponse<LearningProgress>> {
    return this.updateProgress(userId, {
      chapterId,
      timeSpent: 0,
      assessmentScore: score,
    });
  }

  async getChapterProgress(userId: string, chapterId: string): Promise<ApiResponse<{
    completed: boolean;
    timeSpent: number;
    assessmentScore?: number;
    bookmarks: Bookmark[];
  }>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/progress/${userId}/chapters/${chapterId}`, {
        headers: {
          ...this.getAuthHeaders(),
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Failed to get chapter progress',
          timestamp: new Date(),
        };
      }

      return {
        success: true,
        data,
        timestamp: new Date(),
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        timestamp: new Date(),
      };
    }
  }

  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};
    
    // Get token from localStorage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }
    
    return headers;
  }
}