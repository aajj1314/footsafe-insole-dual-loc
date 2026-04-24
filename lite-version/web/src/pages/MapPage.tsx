/**
 * 地图定位页面
 * 采用Accessible & Ethical设计风格，适合医疗健康类应用
 */
import { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Navigation,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  Locate,
  Clock,
} from 'lucide-react';
import { useDeviceStore } from '@/stores/deviceStore';
import * as locationService from '@/services/location';
import type { GPSLocation } from '@/types';

export default function MapPage() {
  const [searchParams] = useSearchParams();
  const deviceIdFromUrl = searchParams.get('device');
  const { devices, fetchDevices } = useDeviceStore();
  const [selectedDeviceImei, setSelectedDeviceImei] = useState<string>(deviceIdFromUrl || '');
  const [trackPoints, setTrackPoints] = useState<GPSLocation[]>([]);
  const [showTrack, setShowTrack] = useState(false);
  const [zoom, setZoom] = useState(15);
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  useEffect(() => {
    if (devices.length > 0 && !selectedDeviceImei) {
      setSelectedDeviceImei(devices[0].imei);
    }
  }, [devices, selectedDeviceImei]);

  const selectedDevice = devices.find((d) => d.imei === selectedDeviceImei);

  const handleShowTrack = async () => {
    if (!selectedDeviceImei) return;

    try {
      const now = new Date();
      const startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000).toISOString();
      const endTime = now.toISOString();

      const response = await locationService.getLocationHistory(selectedDeviceImei, {
        start_time: startTime,
        end_time: endTime,
      });
      const points: GPSLocation[] = response.locations.map((loc: any) => ({
        latitude: parseFloat(loc.latitude),
        longitude: parseFloat(loc.longitude),
        altitude: loc.altitude ? parseFloat(loc.altitude) : undefined,
        speed: loc.speed ? parseFloat(loc.speed) : undefined,
        direction: loc.direction ? parseInt(loc.direction) : undefined,
        accuracy: loc.accuracy ? parseFloat(loc.accuracy) : undefined,
        gpsTimestamp: loc.gps_timestamp,
      }));
      setTrackPoints(points);
      setShowTrack(true);
    } catch (error) {
      console.error('获取轨迹失败:', error);
      setTrackPoints([]);
    }
  };

  const handleZoomIn = () => setZoom((z) => Math.min(z + 2, 20));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 2, 5));

  const currentLocation = selectedDevice?.lastLocation;

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-fade-in-up">
      {/* 页面标题 */}
      <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)] tracking-tight">
            地图定位
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            实时查看设备位置和历史轨迹
          </p>
        </div>
        <button
          onClick={() => fetchDevices()}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-[var(--color-border)] rounded-xl text-sm font-medium text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-secondary)] transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          aria-label="刷新设备列表"
        >
          <RefreshCw className="w-4 h-4" aria-hidden="true" />
          刷新
        </button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 地图区域 */}
        <div className="lg:col-span-3">
          <div
            ref={mapRef}
            className="relative h-[600px] bg-gradient-to-b from-[var(--color-primary-bg)] to-[var(--color-bg-secondary)] rounded-2xl overflow-hidden shadow-sm border border-[var(--color-border)]"
            role="application"
            aria-label="设备位置地图"
          >
            {/* 地图网格背景 */}
            <div className="absolute inset-0" aria-hidden="true">
              <svg className="w-full h-full opacity-20" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="map-grid" width="50" height="50" patternUnits="userSpaceOnUse">
                    <path d="M 50 0 L 0 0 0 50" fill="none" stroke="var(--color-primary)" strokeWidth="0.5" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#map-grid)" />
              </svg>

              {/* 模拟地图元素 */}
              <div className="absolute inset-0 flex items-center justify-center">
                {/* 定位标记 */}
                {currentLocation && (
                  <div className="relative" style={{ transform: `scale(${zoom / 15})` }}>
                    {/* 精度圈 */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 border-2 border-dashed border-[var(--color-primary)]/40 rounded-full animate-circle-rotate" />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-28 h-28 border border-[var(--color-primary)]/30 rounded-full" />
                    {/* 定位点 */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                      <div className="w-16 h-16 bg-[var(--color-primary)] border-4 border-white rounded-full shadow-lg animate-marker-bounce" />
                      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full" />
                    </div>
                  </div>
                )}
              </div>

              {/* 模拟路径 */}
              {showTrack && trackPoints.length > 0 && (
                <svg className="absolute inset-0 w-full h-full pointer-events-none" aria-hidden="true">
                  <polyline
                    fill="none"
                    stroke="var(--color-primary)"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    opacity="0.6"
                    points={trackPoints
                      .map((p) => {
                        const x = 50 + (p.longitude - 116.4074) * 1000;
                        const y = 50 - (p.latitude - 39.9042) * 1000;
                        return `${x},${y}`;
                      })
                      .join(' ')}
                  />
                </svg>
              )}
            </div>

            {/* 地图控件 */}
            <div className="absolute top-4 right-4 flex flex-col gap-2" role="group" aria-label="地图缩放控制">
              <button
                onClick={handleZoomIn}
                className="p-3 bg-white rounded-xl shadow-md hover:bg-[var(--color-bg-secondary)] transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                aria-label="放大地图"
              >
                <ZoomIn className="w-5 h-5 text-[var(--color-text-secondary)]" />
              </button>
              <button
                onClick={handleZoomOut}
                className="p-3 bg-white rounded-xl shadow-md hover:bg-[var(--color-bg-secondary)] transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                aria-label="缩小地图"
              >
                <ZoomOut className="w-5 h-5 text-[var(--color-text-secondary)]" />
              </button>
              <button
                onClick={() => setZoom(15)}
                className="p-3 bg-white rounded-xl shadow-md hover:bg-[var(--color-bg-secondary)] transition-colors btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                aria-label="重置视图"
              >
                <Locate className="w-5 h-5 text-[var(--color-text-secondary)]" />
              </button>
            </div>

            {/* 当前位置信息 */}
            {currentLocation ? (
              <address className="absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl p-4 shadow-md not-italic">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-[var(--color-primary-bg)] rounded-full flex items-center justify-center flex-shrink-0" aria-hidden="true">
                    <Navigation className="w-5 h-5 text-[var(--color-primary)]" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-[var(--color-text-primary)]">
                      {selectedDevice?.nickname || '设备'} - 当前位置
                    </p>
                    <p className="text-xs text-[var(--color-text-muted)] font-mono mt-1">
                      {currentLocation.latitude.toFixed(6)}, {currentLocation.longitude.toFixed(6)}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-[var(--color-text-muted)]">
                      {currentLocation.accuracy && <span>精度: {currentLocation.accuracy.toFixed(1)}米</span>}
                      {currentLocation.speed && <span>速度: {currentLocation.speed.toFixed(1)}m/s</span>}
                      {currentLocation.direction && <span>方向: {currentLocation.direction}°</span>}
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        selectedDevice?.status === 'online'
                          ? 'bg-[var(--color-success-bg)] text-[var(--color-success)]'
                          : 'bg-[var(--color-danger-bg)] text-[var(--color-danger)]'
                      }`}
                      role="status"
                    >
                      {selectedDevice?.status === 'online' ? '在线' : '离线'}
                    </span>
                    {currentLocation.gpsTimestamp && (
                      <p className="text-xs text-[var(--color-text-muted)] mt-1">
                        {new Date(currentLocation.gpsTimestamp).toLocaleTimeString('zh-CN')}
                      </p>
                    )}
                  </div>
                </div>
              </address>
            ) : (
              <div className="absolute bottom-4 left-4 right-4 bg-white/95 backdrop-blur-sm rounded-xl p-4 shadow-md">
                <p className="text-sm text-[var(--color-text-muted)] text-center">
                  {selectedDevice ? '暂无位置数据，请等待设备上报' : '请先绑定设备'}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* 侧边栏 */}
        <aside className="space-y-4" aria-label="设备选择和操作">
          {/* 设备选择 */}
          <section className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)]" aria-labelledby="device-select-title">
            <h3 id="device-select-title" className="text-sm font-semibold text-[var(--color-text-primary)] mb-3">
              选择设备
            </h3>
            <div className="space-y-2" role="listbox" aria-label="设备列表">
              {devices.map((device) => (
                <button
                  key={device.id}
                  onClick={() => {
                    setSelectedDeviceImei(device.imei);
                    setShowTrack(false);
                  }}
                  className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] ${
                    selectedDeviceImei === device.imei
                      ? 'bg-[var(--color-primary-bg)] border border-[var(--color-primary)]'
                      : 'bg-[var(--color-bg-secondary)] hover:bg-[var(--color-bg-tertiary)]'
                  }`}
                  role="option"
                  aria-selected={selectedDeviceImei === device.imei}
                >
                  <span
                    className={`w-3 h-3 rounded-full flex-shrink-0 ${
                      device.status === 'online'
                        ? 'bg-[var(--color-success)]'
                        : 'bg-[var(--color-text-muted)]'
                    }`}
                    aria-hidden="true"
                  />
                  <div className="flex-1 text-left">
                    <p className="text-sm font-medium text-[var(--color-text-primary)]">
                      {device.nickname || `设备 ${device.imei.slice(-4)}`}
                    </p>
                    <p className="text-xs text-[var(--color-text-muted)]">
                      {device.battery}% | {device.signalStrength}%
                    </p>
                  </div>
                </button>
              ))}
              {devices.length === 0 && (
                <p className="text-xs text-[var(--color-text-muted)] text-center py-4">
                  暂无绑定设备
                </p>
              )}
            </div>
          </section>

          {/* 轨迹查询 */}
          <section className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)]" aria-labelledby="track-title">
            <h3 id="track-title" className="text-sm font-semibold text-[var(--color-text-primary)] mb-3">
              历史轨迹
            </h3>
            <button
              onClick={handleShowTrack}
              disabled={!selectedDeviceImei}
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 bg-[var(--color-primary)] text-white rounded-xl font-medium text-sm hover:opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed btn-press cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              aria-label="查询24小时轨迹"
            >
              <Clock className="w-4 h-4" aria-hidden="true" />
              查询24小时轨迹
            </button>
            {showTrack && (
              <p className="text-xs text-[var(--color-text-muted)] text-center mt-2" role="status">
                共 {trackPoints.length} 个轨迹点
              </p>
            )}
          </section>

          {/* 图例 */}
          <section className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)]" aria-labelledby="legend-title">
            <h3 id="legend-title" className="text-sm font-semibold text-[var(--color-text-primary)] mb-3">
              图例
            </h3>
            <dl className="space-y-2">
              <div className="flex items-center gap-2">
                <dt className="w-4 h-4 bg-[var(--color-primary)] rounded-full" aria-hidden="true" />
                <dd className="text-xs text-[var(--color-text-secondary)]">设备位置</dd>
              </div>
              <div className="flex items-center gap-2">
                <dt className="w-8 h-0.5 bg-[var(--color-primary)] rounded" aria-hidden="true" />
                <dd className="text-xs text-[var(--color-text-secondary)]">移动轨迹</dd>
              </div>
              <div className="flex items-center gap-2">
                <dt className="w-4 h-4 border-2 border-dashed border-[var(--color-primary)]/40 rounded-full" aria-hidden="true" />
                <dd className="text-xs text-[var(--color-text-secondary)]">定位精度</dd>
              </div>
            </dl>
          </section>
        </aside>
      </div>
    </div>
  );
}
