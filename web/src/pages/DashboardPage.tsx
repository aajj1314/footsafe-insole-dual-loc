/**
 * 监控首页 - 设备状态总览
 */
import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Battery,
  Signal,
  Thermometer,
  MapPin,
  Clock,
  AlertTriangle,
  RefreshCw,
  ChevronRight,
  Activity,
  ShieldAlert,
} from 'lucide-react';
import { useDeviceStore } from '@/stores/deviceStore';
import { useAlarmStore } from '@/stores/alarmStore';
import type { Device, Alarm } from '@/types';

export default function DashboardPage() {
  const { devices, fetchDevices, isLoading: deviceLoading } = useDeviceStore();
  const { alarms, fetchAlarms, unprocessedCount } = useAlarmStore();

  useEffect(() => {
    fetchDevices();
    fetchAlarms();
  }, [fetchDevices, fetchAlarms]);

  // 自动刷新数据
  useEffect(() => {
    const timer = setInterval(() => {
      fetchDevices();
      fetchAlarms();
    }, 30000);
    return () => clearInterval(timer);
  }, [fetchDevices, fetchAlarms]);

  const currentDevice = devices[0];

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fade-in-up">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">监控首页</h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            实时监控设备状态，保障老人安全
          </p>
        </div>
        <button
          onClick={() => {
            fetchDevices();
            fetchAlarms();
          }}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-[var(--color-border)] rounded-xl text-sm font-medium text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)] transition-colors btn-press"
          disabled={deviceLoading}
        >
          <RefreshCw className={`w-4 h-4 ${deviceLoading ? 'animate-refresh-spin' : ''}`} />
          刷新数据
        </button>
      </div>

      {/* 报警提示横幅 */}
      {unprocessedCount > 0 && (
        <Link
          to="/alarm"
          className="flex items-center justify-between p-4 bg-gradient-to-r from-[var(--color-danger-bg)] to-[var(--color-danger)] border-2 border-[var(--color-danger)] rounded-2xl animate-alarm-flash"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">您有 {unprocessedCount} 条待处理报警</h3>
              <p className="text-white/80 text-sm">点击查看报警详情，及时处理紧急情况</p>
            </div>
          </div>
          <ChevronRight className="w-6 h-6 text-white" />
        </Link>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧 - 设备卡片区域 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 设备在线状态卡片 */}
          <DeviceStatusCard device={currentDevice} isLoading={deviceLoading} />

          {/* 实时位置卡片 */}
          <LocationCard device={currentDevice} />

          {/* 健康状态监测卡片 */}
          <HealthStatusCard device={currentDevice} />
        </div>

        {/* 右侧 - 报警和快捷操作区域 */}
        <div className="space-y-6">
          {/* 最新报警提醒卡片 */}
          <LatestAlarmCard alarms={alarms.filter((a) => a.status === 'pending').slice(0, 3)} />

          {/* 设备列表 */}
          <DeviceListCard devices={devices} />

          {/* 快捷操作 */}
          <QuickActionsCard />
        </div>
      </div>
    </div>
  );
}

/**
 * 设备在线状态卡片
 */
function DeviceStatusCard({ device, isLoading }: { device?: Device; isLoading: boolean }) {
  const getStatusColor = (status: Device['status']) => {
    switch (status) {
      case 'online':
        return 'bg-[var(--color-success)]';
      case 'alarm':
        return 'bg-[var(--color-danger)]';
      default:
        return 'bg-[var(--color-text-muted)]';
    }
  };

  const getStatusText = (status: Device['status']) => {
    switch (status) {
      case 'online':
        return '在线';
      case 'alarm':
        return '报警中';
      default:
        return '离线';
    }
  };

  if (isLoading && !device) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)] animate-pulse">
        <div className="h-6 w-32 bg-[var(--color-bg-tertiary)] rounded mb-4" />
        <div className="space-y-3">
          <div className="h-4 bg-[var(--color-bg-tertiary)] rounded w-3/4" />
          <div className="h-4 bg-[var(--color-bg-tertiary)] rounded w-1/2" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)] card-interactive">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">设备状态</h2>
        {device && (
          <div className="flex items-center gap-2">
            <span className={`w-3 h-3 rounded-full ${getStatusColor(device.status)}`} />
            <span className="text-sm font-medium text-[var(--color-text-secondary)]">
              {getStatusText(device.status)}
            </span>
          </div>
        )}
      </div>

      {device ? (
        <div className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-[var(--color-bg-secondary)] rounded-xl">
            <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-2">
              <Battery className="w-4 h-4" />
              <span className="text-sm">电量</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-[var(--color-text-primary)]">
                {device.battery}%
              </span>
              <div className="flex-1 h-2 bg-[var(--color-bg-tertiary)] rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    device.battery < 20
                      ? 'bg-[var(--color-danger)]'
                      : device.battery < 50
                      ? 'bg-[var(--color-warning)]'
                      : 'bg-[var(--color-success)]'
                  }`}
                  style={{ width: `${device.battery}%` }}
                />
              </div>
            </div>
          </div>

          <div className="p-4 bg-[var(--color-bg-secondary)] rounded-xl">
            <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-2">
              <Signal className="w-4 h-4" />
              <span className="text-sm">信号</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-[var(--color-text-primary)]">
                {device.signalStrength}%
              </span>
              <div className="flex-1 h-2 bg-[var(--color-bg-tertiary)] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[var(--color-primary)] rounded-full transition-all duration-500"
                  style={{ width: `${device.signalStrength}%` }}
                />
              </div>
            </div>
          </div>

          <div className="p-4 bg-[var(--color-bg-secondary)] rounded-xl">
            <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-2">
              <span className="text-sm">设备编号</span>
            </div>
            <span className="font-mono text-lg text-[var(--color-text-primary)]">
              {device.imei}
            </span>
          </div>

          <div className="p-4 bg-[var(--color-bg-secondary)] rounded-xl">
            <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-2">
              <Clock className="w-4 h-4" />
              <span className="text-sm">最后更新</span>
            </div>
            <span className="font-mono text-sm text-[var(--color-text-primary)]">
              {new Date(device.lastSeen).toLocaleTimeString('zh-CN')}
            </span>
          </div>
        </div>
      ) : (
        <div className="text-center py-8 text-[var(--color-text-muted)]">
          <p>暂无设备</p>
          <Link to="/bindDevice" className="text-[var(--color-primary)] hover:underline mt-2 inline-block">
            绑定设备
          </Link>
        </div>
      )}
    </div>
  );
}

/**
 * 实时位置卡片
 */
function LocationCard({ device }: { device?: Device }) {
  return (
    <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-[var(--color-border)] card-interactive">
      <div className="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">实时位置</h2>
        <Link
          to="/map"
          className="flex items-center gap-1 text-sm text-[var(--color-primary)] hover:underline"
        >
          查看地图
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      {device?.lastLocation ? (
        <div className="relative h-48 bg-gradient-to-b from-[var(--color-primary-bg)] to-[var(--color-bg-secondary)]">
          {/* 地图占位区域 */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative">
              {/* 定位精度圈 */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 border-2 border-dashed border-[var(--color-primary)]/40 rounded-full animate-circle-rotate" />
              {/* 定位标记 */}
              <div className="w-12 h-12 bg-[var(--color-primary)] border-4 border-white rounded-full shadow-lg animate-marker-bounce" />
            </div>
          </div>

          {/* 位置信息 */}
          <div className="absolute bottom-4 left-4 right-4 bg-white/90 backdrop-blur-sm rounded-xl p-3 shadow-sm">
            <div className="flex items-start gap-2">
              <MapPin className="w-5 h-5 text-[var(--color-primary)] mt-0.5" />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-[var(--color-text-primary)] font-medium">
                  {device.nickname || '设备'}
                </p>
                <p className="text-xs text-[var(--color-text-muted)] font-mono">
                  {device.lastLocation.latitude.toFixed(6)}, {device.lastLocation.longitude.toFixed(6)}
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="h-48 flex items-center justify-center text-[var(--color-text-muted)]">
          <div className="text-center">
            <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
            <p>暂无位置数据</p>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * 健康状态监测卡片
 */
function HealthStatusCard({ device }: { device?: Device }) {
  const healthItems = [
    {
      label: '行走状态',
      value: device?.lastLocation?.speed && device.lastLocation.speed > 0.1 ? '行走中' : '静止',
      status: device?.lastLocation?.speed && device.lastLocation.speed > 0.1 ? 'success' : 'warning',
      icon: Activity,
    },
    {
      label: '足底压力',
      value: '正常',
      status: 'success',
      icon: ShieldAlert,
    },
    {
      label: '设备防拆',
      value: '正常',
      status: 'success',
      icon: ShieldAlert,
    },
    {
      label: '设备温度',
      value: device?.temperature ? `${device.temperature}°C` : '--',
      status: device?.temperature && device.temperature > 45 ? 'danger' : 'success',
      icon: Thermometer,
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-[var(--color-success-bg)] text-[var(--color-success)]';
      case 'warning':
        return 'bg-[var(--color-warning-bg)] text-[var(--color-warning)]';
      case 'danger':
        return 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]';
      default:
        return 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)]';
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)] card-interactive">
      <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">健康状态监测</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {healthItems.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="p-4 bg-[var(--color-bg-secondary)] rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`w-5 h-5 ${
                  item.status === 'success'
                    ? 'text-[var(--color-success)]'
                    : item.status === 'warning'
                    ? 'text-[var(--color-warning)]'
                    : 'text-[var(--color-danger)]'
                }`} />
                <span className="text-sm text-[var(--color-text-muted)]">{item.label}</span>
              </div>
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(item.status)}`}>
                {item.value}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * 最新报警卡片
 */
function LatestAlarmCard({ alarms }: { alarms: Alarm[] }) {
  const getAlarmTypeColor = (type: Alarm['alarmType']) => {
    const colors: Record<string, string> = {
      fall: 'bg-[var(--color-danger)]',
      tamper: 'bg-[var(--color-warning)]',
      still: 'bg-[var(--color-accent)]',
      low_battery: 'bg-[var(--color-warning)]',
      sos: 'bg-[var(--color-danger)]',
      shutdown: 'bg-[var(--color-text-muted)]',
    };
    return colors[type] || 'bg-[var(--color-text-muted)]';
  };

  const getAlarmTypeText = (type: Alarm['alarmType']) => {
    const texts: Record<string, string> = {
      fall: '摔倒报警',
      tamper: '防拆报警',
      still: '静止报警',
      low_battery: '低电量',
      sos: 'SOS报警',
      shutdown: '关机报警',
    };
    return texts[type] || '未知报警';
  };

  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)]">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">最新报警</h2>
        <Link
          to="/alarm"
          className="text-sm text-[var(--color-primary)] hover:underline"
        >
          查看全部
        </Link>
      </div>

      {alarms.length > 0 ? (
        <div className="space-y-3">
          {alarms.map((alarm, index) => (
            <div
              key={alarm.id}
              className={`p-3 rounded-xl bg-[var(--color-danger-bg)] border border-[var(--color-danger)]/20 animate-card-list-in`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full ${getAlarmTypeColor(alarm.alarmType)} animate-pulse`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[var(--color-danger)]">
                    {getAlarmTypeText(alarm.alarmType)}
                  </p>
                  <p className="text-xs text-[var(--color-text-muted)]">
                    {new Date(alarm.createdAt).toLocaleString('zh-CN')}
                  </p>
                </div>
                <AlertTriangle className="w-5 h-5 text-[var(--color-danger)]" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-[var(--color-text-muted)]">
          <AlertTriangle className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p>暂无报警记录</p>
        </div>
      )}
    </div>
  );
}

/**
 * 设备列表卡片
 */
function DeviceListCard({ devices }: { devices: Device[] }) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)]">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">我的设备</h2>
        <Link
          to="/bindDevice"
          className="text-sm text-[var(--color-primary)] hover:underline"
        >
          添加设备
        </Link>
      </div>

      {devices.length > 0 ? (
        <div className="space-y-2">
          {devices.map((device, index) => (
            <Link
              key={device.id}
              to={`/device/${device.id}`}
              className={`flex items-center gap-3 p-3 rounded-xl hover:bg-[var(--color-bg-secondary)] transition-colors animate-card-list-in`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`w-3 h-3 rounded-full ${
                device.status === 'online'
                  ? 'bg-[var(--color-success)]'
                  : device.status === 'alarm'
                  ? 'bg-[var(--color-danger)] animate-pulse'
                  : 'bg-[var(--color-text-muted)]'
              }`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">
                  {device.nickname || `设备 ${device.imei.slice(-4)}`}
                </p>
                <p className="text-xs text-[var(--color-text-muted)] font-mono">
                  {device.imei}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <Battery className={`w-4 h-4 ${
                  device.battery < 20
                    ? 'text-[var(--color-danger)]'
                    : 'text-[var(--color-success)]'
                }`} />
                <span className="text-xs text-[var(--color-text-muted)]">{device.battery}%</span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-[var(--color-text-muted)]">
          <p>暂无设备</p>
        </div>
      )}
    </div>
  );
}

/**
 * 快捷操作卡片
 */
function QuickActionsCard() {
  const actions = [
    { label: '地图定位', href: '/map', icon: MapPin, color: 'from-[var(--color-primary)] to-[var(--color-primary-dark)]' },
    { label: '电子围栏', href: '/fence', icon: ShieldAlert, color: 'from-[var(--color-success)] to-[var(--color-success-dark)]' },
    { label: '报警记录', href: '/alarm', icon: AlertTriangle, color: 'from-[var(--color-danger)] to-[var(--color-danger-dark)]' },
    { label: '设备管理', href: '/device/1', icon: Activity, color: 'from-[var(--color-accent)] to-[var(--color-accent-dark)]' },
  ];

  return (
    <div className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)]">
      <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">快捷操作</h2>

      <div className="grid grid-cols-2 gap-3">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.label}
              to={action.href}
              className="flex flex-col items-center gap-2 p-4 rounded-xl bg-gradient-to-br text-white shadow-md btn-press card-interactive"
              style={{ background: `linear-gradient(135deg, ${action.color.split(' ')[0]}, ${action.color.split(' ')[1]})` }}
            >
              <Icon className="w-6 h-6" />
              <span className="text-sm font-medium">{action.label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}