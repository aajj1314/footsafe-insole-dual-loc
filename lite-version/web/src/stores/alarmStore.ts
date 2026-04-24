/**
 * 报警状态管理 - Zustand Store
 * 使用 persist 中间件进行状态持久化
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Alarm, AlarmType, AlarmStatus } from '@/types';
import * as alarmService from '@/services/alarm';
import type { GetAlarmsParams } from '@/services/alarm';

export interface AlarmState {
  alarms: Alarm[];
  currentAlarm: Alarm | null;
  total: number;
  unprocessedCount: number;
  isLoading: boolean;
  error: string | null;
  initialized: boolean;
  filter: {
    type: AlarmType | 'all';
    status: AlarmStatus | 'all';
    deviceImei?: string;
  };

  // Actions
  fetchAlarms: (params?: GetAlarmsParams) => Promise<void>;
  fetchAlarm: (alarmId: string) => Promise<void>;
  handleAlarm: (alarmId: string) => Promise<void>;
  ignoreAlarm: (alarmId: string) => Promise<void>;
  updateAlarmStatus: (alarmId: string, status: AlarmStatus) => void;
  setFilter: (filter: Partial<AlarmState['filter']>) => void;
  setCurrentAlarm: (alarm: Alarm | null) => void;
  clearError: () => void;
  clearAlarms: () => void;
  refreshUnprocessedCount: () => void;
}

export const useAlarmStore = create<AlarmState>()(
  persist(
    (set, get) => ({
      // 初始状态
      alarms: [],
      currentAlarm: null,
      total: 0,
      unprocessedCount: 0,
      isLoading: false,
      error: null,
      initialized: false,
      filter: {
        type: 'all',
        status: 'all',
        deviceImei: undefined,
      },

      /**
       * 获取报警列表
       * @param params 查询参数（设备IMEI、报警类型、状态等）
       */
      fetchAlarms: async (params?: GetAlarmsParams) => {
        set({ isLoading: true, error: null });
        try {
          const { filter } = get();
          const queryParams: GetAlarmsParams = {
            ...params,
            device_imei: params?.device_imei || filter.deviceImei,
            alarm_type: params?.alarm_type ?? (filter.type === 'all' ? undefined : filter.type as unknown as number),
            status: params?.status ?? (filter.status === 'all' ? undefined : filter.status),
          };

          const response = await alarmService.getAlarms(queryParams);
          const unprocessedCount = response.alarms.filter(
            (alarm) => alarm.status === 'pending' || alarm.status === 'processing'
          ).length;

          set({
            alarms: response.alarms,
            total: response.total,
            unprocessedCount,
            isLoading: false,
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : '获取报警记录失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 获取报警详情
       * @param alarmId 报警ID
       */
      fetchAlarm: async (alarmId: string) => {
        set({ isLoading: true, error: null });
        try {
          const alarm = await alarmService.getAlarm(alarmId);
          set({ currentAlarm: alarm, isLoading: false });
        } catch (error) {
          const message = error instanceof Error ? error.message : '获取报警详情失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 处理报警
       * @param alarmId 报警ID
       */
      handleAlarm: async (alarmId: string) => {
        set({ isLoading: true, error: null });
        try {
          await alarmService.handleAlarm(alarmId);
          set((state) => {
            const updatedAlarms = state.alarms.map((alarm) =>
              alarm.id === alarmId ? { ...alarm, status: 'resolved' as AlarmStatus } : alarm
            );
            const unprocessedCount = updatedAlarms.filter(
              (alarm) => alarm.status === 'pending' || alarm.status === 'processing'
            ).length;
            return {
              alarms: updatedAlarms,
              currentAlarm:
                state.currentAlarm?.id === alarmId
                  ? { ...state.currentAlarm, status: 'resolved' as AlarmStatus }
                  : state.currentAlarm,
              unprocessedCount,
              isLoading: false,
            };
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : '处理报警失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 忽略报警
       * @param alarmId 报警ID
       */
      ignoreAlarm: async (alarmId: string) => {
        set({ isLoading: true, error: null });
        try {
          await alarmService.ignoreAlarm(alarmId);
          set((state) => {
            const updatedAlarms = state.alarms.map((alarm) =>
              alarm.id === alarmId ? { ...alarm, status: 'ignored' as AlarmStatus } : alarm
            );
            const unprocessedCount = updatedAlarms.filter(
              (alarm) => alarm.status === 'pending' || alarm.status === 'processing'
            ).length;
            return {
              alarms: updatedAlarms,
              currentAlarm:
                state.currentAlarm?.id === alarmId
                  ? { ...state.currentAlarm, status: 'ignored' as AlarmStatus }
                  : state.currentAlarm,
              unprocessedCount,
              isLoading: false,
            };
          });
        } catch (error) {
          const message = error instanceof Error ? error.message : '忽略报警失败';
          set({
            error: message,
            isLoading: false,
          });
          throw error;
        }
      },

      /**
       * 更新报警状态（本地状态更新）
       * @param alarmId 报警ID
       * @param status 新状态
       */
      updateAlarmStatus: (alarmId: string, status: AlarmStatus) => {
        set((state) => {
          const updatedAlarms = state.alarms.map((alarm) =>
            alarm.id === alarmId ? { ...alarm, status } : alarm
          );
          const unprocessedCount = updatedAlarms.filter(
            (alarm) => alarm.status === 'pending' || alarm.status === 'processing'
          ).length;
          return {
            alarms: updatedAlarms,
            currentAlarm:
              state.currentAlarm?.id === alarmId
                ? { ...state.currentAlarm, status }
                : state.currentAlarm,
            unprocessedCount,
          };
        });
      },

      /**
       * 设置筛选条件
       * @param filter 筛选条件（报警类型、状态、设备IMEI）
       */
      setFilter: (filter: Partial<AlarmState['filter']>) => {
        set((state) => ({
          filter: { ...state.filter, ...filter },
        }));
      },

      /**
       * 设置当前查看的报警
       * @param alarm 报警对象或null
       */
      setCurrentAlarm: (alarm: Alarm | null) => {
        set({ currentAlarm: alarm });
      },

      /**
       * 清除错误信息
       */
      clearError: () => {
        set({ error: null });
      },

      /**
       * 清除报警列表（退出登录时调用）
       */
      clearAlarms: () => {
        set({
          alarms: [],
          currentAlarm: null,
          total: 0,
          unprocessedCount: 0,
          error: null,
        });
      },

      /**
       * 刷新未处理报警数量
       */
      refreshUnprocessedCount: () => {
        const { alarms } = get();
        const unprocessedCount = alarms.filter(
          (alarm) => alarm.status === 'pending' || alarm.status === 'processing'
        ).length;
        set({ unprocessedCount });
      },
    }),
    {
      name: 'zu-an-alarm-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        alarms: state.alarms,
        total: state.total,
        unprocessedCount: state.unprocessedCount,
      }), // 只持久化这些字段
    }
  )
);
