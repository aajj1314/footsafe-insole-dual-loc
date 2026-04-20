# 足安智能防走失系统

## 📋 更新说明

> **⚠️ 重要更新**: 本项目已从 MySQL 成功迁移到 MariaDB，并且保持了 100% 的向后兼容性。
> 
> - **数据库**: MariaDB 10.11
> - **兼容性**: 现有代码无需任何修改即可正常运行
> - **详情**: 参见 [MARIADB_MIGRATION_GUIDE.md](./MARIADB_MIGRATION_GUIDE.md)

## 项目简介

**足安智能防走失系统**是一个面向老年人和儿童安全的智能物联网平台，通过智能鞋等可穿戴设备实现实时定位、围栏预警、紧急报警等功能。

---

## 功能特性

### 核心功能

| 功能 | 说明 |
|------|------|
| **设备管理** | 绑定/解绑智能设备，查看设备状态（电量、信号、工作模式） |
| **实时定位** | 获取设备当前位置，在地图上展示实时轨迹 |
| **电子围栏** | 设置圆形/矩形安全区域，出入围栏自动报警 |
| **报警管理** | SOS报警、防拆报警、摔倒报警、低电量报警等 |
| **紧急联系人** | 管理紧急联系人，报警时自动通知 |
| **历史轨迹** | 查看设备历史移动轨迹 |
| **用户认证** | JWT Token认证，支持登录注册 |

### 报警类型

- 🔓 **防拆报警** - 设备被拆卸
- ⚠️ **摔倒报警** - 检测到摔倒事件
- 🛑 **静止报警** - 长时间无活动
- 🔋 **低电量报警** - 电量低于阈值
- 🆘 **SOS报警** - 用户主动呼救
- ⏻ **关机报警** - 设备被关机

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                  │
├──────────────────────┬──────────────────────┬───────────────────┤
│   Web管理后台        │   微信小程序          │   智能鞋设备        │
│   (React + Vite)    │   (原生开发)         │   (嵌入式)         │
└──────────┬───────────┴──────────┬───────────┴───────────┬────────┘
           │                     │                       │
           │    HTTP REST API    │    UDP/TCP Protocol   │
           ▼                     ▼                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                        API网关层 (Port 8090)                      │
│                     FastAPI + Uvicorn + JWT                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │  设备管理   │  │  报警管理   │  │  围栏管理   │  │  位置服务   │ │
│  │ /api/devices│ │ /api/alarms│  │ /api/fences│  │/api/locations│ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                        业务服务层                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ 设备服务     │  │ 报警服务     │  │ 位置服务     │           │
│  │ device_service│ │alarm_service │  │location_service│          │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                        数据存储层                                  │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                │
│  │ MySQL  │  │ Redis  │  │InfluxDB│  │ 内存DB │                │
│  │ 用户/设备│  │ 会话/缓存│  │ 时序数据│  │ 设备状态│                │
│  └────────┘  └────────┘  └────────┘  └────────┘                │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                      协议服务层 (Ports 8888/8889)                │
│  ┌────────────────────────────┐  ┌────────────────────────────┐  │
│  │   UDP服务 (设备数据上报)    │  │   TCP服务 (命令下发)       │  │
│  │   Port 8888                │  │   Port 8889                │  │
│  └────────────────────────────┘  └────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | React 18 + TypeScript | Web管理后台 |
| **前端框架** | Vite 8 | 开发服务器和构建工具 |
| **UI框架** | TailwindCSS 4 | 原子化CSS框架 |
| **状态管理** | Zustand | 轻量级状态管理 |
| **HTTP客户端** | Axios | API请求 |
| **后端框架** | FastAPI + Uvicorn | 异步Web框架 |
| **数据库** | MariaDB 10.11 + SQLAlchemy 2.0 | 关系型数据库 |
| **缓存** | Redis | 会话缓存 |
| **时序数据** | InfluxDB | 位置历史数据 |
| **认证** | JWT + OAuth2 | Token认证 |
| **协议** | UDP/TCP Socket | 设备通信 |

---

## 目录结构

```
Server-Full-Stack/
├── app/                          # 后端应用
│   ├── api/                      # API路由
│   │   └── routes/               # 路由模块
│   │       ├── auth.py           # 认证
│   │       ├── devices.py        # 设备管理
│   │       ├── alarms.py         # 报警管理
│   │       ├── fences.py         # 围栏管理
│   │       ├── contacts.py       # 联系人管理
│   │       └── locations.py      # 位置服务
│   ├── core/                     # 核心模块
│   │   ├── database/             # 数据库连接
│   │   │   ├── mariadb.py        # MariaDB
│   │   │   ├── mysql.py          # MySQL (向后兼容)
│   │   │   ├── redis.py          # Redis
│   │   │   └── influxdb.py       # InfluxDB
│   │   ├── security/             # 安全模块
│   │   │   ├── jwt.py           # JWT认证
│   │   │   └── encryption.py     # 加密
│   │   └── memory/               # 内存管理
│   ├── models/                   # 数据模型
│   │   └── orm/                  # ORM模型
│   │       ├── user.py          # 用户模型
│   │       └── device.py         # 设备模型
│   ├── services/                 # 业务服务
│   │   ├── user_service.py      # 用户服务
│   │   └── demo_data_service.py # 演示数据
│   ├── protocol/                 # 协议处理
│   │   ├── udp/                 # UDP协议
│   │   └── tcp/                 # TCP协议
│   └── main.py                  # 主入口
│
├── web/                          # 前端应用
│   ├── src/
│   │   ├── pages/               # 页面组件
│   │   │   ├── LoginPage.tsx   # 登录页
│   │   │   ├── DashboardPage.tsx# 仪表盘
│   │   │   ├── AlarmPage.tsx   # 报警页
│   │   │   ├── DeviceDetailPage.tsx # 设备详情
│   │   │   └── ...
│   │   ├── services/           # API服务
│   │   │   ├── api.ts         # API客户端
│   │   │   ├── auth.ts        # 认证服务
│   │   │   └── device.ts      # 设备服务
│   │   ├── stores/            # 状态管理
│   │   │   ├── authStore.ts   # 认证状态
│   │   │   └── deviceStore.ts # 设备状态
│   │   └── types/             # 类型定义
│   ├── vite.config.ts         # Vite配置
│   └── package.json
│
├── scripts/                      # 脚本
│   ├── init-db.sql            # 数据库初始化
│   └── device_simulator.py    # 设备模拟器
│
├── start.sh                    # 一键启动脚本
├── start-backend.sh           # 后端启动
├── start-frontend.sh          # 前端启动
├── stop.sh                   # 停止服务
└── requirements.txt           # Python依赖

```

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- MariaDB 10.11+
- Redis 6.0+

### 安装依赖

```bash
# 后端依赖
cd Server-Full-Stack
pip install -r requirements.txt

# 前端依赖
cd web
npm install
```

### 启动服务

#### 方式一：一键启动（推荐）

```bash
cd Server-Full-Stack
./start.sh
```

#### 方式二：分开启动

```bash
# 终端1：启动后端
./start-backend.sh

# 终端2：启动前端
./start-frontend.sh
```

### 启动脚本说明

| 脚本 | 说明 |
|------|------|
| `./start.sh` | 一键启动所有服务（前端+后端） |
| `./start-backend.sh` | 仅启动后端服务 |
| `./start-frontend.sh` | 仅启动前端服务 |
| `./stop.sh` | 停止所有服务 |
| `./restart.sh` | 重启所有服务 |
| `./deploy.sh` | 生产环境部署 |

### 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端** | http://localhost:8000 | Web管理后台 |
| **后端API** | http://localhost:8090 | REST API |
| **UDP服务** | 0.0.0.0:8888 | 设备数据上报 |
| **TCP服务** | 0.0.0.0:8889 | 命令下发 |

### 演示账号

| 用户名 | 密码 | 说明 |
|--------|------|------|
| admin | admin | 演示管理员账号 |

---

## API文档

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 用户登录 |
| POST | `/api/auth/register` | 用户注册 |
| GET | `/api/auth/me` | 获取当前用户 |
| POST | `/api/auth/refresh` | 刷新Token |

### 设备接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/devices/` | 获取设备列表 |
| GET | `/api/devices/{imei}` | 获取设备详情 |
| POST | `/api/devices/bind` | 绑定设备 |
| DELETE | `/api/devices/{imei}/unbind` | 解绑设备 |
| PUT | `/api/devices/{imei}/mode` | 设置工作模式 |
| PUT | `/api/devices/{imei}/interval` | 设置上报间隔 |

### 报警接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/alarms/` | 获取报警列表 |
| GET | `/api/alarms/{id}` | 获取报警详情 |
| PUT | `/api/alarms/{id}/handle` | 处理报警 |
| PUT | `/api/alarms/{id}/ignore` | 忽略报警 |

### 位置接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/locations/{imei}/latest` | 获取最新位置 |
| GET | `/api/locations/{imei}/history` | 获取历史轨迹 |

### 围栏接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/fences/` | 获取围栏列表 |
| GET | `/api/fences/{id}` | 获取围栏详情 |
| POST | `/api/fences/` | 创建围栏 |
| PUT | `/api/fences/{id}` | 更新围栏 |
| DELETE | `/api/fences/{id}` | 删除围栏 |

### 联系人接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/contacts/` | 获取联系人列表 |
| GET | `/api/contacts/{id}` | 获取联系人详情 |
| POST | `/api/contacts/` | 创建联系人 |
| PUT | `/api/contacts/{id}` | 更新联系人 |
| DELETE | `/api/contacts/{id}` | 删除联系人 |

---

## 数据库模型

### 用户表 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| username | VARCHAR(64) | 用户名 |
| password_hash | VARCHAR(255) | 密码哈希 |
| phone | VARCHAR(20) | 手机号 |
| email | VARCHAR(128) | 邮箱 |
| nickname | VARCHAR(64) | 昵称 |
| status | ENUM | 状态(active/inactive) |
| created_at | DATETIME | 创建时间 |
| last_login | DATETIME | 最后登录 |

### 设备表 (devices)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| imei | VARCHAR(32) | 设备IMEI |
| iccid | VARCHAR(32) | SIM卡ICCID |
| firmware_version | VARCHAR(32) | 固件版本 |
| status | ENUM | 设备状态 |
| battery | INT | 电量 |
| signal_strength | INT | 信号强度 |
| mode | ENUM | 工作模式 |

### 用户设备关系表 (user_devices)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| user_id | INT | 用户ID |
| device_id | INT | 设备ID |
| nickname | VARCHAR(64) | 设备昵称 |
| relation | VARCHAR(32) | 关系(爷爷/奶奶等) |
| status | ENUM | 绑定状态 |

---

## 配置文件

### 环境变量 (.env)

```bash
# 数据库配置 (优先使用MariaDB配置)
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/zu_an

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 服务端口
HTTP_API_PORT=8090
UDP_PORT=8888
TCP_PORT=8889
```

---

## 生产环境部署

### 服务器要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **配置**: 2核CPU, 4GB内存, 50GB磁盘
- **网络**: 开放端口 8000(前端)、8090(API)、8888(UDP)、8889(TCP)

### 快速部署（推荐）

```bash
# 1. 上传项目到服务器
scp -r Server-Full-Stack user@your-server:/path/to/

# 2. SSH登录服务器
ssh user@your-server

# 3. 进入项目目录
cd /path/to/Server-Full-Stack

# 4. 安装系统依赖
sudo apt update
sudo apt install -y python3.10-venv python3-pip nodejs npm redis-server mariadb-server

# 5. 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库密码等

# 6. 安装Python依赖
pip install -r requirements.txt

# 7. 安装前端依赖
cd web && npm install && cd ..

# 8. 初始化数据库
python3 scripts/init_db.py

# 9. 设置脚本执行权限
chmod +x start.sh start-backend.sh start-frontend.sh stop.sh restart.sh

# 10. 启动服务
./start.sh
```

### 权限问题说明

如果遇到 `.pid` 文件权限问题，使用 `sudo` 运行或手动创建：

```bash
# 方法1: 使用sudo运行脚本
sudo ./start.sh

# 方法2: 手动创建PID文件目录
mkdir -p /path/to/Server-Full-Stack
touch /path/to/Server-Full-Stack/.backend.pid
touch /path/to/Server-Full-Stack/.frontend.pid
chmod 666 /path/to/Server-Full-Stack/.backend.pid
chmod 666 /path/to/Server-Full-Stack/.frontend.pid
```

### Docker部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动部署（前端生产构建）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python scripts/init_db.py

# 3. 构建前端
cd web && npm install
npm run build
cd ..

# 4. 启动后端服务
./start-backend.sh

# 5. 前端使用 nginx 托管 build 目录
```

---

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行指定测试
pytest tests/unit/test_services/

# 生成覆盖率报告
pytest --cov=app tests/
```

### 代码规范

```bash
# 代码格式化
black app/ web/src/

# 导入排序
isort app/ web/src/

# 代码检查
flake8 app/
mypy app/
```

---

## 演示数据

系统内置演示数据，供测试使用：

### 演示设备

| 设备 | IMEI | 关系 | 电量 | 状态 |
|------|------|------|------|------|
| 奶奶的智能鞋 | 861234567890001 | 奶奶 | 85% | 在线 |
| 爷爷的智能鞋 | 861234567890002 | 爷爷 | 62% | 在线 |
| 外婆的智能鞋 | 861234567890003 | 外婆 | 23% | 离线 |

### 演示报警

| 报警类型 | 设备 | 级别 | 状态 |
|----------|------|------|------|
| SOS报警 | 奶奶的智能鞋 | 紧急 | 待处理 |
| 摔倒报警 | 爷爷的智能鞋 | 高 | 已处理 |
| 低电量报警 | 外婆的智能鞋 | 中 | 待处理 |

---

## 常见问题

### Q: 前端端口被占用？

Vite会自动选择可用端口。如果默认8000端口被占用，会自动切换到8001等其他端口。

### Q: 后端启动失败？

1. 检查MariaDB/Redis服务是否运行
2. 检查数据库连接配置
3. 查看 `backend.log` 日志

### Q: 如何添加新用户？

1. 通过API注册：`POST /api/auth/register`
2. 或在数据库中直接插入

### Q: 设备收不到命令？

1. 检查设备网络连接
2. 检查UDP/TCP端口是否开放
3. 确认设备在线状态

---

## 许可证

本项目仅供学习研究使用。

---

## 联系方式

如有问题，请提交Issue。
