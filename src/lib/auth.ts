// Authentication configuration using NextAuth
import { NextAuthOptions } from 'next-auth';
import { JWT } from 'next-auth/jwt';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';
import { User, UserProfile } from '../types/index';

// Extend the built-in session types
declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      email: string;
      name?: string;
      image?: string;
      profile?: UserProfile;
    };
  }

  interface User {
    id: string;
    email: string;
    name?: string;
    image?: string;
    profile?: UserProfile;
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id: string;
    profile?: UserProfile;
  }
}

export const authOptions: NextAuthOptions = {
  providers: [
    // Credentials provider for email/password authentication
    CredentialsProvider({
      id: 'credentials',
      name: 'credentials',
      credentials: {
        email: {
          label: 'Email',
          type: 'email',
          placeholder: 'your-email@example.com',
        },
        password: {
          label: 'Password',
          type: 'password',
        },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null;
        }

        try {
          // TODO: Replace with actual database authentication
          // For now, we'll use a placeholder implementation
          const user = await authenticateUser(credentials.email, credentials.password);
          
          if (user) {
            return {
              id: user.id,
              email: user.email,
              name: user.profile?.technicalBackground || user.email.split('@')[0],
              profile: user.profile,
            };
          }
          
          return null;
        } catch (error) {
          console.error('Authentication error:', error);
          return null;
        }
      },
    }),

    // Google OAuth provider
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || '',
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
    }),

    // GitHub OAuth provider
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID || '',
      clientSecret: process.env.GITHUB_CLIENT_SECRET || '',
    }),
  ],

  pages: {
    signIn: '/auth/signin',
    error: '/auth/error',
  },

  callbacks: {
    async jwt({ token, user, account }) {
      // Persist the OAuth access_token and user id to the token right after signin
      if (account && user) {
        token.id = user.id;
        token.profile = user.profile;
      }
      return token;
    },

    async session({ session, token }) {
      // Send properties to the client
      if (token && session.user) {
        session.user.id = token.id;
        session.user.profile = token.profile;
      }
      return session;
    },

    async signIn({ user, account, profile }) {
      // Handle OAuth sign-in
      if (account?.provider === 'google' || account?.provider === 'github') {
        try {
          // Check if user exists in database, create if not
          const existingUser = await findUserByEmail(user.email!);
          
          if (!existingUser) {
            // Create new user with default profile
            await createUser({
              email: user.email!,
              name: user.name || '',
              image: user.image || '',
              provider: account.provider,
              providerId: account.providerAccountId,
            });
          }
          
          return true;
        } catch (error) {
          console.error('Sign-in error:', error);
          return false;
        }
      }
      
      return true;
    },
  },

  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },

  jwt: {
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },

  secret: process.env.NEXTAUTH_SECRET,

  debug: process.env.NODE_ENV === 'development',
};

// Placeholder authentication functions (to be implemented with actual database)
async function authenticateUser(email: string, password: string): Promise<User | null> {
  // TODO: Implement actual password verification with database
  // This is a placeholder implementation
  console.log('Authenticating user:', email);
  
  // For development, accept any email/password combination
  if (process.env.NODE_ENV === 'development') {
    return {
      id: `user_${Date.now()}`,
      email,
      profile: {
        id: `profile_${Date.now()}`,
        backgroundLevel: 'beginner',
        learningGoals: [],
        preferredLanguage: 'english',
        technicalBackground: 'Student',
        interests: [],
      },
      preferences: {
        language: 'english',
        contentPersonalization: true,
        chatbotEnabled: true,
        notificationsEnabled: true,
        theme: 'light',
        autoTranslate: false,
      },
      progress: {
        completedChapters: [],
        currentChapter: '',
        timeSpent: 0,
        assessmentScores: {},
        bookmarks: [],
        lastAccessedAt: new Date(),
      },
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }
  
  return null;
}

async function findUserByEmail(email: string): Promise<User | null> {
  // TODO: Implement actual database lookup
  console.log('Finding user by email:', email);
  return null;
}

async function createUser(userData: {
  email: string;
  name: string;
  image: string;
  provider: string;
  providerId: string;
}): Promise<User> {
  // TODO: Implement actual database user creation
  console.log('Creating user:', userData);
  
  return {
    id: `user_${Date.now()}`,
    email: userData.email,
    profile: {
      id: `profile_${Date.now()}`,
      backgroundLevel: 'beginner',
      learningGoals: [],
      preferredLanguage: 'english',
      technicalBackground: userData.name || 'Student',
      interests: [],
    },
    preferences: {
      language: 'english',
      contentPersonalization: true,
      chatbotEnabled: true,
      notificationsEnabled: true,
      theme: 'light',
      autoTranslate: false,
    },
    progress: {
      completedChapters: [],
      currentChapter: '',
      timeSpent: 0,
      assessmentScores: {},
      bookmarks: [],
      lastAccessedAt: new Date(),
    },
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}