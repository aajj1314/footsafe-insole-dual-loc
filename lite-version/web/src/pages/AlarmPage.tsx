/**
 * 报警记录页面
 * 采用Accessible & Ethical设计风格，适合医疗健康类应用
 */
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Bell,
  Filter,
  ChevronRight,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  MapPin,
  X,
} from 'lucide-react';
import { useAlarmStore } from '@/stores/alarmStore';
import type { Alarm, AlarmType, AlarmStatus } from '@/types';
import { getAlarmTypeLabel, getAlarmLevelLabel, getAlarmStatusLabel } from '@/services/alarm';

const alarmTypeFilters: { label: string; value: AlarmType | 'all' }[] = [
  { label: '全部', value: 'all' },
  { label: '摔倒报警', value: 'fall' },
  { label: '防拆报警', value: 'tamper' },
  { label: '静止报警', value: 'still' },
  { label: 'SOS报警', value: 'sos' },
  { label: '低电量', value: 'low_battery' },
];

export default function AlarmPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { alarms, fetchAlarms, updateAlarmStatus, setFilter, isLoading } = useAlarmStore();
  const [selectedAlarm, setSelectedAlarm] = useState<Alarm | null>(null);

  const currentTypeFilter = (searchParams.get('type') as AlarmType) || 'all';

  useEffect(() => {
    fetchAlarms();
  }, [fetchAlarms]);

  const handleTypeFilterChange = (type: AlarmType | 'all') => {
    setFilter({ type });
    if (type === 'all') {
      setSearchParams({});
    } else {
      setSearchParams({ type });
    }
  };

  const handleResolve = async (alarmId: string) => {
    await updateAlarmStatus(alarmId, 'resolved');
  };

  const handleIgnore = async (alarmId: string) => {
    await updateAlarmStatus(alarmId, 'ignored');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up">
      {/* 页面标题 */}
      <header>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)] tracking-tight">
          报警记录
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
          查看和管理所有设备报警信息
        </p>
      </header>

      {/* 筛选器 */}
      <section
        className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)]"
        aria-labelledby="filter-title"
      >
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-[var(--color-text-muted)]" aria-hidden="true" />
          <span id="filter-title" className="text-sm font-medium text-[var(--color-text-secondary)]">
            筛选报警类型
          </span>
        </div>
        <div className="flex flex-wrap gap-2" role="group" aria-label="报警类型筛选">
          {alarmTypeFilters.map((filterOption) => (
            <button
              key={filterOption.value}
              onClick={() => handleTypeFilterChange(filterOption.value)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${
                currentTypeFilter === filterOption.value
                  ? 'bg-[var(--color-primary)] text-white shadow-md'
                  : 'bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)]'
              }`}
              aria-pressed={currentTypeFilter === filterOption.value}
            >
              {filterOption.label}
            </button>
          ))}
        </div>
      </section>

      {/* 报警列表 */}
      <section aria-label="报警列表">
        {isLoading && alarms.length === 0 ? (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[var(--color-border)] text-center" aria-hidden="true">
            <div className="animate-pulse">
              <div className="h-4 bg-[var(--color-bg-tertiary)] rounded w-1/4 mx-auto mb-4" />
              <div className="h-3 bg-[var(--color-bg-tertiary)] rounded w-3/4 mx-auto" />
            </div>
          </div>
        ) : alarms.length > 0 ? (
          alarms.map((alarm, index) => (
            <AlarmCard
              key={alarm.id}
              alarm={alarm}
              onResolve={handleResolve}
              onIgnore={handleIgnore}
              onClick={() => setSelectedAlarm(alarm)}
              style={{ animationDelay: `${index * 0.05}s` }}
            />
          ))
        ) : (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[var(--color-border)] text-center">
            <Bell className="w-12 h-12 mx-auto mb-4 text-[var(--color-text-muted)] opacity-50" aria-hidden="true" />
            <p className="text-[var(--color-text-muted)]">暂无报警记录</p>
          </div>
        )}
      </section>

      {/* 报警详情模态框 */}
      {selectedAlarm && (
        <AlarmDetailModal
          alarm={selectedAlarm}
          onClose={() => setSelectedAlarm(null)}
          onResolve={handleResolve}
          onIgnore={handleIgnore}
        />
      )}
    </div>
  );
}

/**
 * 报警卡片组件
 */
function AlarmCard({
  alarm,
  onResolve,
  onIgnore,
  onClick,
  style,
}: {
  alarm: Alarm;
  onResolve: (id: string) => void;
  onIgnore: (id: string) => void;
  onClick: () => void;
  style?: React.CSSProperties;
}) {
  const getLevelStyles = (level: string) => {
    switch (level) {
      case 'urgent':
        return {
          bg: 'bg-[var(--color-danger-bg)]',
          border: 'border-[var(--color-danger)]',
          text: 'text-[var(--color-danger)]',
          badge: 'bg-[var(--color-danger)] text-white',
        };
      case 'high':
        return {
          bg: 'bg-[var(--color-warning-bg)]',
          border: 'border-[var(--color-warning)]',
          text: 'text-[var(--color-warning)]',
          badge: 'bg-[var(--color-warning)] text-white',
        };
      case 'medium':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-300',
          text: 'text-blue-600',
          badge: 'bg-blue-500 text-white',
        };
      default:
        return {
          bg: 'bg-[var(--color-success-bg)]',
          border: 'border-[var(--color-success)]',
          text: 'text-[var(--color-success)]',
          badge: 'bg-[var(--color-success)] text-white',
        };
    }
  };

  const levelStyles = getLevelStyles(alarm.alarmLevel);

  const getStatusIcon = (status: AlarmStatus) => {
    switch (status) {
      case 'resolved':
        return <CheckCircle className="w-4 h-4 text-[var(--color-success)]" aria-hidden="true" />;
      case 'ignored':
        return <XCircle className="w-4 h-4 text-[var(--color-text-muted)]" aria-hidden="true" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-[var(--color-primary)]" aria-hidden="true" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-[var(--color-danger)]" aria-hidden="true" />;
    }
  };

  return (
    <article
      className={`${levelStyles.bg} border-2 ${levelStyles.border} rounded-2xl p-4 mb-4 card-interactive animate-card-list-in cursor-pointer focus-within:ring-2 focus-within:ring-[var(--color-primary)]`}
      style={style}
    >
      <button
        onClick={onClick}
        className="w-full text-left focus:outline-none"
        aria-label={`查看${getAlarmTypeLabel(alarm.alarmType)}详情`}
      >
        <div className="flex items-start gap-4">
          {/* 报警类型图标 */}
          <div
            className={`w-12 h-12 rounded-full ${levelStyles.badge} flex items-center justify-center text-white font-bold text-sm flex-shrink-0`}
            aria-hidden="true"
          >
            {alarm.alarmType === 'fall' && '!'}
            {alarm.alarmType === 'tamper' && 'T'}
            {alarm.alarmType === 'still' && 'S'}
            {alarm.alarmType === 'sos' && 'SOS'}
            {alarm.alarmType === 'low_battery' && 'Low'}
          </div>

          {/* 报警信息 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className={`text-sm font-semibold ${levelStyles.text}`}>
                {getAlarmTypeLabel(alarm.alarmType)}
              </span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${levelStyles.badge}`}>
                {getAlarmLevelLabel(alarm.alarmLevel)}
              </span>
            </div>
            <p className="text-sm text-[var(--color-text-secondary)] mb-2">
              设备: <span className="font-mono">{alarm.deviceId}</span>
            </p>
            {alarm.location && (
              <div className="flex items-center gap-1 text-xs text-[var(--color-text-muted)]">
                <MapPin className="w-3 h-3" aria-hidden="true" />
                <span className="font-mono">
                  {alarm.location.latitude.toFixed(6)}, {alarm.location.longitude.toFixed(6)}
                </span>
              </div>
            )}
            <p className="text-xs text-[var(--color-text-muted)] mt-1">
              {new Date(alarm.createdAt).toLocaleString('zh-CN')}
            </p>
          </div>

          {/* 状态和操作 */}
          <div className="flex flex-col items-end gap-2">
            <div className="flex items-center gap-1">
              {getStatusIcon(alarm.status)}
              <span className="text-xs text-[var(--color-text-muted)]">
                {getAlarmStatusLabel(alarm.status)}
              </span>
            </div>

            {alarm.status === 'pending' && (
              <div className="flex gap-2 mt-2" onClick={(e) => e.stopPropagation()}>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onIgnore(alarm.id);
                  }}
                  className="px-3 py-1 text-xs font-medium text-[var(--color-text-muted)] bg-white border border-[var(--color-border)] rounded-full hover:bg-[var(--color-bg-tertiary)] transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  忽略
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onResolve(alarm.id);
                  }}
                  className="px-3 py-1 text-xs font-medium text-white bg-[var(--color-success)] rounded-full hover:opacity-90 transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-success)]"
                >
                  已处理
                </button>
              </div>
            )}

            <ChevronRight className="w-5 h-5 text-[var(--color-text-muted)] mt-2" aria-hidden="true" />
          </div>
        </div>
      </button>
    </article>
  );
}

/**
 * 报警详情模态框
 */
function AlarmDetailModal({
  alarm,
  onClose,
  onResolve,
  onIgnore,
}: {
  alarm: Alarm;
  onClose: () => void;
  onResolve: (id: string) => void;
  onIgnore: (id: string) => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="alarm-detail-title"
    >
      {/* 背景遮罩 */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* 模态框内容 */}
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[80vh] overflow-hidden animate-fade-in-up">
        {/* 头部 */}
        <header className="p-6 border-b border-[var(--color-border)] flex items-center justify-between">
          <div>
            <h3 id="alarm-detail-title" className="text-xl font-bold text-[var(--color-text-primary)]">
              报警详情
            </h3>
            <p className="text-sm text-[var(--color-text-muted)] mt-1">
              报警ID: <span className="font-mono">{alarm.id}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-tertiary)] transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            aria-label="关闭"
          >
            <X className="w-5 h-5" />
          </button>
        </header>

        {/* 内容 */}
        <div className="p-6 space-y-4 overflow-y-auto max-h-[50vh]">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-[var(--color-text-muted)]">报警类型</label>
              <p className="text-sm font-medium text-[var(--color-text-primary)]">
                {getAlarmTypeLabel(alarm.alarmType)}
              </p>
            </div>
            <div>
              <label className="text-xs text-[var(--color-text-muted)]">报警级别</label>
              <p className="text-sm font-medium text-[var(--color-text-primary)]">
                {getAlarmLevelLabel(alarm.alarmLevel)}
              </p>
            </div>
            <div>
              <label className="text-xs text-[var(--color-text-muted)]">设备ID</label>
              <p className="text-sm font-medium text-[var(--color-text-primary)] font-mono">
                {alarm.deviceId}
              </p>
            </div>
            <div>
              <label className="text-xs text-[var(--color-text-muted)]">当前状态</label>
              <p className="text-sm font-medium text-[var(--color-text-primary)]">
                {getAlarmStatusLabel(alarm.status)}
              </p>
            </div>
          </div>

          {alarm.location && (
            <div>
              <label className="text-xs text-[var(--color-text-muted)]">报警位置</label>
              <div className="mt-1 p-3 bg-[var(--color-bg-secondary)] rounded-xl">
                <p className="text-sm font-mono text-[var(--color-text-primary)]">
                  {alarm.location.latitude.toFixed(6)}, {alarm.location.longitude.toFixed(6)}
                </p>
                {alarm.location.accuracy && (
                  <p className="text-xs text-[var(--color-text-muted)] mt-1">
                    精度: {alarm.location.accuracy.toFixed(1)}米
                  </p>
                )}
              </div>
            </div>
          )}

          <div>
            <label className="text-xs text-[var(--color-text-muted)]">报警时间</label>
            <p className="text-sm font-medium text-[var(--color-text-primary)]">
              {new Date(alarm.createdAt).toLocaleString('zh-CN')}
            </p>
          </div>

          {alarm.battery !== undefined && (
            <div>
              <label className="text-xs text-[var(--color-text-muted)]">设备电量</label>
              <p className="text-sm font-medium text-[var(--color-text-primary)]">
                {alarm.battery}%
              </p>
            </div>
          )}
        </div>

        {/* 操作按钮 */}
        <footer className="p-6 border-t border-[var(--color-border)] flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 text-sm font-medium text-[var(--color-text-secondary)] bg-[var(--color-bg-secondary)] rounded-xl hover:bg-[var(--color-bg-tertiary)] transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            关闭
          </button>
          {alarm.status === 'pending' && (
            <>
              <button
                onClick={() => {
                  onIgnore(alarm.id);
                  onClose();
                }}
                className="flex-1 px-4 py-3 text-sm font-medium text-[var(--color-text-muted)] bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl hover:bg-[var(--color-bg-tertiary)] transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              >
                忽略
              </button>
              <button
                onClick={() => {
                  onResolve(alarm.id);
                  onClose();
                }}
                className="flex-1 px-4 py-3 text-sm font-medium text-white bg-[var(--color-success)] rounded-xl hover:opacity-90 transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-success)]"
              >
                标记已处理
              </button>
            </>
          )}
        </footer>
      </div>
    </div>
  );
}
