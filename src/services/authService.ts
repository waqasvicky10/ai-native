// Authentication service implementation
import { User, UserProfile, UserPreferences, ApiResponse } from '../types/index';

export interface AuthCredentials {
  email: string;
  password: string;
}

export interface SignUpData extends AuthCredentials {
  name?: string;
  profile?: Partial<UserProfile>;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken: string;
}

export class AuthService {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.apiKey = process.env.NEXT_PUBLIC_API_KEY;
  }

  async signUp(signUpData: SignUpData): Promise<ApiResponse<AuthResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'X-API-Key': this.apiKey }),
        },
        body: JSON.stringify(signUpData),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Sign up failed',
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

  async signIn(credentials: AuthCredentials): Promise<ApiResponse<AuthResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/auth/signin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'X-API-Key': this.apiKey }),
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Sign in failed',
          timestamp: new Date(),
        };
      }

      // Store tokens in localStorage
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
      }
      if (data.refreshToken) {
        localStorage.setItem('refresh_token', data.refreshToken);
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

  async signOut(): Promise<ApiResponse<void>> {
    try {
      const token = this.getStoredToken();
      
      if (token) {
        await fetch(`${this.baseUrl}/api/v1/auth/signout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            ...(this.apiKey && { 'X-API-Key': this.apiKey }),
          },
        });
      }

      // Clear stored tokens
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');

      return {
        success: true,
        timestamp: new Date(),
      };
    } catch (error) {
      // Even if the API call fails, clear local tokens
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');

      return {
        success: false,
        error: error instanceof Error ? error.message : 'Sign out error',
        timestamp: new Date(),
      };
    }
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    try {
      const token = this.getStoredToken();
      
      if (!token) {
        return {
          success: false,
          error: 'No authentication token found',
          timestamp: new Date(),
        };
      }

      const response = await fetch(`${this.baseUrl}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          ...(this.apiKey && { 'X-API-Key': this.apiKey }),
        },
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, try to refresh
          const refreshResult = await this.refreshToken();
          if (refreshResult.success) {
            // Retry with new token
            return this.getCurrentUser();
          }
        }

        return {
          success: false,
          error: data.message || 'Failed to get user',
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

  async updateProfile(profileData: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    try {
      const token = this.getStoredToken();
      
      if (!token) {
        return {
          success: false,
          error: 'No authentication token found',
          timestamp: new Date(),
        };
      }

      const response = await fetch(`${this.baseUrl}/api/v1/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          ...(this.apiKey && { 'X-API-Key': this.apiKey }),
        },
        body: JSON.stringify(profileData),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Failed to update profile',
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

  async updatePreferences(preferences: Partial<UserPreferences>): Promise<ApiResponse<UserPreferences>> {
    try {
      const token = this.getStoredToken();
      
      if (!token) {
        return {
          success: false,
          error: 'No authentication token found',
          timestamp: new Date(),
        };
      }

      const response = await fetch(`${this.baseUrl}/api/v1/auth/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          ...(this.apiKey && { 'X-API-Key': this.apiKey }),
        },
        body: JSON.stringify(preferences),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          success: false,
          error: data.message || 'Failed to update preferences',
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

  private async refreshToken(): Promise<ApiResponse<{ token: string; refreshToken: string }>> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        return {
          success: false,
          error: 'No refresh token found',
          timestamp: new Date(),
        };
      }

      const response = await fetch(`${this.baseUrl}/api/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'X-API-Key': this.apiKey }),
        },
        body: JSON.stringify({ refreshToken }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Refresh failed, clear tokens
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        
        return {
          success: false,
          error: data.message || 'Token refresh failed',
          timestamp: new Date(),
        };
      }

      // Store new tokens
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('refresh_token', data.refreshToken);

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

  private getStoredToken(): string | null {
    if (typeof window === 'undefined') {
      return null;
    }
    return localStorage.getItem('auth_token');
  }

  public isAuthenticated(): boolean {
    return !!this.getStoredToken();
  }

  public getAuthHeaders(): Record<string, string> {
    const token = this.getStoredToken();
    const headers: Record<string, string> = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }
    
    return headers;
  }
}