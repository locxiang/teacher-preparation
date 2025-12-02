# 配置指南

## .env 文件配置说明

`.env` 文件已创建，包含以下配置项：

### 必需配置

#### SECRET_KEY
- **说明**：Flask应用的密钥，用于加密会话和JWT令牌
- **默认值**：`dev-secret-key-change-in-production-please-modify-in-production`
- **生产环境**：必须修改为强随机字符串
- **生成方法**：
  ```python
  import secrets
  print(secrets.token_hex(32))
  ```

### 可选配置（通义听悟服务）

如果需要使用通义听悟的完整功能（实时转写、摘要生成等），需要配置以下项：

#### ALIBABA_CLOUD_ACCESS_KEY_ID
- **说明**：阿里云AccessKey ID
- **获取方式**：
  1. 登录 [阿里云控制台](https://www.aliyun.com/)
  2. 进入"访问控制" -> "用户" -> "创建AccessKey"
  3. 复制 AccessKey ID

#### ALIBABA_CLOUD_ACCESS_KEY_SECRET
- **说明**：阿里云AccessKey Secret
- **获取方式**：与AccessKey ID一起创建，请妥善保管

#### TYTINGWU_APP_KEY
- **说明**：通义听悟项目的AppKey（只需要AppKey，不需要AppSecret）
- **获取方式**：
  1. 登录 [阿里云控制台](https://www.aliyun.com/)
  2. 开通"通义听悟"服务
  3. 创建项目，获取AppKey
- **注意**：根据官方文档，实时记录接口只需要AppKey，不需要AppSecret

### Flask应用配置

#### FLASK_ENV
- **说明**：Flask运行环境
- **可选值**：`development`（开发）或 `production`（生产）
- **默认值**：`development`

#### FLASK_DEBUG
- **说明**：是否启用调试模式
- **可选值**：`True` 或 `False`
- **默认值**：`True`
- **注意**：生产环境必须设置为 `False`

#### FLASK_HOST
- **说明**：服务监听地址
- **默认值**：`0.0.0.0`（监听所有网络接口）
- **本地开发**：可以使用 `127.0.0.1` 或 `localhost`

#### FLASK_PORT
- **说明**：服务监听端口
- **默认值**：`5001`（避免与macOS AirPlay Receiver冲突）
- **注意**：如果端口被占用，可以修改为其他端口（如8080、3000等）

### 数据库配置

#### DATABASE_URL
- **说明**：数据库连接URL
- **默认**：使用SQLite，数据库文件为 `meetings.db`
- **PostgreSQL示例**：
  ```
  DATABASE_URL=postgresql://username:password@localhost:5432/dbname
  ```
- **MySQL示例**：
  ```
  DATABASE_URL=mysql://username:password@localhost:3306/dbname
  ```

## 配置示例

### 最小配置（仅开发测试）
```env
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
```

### 完整配置（包含通义听悟）
```env
SECRET_KEY=your-strong-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
TYTINGWU_APP_KEY=your_app_key
```

**注意**：
- AccessKey信息已配置到 `.env` 文件中，请妥善保管，不要泄露
- 通义听悟只需要AppKey，不需要AppSecret

### 生产环境配置
```env
SECRET_KEY=your-production-secret-key-minimum-32-characters
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
TYTINGWU_APP_KEY=your_app_key

DATABASE_URL=postgresql://user:password@localhost:5432/meetings_db
```

## 配置验证

启动服务时，系统会自动验证配置：
- ✅ 如果配置完整，服务正常启动
- ⚠️ 如果通义听悟配置缺失，会显示警告，但服务仍可启动（功能受限）
- ❌ 如果必需配置缺失，服务无法启动

## 安全提示

1. **不要将 `.env` 文件提交到Git仓库**
   - `.env` 文件已在 `.gitignore` 中，不会被提交
   - 敏感信息（如AccessKey）不要泄露

2. **生产环境必须修改SECRET_KEY**
   - 使用强随机字符串
   - 长度至少32个字符

3. **定期轮换AccessKey**
   - 建议每3-6个月更换一次
   - 更换后及时更新 `.env` 文件

4. **使用环境变量而非硬编码**
   - 所有敏感配置都应通过 `.env` 文件管理
   - 不要将密钥硬编码在代码中

