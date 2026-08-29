import React, { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, fetchCurrentUser, UserProfile, UserRole } from '../api/client';

export type { UserRole };

export const ROLE_HIERARCHY: Record<UserRole, number> = {
  VIEWER: 1,
  OPERATOR: 2,
  ENGINEER: 3,
  ADMIN: 4,
};

export interface AuthUser {
  username: string;
  role: UserRole;
  name: string;
  title: string;
  token: string;
}

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password?: string) => Promise<void>;
  logout: () => void;
  switchRole: (role: UserRole) => Promise<void>;
  hasRole: (minRole: UserRole) => boolean;
  isLoginModalOpen: boolean;
  openLoginModal: () => void;
  closeLoginModal: () => void;
}

// Preset default demo accounts
export const DEMO_PRESETS: Record<UserRole, { username: string; name: string; title: string; password: string }> = {
  ADMIN: {
    username: 'admin',
    name: 'Dr. Elena Rostova',
    title: 'Principal Reliability Engineer & System Admin',
    password: 'PredictX@Admin2026',
  },
  ENGINEER: {
    username: 'engineer',
    name: 'Marcus Vance',
    title: 'Senior Mechanical Diagnostics Engineer',
    password: 'Engineer@2026',
  },
  OPERATOR: {
    username: 'operator',
    name: 'Sarah Chen',
    title: 'Industrial Control & Telemetry Operator',
    password: 'Operator@2026',
  },
  VIEWER: {
    username: 'viewer',
    name: 'Alex Mercer',
    title: 'Plant Operations Auditor & Viewer',
    password: 'Viewer@2026',
  },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'predictx_jwt_token';
const USER_KEY = 'predictx_user_profile';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(() => {
    try {
      const savedUser = localStorage.getItem(USER_KEY);
      const savedToken = localStorage.getItem(TOKEN_KEY);
      if (savedUser && savedToken) {
        const parsed = JSON.parse(savedUser);
        return { ...parsed, token: savedToken };
      }
    } catch (e) {
      console.error('Error loading saved auth:', e);
    }
    // Default initial session as Engineer for full interactive exploration
    const defaultPreset = DEMO_PRESETS.ENGINEER;
    return {
      username: defaultPreset.username,
      role: 'ENGINEER',
      name: defaultPreset.name,
      title: defaultPreset.title,
      token: 'demo-initial-token',
    };
  });

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState<boolean>(false);

  // Sync token in localStorage
  useEffect(() => {
    if (user?.token) {
      localStorage.setItem(TOKEN_KEY, user.token);
      localStorage.setItem(
        USER_KEY,
        JSON.stringify({
          username: user.username,
          role: user.role,
          name: user.name,
          title: user.title,
        })
      );
    } else {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
  }, [user]);

  const login = async (username: string, password?: string) => {
    setIsLoading(true);
    try {
      const lower = username.toLowerCase();
      const preset = Object.values(DEMO_PRESETS).find(
        (p) => p.username.toLowerCase() === lower
      );
      const pwd = password || (preset ? preset.password : 'PredictX@2026');

      const data = await loginUser(username, pwd);
      setUser({
        username: data.username,
        role: data.role as UserRole,
        name: data.name || (preset ? preset.name : username),
        title: data.title || (preset ? preset.title : 'Plant Staff'),
        token: data.access_token,
      });
      setIsLoginModalOpen(false);
    } catch (err) {
      console.warn('API login failed, falling back to local demo credential token:', err);
      const targetRole: UserRole = (username.toUpperCase() in ROLE_HIERARCHY)
        ? (username.toUpperCase() as UserRole)
        : 'ENGINEER';
      const preset = DEMO_PRESETS[targetRole] || DEMO_PRESETS.ENGINEER;
      setUser({
        username: preset.username,
        role: targetRole,
        name: preset.name,
        title: preset.title,
        token: `mock-jwt-${targetRole.toLowerCase()}-${Date.now()}`,
      });
      setIsLoginModalOpen(false);
    } finally {
      setIsLoading(false);
    }
  };

  const switchRole = async (targetRole: UserRole) => {
    const preset = DEMO_PRESETS[targetRole];
    if (preset) {
      await login(preset.username, preset.password);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  const hasRole = (minRole: UserRole): boolean => {
    if (!user) return false;
    const userLevel = ROLE_HIERARCHY[user.role] || 0;
    const requiredLevel = ROLE_HIERARCHY[minRole] || 99;
    return userLevel >= requiredLevel;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        switchRole,
        hasRole,
        isLoginModalOpen,
        openLoginModal: () => setIsLoginModalOpen(true),
        closeLoginModal: () => setIsLoginModalOpen(false),
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
