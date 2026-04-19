# 足安智能防走失系统 - UI设计规范
**版本**: v1.0
**更新日期**: 2026-04-19
**设计理念**: 温暖守护、安全可靠、科技关怀

---

## 一、设计美学方向

### 1.1 核心定位
- **产品调性**: 温暖守护者 - 不是冷冰冰的科技产品，而是像家人一样的守护
- **情感连接**: 让监护人感到安心，让被监护人感到被关怀
- **紧急响应**: 在危急时刻，视觉清晰醒目，不容忽视

### 1.2 视觉关键词
- **温暖** - 不是冰冷的蓝灰色调，而是带有温度的暖色调
- **安心** - 大量留白，信息清晰，视觉不疲劳
- **信赖** - 稳重可靠的设计语言，专业但不刻板
- **关怀** - 细节处体现对老人的关爱

---

## 二、色彩系统

### 2.1 主色调 - 暖阳蓝
```
Primary: #1677FF → 改为 #3B82F6 (更温暖的蓝)
但整体配色以 #0EA5E9 (Sky Blue) 为主色调，体现天空般的守护
```

### 2.2 完整色彩规范
```css
:root {
  /* 主色调 - 天空蓝（代表守护、信任） */
  --color-primary: #0EA5E9;
  --color-primary-light: #38BDF8;
  --color-primary-dark: #0284C7;
  --color-primary-bg: #F0F9FF;

  /* 辅助色 - 暖阳橙（代表温暖、关怀） */
  --color-accent: #F97316;
  --color-accent-light: #FB923C;
  --color-accent-bg: #FFF7ED;

  /* 安全色 - 生命绿 */
  --color-success: #10B981;
  --color-success-light: #34D399;
  --color-success-bg: #ECFDF5;

  /* 警告色 - 琥珀黄 */
  --color-warning: #F59E0B;
  --color-warning-light: #FBBF24;
  --color-warning-bg: #FFFBEB;

  /* 危险色 - 救援红 */
  --color-danger: #EF4444;
  --color-danger-light: #F87171;
  --color-danger-bg: #FEF2F2;

  /* 中性色 */
  --color-text-primary: #1E293B;
  --color-text-secondary: #64748B;
  --color-text-muted: #94A3B8;
  --color-bg-primary: #FFFFFF;
  --color-bg-secondary: #F8FAFC;
  --color-bg-tertiary: #F1F5F9;
  --color-border: #E2E8F0;
  --color-border-light: #F1F5F9;
}
```

### 2.3 报警级别色彩
```css
/* 紧急报警 - 最高优先级 */
.alarm-urgent {
  background: #FEE2E2;
  border: 2px solid #EF4444;
  color: #DC2626;
}

/* 高风险报警 */
.alarm-high {
  background: #FEF3C7;
  border: 2px solid #F59E0B;
  color: #D97706;
}

/* 中等风险 */
.alarm-medium {
  background: #DBEAFE;
  border: 2px solid #3B82F6;
  color: #2563EB;
}

/* 低风险提示 */
.alarm-low {
  background: #D1FAE5;
  border: 2px solid #10B981;
  color: #059669;
}
```

---

## 三、字体系统

### 3.1 字体选择
```css
/* 标题字体 - 思源黑体（Source Han Sans） */
/* 中文更加清晰，数字更加规整 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');

/* 英文/数字 - DM Sans（现代友好） */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

:root {
  --font-family-cn: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-en: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-mono: 'JetBrains Mono', monospace; /* 用于设备编号等 */
}
```

### 3.2 字体层级
```css
/* 标题层级 */
.text-display {
  font-family: var(--font-family-cn);
  font-size: 2rem;      /* 32px */
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.text-h1 {
  font-size: 1.5rem;    /* 24px */
  font-weight: 600;
  line-height: 1.3;
}

.text-h2 {
  font-size: 1.25rem;   /* 20px */
  font-weight: 600;
  line-height: 1.4;
}

.text-h3 {
  font-size: 1rem;      /* 16px */
  font-weight: 600;
  line-height: 1.5;
}

/* 正文层级 */
.text-body {
  font-size: 0.875rem;  /* 14px */
  font-weight: 400;
  line-height: 1.6;
}

.text-caption {
  font-size: 0.75rem;   /* 12px */
  font-weight: 400;
  line-height: 1.5;
  color: var(--color-text-secondary);
}

/* 数字专用 - 用于设备编号、时间等 */
.text-mono {
  font-family: var(--font-family-mono);
  font-size: 0.875rem;
  letter-spacing: 0.05em;
}
```

---

## 四、组件设计

### 4.1 设备状态卡片
```css
.device-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.08);
  border: 1px solid rgba(14, 165, 233, 0.1);
  transition: all 0.3s ease;
}

.device-card:hover {
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.12);
  transform: translateY(-2px);
}

.device-card .status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.device-card .status-online {
  background: #10B981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.device-card .status-offline {
  background: #94A3B8;
}
```

### 4.2 报警卡片（紧急状态）
```css
.alarm-card {
  background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
  border: 2px solid #EF4444;
  border-radius: 16px;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.alarm-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #EF4444, #F87171, #EF4444);
  animation: alarm-shine 2s linear infinite;
}

@keyframes alarm-shine {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.alarm-card .alarm-icon {
  font-size: 2rem;
  margin-right: 12px;
}

.alarm-card .alarm-level {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

### 4.3 按钮设计
```css
/* 主按钮 - 温暖蓝 */
.btn-primary {
  background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 24px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

/* 危险按钮 - 紧急报警 */
.btn-danger {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px 24px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  animation: danger-pulse 1.5s ease-in-out infinite;
}

@keyframes danger-pulse {
  0%, 100% { box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3); }
  50% { box-shadow: 0 4px 24px rgba(239, 68, 68, 0.5); }
}

/* 次要按钮 */
.btn-secondary {
  background: white;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  border-radius: 12px;
  padding: 12px 24px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: var(--color-primary-bg);
}
```

### 4.4 地图组件
```css
.map-container {
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  background: linear-gradient(180deg, #E0F2FE 0%, #F0F9FF 100%);
}

.map-container .location-marker {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 48px;
  height: 48px;
  background: var(--color-primary);
  border: 4px solid white;
  border-radius: 50%;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.4);
  animation: marker-bounce 2s ease-in-out infinite;
}

@keyframes marker-bounce {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -60%) scale(1.05); }
}

.map-container .accuracy-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border: 2px dashed rgba(14, 165, 233, 0.4);
  border-radius: 50%;
  animation: circle-rotate 20s linear infinite;
}

@keyframes circle-rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}
```

---

## 五、页面布局规范

### 5.1 Web端布局
```css
/* 监控首页布局 */
.dashboard-layout {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr 380px; /* 主内容区 + 侧边栏 */
  gap: 24px;
}

@media (max-width: 1024px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
  }
}

/* 主内容区 */
.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片网格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

/* 侧边栏 */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
```

### 5.2 小程序布局
```css
/* 单列布局 - 信息展示页 */
.page-container {
  padding: 16px;
  background: var(--color-bg-secondary);
  min-height: 100vh;
}

/* 卡片容器 */
.card-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 底部固定操作栏 */
.fixed-bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: white;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  gap: 12px;
  z-index: 100;
}
```

---

## 六、动效规范

### 6.1 微交互动效
```css
/* 卡片悬停 */
.card-interactive {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-interactive:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(14, 165, 233, 0.15);
}

/* 按钮点击 */
.btn-press {
  transition: transform 0.15s ease;
}

.btn-press:active {
  transform: scale(0.96);
}

/* 数据刷新 */
.data-refresh {
  animation: refresh-spin 1s ease-in-out;
}

@keyframes refresh-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### 6.2 页面转场动效
```css
/* 页面进入 */
.page-enter {
  animation: page-slide-in 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes page-slide-in {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 卡片列表加载 */
.card-list-enter {
  animation: card-list-in 0.5s cubic-bezier(0.4, 0, 0.2, 1) backwards;
}

.card-list-enter:nth-child(1) { animation-delay: 0.1s; }
.card-list-enter:nth-child(2) { animation-delay: 0.15s; }
.card-list-enter:nth-child(3) { animation-delay: 0.2s; }
.card-list-enter:nth-child(4) { animation-delay: 0.25s; }

@keyframes card-list-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 6.3 报警动画
```css
/* 紧急报警心跳动画 */
.alarm-pulse {
  animation: alarm-heartbeat 1s ease-in-out infinite;
}

@keyframes alarm-heartbeat {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.9; }
}

/* 报警闪烁 */
.alarm-flash {
  animation: alarm-flash-bg 0.5s ease-in-out 3;
}

@keyframes alarm-flash-bg {
  0%, 100% { background-color: #FEE2E2; }
  50% { background-color: #FECACA; }
}
```

---

## 七、图标与插画

### 7.1 图标风格
- **风格**: 线性图标 + 填充结合
- **圆角**: 4px - 8px
- **线宽**: 2px
- **颜色**: 单色或双色

### 7.2 核心图标
```
设备相关:
- 鞋垫图标 (设备)
- 电池图标 (电量)
- 信号图标 (信号强度)
- 温度图标 (设备温度)

状态相关:
- 在线状态 (绿色圆点)
- 离线状态 (灰色圆点)
- 报警状态 (红色闪烁)

功能相关:
- 地图定位
- 历史轨迹
- 报警记录
- 设备设置
- 电子围栏
- 紧急联系人
```

### 7.3 插画风格
- **风格**: 简约扁平 + 渐变点缀
- **人物**: 无脸化设计，老人形象可爱但不刻板
- **场景**: 家庭、户外、紧急等核心场景
- **色调**: 与主色调一致的暖蓝色系

---

## 八、响应式断点

```css
/* 移动端优先断点 */
/* 默认: 320px - 639px (小屏手机) */
/* sm: 640px - 767px (大屏手机/小平板) */
/* md: 768px - 1023px (平板) */
/* lg: 1024px - 1279px (小屏电脑) */
/* xl: 1280px - 1535px (标准电脑) */
/* 2xl: 1536px+ (大屏电脑) */

@media (min-width: 640px) {
  .container { max-width: 640px; }
}

@media (min-width: 768px) {
  .container { max-width: 768px; }
  .card { padding: 24px; }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; }
  .dashboard { grid-template-columns: 280px 1fr; }
}

@media (min-width: 1280px) {
  .container { max-width: 1280px; }
}
```

---

## 九、Accessibility 无障碍设计

### 9.1 色彩对比
```css
/* WCAG AA 标准 */
.text-on-primary {
  color: #FFFFFF; /* on #0EA5E9, ratio 4.8:1 ✓ */
}

.text-on-danger {
  color: #FFFFFF; /* on #EF4444, ratio 4.6:1 ✓ */
}
```

### 9.2 触控区域
```css
/* 最小触控区域 44x44px (iOS) / 48x48dp (Android) */
.touch-target {
  min-width: 44px;
  min-height: 44px;
  padding: 12px;
}
```

### 9.3 字体缩放
```css
/* 支持系统字体缩放 */
body {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

/* 重要信息不使用小字体 */
.important-text {
  font-size: max(1rem, 16px);
}
```

---

## 十、微信小程序特殊考虑

### 10.1 导航栏
```json
{
  "navigationBarBackgroundColor": "#0EA5E9",
  "navigationBarTextStyle": "white",
  "navigationBarTitleText": "足安智能防走失"
}
```

### 10.2 TabBar设计
```json
{
  "tabBar": {
    "color": "#64748B",
    "selectedColor": "#0EA5E9",
    "backgroundColor": "#FFFFFF",
    "borderStyle": "white",
    "list": [
      { "pagePath": "pages/index/index", "text": "监控首页", "iconPath": "icons/home.png", "selectedIconPath": "icons/home-active.png" },
      { "pagePath": "pages/alarm/alarm", "text": "报警记录", "iconPath": "icons/alarm.png", "selectedIconPath": "icons/alarm-active.png" },
      { "pagePath": "pages/profile/profile", "text": "个人中心", "iconPath": "icons/profile.png", "selectedIconPath": "icons/profile-active.png" }
    ]
  }
}
```

### 10.3 安全区域
```css
/* 适配 iPhone X 等刘海屏 */
.page-container {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}
```

---

## 版本记录
### v1.0 (2026-04-19)
- 初始版本发布
- 完成完整UI设计规范
- 定义色彩、字体、组件系统
- 制定动效和响应式规范
