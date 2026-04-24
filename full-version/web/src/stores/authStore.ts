/**
 * 认证状态管理 - Zustand Store
 * 使用 persist 中间件进行状态持久化
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User, LoginRequest, RegisterRequest } from '@/types';
import * as authService from '@/services/auth';

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  initialized: boolean;

  // Actions
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  checkAuth: () => Promise<void>;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始状态
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      initialized: false,

      /**
       * 用户登录
       * @param credentials 登录凭证（用户名和密码）
       */
      login: async (credentials: LoginRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login(credentials);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : '登录失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 用户注册
       * @param data 注册信息（用户名、密码、可选手机号）
       */
      register: async (data: RegisterRequest) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.register(data);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : '注册失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 退出登录
       * 清除本地认证状态
       */
      logout: () => {
        authService.logout();
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },

      /**
       * 清除错误信息
       */
      clearError: () => {
        set({ error: null });
      },

      /**
       * 检查认证状态
       * 验证本地token是否仍然有效
       */
      checkAuth: async () => {
        const { token } = get();
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        try {
          const user = await authService.getCurrentUser();
          if (user) {
            set({ user, isAuthenticated: true });
          } else {
            set({ user: null, token: null, isAuthenticated: false });
          }
        } catch {
          set({ user: null, token: null, isAuthenticated: false });
        }
      },

      /**
       * 初始化认证状态
       * 从本地存储恢复状态
       */
      initialize: () => {
        const user = authService.getStoredUser();
        const token = authService.getStoredToken();
        set({
          user,
          token,
          isAuthenticated: !!token,
          initialized: true,
        });
      },
    }),
    {
      name: 'zu-an-auth-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }), // 只持久化这些字段
    }
  )
);
