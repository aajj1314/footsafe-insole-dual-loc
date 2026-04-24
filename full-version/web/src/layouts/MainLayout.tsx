/**
 * 主应用布局组件
 * 包含侧边栏导航和顶部栏
 */
import { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  Home,
  Bell,
  MapPin,
  Shield,
  User,
  Menu,
  X,
  LogOut,
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useAlarmStore } from '@/stores/alarmStore';

const navigation = [
  { name: '监控首页', href: '/', icon: Home },
  { name: '报警记录', href: '/alarm', icon: Bell },
  { name: '地图定位', href: '/map', icon: MapPin },
  { name: '电子围栏', href: '/fence', icon: Shield },
  { name: '个人中心', href: '/profile', icon: User },
];

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { unprocessedCount } = useAlarmStore();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-[var(--color-bg-secondary)]">
      {/* 移动端侧边栏遮罩 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 侧边栏 */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-64 bg-white shadow-lg
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo区域 */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[var(--color-border)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--color-primary)] to-[var(--color-primary-dark)] flex items-center justify-center shadow-md">
              <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-[var(--color-text-primary)]">足安智能防走失</h1>
              <p className="text-xs text-[var(--color-text-muted)]">安心守护每一天</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-[var(--color-bg-tertiary)]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 导航菜单 */}
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            const Icon = item.icon;
            const showBadge = item.href === '/alarm' && unprocessedCount > 0;

            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl
                  transition-all duration-200
                  ${
                    isActive
                      ? 'bg-[var(--color-primary-bg)] text-[var(--color-primary)] font-medium shadow-sm'
                      : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)]'
                  }
                `}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-[var(--color-primary)]' : ''}`} />
                <span>{item.name}</span>
                {showBadge && (
                  <span className="ml-auto px-2 py-0.5 text-xs font-medium bg-[var(--color-danger)] text-white rounded-full">
                    {unprocessedCount}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* 用户信息 */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-[var(--color-border)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[var(--color-accent-bg)] flex items-center justify-center">
              <span className="text-[var(--color-accent)] font-medium">
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">
                {user?.username || '用户'}
              </p>
              <p className="text-xs text-[var(--color-text-muted)]">
                {user?.phone || '未设置手机号'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg text-[var(--color-text-muted)] hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-danger)] transition-colors"
              title="退出登录"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <div className="lg:pl-64">
        {/* 顶部栏 */}
        <header className="h-16 bg-white border-b border-[var(--color-border)] px-4 lg:px-6 flex items-center justify-between sticky top-0 z-30">
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-lg hover:bg-[var(--color-bg-tertiary)]"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="hidden lg:flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
            <span>首页</span>
            {location.pathname !== '/' && (
              <>
                <span>/</span>
                <span className="text-[var(--color-text-primary)]">
                  {navigation.find((n) => n.href === location.pathname)?.name || ''}
                </span>
              </>
            )}
          </div>

          <div className="flex items-center gap-4">
            {/* 报警数量提示 */}
            {unprocessedCount > 0 && (
              <Link
                to="/alarm"
                className="flex items-center gap-2 px-3 py-1.5 bg-[var(--color-danger-bg)] text-[var(--color-danger)] rounded-full text-sm font-medium animate-alarm-heartbeat"
              >
                <span className="w-2 h-2 rounded-full bg-[var(--color-danger)] animate-pulse" />
                {unprocessedCount} 条待处理报警
              </Link>
            )}

            {/* 当前时间 */}
            <div className="hidden md:block text-sm text-[var(--color-text-muted)]">
              {new Date().toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long',
              })}
            </div>
          </div>
        </header>

        {/* 页面内容 */}
        <main className="p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}