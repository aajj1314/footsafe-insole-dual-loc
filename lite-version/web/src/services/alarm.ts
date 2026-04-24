/**
 * 报警服务
 * 报警列表：GET /api/alarms/ → {alarms:[], total}
 * 报警处理：PUT /api/alarms/{id}/handle → {message}
 * 报警忽略：PUT /api/alarms/{id}/ignore → {message}
 */
import { apiClient, handleApiResponse } from './api';
import type { Alarm, AlarmType, AlarmLevel, AlarmStatus, GPSLocation } from '@/types';

/**
 * 后端报警响应数据结构（下划线命名）
 */
export interface BackendAlarm {
  id: number;
  alarm_id: string;
  device_id: string;
  alarm_type: number;
  alarm_level: number;
  latitude?: string;
  longitude?: string;
  altitude?: string;
  speed?: string;
  direction?: string;
  accuracy?: string;
  satellites?: number;
  battery?: number;
  status: string;
  alarm_data?: string;
  created_at?: string;
  updated_at?: string;
}

/**
 * 后端报警列表响应
 */
export interface BackendAlarmListResponse {
  alarms: BackendAlarm[];
  total: number;
}

/**
 * 报警类型映射（数字 -> 字符串）
 */
const ALARM_TYPE_NUM_TO_STRING: Record<number, AlarmType> = {
  1: 'tamper',
  2: 'fall',
  3: 'still',
  4: 'low_battery',
  5: 'sos',
  6: 'shutdown',
};

/**
 * 报警级别映射（数字 -> 字符串）
 */
const ALARM_LEVEL_NUM_TO_STRING: Record<number, AlarmLevel> = {
  1: 'low',
  2: 'medium',
  3: 'high',
  4: 'urgent',
};

/**
 * 转换后端报警数据为前端格式
 * @param backendAlarm 后端报警数据（下划线命名）
 * @returns 前端报警数据（驼峰命名）
 */
function convertBackendAlarm(backendAlarm: BackendAlarm): Alarm {
  let location: GPSLocation | undefined;

  if (backendAlarm.latitude && backendAlarm.longitude) {
    location = {
      latitude: parseFloat(backendAlarm.latitude),
      longitude: parseFloat(backendAlarm.longitude),
      altitude: backendAlarm.altitude ? parseFloat(backendAlarm.altitude) : undefined,
      speed: backendAlarm.speed ? parseFloat(backendAlarm.speed) : undefined,
      direction: backendAlarm.direction ? parseInt(backendAlarm.direction) : undefined,
      accuracy: backendAlarm.accuracy ? parseFloat(backendAlarm.accuracy) : undefined,
      satellites: backendAlarm.satellites,
    };
  }

  return {
    id: String(backendAlarm.id),
    deviceId: backendAlarm.device_id,
    alarmType: ALARM_TYPE_NUM_TO_STRING[backendAlarm.alarm_type] || 'fall',
    alarmLevel: ALARM_LEVEL_NUM_TO_STRING[backendAlarm.alarm_level] || 'medium',
    status: backendAlarm.status as AlarmStatus,
    location,
    battery: backendAlarm.battery,
    alarmData: backendAlarm.alarm_data ? JSON.parse(backendAlarm.alarm_data) : undefined,
    createdAt: backendAlarm.created_at || new Date().toISOString(),
    updatedAt: backendAlarm.updated_at || backendAlarm.created_at || new Date().toISOString(),
  };
}

/**
 * 报警查询参数
 */
export interface GetAlarmsParams {
  device_imei?: string;
  alarm_type?: number;
  status?: string;
  start_time?: string;
  end_time?: string;
  limit?: number;
  offset?: number;
}

/**
 * 报警类型映射配置
 */
export const ALARM_TYPE_MAP: Record<number, { label: string; icon: string; color: string }> = {
  1: { label: '防拆报警', icon: '🔓', color: '#F97316' },
  2: { label: '摔倒报警', icon: '⚠️', color: '#EF4444' },
  3: { label: '静止报警', icon: '🛑', color: '#F59E0B' },
  4: { label: '低电量报警', icon: '🔋', color: '#10B981' },
  5: { label: 'SOS报警', icon: '🆘', color: '#EF4444' },
  6: { label: '关机报警', icon: '⏻', color: '#64748B' },
};

/**
 * 报警类型字符串映射
 */
const ALARM_TYPE_STRING_MAP: Record<string, string> = {
  'tamper': '防拆报警',
  'fall': '摔倒报警',
  'still': '静止报警',
  'low_battery': '低电量报警',
  'sos': 'SOS报警',
  'shutdown': '关机报警',
};

/**
 * 报警级别映射配置
 */
export const ALARM_LEVEL_MAP: Record<number, { label: string; color: string }> = {
  1: { label: '低', color: '#10B981' },
  2: { label: '中', color: '#3B82F6' },
  3: { label: '高', color: '#F59E0B' },
  4: { label: '紧急', color: '#EF4444' },
};

/**
 * 报警级别字符串映射
 */
const ALARM_LEVEL_STRING_MAP: Record<string, string> = {
  'low': '低',
  'medium': '中',
  'high': '高',
  'urgent': '紧急',
};

/**
 * 报警状态映射
 */
export const ALARM_STATUS_MAP: Record<string, { label: string; color: string }> = {
  pending: { label: '待处理', color: '#F59E0B' },
  processing: { label: '处理中', color: '#3B82F6' },
  resolved: { label: '已处理', color: '#10B981' },
  ignored: { label: '已忽略', color: '#64748B' },
};

/**
 * 获取报警类型标签
 * @param type 报警类型（数字或字符串）
 * @returns 报警类型标签
 */
export function getAlarmTypeLabel(type: number | string): string {
  if (typeof type === 'string') {
    return ALARM_TYPE_STRING_MAP[type] || '未知报警';
  }
  return ALARM_TYPE_MAP[type]?.label || '未知报警';
}

/**
 * 获取报警类型图标
 * @param type 报警类型（数字或字符串）
 * @returns 报警类型图标
 */
export function getAlarmTypeIcon(type: number | string): string {
  if (typeof type === 'string') {
    const labels: Record<string, string> = {
      'tamper': '🔓', 'fall': '⚠️', 'still': '🛑',
      'low_battery': '🔋', 'sos': '🆘', 'shutdown': '⏻',
    };
    return labels[type] || '❓';
  }
  return ALARM_TYPE_MAP[type]?.icon || '❓';
}

/**
 * 获取报警类型颜色
 * @param type 报警类型（数字或字符串）
 * @returns 报警类型颜色
 */
export function getAlarmTypeColor(type: number | string): string {
  if (typeof type === 'string') {
    const colors: Record<string, string> = {
      'tamper': '#F97316', 'fall': '#EF4444', 'still': '#F59E0B',
      'low_battery': '#10B981', 'sos': '#EF4444', 'shutdown': '#64748B',
    };
    return colors[type] || '#64748B';
  }
  return ALARM_TYPE_MAP[type]?.color || '#64748B';
}

/**
 * 获取报警级别标签
 * @param level 报警级别（数字或字符串）
 * @returns 报警级别标签
 */
export function getAlarmLevelLabel(level: number | string): string {
  if (typeof level === 'string') {
    return ALARM_LEVEL_STRING_MAP[level] || '未知';
  }
  return ALARM_LEVEL_MAP[level]?.label || '未知';
}

/**
 * 获取报警级别颜色
 * @param level 报警级别（数字或字符串）
 * @returns 报警级别颜色
 */
export function getAlarmLevelColor(level: number | string): string {
  if (typeof level === 'string') {
    const colors: Record<string, string> = {
      'low': '#10B981', 'medium': '#3B82F6', 'high': '#F59E0B', 'urgent': '#EF4444',
    };
    return colors[level] || '#64748B';
  }
  return ALARM_LEVEL_MAP[level]?.color || '#64748B';
}

/**
 * 获取报警状态标签
 * @param status 报警状态
 * @returns 报警状态标签
 */
export function getAlarmStatusLabel(status: string): string {
  return ALARM_STATUS_MAP[status]?.label || '未知';
}

/**
 * 获取报警状态颜色
 * @param status 报警状态
 * @returns 报警状态颜色
 */
export function getAlarmStatusColor(status: string): string {
  return ALARM_STATUS_MAP[status]?.color || '#64748B';
}

/**
 * 获取报警列表
 * @param params 查询参数
 * @returns 报警列表和总数
 * @throws ApiError 请求失败时抛出错误
 */
export async function getAlarms(params: GetAlarmsParams = {}): Promise<{ alarms: Alarm[]; total: number }> {
  const response = await apiClient.get('/alarms/', { params });
  const backendResponse = handleApiResponse<BackendAlarmListResponse>(response);
  return {
    alarms: backendResponse.alarms.map(convertBackendAlarm),
    total: backendResponse.total,
  };
}

/**
 * 获取报警详情
 * @param alarmId 报警ID
 * @returns 报警详情
 * @throws ApiError 请求失败时抛出错误
 */
export async function getAlarm(alarmId: string): Promise<Alarm> {
  const response = await apiClient.get(`/alarms/${alarmId}`);
  const backendAlarm = handleApiResponse<BackendAlarm>(response);
  return convertBackendAlarm(backendAlarm);
}

/**
 * 处理报警
 * @param alarmId 报警ID
 * @returns 操作结果消息
 * @throws ApiError 请求失败时抛出错误
 */
export async function handleAlarm(alarmId: string): Promise<{ message: string }> {
  const response = await apiClient.put(`/alarms/${alarmId}/handle`);
  return handleApiResponse<{ message: string }>(response);
}

/**
 * 忽略报警
 * @param alarmId 报警ID
 * @returns 操作结果消息
 * @throws ApiError 请求失败时抛出错误
 */
export async function ignoreAlarm(alarmId: string): Promise<{ message: string }> {
  const response = await apiClient.put(`/alarms/${alarmId}/ignore`);
  return handleApiResponse<{ message: string }>(response);
}

/**
 * 更新报警状态
 * @param alarmId 报警ID
 * @param status 新状态（resolved/ignored）
 * @throws ApiError 请求失败时抛出错误
 */
export async function updateAlarmStatus(alarmId: string, status: string): Promise<void> {
  if (status === 'resolved') {
    await handleAlarm(alarmId);
  } else if (status === 'ignored') {
    await ignoreAlarm(alarmId);
  }
}
