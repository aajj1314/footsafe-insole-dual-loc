/**
 * 电子围栏页面
 */
import { useEffect, useState } from 'react';
import {
  Shield,
  Plus,
  Edit2,
  Trash2,
  MapPin,
  Clock,
  Bell,
  Circle,
  Square,
  X,
} from 'lucide-react';
import { getFences, createFence, deleteFence, updateFence } from '@/services/fence';
import { useDeviceStore } from '@/stores/deviceStore';
import type { Fence } from '@/types';

export default function FencePage() {
  const { devices, fetchDevices } = useDeviceStore();
  const [fences, setFences] = useState<Fence[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingFence, setEditingFence] = useState<Fence | null>(null);

  useEffect(() => {
    fetchDevices();
    loadFences();
  }, [fetchDevices]);

  const loadFences = async () => {
    setIsLoading(true);
    try {
      const data = await getFences();
      setFences(data);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (fenceId: string) => {
    if (window.confirm('确定要删除这个围栏吗？')) {
      await deleteFence(fenceId);
      loadFences();
    }
  };

  const handleToggle = async (fence: Fence) => {
    await updateFence(fence.id, { enabled: !fence.enabled });
    loadFences();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">电子围栏</h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            设置安全区域，实时监控老人位置
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[var(--color-primary)] text-white rounded-xl font-medium text-sm hover:opacity-90 transition-colors btn-press shadow-md"
        >
          <Plus className="w-4 h-4" />
          添加围栏
        </button>
      </div>

      {/* 围栏列表 */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[var(--color-border)] animate-pulse">
            <div className="h-4 bg-[var(--color-bg-tertiary)] rounded w-1/4 mb-4" />
            <div className="h-3 bg-[var(--color-bg-tertiary)] rounded w-3/4" />
          </div>
        ) : fences.length > 0 ? (
          fences.map((fence, index) => (
            <FenceCard
              key={fence.id}
              fence={fence}
              onEdit={() => setEditingFence(fence)}
              onDelete={() => handleDelete(fence.id)}
              onToggle={() => handleToggle(fence)}
              style={{ animationDelay: `${index * 0.1}s` }}
            />
          ))
        ) : (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[var(--color-border)] text-center">
            <Shield className="w-12 h-12 mx-auto mb-4 text-[var(--color-text-muted)] opacity-50" />
            <p className="text-[var(--color-text-muted)]">暂无电子围栏</p>
            <button
              onClick={() => setShowAddModal(true)}
              className="text-[var(--color-primary)] hover:underline mt-2"
            >
              添加第一个围栏
            </button>
          </div>
        )}
      </div>

      {/* 添加/编辑围栏模态框 */}
      {(showAddModal || editingFence) && (
        <FenceModal
          fence={editingFence}
          devices={devices}
          onClose={() => {
            setShowAddModal(false);
            setEditingFence(null);
          }}
          onSave={() => {
            setShowAddModal(false);
            setEditingFence(null);
            loadFences();
          }}
        />
      )}
    </div>
  );
}

/**
 * 围栏卡片组件
 */
function FenceCard({
  fence,
  onEdit,
  onDelete,
  onToggle,
  style,
}: {
  fence: Fence;
  onEdit: () => void;
  onDelete: () => void;
  onToggle: () => void;
  style?: React.CSSProperties;
}) {
  return (
    <div
      className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)] card-interactive animate-card-list-in"
      style={style}
    >
      <div className="flex items-start gap-4">
        {/* 围栏类型图标 */}
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
          fence.enabled
            ? 'bg-[var(--color-success-bg)]'
            : 'bg-[var(--color-bg-tertiary)]'
        }`}>
          {fence.type === 'circle' ? (
            <Circle className={`w-6 h-6 ${fence.enabled ? 'text-[var(--color-success)]' : 'text-[var(--color-text-muted)]'}`} />
          ) : (
            <Square className={`w-6 h-6 ${fence.enabled ? 'text-[var(--color-success)]' : 'text-[var(--color-text-muted)]'}`} />
          )}
        </div>

        {/* 围栏信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-semibold text-[var(--color-text-primary)]">
              {fence.name}
            </h3>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${
              fence.enabled
                ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]'
                : 'bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)]'
            }`}>
              {fence.enabled ? '已启用' : '已禁用'}
            </span>
          </div>
          <p className="text-sm text-[var(--color-text-muted)]">
            类型: {fence.type === 'circle' ? '圆形围栏' : '矩形围栏'}
            {fence.type === 'circle' && fence.radius && ` | 半径: ${fence.radius}米`}
          </p>
          {fence.center && (
            <div className="flex items-center gap-1 mt-2 text-xs text-[var(--color-text-muted)]">
              <MapPin className="w-3 h-3" />
              <span>
                {fence.center.latitude.toFixed(6)}, {fence.center.longitude.toFixed(6)}
              </span>
            </div>
          )}
          <div className="flex items-center gap-1 mt-1 text-xs text-[var(--color-text-muted)]">
            <Clock className="w-3 h-3" />
            <span>创建于 {new Date(fence.createdAt).toLocaleDateString('zh-CN')}</span>
          </div>
        </div>

        {/* 操作按钮 */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1">
            <button
              onClick={onToggle}
              className={`p-2 rounded-lg transition-colors ${
                fence.enabled
                  ? 'text-[var(--color-success)] hover:bg-[var(--color-success-bg)]'
                  : 'text-[var(--color-text-muted)] hover:bg-[var(--color-bg-tertiary)]'
              }`}
              title={fence.enabled ? '禁用围栏' : '启用围栏'}
            >
              <Bell className="w-5 h-5" />
            </button>
            <button
              onClick={onEdit}
              className="p-2 rounded-lg text-[var(--color-text-muted)] hover:bg-[var(--color-bg-tertiary)] transition-colors"
              title="编辑围栏"
            >
              <Edit2 className="w-5 h-5" />
            </button>
            <button
              onClick={onDelete}
              className="p-2 rounded-lg text-[var(--color-danger)] hover:bg-[var(--color-danger-bg)] transition-colors"
              title="删除围栏"
            >
              <Trash2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * 围栏添加/编辑模态框
 */
function FenceModal({
  fence,
  devices,
  onClose,
  onSave,
}: {
  fence: Fence | null;
  devices: { id: string; nickname?: string; imei: string }[];
  onClose: () => void;
  onSave: () => void;
}) {
  const [name, setName] = useState(fence?.name || '');
  const [deviceId, setDeviceId] = useState(fence?.deviceId || (devices[0]?.id || ''));
  const [type, setType] = useState<'circle' | 'rectangle'>(fence?.type || 'circle');
  const [radius, setRadius] = useState(fence?.radius?.toString() || '200');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !deviceId) return;

    setIsSubmitting(true);
    try {
      const params: Parameters<typeof createFence>[0] = {
        name,
        deviceId,
        type,
        enabled: true,
        alarmEnabled: true,
      };

      if (type === 'circle') {
        params.center = { latitude: 39.9042, longitude: 116.4074 };
        params.radius = parseInt(radius);
      } else {
        params.bounds = {
          northEast: { latitude: 39.9142, longitude: 116.4174 },
          southWest: { latitude: 39.8942, longitude: 116.3974 },
        };
      }

      if (fence) {
        await updateFence(fence.id, params);
      } else {
        await createFence(params);
      }
      onSave();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-md animate-fade-in-up">
        {/* 头部 */}
        <div className="p-6 border-b border-[var(--color-border)] flex items-center justify-between">
          <h3 className="text-lg font-bold text-[var(--color-text-primary)]">
            {fence ? '编辑围栏' : '添加围栏'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-tertiary)] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit}>
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                围栏名称
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="例如：家中、小区"
                className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                绑定设备
              </label>
              <select
                value={deviceId}
                onChange={(e) => setDeviceId(e.target.value)}
                className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
              >
                {devices.map((device) => (
                  <option key={device.id} value={device.id}>
                    {device.nickname || `设备 ${device.imei.slice(-4)}`}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                围栏类型
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setType('circle')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    type === 'circle'
                      ? 'bg-[var(--color-primary)] text-white shadow-md'
                      : 'bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]'
                  }`}
                >
                  <Circle className="w-4 h-4" />
                  圆形
                </button>
                <button
                  type="button"
                  onClick={() => setType('rectangle')}
                  className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    type === 'rectangle'
                      ? 'bg-[var(--color-primary)] text-white shadow-md'
                      : 'bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]'
                  }`}
                >
                  <Square className="w-4 h-4" />
                  矩形
                </button>
              </div>
            </div>

            {type === 'circle' && (
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                  半径 (米)
                </label>
                <input
                  type="number"
                  value={radius}
                  onChange={(e) => setRadius(e.target.value)}
                  min="50"
                  max="5000"
                  className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                  required
                />
              </div>
            )}
          </div>

          {/* 操作按钮 */}
          <div className="p-6 border-t border-[var(--color-border)] flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 text-sm font-medium text-[var(--color-text-secondary)] bg-[var(--color-bg-secondary)] rounded-xl hover:bg-[var(--color-bg-tertiary)] transition-colors btn-press"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-3 text-sm font-medium text-white bg-[var(--color-primary)] rounded-xl hover:opacity-90 transition-colors btn-press disabled:opacity-50"
            >
              {isSubmitting ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}