/**
 * 类型定义 - 足安智能防走失系统Web前端
 */

// 设备状态
export type DeviceStatus = 'online' | 'offline' | 'alarm';

// 报警类型
export type AlarmType =
  | 'fall'           // 摔倒报警
  | 'tamper'         // 防拆报警
  | 'still'          // 静止报警
  | 'low_battery'    // 低电量报警
  | 'sos'            // SOS报警
  | 'shutdown';;     // 关机报警

// 报警级别
export type AlarmLevel = 'low' | 'medium' | 'high' | 'urgent';

// 报警状态
export type AlarmStatus = 'pending' | 'processing' | 'resolved' | 'ignored';

// 工作模式
export type DeviceMode = 'normal' | 'power_save' | 'tracking';

// 用户信息
export interface User {
  id: string;
  username: string;
  phone?: string;
  avatar?: string;
  createdAt: string;
}

// 设备信息
export interface Device {
  id: string;
  imei: string;
  userId?: string;
  nickname?: string;
  model?: string;
  firmwareVersion?: string;
  hardwareVersion?: string;
  status: DeviceStatus;
  battery: number;
  signalStrength: number;
  temperature?: number;
  mode: DeviceMode;
  lastLocation?: GPSLocation;
  lastSeen: string;
  createdAt: string;
  updatedAt: string;
}

// GPS位置信息
export interface GPSLocation {
  latitude: number;
  longitude: number;
  altitude?: number;
  speed?: number;
  direction?: number;
  accuracy?: number;
  satellites?: number;
  gpsTimestamp?: string;
}

// 报警记录
export interface Alarm {
  id: string;
  deviceId: string;
  device?: Device;
  alarmType: AlarmType;
  alarmLevel: AlarmLevel;
  status: AlarmStatus;
  location?: GPSLocation;
  battery?: number;
  alarmData?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

// 电子围栏
export interface Fence {
  id: string;
  name: string;
  deviceId: string;
  type: 'circle' | 'rectangle';
  center?: GPSLocation;      // 圆形围栏中心
  radius?: number;           // 圆形围栏半径(米)
  bounds?: {                // 矩形围栏边界
    northEast: GPSLocation;
    southWest: GPSLocation;
  };
  enabled: boolean;
  alarmEnabled: boolean;
  createdAt: string;
  updatedAt: string;
}

// 围栏报警
export interface FenceAlarm {
  id: string;
  fenceId: string;
  deviceId: string;
  alarmType: 'enter' | 'exit';
  location: GPSLocation;
  createdAt: string;
}

// 紧急联系人
export interface Contact {
  id: string;
  userId: string;
  name: string;
  phone: string;
  relationship?: string;
  isEmergency: boolean;
  createdAt: string;
  updatedAt: string;
}

// 设备命令
export interface DeviceCommand {
  commandId: string;
  deviceId: string;
  commandType: string;
  params?: Record<string, unknown>;
  result?: 'success' | 'failed';
  resultData?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

// 地图标记点
export interface MapMarker {
  id: string;
  position: GPSLocation;
  title?: string;
  description?: string;
  type: 'device' | 'fence' | 'alarm';
  icon?: string;
}

// 轨迹点
export interface TrackPoint extends GPSLocation {
  timestamp: string;
}

// 认证相关
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  phone?: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

// API响应
export interface ApiResponse<T> {
  code: number;
  message: string;
  data?: T;
}

// 分页
export interface Pagination {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

export interface PaginatedResponse<T> {
  list: T[];
  pagination: Pagination;
}