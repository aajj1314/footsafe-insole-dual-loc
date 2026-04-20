/**
 * 设备状态管理 - Zustand Store
 * 使用 persist 中间件进行状态持久化
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Device, GPSLocation, DeviceStatus } from '@/types';
import * as deviceService from '@/services/device';
import type { BindDeviceRequest } from '@/services/device';

export interface DeviceState {
  devices: Device[];
  currentDevice: Device | null;
  total: number;
  isLoading: boolean;
  error: string | null;
  initialized: boolean;

  // Actions
  fetchDevices: () => Promise<void>;
  fetchDevice: (deviceImei: string) => Promise<void>;
  bindDevice: (data: BindDeviceRequest) => Promise<Device>;
  unbindDevice: (deviceImei: string) => Promise<void>;
  setDeviceMode: (deviceImei: string, mode: 'normal' | 'power_save' | 'tracking') => Promise<void>;
  updateDeviceStatus: (deviceId: string, status: DeviceStatus) => void;
  updateDeviceLocation: (deviceId: string, location: GPSLocation) => void;
  setCurrentDevice: (device: Device | null) => void;
  clearError: () => void;
  clearDevices: () => void;
}

export const useDeviceStore = create<DeviceState>()(
  persist(
    (set, _get) => ({
      // 初始状态
      devices: [],
      currentDevice: null,
      total: 0,
      isLoading: false,
      error: null,
      initialized: false,

      /**
       * 获取设备列表
       * 从服务层获取并正确解构 {devices: [], total} 响应
       */
      fetchDevices: async () => {
        set({ isLoading: true, error: null });
        try {
          const response = await deviceService.getDevices();
          set({
            devices: response.devices,
            total: response.total,
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : '获取设备列表失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 获取设备详情
       * @param deviceImei 设备IMEI号
       */
      fetchDevice: async (deviceImei: string) => {
        set({ isLoading: true, error: null });
        try {
          const device = await deviceService.getDevice(deviceImei);
          set({ currentDevice: device, isLoading: false });
        } catch (error) {
          const message = error instanceof Error ? error.message : '获取设备信息失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 绑定设备
       * @param data 绑定请求参数（设备IMEI、昵称、关系）
       */
      bindDevice: async (data: BindDeviceRequest): Promise<Device> => {
        set({ isLoading: true, error: null });
        try {
          const device = await deviceService.bindDevice(data);
          set((state) => ({
            devices: [...state.devices, device],
            total: state.total + 1,
            isLoading: false,
          }));
          return device;
        } catch (error) {
          const message = error instanceof Error ? error.message : '绑定设备失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 解绑设备
       * @param deviceImei 设备IMEI号
       */
      unbindDevice: async (deviceImei: string) => {
        set({ isLoading: true, error: null });
        try {
          await deviceService.unbindDevice(deviceImei);
          set((state) => ({
            devices: state.devices.filter((d) => d.imei !== deviceImei),
            total: Math.max(0, state.total - 1),
            currentDevice:
              state.currentDevice?.imei === deviceImei ? null : state.currentDevice,
            isLoading: false,
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : '解绑设备失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 设置设备工作模式
       * @param deviceImei 设备IMEI号
       * @param mode 工作模式（normal/power_save/tracking）
       */
      setDeviceMode: async (
        deviceImei: string,
        mode: 'normal' | 'power_save' | 'tracking'
      ) => {
        set({ isLoading: true, error: null });
        try {
          await deviceService.setDeviceMode(deviceImei, mode);
          set((state) => ({
            devices: state.devices.map((device) =>
              device.imei === deviceImei ? { ...device, mode } : device
            ),
            currentDevice:
              state.currentDevice?.imei === deviceImei
                ? { ...state.currentDevice, mode }
                : state.currentDevice,
            isLoading: false,
          }));
        } catch (error) {
          const message = error instanceof Error ? error.message : '设置设备模式失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 更新设备状态（本地状态更新，用于实时更新）
       * @param deviceId 设备ID
       * @param status 设备状态
       */
      updateDeviceStatus: (deviceId: string, status: DeviceStatus) => {
        set((state) => ({
          devices: state.devices.map((device) =>
            device.id === deviceId ? { ...device, status } : device
          ),
          currentDevice:
            state.currentDevice?.id === deviceId
              ? { ...state.currentDevice, status }
              : state.currentDevice,
        }));
      },

      /**
       * 更新设备位置（本地状态更新，用于实时更新）
       * @param deviceId 设备ID
       * @param location GPS位置信息
       */
      updateDeviceLocation: (deviceId: string, location: GPSLocation) => {
        set((state) => ({
          devices: state.devices.map((device) =>
            device.id === deviceId ? { ...device, lastLocation: location } : device
          ),
          currentDevice:
            state.currentDevice?.id === deviceId
              ? { ...state.currentDevice, lastLocation: location }
              : state.currentDevice,
        }));
      },

      /**
       * 设置当前选中的设备
       * @param device 设备对象或null
       */
      setCurrentDevice: (device: Device | null) => {
        set({ currentDevice: device });
      },

      /**
       * 清除错误信息
       */
      clearError: () => {
        set({ error: null });
      },

      /**
       * 清除设备列表（退出登录时调用）
       */
      clearDevices: () => {
        set({
          devices: [],
          currentDevice: null,
          total: 0,
          error: null,
        });
      },
    }),
    {
      name: 'zu-an-device-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        devices: state.devices,
        currentDevice: state.currentDevice,
        total: state.total,
      }), // 只持久化这些字段
    }
  )
);
