/**
 * 应用路由配置
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

// 布局组件
import MainLayout from '@/layouts/MainLayout';

// 页面组件
import DashboardPage from '@/pages/DashboardPage';
import AlarmPage from '@/pages/AlarmPage';
import DeviceDetailPage from '@/pages/DeviceDetailPage';
import MapPage from '@/pages/MapPage';
import FencePage from '@/pages/FencePage';
import ProfilePage from '@/pages/ProfilePage';
import BindDevicePage from '@/pages/BindDevicePage';
import ContactsPage from '@/pages/ContactsPage';
import LoginPage from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';

/**
 * 受保护的路由 - 需要登录才能访问
 */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

/**
 * 公共路由 - 已登录用户访问时跳转到首页
 */
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

/**
 * 应用路由组件
 */
export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 公共路由 */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <RegisterPage />
            </PublicRoute>
          }
        />

        {/* 受保护的路由 */}
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<DashboardPage />} />
          <Route path="/alarm" element={<AlarmPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/fence" element={<FencePage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/bindDevice" element={<BindDevicePage />} />
          <Route path="/contacts" element={<ContactsPage />} />
          <Route path="/device/:deviceId" element={<DeviceDetailPage />} />
        </Route>

        {/* 404 重定向 */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}