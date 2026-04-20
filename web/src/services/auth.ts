/**
 * 认证服务 - 用户登录注册
 * 登录：POST /api/auth/login → {access_token, user}
 * 注册：POST /api/auth/register → {access_token, user}
 * 当前用户：GET /api/auth/me → User
 */
import { apiClient, handleApiResponse, saveToken, clearToken, getStoredToken } from './api';
import type { User } from '@/types';

// 重新导出 api 中的 getStoredToken 以便其他模块使用
export { getStoredToken };

const CURRENT_USER_KEY = 'zu_an_current_user';

/**
 * 登录请求参数
 */
export interface LoginRequest {
  username: string;
  password: string;
}

/**
 * 注册请求参数
 */
export interface RegisterRequest {
  username: string;
  password: string;
  phone?: string;
}

/**
 * 认证响应（后端返回）
 */
export interface AuthResponse {
  access_token: string;
  user: User;
}

/**
 * 后端用户数据结构
 */
export interface BackendUser {
  id: number;
  username: string;
  phone?: string;
  avatar?: string;
  created_at: string;
}

/**
 * 转换后端用户数据为前端格式
 * @param backendUser 后端用户数据（下划线命名）
 * @returns 前端用户数据（驼峰命名）
 */
function convertBackendUser(backendUser: BackendUser): User {
  return {
    id: String(backendUser.id),
    username: backendUser.username,
    phone: backendUser.phone,
    avatar: backendUser.avatar,
    createdAt: backendUser.created_at || new Date().toISOString(),
  };
}

/**
 * 保存用户信息到本地
 * @param user 用户对象
 */
function saveUser(user: User): void {
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
}

/**
 * 获取本地存储的当前用户（同步）
 * @returns 本地存储的用户对象，如果不存在则返回null
 */
export function getStoredUser(): User | null {
  const stored = localStorage.getItem(CURRENT_USER_KEY);
  return stored ? JSON.parse(stored) : null;
}

/**
 * 用户登录
 * @param credentials 登录凭证（用户名和密码）
 * @returns 认证响应（包含access_token和user）
 * @throws ApiError 登录失败时抛出错误
 */
export async function login(credentials: LoginRequest): Promise<AuthResponse> {
  const response = await apiClient.post('/auth/login', credentials);
  const result = handleApiResponse<AuthResponse>(response);

  // 保存token和用户信息
  if (result.access_token) {
    saveToken(result.access_token);
    saveUser(result.user);
  }

  return result;
}

/**
 * 用户注册
 * @param data 注册信息（用户名、密码、可选手机号）
 * @returns 认证响应（包含access_token和user）
 * @throws ApiError 注册失败时抛出错误
 */
export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await apiClient.post('/auth/register', data);
  const result = handleApiResponse<AuthResponse>(response);

  // 保存token和用户信息
  if (result.access_token) {
    saveToken(result.access_token);
    saveUser(result.user);
  }

  return result;
}

/**
 * 获取当前用户信息
 * @returns 当前用户信息，如果未登录或token无效则返回null
 * @throws ApiError 请求失败时抛出错误
 */
export async function getCurrentUser(): Promise<User | null> {
  const token = getStoredToken();
  if (!token) {
    return null;
  }

  try {
    const response = await apiClient.get('/auth/me');
    const backendUser = handleApiResponse<BackendUser>(response);
    const user = convertBackendUser(backendUser);
    saveUser(user);
    return user;
  } catch {
    // token无效，清除认证状态
    clearToken();
    localStorage.removeItem(CURRENT_USER_KEY);
    return null;
  }
}

/**
 * 退出登录
 * 清除本地存储的token和用户信息
 */
export async function logout(): Promise<void> {
  clearToken();
  localStorage.removeItem(CURRENT_USER_KEY);

  try {
    await apiClient.post('/auth/logout');
  } catch {
    // 忽略退出登录接口的错误
  }
}
