# 会议系统后端服务

基于 Python3 + Flask + 通义听悟 开发的会议系统后端服务，提供实时语音转写、会议管理、摘要生成等功能。

## 功能特性

- ✅ 会议管理（创建、查询、停止）
- ✅ 实时语音转写（WebSocket支持）
- ✅ 会议摘要生成
- ✅ 会议要点提取
- ✅ RESTful API接口
- ✅ WebSocket实时通信
- ✅ 用户认证和授权（JWT）
- ✅ 数据库存储（SQLite）
- ✅ 音频文件上传和处理
- ✅ 音频格式转换（支持多种格式）

## 技术栈

- Python 3.x
- Flask 3.0
- Flask-SocketIO（WebSocket支持）
- Flask-SQLAlchemy（数据库ORM）
- Flask-JWT-Extended（JWT认证）
- 通义听悟SDK（阿里云智能语音服务）
- Flask-CORS（跨域支持）
- pydub（音频处理）

## 项目结构

```
TeacherPreparationServer/
├── app.py                 # Flask应用主文件
├── config.py             # 配置文件
├── database.py           # 数据库配置
├── requirements.txt      # Python依赖
├── .env.example         # 环境变量示例
├── routes/              # 路由模块
│   ├── __init__.py
│   ├── health.py        # 健康检查
│   ├── auth.py          # 用户认证API
│   ├── meeting.py       # 会议相关API
│   └── audio.py         # 音频上传API
├── models/              # 数据模型
│   ├── __init__.py
│   ├── user.py          # 用户模型
│   ├── meeting.py       # 会议模型
│   └── transcript.py    # 转写记录模型
├── services/            # 服务层
│   ├── __init__.py
│   ├── tytingwu_service.py      # 通义听悟服务集成
│   ├── tytingwu_websocket.py   # 通义听悟WebSocket客户端
│   ├── meeting_service.py       # 会议服务
│   ├── auth_service.py          # 认证服务
│   ├── audio_service.py         # 音频处理服务
│   └── websocket_service.py     # WebSocket服务
├── utils/               # 工具模块
│   ├── __init__.py
│   └── error_handler.py # 错误处理
└── tests/               # 测试
    ├── __init__.py
    └── test_api.py      # API测试脚本
```

## 安装和配置

### 1. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装通义听悟实时转写SDK（需要先下载whl文件）
# 步骤：
# 1. 访问阿里云官方文档下载whl文件: https://help.aliyun.com/zh/tingwu/install-the-sdk
# 2. 下载 nls-1.1.0-py3-none-any.whl 文件
# 3. 执行安装命令:
pip install nls-1.1.0-py3-none-any.whl

# 如果whl文件在其他路径，使用完整路径:
# pip install /path/to/nls-1.1.0-py3-none-any.whl
```

**注意**：
- 实时转写SDK的whl文件需要从阿里云官方文档下载，无法通过pip直接安装
- 如果不需要实时转写功能，可以跳过SDK安装，但创建实时转写任务的功能将不可用

### 2. 配置环境变量

项目已包含 `.env` 文件，你可以直接编辑它来配置：

```bash
# 编辑.env文件
nano .env
# 或使用其他编辑器
```

`.env` 文件配置说明：

```env
# Flask应用配置（必需）
SECRET_KEY=your-secret-key-here  # 生产环境请修改为强密码
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5001  # 默认5001，避免与macOS AirPlay冲突

# 阿里云AccessKey配置（可选，用于通义听悟服务）
# 如果未配置，通义听悟相关功能将不可用，但其他功能正常
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret

# 通义听悟项目AppKey（可选，只需要AppKey，不需要AppSecret）
# 在阿里云控制台创建通义听悟项目后获取
TYTINGWU_APP_KEY=your_app_key

# 数据库配置（可选，默认使用SQLite）
# DATABASE_URL=sqlite:///meetings.db
```

**重要提示**：
- ✅ **必需配置**：`SECRET_KEY`（生产环境必须修改）
- ⚠️ **可选配置**：通义听悟相关配置（未配置时功能受限，但服务可正常启动）
- 📝 如果只是开发和测试，可以保持默认配置，服务会正常启动

### 3. 获取通义听悟配置

1. 登录[阿里云控制台](https://www.aliyun.com/)
2. 开通通义听悟服务
3. 创建项目，获取 AppKey（只需要AppKey，不需要AppSecret）
4. 获取 AccessKey ID 和 AccessKey Secret（用于API认证）

## 运行服务

```bash
python app.py
```

服务将在 `http://0.0.0.0:5001` 启动（默认端口5001，避免与macOS AirPlay Receiver冲突）。

**注意**：如果端口5001也被占用，可以在`.env`文件中修改`FLASK_PORT`配置。

### 访问在线API文档

启动服务后，访问以下地址查看完整的API文档：

```
http://localhost:5001/api/docs
```

Swagger UI 提供了：
- 📖 完整的API接口文档
- 🧪 在线API测试功能
- 📝 请求/响应示例
- 🔐 JWT认证测试支持

## API文档

### 健康检查

```http
GET /health
```

响应：
```json
{
  "status": "ok",
  "message": "服务运行正常"
}
```

### 用户认证

#### 用户注册

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

响应：
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "注册成功"
}
```

#### 用户登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

或使用邮箱登录：
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

#### 获取当前用户信息

```http
GET /api/auth/me
Authorization: Bearer {access_token}
```

### 会议管理

##### 创建会议

```http
POST /api/meetings
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "项目讨论会",
  "description": "讨论项目进度"
}
```

响应：
```json
{
  "success": true,
  "data": {
    "id": "meeting-uuid",
    "name": "项目讨论会",
    "status": "running",
    "task_id": "task-id",
    "stream_url": "ws://...",
    "created_at": "2024-01-01T00:00:00",
    ...
  }
}
```

#### 获取会议信息

```http
GET /api/meetings/{meeting_id}
Authorization: Bearer {access_token}
```

#### 列出所有会议

```http
GET /api/meetings?status=running
Authorization: Bearer {access_token}
```

#### 停止会议

```http
POST /api/meetings/{meeting_id}/stop
Authorization: Bearer {access_token}
```

#### 更新转写文本

```http
PUT /api/meetings/{meeting_id}/transcript
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "transcript": "转写文本内容..."
}
```

#### 生成会议摘要

```http
POST /api/meetings/{meeting_id}/summary
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "type": "brief"  // brief 或 detailed
}
```

#### 提取会议要点

```http
POST /api/meetings/{meeting_id}/key-points
Authorization: Bearer {access_token}
```

### 音频上传

#### 上传音频文件

```http
POST /api/audio/upload/{meeting_id}
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: [音频文件]
convert_to_wav: true  // 可选，是否转换为WAV格式
```

支持的音频格式：wav, mp3, m4a, aac, flac, ogg, wma

响应：
```json
{
  "success": true,
  "data": {
    "filename": "meeting-id_abc123.wav",
    "file_path": "/path/to/file.wav",
    "audio_info": {
      "duration": 120.5,
      "sample_rate": 16000,
      "channels": 1,
      "format": "wav",
      "file_size": 1920000
    },
    "meeting_id": "meeting-uuid"
  },
  "message": "音频文件上传成功"
}
```

#### 列出会议音频文件

```http
GET /api/audio/info/{meeting_id}
Authorization: Bearer {access_token}
```

## WebSocket API

### 连接

```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('已连接');
});
```

### 加入会议房间

```javascript
socket.emit('join_meeting', {
  meeting_id: 'meeting-uuid'
});

socket.on('joined', (data) => {
  console.log('已加入房间', data);
});
```

### 发送音频数据

```javascript
socket.emit('audio_data', {
  meeting_id: 'meeting-uuid',
  audio_data: audioBuffer  // 音频数据
});
```

### 接收转写结果

```javascript
socket.on('transcript_update', (data) => {
  console.log('转写结果:', data.text);
});
```

### 离开会议房间

```javascript
socket.emit('leave_meeting', {
  meeting_id: 'meeting-uuid'
});
```

## 注意事项

1. **通义听悟SDK集成**：当前代码中的通义听悟API调用是基于通用REST API实现的。实际使用时，需要根据通义听悟的官方文档调整：
   - API端点地址
   - 认证方式
   - 请求参数格式
   - WebSocket协议细节

2. **数据存储**：当前使用内存存储会议数据，生产环境建议使用数据库（如PostgreSQL、MySQL等）。

3. **音频处理**：WebSocket中的音频数据处理需要根据通义听悟的实际协议实现，当前为框架代码。

4. **错误处理**：已实现基础错误处理，可根据实际需求扩展。

## 测试

运行API测试脚本：

```bash
# 确保服务已启动
python app.py

# 在另一个终端运行测试
python tests/test_api.py
```

## 开发计划

- [x] 项目基础结构
- [x] Flask应用框架
- [x] 通义听悟SDK集成
- [x] 会议管理API
- [x] WebSocket实时通信
- [x] 会议摘要和要点提取
- [x] 错误处理和日志
- [x] 数据库集成（SQLite）
- [x] 用户认证和授权（JWT）
- [x] 音频文件上传和处理
- [x] 通义听悟WebSocket集成框架
- [ ] 完整的通义听悟WebSocket协议实现（需官方文档）
- [ ] 数据库迁移工具（Flask-Migrate）
- [ ] 单元测试和集成测试
- [ ] Docker容器化部署
- [ ] 生产环境配置优化

## 许可证

MIT License

