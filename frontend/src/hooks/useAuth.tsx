import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '../services/api';
import { User, LoginForm, RegisterForm } from '../types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (data: LoginForm) => Promise<void>;
  register: (data: RegisterForm) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const isAuthenticated = !!user && !!localStorage.getItem('access_token');

  useEffect(() => {
    const initializeAuth = () => {
      // Check if user is already logged in
      const token = localStorage.getItem('access_token');
      if (token) {
        // Set a dummy user for now - in production you'd validate the token
        setUser({
          id: 1,
          email: 'demo@vulnpatch.ai',
          full_name: 'Demo User',
          role: 'user',
          is_active: true,
          created_at: new Date().toISOString(),
        });
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (data: LoginForm): Promise<void> => {
    try {
      const response = await authAPI.login(data);
      localStorage.setItem('access_token', response.access_token);
      
      // Set user data based on login email
      setUser({
        id: 1,
        email: data.email,
        full_name: data.email === 'demo@vulnpatch.ai' ? 'Demo User' : 'User',
        role: 'user',
        is_active: true,
        created_at: new Date().toISOString(),
      });
    } catch (error) {
      throw error;
    }
  };

  const register = async (data: RegisterForm): Promise<void> => {
    try {
      const user = await authAPI.register(data);
      setUser(user);
    } catch (error) {
      throw error;
    }
  };

  const logout = (): void => {
    localStorage.removeItem('access_token');
    setUser(null);
    authAPI.logout().catch(console.error);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    login,
    register,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};