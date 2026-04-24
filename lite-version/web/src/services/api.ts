/**
 * API服务 - 基础配置和工具函数
 * 基于axios的API客户端，带token自动注入和错误处理
 */
import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// localStorage键名
const AUTH_TOKEN_KEY = 'zu_an_auth_token';

/**
 * 获取存储的token
 */
export function getStoredToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * 保存token
 */
export function saveToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

/**
 * 清除token
 */
export function clearToken(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

// 请求拦截器 - 添加认证token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getStoredToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: unknown) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误
apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    const axiosError = error as AxiosError;
    if (axiosError.response?.status === 401) {
      // Token过期或无效，清除认证状态
      clearToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * API错误类
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public code?: string | number,
    public statusCode?: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * 处理API响应，提取data字段
 * @param response axios响应对象
 * @returns 响应中的data数据
 */
export function handleApiResponse<T>(response: { data: T }): T {
  return response.data;
}

/**
 * 处理API错误
 * @param error axios错误对象
 * @throws ApiError 转换后的API错误
 */
export function handleApiError(error: unknown): never {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ message?: string; detail?: string }>;
    const message = axiosError.response?.data?.message
      || axiosError.response?.data?.detail
      || axiosError.message
      || '请求失败';
    throw new ApiError(
      message,
      axiosError.code,
      axiosError.response?.status
    );
  }
  throw new ApiError('未知错误');
}
