import React, { createContext, useContext, useEffect, useState } from 'react';
import { AuthState, AuthTokens, User } from '../types/auth';
import { authService } from '../services/authService';

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedTokens = localStorage.getItem('psx_auth_tokens');
      const storedUser = localStorage.getItem('psx_auth_user');

      if (storedTokens && storedUser) {
        try {
          setTokens(JSON.parse(storedTokens));
          setUser(JSON.parse(storedUser));
          // Always refresh live user state and role from backend
          const me = await authService.getMe();
          if (me && me.user) {
            setUser(me.user);
            localStorage.setItem('psx_auth_user', JSON.stringify(me.user));
          }
        } catch {
          localStorage.removeItem('psx_auth_tokens');
          localStorage.removeItem('psx_auth_user');
          setUser(null);
          setTokens(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const data = await authService.login(email, password);
    setUser(data.user);
    setTokens(data.tokens);
    localStorage.setItem('psx_auth_tokens', JSON.stringify(data.tokens));
    localStorage.setItem('psx_auth_user', JSON.stringify(data.user));
  };

  const register = async (email: string, password: string, fullName: string) => {
    const data = await authService.register(email, password, fullName);
    setUser(data.user);
    setTokens(data.tokens);
    localStorage.setItem('psx_auth_tokens', JSON.stringify(data.tokens));
    localStorage.setItem('psx_auth_user', JSON.stringify(data.user));
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch {
      // Ignored
    } finally {
      localStorage.removeItem('psx_auth_tokens');
      localStorage.removeItem('psx_auth_user');
      setUser(null);
      setTokens(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        tokens,
        isAuthenticated: !!tokens && !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};