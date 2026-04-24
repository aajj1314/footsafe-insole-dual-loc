/**
 * 位置服务
 * 位置详情：GET /api/locations/{imei}/latest → Location
 * 位置历史：GET /api/locations/{imei}/history → {locations:[], total}
 */
import { apiClient, handleApiResponse } from './api';
import type { GPSLocation } from '@/types';

/**
 * 后端位置响应数据结构（下划线命名）
 */
export interface BackendLocation {
  latitude: string;
  longitude: string;
  altitude?: string;
  speed?: string;
  direction?: string;
  accuracy?: string;
  satellites?: number;
  battery?: number;
  signal_strength?: number;
  mode?: string;
  gps_timestamp?: string;
  created_at?: string;
}

/**
 * 后端位置历史响应
 */
export interface BackendLocationHistoryResponse {
  locations: BackendLocation[];
  total: number;
}

/**
 * 转换后端位置数据为前端格式
 * @param loc 后端位置数据（下划线命名）
 * @returns 前端位置数据（驼峰命名）
 */
function convertBackendLocation(loc: BackendLocation): GPSLocation {
  return {
    latitude: parseFloat(loc.latitude),
    longitude: parseFloat(loc.longitude),
    altitude: loc.altitude ? parseFloat(loc.altitude) : undefined,
    speed: loc.speed ? parseFloat(loc.speed) : undefined,
    direction: loc.direction ? parseInt(loc.direction) : undefined,
    accuracy: loc.accuracy ? parseFloat(loc.accuracy) : undefined,
    satellites: loc.satellites,
    gpsTimestamp: loc.gps_timestamp || loc.created_at,
  };
}

/**
 * 位置历史查询结果
 */
export interface LocationHistoryResult {
  locations: GPSLocation[];
  total: number;
}

/**
 * 位置历史查询参数
 */
export interface LocationHistoryParams {
  start_time?: string;
  end_time?: string;
  limit?: number;
  offset?: number;
}

/**
 * 获取设备最新位置
 * @param deviceImei 设备IMEI号
 * @returns 最新位置信息
 * @throws ApiError 请求失败时抛出错误
 */
export async function getLatestLocation(deviceImei: string): Promise<GPSLocation> {
  const response = await apiClient.get(`/locations/${deviceImei}/latest`);
  const loc = handleApiResponse<BackendLocation>(response);
  return convertBackendLocation(loc);
}

/**
 * 获取设备历史轨迹
 * @param deviceImei 设备IMEI号
 * @param params 查询参数（开始时间、结束时间、限制条数）
 * @returns 历史轨迹位置列表和总数
 * @throws ApiError 请求失败时抛出错误
 */
export async function getLocationHistory(
  deviceImei: string,
  params: LocationHistoryParams = {}
): Promise<LocationHistoryResult> {
  const queryParams: Record<string, string | number> = {};

  if (params.start_time) queryParams.start_time = params.start_time;
  if (params.end_time) queryParams.end_time = params.end_time;
  if (params.limit) queryParams.limit = params.limit;
  if (params.offset) queryParams.offset = params.offset;

  const response = await apiClient.get(`/locations/${deviceImei}/history`, {
    params: queryParams,
  });
  const data = handleApiResponse<BackendLocationHistoryResponse>(response);

  return {
    locations: data.locations.map(convertBackendLocation),
    total: data.total,
  };
}
