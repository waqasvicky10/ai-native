// Authentication layout component
import React, { useState } from 'react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';

interface AuthLayoutProps {
  initialMode?: 'login' | 'register';
  onSuccess?: () => void;
  redirectTo?: string;
  showModeSwitch?: boolean;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({
  initialMode = 'login',
  onSuccess,
  redirectTo,
  showModeSwitch = true,
}) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);

  const handleSuccess = () => {
    onSuccess?.();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Physical AI & Robotics
          </h1>
          <p className="text-lg text-gray-600">
            AI-Native Learning Platform
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        {mode === 'login' ? (
          <LoginForm
            onSuccess={handleSuccess}
            onSwitchToRegister={showModeSwitch ? () => setMode('register') : undefined}
            redirectTo={redirectTo}
          />
        ) : (
          <RegisterForm
            onSuccess={handleSuccess}
            onSwitchToLogin={showModeSwitch ? () => setMode('login') : undefined}
            redirectTo={redirectTo}
          />
        )}
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <div className="text-sm text-gray-500">
          <p>
            By signing up, you agree to our{' '}
            <a href="/terms" className="text-blue-600 hover:text-blue-500">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-blue-600 hover:text-blue-500">
              Privacy Policy
            </a>
          </p>
        </div>
        
        <div className="mt-4 text-xs text-gray-400">
          <p>© 2024 Physical AI & Robotics. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};