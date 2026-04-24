/**
 * 围栏服务
 * 围栏列表：GET /api/fences/ → {fences:[], total}
 */
import { apiClient, handleApiResponse } from './api';
import type { Fence, FenceAlarm, GPSLocation } from '@/types';

/**
 * 后端围栏响应数据结构（下划线命名）
 */
export interface BackendFence {
  id: number;
  name: string;
  device_imei: string;
  fence_type: 'circle' | 'rectangle';
  // 圆形围栏字段
  center_lat?: string;
  center_lng?: string;
  radius?: string;
  // 矩形围栏字段
  min_lat?: string;
  max_lat?: string;
  min_lng?: string;
  max_lng?: string;
  // 状态字段
  enabled: boolean;
  alarm_enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * 后端围栏列表响应
 */
export interface BackendFenceListResponse {
  fences: BackendFence[];
  total: number;
}

/**
 * 转换后端围栏数据为前端格式
 * @param f 后端围栏数据（下划线命名）
 * @returns 前端围栏数据（驼峰命名）
 */
function convertBackendFence(f: BackendFence): Fence {
  let center: GPSLocation | undefined;
  let bounds: { northEast: GPSLocation; southWest: GPSLocation } | undefined;

  if (f.fence_type === 'circle' && f.center_lat && f.center_lng) {
    center = {
      latitude: parseFloat(f.center_lat),
      longitude: parseFloat(f.center_lng),
    };
  }

  if (f.fence_type === 'rectangle' && f.min_lat && f.max_lat && f.min_lng && f.max_lng) {
    bounds = {
      northEast: {
        latitude: parseFloat(f.max_lat),
        longitude: parseFloat(f.max_lng),
      },
      southWest: {
        latitude: parseFloat(f.min_lat),
        longitude: parseFloat(f.min_lng),
      },
    };
  }

  return {
    id: String(f.id),
    name: f.name,
    deviceId: f.device_imei,
    type: f.fence_type,
    center,
    radius: f.radius ? parseFloat(f.radius) : undefined,
    bounds,
    enabled: f.enabled,
    alarmEnabled: f.alarm_enabled,
    createdAt: f.created_at || new Date().toISOString(),
    updatedAt: f.updated_at || f.created_at || new Date().toISOString(),
  };
}

/**
 * 创建围栏请求参数
 */
export interface CreateFenceParams {
  name: string;
  device_imei: string;
  fence_type: 'circle' | 'rectangle';
  // 圆形围栏参数
  center_lat?: string;
  center_lng?: string;
  radius?: string;
  // 矩形围栏参数
  min_lat?: string;
  max_lat?: string;
  min_lng?: string;
  max_lng?: string;
  enabled?: boolean;
  alarm_enabled?: boolean;
}

/**
 * 更新围栏请求参数
 */
export interface UpdateFenceParams {
  name?: string;
  fence_type?: 'circle' | 'rectangle';
  center_lat?: string;
  center_lng?: string;
  radius?: string;
  min_lat?: string;
  max_lat?: string;
  min_lng?: string;
  max_lng?: string;
  enabled?: boolean;
  alarm_enabled?: boolean;
}

/**
 * 获取围栏列表
 * @param deviceImei 可选的设备IMEI筛选条件
 * @returns 围栏列表和总数
 * @throws ApiError 请求失败时抛出错误
 */
export async function getFences(deviceImei?: string): Promise<{ fences: Fence[]; total: number }> {
  const params = deviceImei ? { device_imei: deviceImei } : {};
  const response = await apiClient.get('/fences/', { params });
  const data = handleApiResponse<BackendFenceListResponse>(response);

  return {
    fences: data.fences.map(convertBackendFence),
    total: data.total,
  };
}

/**
 * 获取围栏详情
 * @param fenceId 围栏ID
 * @returns 围栏详情
 * @throws ApiError 请求失败时抛出错误
 */
export async function getFence(fenceId: string): Promise<Fence> {
  const response = await apiClient.get(`/fences/${fenceId}`);
  const f = handleApiResponse<BackendFence>(response);
  return convertBackendFence(f);
}

/**
 * 创建围栏
 * @param params 围栏参数
 * @returns 创建的围栏信息
 * @throws ApiError 请求失败时抛出错误
 */
export async function createFence(params: CreateFenceParams): Promise<Fence> {
  const response = await apiClient.post('/fences/', params);
  const f = handleApiResponse<BackendFence>(response);
  return convertBackendFence(f);
}

/**
 * 更新围栏
 * @param fenceId 围栏ID
 * @param params 更新参数
 * @returns 更新后的围栏信息
 * @throws ApiError 请求失败时抛出错误
 */
export async function updateFence(fenceId: string, params: UpdateFenceParams): Promise<Fence> {
  const response = await apiClient.put(`/fences/${fenceId}`, params);
  const f = handleApiResponse<BackendFence>(response);
  return convertBackendFence(f);
}

/**
 * 删除围栏
 * @param fenceId 围栏ID
 * @throws ApiError 请求失败时抛出错误
 */
export async function deleteFence(fenceId: string): Promise<void> {
  await apiClient.delete(`/fences/${fenceId}`);
}

/**
 * 获取围栏报警记录（预留接口）
 * @param fenceId 可选的围栏ID筛选条件
 * @returns 围栏报警列表
 */
export async function getFenceAlarms(_fenceId?: string): Promise<FenceAlarm[]> {
  // TODO: 后端API待实现
  return [];
}
