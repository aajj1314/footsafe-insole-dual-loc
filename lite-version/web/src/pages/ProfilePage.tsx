/**
 * 个人中心页面
 */
import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  Phone,
  LogOut,
  Bell,
  Shield,
  ChevronRight,
  Battery,
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useDeviceStore } from '@/stores/deviceStore';

export default function ProfilePage() {
  const { user, logout } = useAuthStore();
  const { devices, fetchDevices } = useDeviceStore();

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  const handleLogout = () => {
    if (window.confirm('确定要退出登录吗？')) {
      logout();
    }
  };

  const menuItems = [
    {
      icon: User,
      label: '个人信息',
      description: '查看和编辑个人资料',
      href: '/profile/edit',
      color: 'text-[var(--color-primary)]',
      bgColor: 'bg-[var(--color-primary-bg)]',
    },
    {
      icon: Phone,
      label: '紧急联系人',
      description: '管理紧急联系方式',
      href: '/contacts',
      color: 'text-[var(--color-accent)]',
      bgColor: 'bg-[var(--color-accent-bg)]',
    },
    {
      icon: Battery,
      label: '设备绑定',
      description: '管理已绑定的设备',
      href: '/bindDevice',
      color: 'text-[var(--color-success)]',
      bgColor: 'bg-[var(--color-success-bg)]',
    },
    {
      icon: Bell,
      label: '消息通知',
      description: '报警通知设置',
      href: '/settings/notification',
      color: 'text-[var(--color-warning)]',
      bgColor: 'bg-[var(--color-warning-bg)]',
    },
    {
      icon: Shield,
      label: '隐私安全',
      description: '账户安全和隐私设置',
      href: '/settings/security',
      color: 'text-[var(--color-danger)]',
      bgColor: 'bg-[var(--color-danger-bg)]',
    },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">个人中心</h1>
        <p className="text-sm text-[var(--color-text-muted)] mt-1">
          管理您的账户和设备
        </p>
      </div>

      {/* 用户信息卡片 */}
      <div className="bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-primary-dark)] rounded-2xl p-6 shadow-lg">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
            <span className="text-2xl font-bold text-white">
              {user?.username?.charAt(0).toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-white">{user?.username || '用户'}</h2>
            <p className="text-white/80 text-sm mt-1">{user?.phone || '未绑定手机号'}</p>
          </div>
          <Link
            to="/profile/edit"
            className="px-4 py-2 bg-white/20 rounded-lg text-white text-sm font-medium hover:bg-white/30 transition-colors"
          >
            编辑
          </Link>
        </div>
      </div>

      {/* 设备统计 */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-[var(--color-border)]">
        <h3 className="text-sm font-semibold text-[var(--color-text-secondary)] mb-4">设备统计</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-[var(--color-bg-secondary)] rounded-xl">
            <p className="text-2xl font-bold text-[var(--color-primary)]">{devices.length}</p>
            <p className="text-xs text-[var(--color-text-muted)]">绑定设备</p>
          </div>
          <div className="text-center p-4 bg-[var(--color-bg-secondary)] rounded-xl">
            <p className="text-2xl font-bold text-[var(--color-success)]">
              {devices.filter((d) => d.status === 'online').length}
            </p>
            <p className="text-xs text-[var(--color-text-muted)]">在线设备</p>
          </div>
          <div className="text-center p-4 bg-[var(--color-bg-secondary)] rounded-xl">
            <p className="text-2xl font-bold text-[var(--color-warning)]">
              {devices.filter((d) => d.battery < 20).length}
            </p>
            <p className="text-xs text-[var(--color-text-muted)]">低电量</p>
          </div>
        </div>
      </div>

      {/* 菜单列表 */}
      <div className="bg-white rounded-2xl shadow-sm border border-[var(--color-border)] overflow-hidden">
        {menuItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.label}
              to={item.href}
              className={`flex items-center gap-4 p-4 hover:bg-[var(--color-bg-secondary)] transition-colors animate-card-list-in ${
                index !== menuItems.length - 1 ? 'border-b border-[var(--color-border)]' : ''
              }`}
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className={`w-10 h-10 rounded-xl ${item.bgColor} flex items-center justify-center`}>
                <Icon className={`w-5 h-5 ${item.color}`} />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-[var(--color-text-primary)]">{item.label}</p>
                <p className="text-xs text-[var(--color-text-muted)]">{item.description}</p>
              </div>
              <ChevronRight className="w-5 h-5 text-[var(--color-text-muted)]" />
            </Link>
          );
        })}
      </div>

      {/* 退出登录 */}
      <button
        onClick={handleLogout}
        className="w-full flex items-center justify-center gap-2 p-4 bg-[var(--color-danger-bg)] text-[var(--color-danger)] rounded-2xl font-medium hover:bg-[var(--color-danger)]/10 transition-colors btn-press"
      >
        <LogOut className="w-5 h-5" />
        退出登录
      </button>

      {/* 版本信息 */}
      <p className="text-center text-xs text-[var(--color-text-muted)]">
        足安智能防走失系统 Web端 v1.0.0
      </p>
    </div>
  );
}