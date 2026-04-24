/**
 * 状态管理 Store 导出
 * 统一导出所有Zustand store
 */

// 认证状态管理
export { useAuthStore } from './authStore';
export type { AuthState } from './authStore';

// 设备状态管理
export { useDeviceStore } from './deviceStore';
export type { DeviceState } from './deviceStore';

// 报警状态管理
export { useAlarmStore } from './alarmStore';
export type { AlarmState } from './alarmStore';
