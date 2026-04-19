/**
 * 设备服务
 * 设备列表：GET /api/devices/ → {devices:[], total}
 * 设备详情：GET /api/devices/{imei} → Device
 * 绑定设备：POST /api/devices/bind → Device
 */
import { apiClient, handleApiResponse } from './api';
import type { Device, GPSLocation } from '@/types';

/**
 * 后端设备响应数据结构（下划线命名）
 */
export interface BackendDevice {
  id: number;
  imei: string;
  nickname?: string;
  relation?: string;
  iccid?: string;
  firmware_version?: string;
  hardware_version?: string;
  battery?: number;
  signal_strength?: number;
  mode?: string;
  status?: string;
  last_location_lat?: string;
  last_location_lng?: string;
  last_location_alt?: string;
  last_location_speed?: string;
  last_location_direction?: string;
  last_location_accuracy?: string;
  last_location_time?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * 后端设备列表响应
 */
export interface BackendDeviceListResponse {
  devices: BackendDevice[];
  total: number;
}

/**
 * 转换后端设备数据为前端格式
 * @param d 后端设备数据（下划线命名）
 * @returns 前端设备数据（驼峰命名）
 */
function convertBackendDevice(d: BackendDevice): Device {
  let lastLocation: GPSLocation | undefined;

  if (d.last_location_lat && d.last_location_lng) {
    lastLocation = {
      latitude: parseFloat(d.last_location_lat),
      longitude: parseFloat(d.last_location_lng),
      altitude: d.last_location_alt ? parseFloat(d.last_location_alt) : undefined,
      speed: d.last_location_speed ? parseFloat(d.last_location_speed) : undefined,
      direction: d.last_location_direction ? parseInt(d.last_location_direction) : undefined,
      accuracy: d.last_location_accuracy ? parseFloat(d.last_location_accuracy) : undefined,
    };
  }

  return {
    id: String(d.id),
    imei: d.imei,
    userId: undefined,
    nickname: d.nickname,
    model: d.iccid,
    firmwareVersion: d.firmware_version,
    hardwareVersion: d.hardware_version,
    status: (d.status as Device['status']) || 'offline',
    battery: d.battery ?? 0,
    signalStrength: d.signal_strength ?? 0,
    temperature: undefined,
    mode: (d.mode as Device['mode']) || 'normal',
    lastLocation,
    lastSeen: d.last_location_time || d.created_at || new Date().toISOString(),
    createdAt: d.created_at || new Date().toISOString(),
    updatedAt: d.updated_at || d.created_at || new Date().toISOString(),
  };
}

/**
 * 绑定设备请求参数
 */
export interface BindDeviceRequest {
  device_imei: string;
  nickname?: string;
  relation?: string;
}

/**
 * 获取设备列表
 * @returns 设备列表和总数
 * @throws ApiError 请求失败时抛出错误
 */
export async function getDevices(): Promise<{ devices: Device[]; total: number }> {
  const response = await apiClient.get('/devices/');
  const data = handleApiResponse<BackendDeviceListResponse>(response);
  return {
    devices: data.devices.map(convertBackendDevice),
    total: data.total,
  };
}

/**
 * 获取设备详情
 * @param deviceImei 设备IMEI号
 * @returns 设备详情
 * @throws ApiError 请求失败时抛出错误
 */
export async function getDevice(deviceImei: string): Promise<Device> {
  const response = await apiClient.get(`/devices/${deviceImei}`);
  const d = handleApiResponse<BackendDevice>(response);
  return convertBackendDevice(d);
}

/**
 * 绑定设备
 * @param data 绑定请求参数（设备IMEI、昵称、关系）
 * @returns 绑定后的设备信息
 * @throws ApiError 请求失败时抛出错误
 */
export async function bindDevice(data: BindDeviceRequest): Promise<Device> {
  const response = await apiClient.post('/devices/bind', data);
  const d = handleApiResponse<BackendDevice>(response);
  return convertBackendDevice(d);
}

/**
 * 解绑设备
 * @param deviceImei 设备IMEI号
 * @throws ApiError 请求失败时抛出错误
 */
export async function unbindDevice(deviceImei: string): Promise<void> {
  await apiClient.delete(`/devices/${deviceImei}/unbind`);
}

/**
 * 设置设备工作模式
 * @param deviceImei 设备IMEI号
 * @param mode 工作模式（normal/power_save/tracking）
 * @throws ApiError 请求失败时抛出错误
 */
export async function setDeviceMode(
  deviceImei: string,
  mode: 'normal' | 'power_save' | 'tracking'
): Promise<void> {
  await apiClient.put(`/devices/${deviceImei}/mode`, { mode });
}

/**
 * 设置设备上报间隔
 * @param deviceImei 设备IMEI号
 * @param interval 上报间隔（秒）
 * @throws ApiError 请求失败时抛出错误
 */
export async function setDeviceInterval(
  deviceImei: string,
  interval: number
): Promise<void> {
  await apiClient.put(`/devices/${deviceImei}/interval`, { interval });
}
