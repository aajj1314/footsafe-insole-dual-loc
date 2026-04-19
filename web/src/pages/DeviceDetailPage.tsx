/**
 * 设备详情页面
 */
import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Battery,
  Signal,
  Thermometer,
  Settings,
  RefreshCw,
  MapPin,
  Clock,
  Cpu,
  ShieldAlert,
  Activity,
  ChevronRight,
} from 'lucide-react';
import { useDeviceStore } from '@/stores/deviceStore';
import { setDeviceMode } from '@/services/device';
import type { DeviceMode } from '@/types';

export default function DeviceDetailPage() {
  const { deviceId } = useParams<{ deviceId: string }>();
  const navigate = useNavigate();
  const { currentDevice, fetchDevice, isLoading } = useDeviceStore();
  const [mode, setMode] = useState<DeviceMode>('normal');

  useEffect(() => {
    if (deviceId) {
      fetchDevice(deviceId);
    }
  }, [deviceId, fetchDevice]);

  useEffect(() => {
    if (currentDevice) {
      setMode(currentDevice.mode);
    }
  }, [currentDevice]);

  const handleModeChange = async (newMode: DeviceMode) => {
    setMode(newMode);
    if (deviceId) {
      try {
        const backendMode = newMode === 'power_save' ? 'low_power' : newMode;
        await setDeviceMode(deviceId, backendMode as 'normal' | 'low_power' | 'alarm' | 'sleep');
      } catch (error) {
        console.error('更新设备模式失败:', error);
        setMode(currentDevice?.mode || 'normal');
      }
    }
  };

  if (isLoading && !currentDevice) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)] animate-pulse">
          <div className="h-8 bg-[var(--color-bg-tertiary)] rounded w-1/3 mb-4" />
          <div className="space-y-3">
            <div className="h-4 bg-[var(--color-bg-tertiary)] rounded w-2/3" />
            <div className="h-4 bg-[var(--color-bg-tertiary)] rounded w-1/2" />
          </div>
        </div>
      </div>
    );
  }

  if (!currentDevice) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up">
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-[var(--color-border)] text-center">
          <p className="text-[var(--color-text-muted)]">设备不存在</p>
          <Link to="/" className="text-[var(--color-primary)] hover:underline mt-2 inline-block">
            返回首页
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up">
      {/* 页面标题 */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="p-2 rounded-xl hover:bg-[var(--color-bg-tertiary)] transition-colors"
        >
          <ArrowLeft className="w-6 h-6 text-[var(--color-text-secondary)]" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
            {currentDevice.nickname || `设备 ${currentDevice.imei.slice(-4)}`}
          </h1>
          <p className="text-sm text-[var(--color-text-muted)] font-mono">{currentDevice.imei}</p>
        </div>
      </div>

      {/* 设备信息卡片 */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)]">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">设备信息</h2>
          <button
            onClick={() => fetchDevice(deviceId!)}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-tertiary)] transition-colors"
            disabled={isLoading}
          >
            <RefreshCw className={`w-5 h-5 text-[var(--color-text-muted)] ${isLoading ? 'animate-refresh-spin' : ''}`} />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <InfoItem label="设备型号" value={currentDevice.model || '--'} icon={Cpu} />
          <InfoItem label="固件版本" value={currentDevice.firmwareVersion || '--'} icon={Settings} />
          <InfoItem label="硬件版本" value={currentDevice.hardwareVersion || '--'} icon={Cpu} />
          <InfoItem label="IMEI" value={currentDevice.imei} icon={Settings} mono />
          <InfoItem
            label="注册时间"
            value={new Date(currentDevice.createdAt).toLocaleDateString('zh-CN')}
            icon={Clock}
          />
          <InfoItem
            label="最后在线"
            value={new Date(currentDevice.lastSeen).toLocaleString('zh-CN')}
            icon={Clock}
          />
        </div>
      </div>

      {/* 设备状态卡片 */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)]">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-6">设备状态</h2>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <StatusCard
            label="电量"
            value={`${currentDevice.battery}%`}
            icon={Battery}
            status={currentDevice.battery < 20 ? 'danger' : currentDevice.battery < 50 ? 'warning' : 'success'}
          />
          <StatusCard
            label="信号"
            value={`${currentDevice.signalStrength}%`}
            icon={Signal}
            status="primary"
          />
          <StatusCard
            label="温度"
            value={currentDevice.temperature ? `${currentDevice.temperature}°C` : '--'}
            icon={Thermometer}
            status={currentDevice.temperature && currentDevice.temperature > 45 ? 'danger' : 'success'}
          />
          <StatusCard
            label="工作模式"
            value={currentDevice.mode === 'normal' ? '正常' : currentDevice.mode === 'power_save' ? '省电' : '追踪'}
            icon={Activity}
            status="primary"
          />
        </div>

        {/* 电量进度条 */}
        <div className="mb-6">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-[var(--color-text-muted)]">电量使用情况</span>
            <span className="text-[var(--color-text-primary)] font-medium">{currentDevice.battery}%</span>
          </div>
          <div className="h-3 bg-[var(--color-bg-tertiary)] rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                currentDevice.battery < 20
                  ? 'bg-[var(--color-danger)]'
                  : currentDevice.battery < 50
                  ? 'bg-[var(--color-warning)]'
                  : 'bg-[var(--color-success)]'
              }`}
              style={{ width: `${currentDevice.battery}%` }}
            />
          </div>
        </div>

        {/* 信号强度进度条 */}
        <div>
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-[var(--color-text-muted)]">信号强度</span>
            <span className="text-[var(--color-text-primary)] font-medium">{currentDevice.signalStrength}%</span>
          </div>
          <div className="h-3 bg-[var(--color-bg-tertiary)] rounded-full overflow-hidden">
            <div
              className="h-full bg-[var(--color-primary)] rounded-full transition-all duration-500"
              style={{ width: `${currentDevice.signalStrength}%` }}
            />
          </div>
        </div>
      </div>

      {/* 设备操作卡片 */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)]">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-6">设备操作</h2>

        <div className="space-y-4">
          {/* 设置工作模式 */}
          <div className="p-4 bg-[var(--color-bg-secondary)] rounded-xl">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-[var(--color-primary)]" />
                <span className="text-sm font-medium text-[var(--color-text-primary)]">设置工作模式</span>
              </div>
            </div>
            <div className="flex gap-2">
              {[
                { value: 'normal', label: '正常模式' },
                { value: 'power_save', label: '省电模式' },
                { value: 'tracking', label: '追踪模式' },
              ].map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleModeChange(option.value as DeviceMode)}
                  className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    mode === option.value
                      ? 'bg-[var(--color-primary)] text-white shadow-md'
                      : 'bg-white text-[var(--color-text-secondary)] border border-[var(--color-border)] hover:bg-[var(--color-bg-tertiary)]'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {/* 快速操作 */}
          <div className="grid grid-cols-2 gap-4">
            <Link
              to={`/map?device=${deviceId}`}
              className="flex items-center gap-3 p-4 bg-[var(--color-bg-secondary)] rounded-xl hover:bg-[var(--color-bg-tertiary)] transition-colors"
            >
              <MapPin className="w-5 h-5 text-[var(--color-primary)]" />
              <span className="text-sm font-medium text-[var(--color-text-primary)]">查看位置</span>
              <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)] ml-auto" />
            </Link>
            <Link
              to={`/fence?device=${deviceId}`}
              className="flex items-center gap-3 p-4 bg-[var(--color-bg-secondary)] rounded-xl hover:bg-[var(--color-bg-tertiary)] transition-colors"
            >
              <ShieldAlert className="w-5 h-5 text-[var(--color-success)]" />
              <span className="text-sm font-medium text-[var(--color-text-primary)]">电子围栏</span>
              <ChevronRight className="w-4 h-4 text-[var(--color-text-muted)] ml-auto" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * 信息项组件
 */
function InfoItem({
  label,
  value,
  icon: Icon,
  mono = false,
}: {
  label: string;
  value: string;
  icon: React.ElementType;
  mono?: boolean;
}) {
  return (
    <div className="flex items-start gap-3 p-3 bg-[var(--color-bg-secondary)] rounded-xl">
      <Icon className="w-5 h-5 text-[var(--color-text-muted)] mt-0.5" />
      <div>
        <p className="text-xs text-[var(--color-text-muted)]">{label}</p>
        <p className={`text-sm font-medium text-[var(--color-text-primary)] ${mono ? 'font-mono' : ''}`}>
          {value}
        </p>
      </div>
    </div>
  );
}

/**
 * 状态卡片组件
 */
function StatusCard({
  label,
  value,
  icon: Icon,
  status,
}: {
  label: string;
  value: string;
  icon: React.ElementType;
  status: 'success' | 'warning' | 'danger' | 'primary';
}) {
  const statusColors = {
    success: 'text-[var(--color-success)]',
    warning: 'text-[var(--color-warning)]',
    danger: 'text-[var(--color-danger)]',
    primary: 'text-[var(--color-primary)]',
  };

  return (
    <div className="p-4 bg-[var(--color-bg-secondary)] rounded-xl">
      <Icon className={`w-5 h-5 ${statusColors[status]} mb-2`} />
      <p className="text-xs text-[var(--color-text-muted)]">{label}</p>
      <p className="text-lg font-bold text-[var(--color-text-primary)]">{value}</p>
    </div>
  );
}