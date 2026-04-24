/**
 * 绑定设备页面
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  QrCode,
  Keyboard,
  CheckCircle,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { bindDevice } from '@/services/device';

export default function BindDevicePage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<'scan' | 'manual'>('scan');
  const [imei, setImei] = useState('');
  const [nickname, setNickname] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!imei.trim()) {
      setError('请输入设备IMEI号');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await bindDevice({ device_imei: imei.trim(), nickname: nickname.trim() || undefined });
      setSuccess(true);
      setTimeout(() => {
        navigate('/profile');
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : '绑定设备失败');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-md mx-auto space-y-6 animate-fade-in-up">
      {/* 页面标题 */}
      <div className="text-center">
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">绑定设备</h1>
        <p className="text-sm text-[var(--color-text-muted)] mt-1">
          将足安智能防走失设备绑定到您的账户
        </p>
      </div>

      {/* 成功提示 */}
      {success && (
        <div className="bg-[var(--color-success-bg)] border border-[var(--color-success)] rounded-2xl p-6 text-center animate-card-list-in">
          <CheckCircle className="w-12 h-12 text-[var(--color-success)] mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-[var(--color-success)]">绑定成功</h3>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">正在跳转到个人中心...</p>
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="bg-[var(--color-danger-bg)] border border-[var(--color-danger)] rounded-2xl p-4 flex items-center gap-3 animate-card-list-in">
          <AlertCircle className="w-5 h-5 text-[var(--color-danger)] flex-shrink-0" />
          <p className="text-sm text-[var(--color-danger)]">{error}</p>
        </div>
      )}

      {/* 模式切换 */}
      {!success && (
        <>
          <div className="bg-white rounded-2xl p-2 shadow-sm border border-[var(--color-border)]">
            <div className="flex">
              <button
                onClick={() => setMode('scan')}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  mode === 'scan'
                    ? 'bg-[var(--color-primary)] text-white shadow-md'
                    : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-secondary)]'
                }`}
              >
                <QrCode className="w-4 h-4" />
                扫描二维码
              </button>
              <button
                onClick={() => setMode('manual')}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  mode === 'manual'
                    ? 'bg-[var(--color-primary)] text-white shadow-md'
                    : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-secondary)]'
                }`}
              >
                <Keyboard className="w-4 h-4" />
                手动输入
              </button>
            </div>
          </div>

          {/* 扫描二维码模式 */}
          {mode === 'scan' && (
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)]">
              <div className="aspect-square bg-[var(--color-bg-secondary)] rounded-xl flex flex-col items-center justify-center mb-4">
                <QrCode className="w-24 h-24 text-[var(--color-text-muted)] mb-4" />
                <p className="text-sm text-[var(--color-text-muted)] text-center px-8">
                  请使用手机App扫描设备上的二维码进行绑定
                </p>
              </div>
              <button
                onClick={() => setMode('manual')}
                className="w-full text-center text-sm text-[var(--color-primary)] hover:underline"
              >
                无法扫描？手动输入IMEI
              </button>
            </div>
          )}

          {/* 手动输入模式 */}
          {mode === 'manual' && (
            <form onSubmit={handleSubmit} className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)] space-y-4">
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                  设备IMEI号 *
                </label>
                <input
                  type="text"
                  value={imei}
                  onChange={(e) => setImei(e.target.value)}
                  placeholder="请输入15位IMEI号"
                  maxLength={15}
                  className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent font-mono"
                  required
                />
                <p className="text-xs text-[var(--color-text-muted)] mt-2">
                  IMEI号通常位于设备背面或包装盒上
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                  设备昵称 (选填)
                </label>
                <input
                  type="text"
                  value={nickname}
                  onChange={(e) => setNickname(e.target.value)}
                  placeholder="例如：爸爸的鞋垫"
                  maxLength={20}
                  className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                />
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[var(--color-primary)] text-white rounded-xl font-medium text-sm hover:opacity-90 transition-colors btn-press disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-refresh-spin" />
                    绑定中...
                  </>
                ) : (
                  '确认绑定'
                )}
              </button>
            </form>
          )}

          {/* 绑定说明 */}
          <div className="bg-[var(--color-primary-bg)] rounded-2xl p-4 border border-[var(--color-primary)]/20">
            <h4 className="text-sm font-semibold text-[var(--color-primary)] mb-2">绑定说明</h4>
            <ul className="text-xs text-[var(--color-text-secondary)] space-y-1">
              <li>1. 请确保设备已开机并处于配对状态</li>
              <li>2. IMEI号是设备的唯一标识，共15位数字</li>
              <li>3. 一个账户最多可绑定5台设备</li>
              <li>4. 绑定成功后即可实时查看设备位置和状态</li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
}