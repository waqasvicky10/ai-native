// JWT token utilities
import { SignJWT, jwtVerify, JWTPayload as JoseJWTPayload } from 'jose';

const JWT_SECRET = new TextEncoder().encode(
  process.env.NEXTAUTH_SECRET || 'development_secret_key'
);

export interface CustomJWTPayload extends JoseJWTPayload {
  userId: string;
  email: string;
}

export class JWTUtils {
  static async signToken(payload: CustomJWTPayload, expiresIn: string = '7d'): Promise<string> {
    const jwt = new SignJWT(payload as JoseJWTPayload)
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime(expiresIn);

    return await jwt.sign(JWT_SECRET);
  }

  static async verifyToken(token: string): Promise<CustomJWTPayload | null> {
    try {
      const { payload } = await jwtVerify(token, JWT_SECRET);
      return payload as CustomJWTPayload;
    } catch (error) {
      console.error('JWT verification failed:', error);
      return null;
    }
  }

  static async refreshToken(token: string): Promise<string | null> {
    const payload = await this.verifyToken(token);

    if (!payload) {
      return null;
    }

    // Create new token with extended expiration
    const newPayload: CustomJWTPayload = {
      userId: payload.userId,
      email: payload.email,
    };

    return await this.signToken(newPayload);
  }

  static isTokenExpired(token: string): boolean {
    try {
      const [, payloadBase64] = token.split('.');
      const payload = JSON.parse(atob(payloadBase64));
      const currentTime = Math.floor(Date.now() / 1000);

      return payload.exp < currentTime;
    } catch (error) {
      return true;
    }
  }

  static getTokenPayload(token: string): CustomJWTPayload | null {
    try {
      const [, payloadBase64] = token.split('.');
      const payload = JSON.parse(atob(payloadBase64));
      return payload as CustomJWTPayload;
    } catch (error) {
      return null;
    }
  }
}