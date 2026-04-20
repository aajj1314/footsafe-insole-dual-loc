# 足安智能防走失系统 Code Wiki

## 1. 仓库概览

**足安智能防走失系统**是一个面向老年人和儿童安全的智能物联网平台，通过智能鞋等可穿戴设备实现实时定位、围栏预警、紧急报警等功能。

### 主要功能/亮点：
- **设备管理**：绑定/解绑智能设备，查看设备状态（电量、信号、工作模式）
- **实时定位**：获取设备当前位置，在地图上展示实时轨迹
- **电子围栏**：设置圆形/矩形安全区域，出入围栏自动报警
- **报警管理**：SOS报警、防拆报警、摔倒报警、低电量报警等
- **紧急联系人**：管理紧急联系人，报警时自动通知
- **历史轨迹**：查看设备历史移动轨迹
- **用户认证**：JWT Token认证，支持登录注册

### 典型应用场景：
- 老年人照护：通过智能鞋实时监控老人位置，设置安全区域，防止走失
- 儿童安全：实时追踪儿童位置，设置学校、家等安全区域，异常情况及时报警
- 特殊人群监护：为认知障碍患者提供定位服务，确保其安全

## 2. 目录结构

项目采用前后端分离架构，后端基于FastAPI构建，前端使用React + TypeScript。整体结构清晰，分为后端应用、前端应用、脚本和测试四大部分。

```text
├── app/                  # 后端应用
│   ├── api/              # API路由
│   │   └── routes/       # 路由模块
│   │       ├── auth.py   # 认证
│   │       ├── devices.py# 设备管理
│   │       ├── alarms.py # 报警管理
│   │       ├── fences.py # 围栏管理
│   │       ├── contacts.py # 联系人管理
│   │       └── locations.py # 位置服务
│   ├── config/           # 配置模块
│   ├── core/             # 核心模块
│   │   ├── database/     # 数据库连接
│   │   ├── memory/       # 内存管理
│   │   ├── network/      # 网络相关
│   │   └── security/     # 安全模块
│   ├── middleware/       # 中间件
│   ├── models/           # 数据模型
│   │   ├── orm/          # ORM模型
│   │   └── schemas/      # 数据校验
│   ├── protocol/         # 协议处理
│   │   ├── tcp/          # TCP协议
│   │   └── udp/          # UDP协议
│   ├── services/         # 业务服务
│   ├── tasks/            # 后台任务
│   ├── utils/            # 工具函数
│   └── main.py           # 主入口
├── web/                  # 前端应用
│   ├── src/              # 源代码
│   │   ├── pages/        # 页面组件
│   │   ├── services/     # API服务
│   │   ├── stores/       # 状态管理
│   │   └── types/        # 类型定义
│   ├── public/           # 静态资源
│   └── package.json      # 依赖配置
├── scripts/              # 脚本
│   ├── init_db.py        # 数据库初始化
│   └── device_simulator.py # 设备模拟器
├── tests/                # 测试
│   ├── unit/             # 单元测试
│   └── integration/      # 集成测试
├── requirements.txt      # Python依赖
├── start.sh              # 一键启动脚本
└── docker-compose.yml    # Docker配置
```

### 核心目录详解：

| 目录 | 主要职责 | 文件位置 | 说明 |
|------|---------|----------|------|
| **api/routes** | API路由定义 | [app/api/routes/](file:///workspace/app/api/routes/) | 包含认证、设备、报警、围栏、联系人和位置服务的API路由 |
| **core/database** | 数据库连接管理 | [app/core/database/](file:///workspace/app/core/database/) | 管理MySQL、Redis和InfluxDB的连接 |
| **core/security** | 安全相关功能 | [app/core/security/](file:///workspace/app/core/security/) | 包含JWT认证、加密、校验和等安全功能 |
| **protocol** | 设备通信协议 | [app/protocol/](file:///workspace/app/protocol/) | 处理UDP和TCP协议的设备通信 |
| **services** | 业务逻辑服务 | [app/services/](file:///workspace/app/services/) | 包含设备、报警、位置等核心业务逻辑 |
| **web/src** | 前端源代码 | [web/src/](file:///workspace/web/src/) | 包含前端页面、服务和状态管理 |

## 3. 系统架构与主流程

### 架构设计

系统采用分层架构，从客户端到数据存储层清晰分离，确保系统的可扩展性和可维护性。

```mermaid
flowchart TD
    subgraph 客户端层
        Web[Web管理后台<br>React + TypeScript] --> API
        WeChat[微信小程序<br>原生开发] --> API
        Device[智能鞋设备<br>嵌入式] --> UDP
        Device --> TCP
    end

    subgraph API网关层
        API[HTTP REST API<br>FastAPI + Uvicorn] --> Auth[认证服务]
        API --> DeviceAPI[设备管理]
        API --> AlarmAPI[报警管理]
        API --> FenceAPI[围栏管理]
        API --> LocationAPI[位置服务]
    end

    subgraph 业务服务层
        Auth --> UserService[用户服务]
        DeviceAPI --> DeviceService[设备服务]
        AlarmAPI --> AlarmService[报警服务]
        FenceAPI --> FenceService[围栏服务]
        LocationAPI --> LocationService[位置服务]
    end

    subgraph 数据存储层
        UserService --> MySQL[(MySQL<br>用户/设备数据)]
        DeviceService --> MySQL
        AlarmService --> MySQL
        FenceService --> MySQL
        LocationService --> InfluxDB[(InfluxDB<br>时序数据)]
        DeviceService --> Redis[(Redis<br>会话/缓存)]
        Auth --> Redis
    end

    subgraph 协议服务层
        UDP[UDP服务<br>设备数据上报] --> DeviceService
        UDP --> LocationService
        UDP --> AlarmService
        TCP[TCP服务<br>命令下发] --> DeviceService
    end
```

### 主要流程

1. **设备通信流程**：
   - 设备通过UDP协议上报位置、状态和报警信息
   - 服务器接收UDP数据包并解析
   - 根据消息类型分发到对应的处理服务
   - 服务器通过TCP协议向设备下发命令

2. **用户操作流程**：
   - 用户通过Web后台或小程序登录系统
   - 绑定智能设备到账户
   - 查看设备实时位置和状态
   - 设置电子围栏和报警规则
   - 接收和处理设备报警

3. **数据处理流程**：
   - 位置数据存储到InfluxDB作为时序数据
   - 设备和用户数据存储到MySQL
   - 会话和缓存数据存储到Redis
   - 实时数据通过内存缓存提高性能

## 4. 核心功能模块

### 4.1 设备管理

**功能说明**：管理智能设备的绑定、解绑、状态监控等操作。

**实现细节**：
- 设备绑定：用户通过IMEI号绑定设备到账户
- 设备状态：实时监控设备电量、信号强度、工作模式
- 设备管理：支持设备解绑、模式切换、上报间隔设置

**核心代码**：
- [设备路由](file:///workspace/app/api/routes/devices.py)：处理设备相关API请求
- [设备服务](file:///workspace/app/services/device_service.py)：实现设备管理业务逻辑

### 4.2 实时定位

**功能说明**：获取设备实时位置，展示历史轨迹。

**实现细节**：
- 设备通过UDP协议定期上报位置数据
- 位置数据存储到InfluxDB作为时序数据
- 提供API查询最新位置和历史轨迹
- 地图展示设备位置和移动轨迹

**核心代码**：
- [位置路由](file:///workspace/app/api/routes/locations.py)：处理位置相关API请求
- [位置服务](file:///workspace/app/services/location_service.py)：处理位置数据业务逻辑

### 4.3 电子围栏

**功能说明**：设置安全区域，当设备进出围栏时触发报警。

**实现细节**：
- 支持圆形和矩形围栏设置
- 围栏边界计算和位置判断
- 进出围栏事件检测和报警

**核心代码**：
- [围栏路由](file:///workspace/app/api/routes/fences.py)：处理围栏相关API请求
- 围栏服务：实现围栏管理和边界检测逻辑

### 4.4 报警管理

**功能说明**：处理和管理设备产生的各种报警。

**实现细节**：
- 支持多种报警类型：SOS、防拆、摔倒、低电量等
- 报警分级和处理流程
- 报警通知和紧急联系人提醒

**核心代码**：
- [报警路由](file:///workspace/app/api/routes/alarms.py)：处理报警相关API请求
- [报警服务](file:///workspace/app/services/alarm_service.py)：处理报警业务逻辑

### 4.5 用户认证

**功能说明**：用户注册、登录和权限管理。

**实现细节**：
- JWT Token认证
- 用户注册和登录
- 权限控制和会话管理

**核心代码**：
- [认证路由](file:///workspace/app/api/routes/auth.py)：处理认证相关API请求
- [用户服务](file:///workspace/app/services/user_service.py)：处理用户管理业务逻辑
- [JWT模块](file:///workspace/app/core/security/jwt.py)：实现JWT认证功能

### 4.6 协议处理

**功能说明**：处理设备与服务器之间的通信协议。

**实现细节**：
- UDP协议：设备数据上报（位置、状态、报警）
- TCP协议：服务器命令下发（配置、控制）
- 消息解析和序列化
- 安全验证（校验和、nonce）

**核心代码**：
- [UDP服务器](file:///workspace/app/protocol/udp/server.py)：处理UDP协议数据
- [TCP服务器](file:///workspace/app/protocol/tcp/server.py)：处理TCP协议数据
- [消息解析器](file:///workspace/app/protocol/parser.py)：解析设备消息

## 5. 核心 API/类/函数

### 5.1 后端核心API

| API路径 | 方法 | 功能说明 | 模块 |
|---------|------|----------|------|
| `/api/auth/login` | POST | 用户登录 | [auth.py](file:///workspace/app/api/routes/auth.py) |
| `/api/auth/register` | POST | 用户注册 | [auth.py](file:///workspace/app/api/routes/auth.py) |
| `/api/devices/` | GET | 获取设备列表 | [devices.py](file:///workspace/app/api/routes/devices.py) |
| `/api/devices/bind` | POST | 绑定设备 | [devices.py](file:///workspace/app/api/routes/devices.py) |
| `/api/devices/{imei}/unbind` | DELETE | 解绑设备 | [devices.py](file:///workspace/app/api/routes/devices.py) |
| `/api/alarms/` | GET | 获取报警列表 | [alarms.py](file:///workspace/app/api/routes/alarms.py) |
| `/api/alarms/{id}/handle` | PUT | 处理报警 | [alarms.py](file:///workspace/app/api/routes/alarms.py) |
| `/api/locations/{imei}/latest` | GET | 获取最新位置 | [locations.py](file:///workspace/app/api/routes/locations.py) |
| `/api/locations/{imei}/history` | GET | 获取历史轨迹 | [locations.py](file:///workspace/app/api/routes/locations.py) |
| `/api/fences/` | POST | 创建围栏 | [fences.py](file:///workspace/app/api/routes/fences.py) |
| `/api/contacts/` | POST | 创建联系人 | [contacts.py](file:///workspace/app/api/routes/contacts.py) |

### 5.2 核心类

#### DeviceService
**功能**：设备管理核心服务，负责设备信息的获取、更新和状态管理。

**主要方法**：
- `get_device(device_id)`：获取设备信息
- `register_device(device_id, iccid, firmware_version, hardware_version)`：注册设备
- `update_device(device_id, updates)`：更新设备信息
- `update_location(device_id, latitude, longitude, battery, signal_strength, mode)`：更新设备位置

**文件位置**：[app/services/device_service.py](file:///workspace/app/services/device_service.py)

#### UDPServer
**功能**：UDP服务器，负责接收设备上报的数据。

**主要方法**：
- `start()`：启动UDP服务器
- `stop()`：停止UDP服务器
- `handle_packet(data, addr)`：处理接收到的UDP数据包

**文件位置**：[app/protocol/udp/server.py](file:///workspace/app/protocol/udp/server.py)

#### TCPServer
**功能**：TCP服务器，负责向设备下发命令。

**主要方法**：
- `start()`：启动TCP服务器
- `stop()`：停止TCP服务器
- `send_command(device_id, command)`：向设备发送命令

**文件位置**：[app/protocol/tcp/server.py](file:///workspace/app/protocol/tcp/server.py)

#### UserService
**功能**：用户管理服务，负责用户认证和管理。

**主要方法**：
- `create_user(username, password, phone, email)`：创建用户
- `authenticate(username, password)`：用户认证
- `get_by_id(user_id)`：根据ID获取用户
- `get_by_username(username)`：根据用户名获取用户

**文件位置**：[app/services/user_service.py](file:///workspace/app/services/user_service.py)

#### SecurityAuditor
**功能**：安全审计器，负责记录安全相关事件。

**主要方法**：
- `start()`：启动安全审计
- `log_event(event_type, device_id, extra_data)`：记录安全事件

**文件位置**：[app/core/security/audit.py](file:///workspace/app/core/security/audit.py)

### 5.3 核心函数

#### handle_location(message, addr)
**功能**：处理设备上报的位置数据。

**参数**：
- `message`：位置消息字典
- `addr`：设备地址

**文件位置**：[app/services/location_service.py](file:///workspace/app/services/location_service.py)

#### handle_alarm(message, addr)
**功能**：处理设备上报的报警数据。

**参数**：
- `message`：报警消息字典
- `addr`：设备地址

**文件位置**：[app/services/alarm_service.py](file:///workspace/app/services/alarm_service.py)

#### handle_heartbeat(message, remote_addr)
**功能**：处理设备上报的心跳数据。

**参数**：
- `message`：心跳消息字典
- `remote_addr`：设备地址

**文件位置**：[app/services/device_service.py](file:///workspace/app/services/device_service.py)

#### create_access_token(data)
**功能**：创建JWT访问令牌。

**参数**：
- `data`：令牌数据

**返回值**：JWT令牌字符串

**文件位置**：[app/core/security/jwt.py](file:///workspace/app/core/security/jwt.py)

#### verify_token(token)
**功能**：验证JWT令牌。

**参数**：
- `token`：JWT令牌字符串

**返回值**：令牌载荷或None

**文件位置**：[app/core/security/jwt.py](file:///workspace/app/core/security/jwt.py)

## 6. 技术栈与依赖

### 6.1 后端技术栈

| 技术 | 版本 | 用途 | 来源 |
|------|------|------|------|
| Python | 3.10+ | 主要开发语言 | [requirements.txt](file:///workspace/requirements.txt) |
| FastAPI | 0.104.1 | 异步Web框架 | [requirements.txt](file:///workspace/requirements.txt) |
| Uvicorn | 0.24.0 | ASGI服务器 | [requirements.txt](file:///workspace/requirements.txt) |
| SQLAlchemy | 2.0.23 | ORM框架 | [requirements.txt](file:///workspace/requirements.txt) |
| MySQL | 8.0+ | 关系型数据库 | [README.md](file:///workspace/README.md) |
| Redis | 6.0+ | 缓存和会话管理 | [README.md](file:///workspace/README.md) |
| InfluxDB | - | 时序数据库 | [README.md](file:///workspace/README.md) |
| JWT | - | 认证令牌 | [app/core/security/jwt.py](file:///workspace/app/core/security/jwt.py) |

### 6.2 前端技术栈

| 技术 | 版本 | 用途 | 来源 |
|------|------|------|------|
| React | 18+ | 前端框架 | [web/package.json](file:///workspace/web/package.json) |
| TypeScript | - | 类型系统 | [web/package.json](file:///workspace/web/package.json) |
| Vite | 8+ | 构建工具 | [web/package.json](file:///workspace/web/package.json) |
| TailwindCSS | 4+ | CSS框架 | [web/package.json](file:///workspace/web/package.json) |
| Zustand | - | 状态管理 | [web/package.json](file:///workspace/web/package.json) |
| Axios | - | HTTP客户端 | [web/package.json](file:///workspace/web/package.json) |

### 6.3 依赖关系

```mermaid
graph TD
    FastAPI --> Uvicorn
    FastAPI --> SQLAlchemy
    SQLAlchemy --> MySQL
    DeviceService --> Redis
    DeviceService --> MySQL
    LocationService --> InfluxDB
    LocationService --> MySQL
    AlarmService --> MySQL
    UserService --> MySQL
    UserService --> JWT
    UDPServer --> DeviceService
    UDPServer --> LocationService
    UDPServer --> AlarmService
    TCPServer --> DeviceService
    WebUI --> FastAPI
```

## 7. 关键模块与典型用例

### 7.1 设备绑定流程

**功能说明**：用户将智能设备绑定到自己的账户。

**配置与依赖**：
- 需要设备IMEI号
- 用户已登录系统

**使用示例**：

```python
# API调用示例
POST /api/devices/bind
{
  "device_imei": "861234567890001",
  "nickname": "奶奶的智能鞋",
  "relation": "奶奶"
}

# 后端处理流程
1. 验证设备是否存在
2. 检查设备是否已被其他用户绑定
3. 创建用户设备绑定关系
4. 返回绑定结果
```

### 7.2 实时定位查询

**功能说明**：查询设备的实时位置和历史轨迹。

**配置与依赖**：
- 设备已绑定到用户账户
- 设备已开启定位功能

**使用示例**：

```python
# 获取最新位置
GET /api/locations/{imei}/latest

# 获取历史轨迹
GET /api/locations/{imei}/history?start_time=2026-04-19T00:00:00&end_time=2026-04-20T00:00:00
```

### 7.3 电子围栏设置

**功能说明**：设置安全区域，当设备进出围栏时触发报警。

**配置与依赖**：
- 设备已绑定到用户账户
- 围栏类型（圆形/矩形）
- 围栏边界参数

**使用示例**：

```python
# 创建圆形围栏
POST /api/fences/
{
  "name": "家",
  "type": "circle",
  "center_lat": 39.9042,
  "center_lng": 116.4074,
  "radius": 100,
  "device_imei": "861234567890001",
  "alert_on_enter": true,
  "alert_on_exit": true
}
```

### 7.4 报警处理

**功能说明**：处理设备产生的各种报警。

**配置与依赖**：
- 设备已绑定到用户账户
- 紧急联系人已设置

**使用示例**：

```python
# 获取报警列表
GET /api/alarms/

# 处理报警
PUT /api/alarms/{id}/handle
{
  "status": "handled",
  "note": "已确认安全"
}
```

## 8. 配置、部署与开发

### 8.1 环境配置

**环境变量**：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | MySQL数据库连接URL | mysql+aiomysql://user:password@localhost:3306/zu_an |
| REDIS_URL | Redis连接URL | redis://localhost:6379/0 |
| JWT_SECRET_KEY | JWT密钥 | your-secret-key |
| JWT_ALGORITHM | JWT算法 | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 令牌过期时间 | 1440 |
| HTTP_API_PORT | HTTP API端口 | 8090 |
| UDP_PORT | UDP服务端口 | 8888 |
| TCP_PORT | TCP服务端口 | 8889 |

**配置文件**：
- [.env.example](file:///workspace/.env.example)：环境变量示例
- [app/config/settings.py](file:///workspace/app/config/settings.py)：应用配置

### 8.2 部署方式

#### 一键启动（推荐）

```bash
cd Server-Full-Stack
./start.sh
```

#### 分开启动

```bash
# 启动后端
./start-backend.sh

# 启动前端
./start-frontend.sh
```

#### Docker部署

```bash
docker-compose up -d
```

### 8.3 开发流程

**安装依赖**：

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd web
npm install
```

**运行测试**：

```bash
# 运行所有测试
pytest

# 运行指定测试
pytest tests/unit/test_services/

# 生成覆盖率报告
pytest --cov=app tests/
```

**代码规范**：

```bash
# 代码格式化
black app/ web/src/

# 导入排序
isort app/ web/src/

# 代码检查
flake8 app/
mypy app/
```

## 9. 监控与维护

### 9.1 日志管理

**日志文件**：
- 后端日志：`backend.log`
- 前端日志：浏览器控制台

**日志级别**：
- INFO：常规信息
- WARNING：警告信息
- ERROR：错误信息
- DEBUG：调试信息

### 9.2 内存监控

系统内置内存监控功能，通过`memory_monitor`模块监控内存使用情况，防止内存泄漏。

**核心文件**：
- [app/core/memory/monitor.py](file:///workspace/app/core/memory/monitor.py)
- [app/core/memory/gc_manager.py](file:///workspace/app/core/memory/gc_manager.py)

### 9.3 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 前端端口被占用 | 端口8000已被其他服务使用 | Vite会自动切换到可用端口 |
| 后端启动失败 | 数据库连接失败 | 检查MySQL/Redis服务是否运行，检查数据库连接配置 |
| 设备收不到命令 | 网络连接问题 | 检查设备网络连接，检查UDP/TCP端口是否开放 |
| 定位不准确 | GPS信号问题 | 确保设备在开阔环境中，检查设备GPS模块 |
| 报警不触发 | 围栏设置问题 | 检查围栏设置是否正确，检查设备位置上报是否正常 |

## 10. 总结与亮点回顾

### 10.1 系统亮点

1. **完整的物联网架构**：实现了从设备端到服务器端的完整物联网解决方案，包括设备通信、数据处理、用户交互等各个环节。

2. **多协议支持**：同时支持UDP和TCP协议，UDP用于设备数据上报，TCP用于命令下发，优化了通信效率和可靠性。

3. **多层次数据存储**：根据数据类型选择合适的存储方案，MySQL存储关系数据，InfluxDB存储时序数据，Redis存储缓存和会话数据。

4. **安全性设计**：实现了JWT认证、数据校验和、nonce验证等多重安全机制，保障系统和数据安全。

5. **实时监控**：通过内存监控、安全审计等模块，实现了系统运行状态的实时监控。

6. **可扩展性**：采用模块化设计，各组件职责清晰，便于功能扩展和维护。

7. **用户友好**：提供了Web管理后台和微信小程序两种访问方式，界面直观易用。

### 10.2 应用价值

足安智能防走失系统通过物联网技术，为老年人和儿童的安全提供了有力保障：

- **减少走失风险**：实时定位和电子围栏功能，有效防止老年人和儿童走失。
- **及时响应紧急情况**：SOS报警、摔倒报警等功能，确保在紧急情况下能够及时得到救助。
- **减轻照护负担**：通过技术手段，减轻家人的照护负担，提高照护效率。
- **数据驱动决策**：通过历史轨迹和行为分析，为照护提供数据支持。

### 10.3 未来发展方向

1. **AI智能分析**：引入AI技术，分析用户行为模式，预测可能的危险情况。
2. **多设备支持**：扩展支持更多类型的可穿戴设备，如智能手表、手环等。
3. **5G网络优化**：利用5G网络的低延迟特性，进一步提高定位精度和实时性。
4. **健康监测**：集成健康监测功能，如心率、血压等，提供更全面的健康管理。
5. **社区联防**：建立社区联防机制，当老年人或儿童走失时，发动社区力量共同寻找。

足安智能防走失系统不仅是一个技术产品，更是一个关爱老人和儿童的社会责任项目，通过科技手段为弱势群体提供安全保障，体现了科技向善的理念。