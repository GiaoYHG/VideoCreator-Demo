# 视频生成服务 API

基于阿里云 DashScope 通义万相的视频生成服务后端，提供图生视频、文生视频、参考生视频三种生成方式。

## 功能特性

- ✅ **图生视频 (I2V)**: 根据首帧图像 + 文本描述生成视频
- ✅ **文生视频 (T2V)**: 纯文本描述生成视频
- ✅ **参考生视频 (R2V)**: 参考输入视频中的角色形象生成新视频
- ✅ **统一查询接口**: 单一接口查询所有任务状态
- ✅ **自动文件上传**: 自动上传到 AWS S3 并生成公网 URL
- ✅ **视频永久存储**: 自动将生成的视频转存到自有 S3
- ✅ **任务记录**: SQLite数据库记录所有任务创建信息
- ✅ **费用统计**: UI自动计算并显示视频生成费用
- ✅ **Swagger 文档**: 自动生成 API 文档
- ✅ **模块化设计**: 清晰的代码结构，易于维护

## 项目结构

```
VideoCreator/
├── app/                             # 应用代码
│   ├── main.py                      # FastAPI 应用入口
│   ├── config.py                    # 配置管理
│   ├── models/                      # 数据模型
│   │   ├── request.py              # 请求模型
│   │   └── response.py             # 响应模型
│   ├── api/                         # API 端点
│   │   └── endpoints/
│   │       ├── video_generation.py # 视频生成端点
│   │       ├── task_query.py       # 任务查询端点
│   │       └── ui.py               # 测试 UI 端点
│   ├── services/                    # 业务服务
│   │   ├── s3_service.py           # S3 上传服务
│   │   ├── dashscope_service.py    # DashScope API 服务
│   │   └── video_service.py        # 业务逻辑服务
│   ├── db/                          # 数据库模块
│   │   ├── database.py             # 数据库连接管理
│   │   ├── models.py               # 数据库模型
│   │   └── crud.py                 # 数据库操作
│   └── utils/                       # 工具类
│       ├── exceptions.py           # 自定义异常
│       └── validators.py           # 文件验证器
├── data/                            # 数据目录
│   └── video_tasks.db              # SQLite数据库
├── config.yaml                      # 配置文件（含密钥，不提交到Git）
├── requirements.txt                 # Python 依赖
├── Dockerfile                       # Docker 镜像定义
├── docker-compose.yml               # Docker Compose 配置
├── .gitignore                       # Git 忽略规则
├── .dockerignore                    # Docker 忽略规则
└── README.md                        # 本文档
```

## 快速开始

### 方式一：Docker 部署（推荐）

#### 1. 准备配置文件

编辑 `config.yaml`，填入你的密钥：

```yaml
dashscope:
  api_key: your_dashscope_api_key_here
  region: singapore  # 或 beijing

s3:
  access_key_id: your_aws_access_key_id
  secret_access_key: your_aws_secret_access_key
  bucket_name: your_bucket_name
  region: us-east-1

database:
  path: data/video_tasks.db

app:
  port: 9992
  host: 0.0.0.0
```

#### 2. 构建并启动服务

```bash
docker compose up -d --build
```

#### 3. 查看服务状态

```bash
# 查看日志
docker compose logs -f video-creator

# 查看容器状态
docker ps
```

#### 4. 访问服务

- Swagger 文档: http://localhost:9992/docs
- 测试 UI: http://localhost:9992/ui
- 健康检查: http://localhost:9992/health

### 方式二：本地开发

#### 1. 环境要求

- Python 3.11+
- AWS S3 账号
- 阿里云 DashScope API Key

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置应用

编辑 `config.yaml` 文件，参考上方配置说明。

#### 4. 运行服务

```bash
# 开发模式（自动重载）
python -m app.main

# 或使用 uvicorn 直接运行
uvicorn app.main:app --reload --host 0.0.0.0 --port 9992
```

#### 5. 访问文档

服务启动后，访问以下地址：

- Swagger UI: http://localhost:9992/docs
- ReDoc: http://localhost:9992/redoc
- 测试 UI: http://localhost:9992/ui

## 配置说明

### DashScope API 配置

```yaml
dashscope:
  api_key: your_dashscope_api_key_here  # DashScope API Key
  region: singapore  # beijing 或 singapore
```

**获取 API Key**:
- [阿里云 DashScope 控制台](https://www.alibabacloud.com/help/zh/model-studio/get-api-key)
- 注意：北京和新加坡地域的 API Key 不同，不可混用

### AWS S3 配置

```yaml
s3:
  access_key_id: your_aws_access_key_id
  secret_access_key: your_aws_secret_access_key
  bucket_name: your_bucket_name
  region: us-east-1
  endpoint_url: ""  # 可选，用于兼容S3 API的服务

  paths:
    images: video-creator/images/
    audios: video-creator/audios/
    reference_videos: video-creator/reference-videos/
    output_videos: video-creator/output-videos/

  url_expiration: 86400  # 签名URL过期时间（秒）
```

**获取 AWS 凭证**:
- [AWS IAM 控制台](https://console.aws.amazon.com/iam/)
- 需要 S3 读写权限

### 数据库配置

```yaml
database:
  path: data/video_tasks.db  # SQLite数据库路径
```

数据库会在应用启动时自动创建，记录所有视频生成任务。

## API 接口

### 图生视频 (I2V)

```http
POST /api/v1/video/i2v
Content-Type: multipart/form-data

img: <file>              # 图片文件（必填）
prompt: string           # 视频描述（可选）
resolution: 720P|1080P   # 分辨率（默认1080P）
duration: 5-15           # 时长（秒）
...
```

### 文生视频 (T2V)

```http
POST /api/v1/video/t2v
Content-Type: multipart/form-data

prompt: string           # 视频描述（必填）
size: 1920*1080         # 分辨率
duration: 5|10|15       # 时长（秒）
...
```

### 参考生视频 (R2V)

```http
POST /api/v1/video/r2v
Content-Type: multipart/form-data

prompt: string           # 视频描述（必填，用character1等引用）
reference_videos: <files> # 参考视频（1-3个）
...
```

### Seedance 1.5 pro（创建/查询）

```http
POST /api/v1/seedance/task
Content-Type: multipart/form-data

model: string              # 可选（默认 seedance-1-5-pro-251215）
prompt: string             # 必填
first_frame: <file>        # 可选（首帧图）
last_frame: <file>         # 可选（尾帧图；有 last_frame 必须同时传 first_frame）
generate_audio: true|false # 可选（默认 true）
resolution: 480p|720p      # 可选（默认 720p）
ratio: 16:9|9:16|...|adaptive # 可选
duration: 4~12|-1          # 可选（-1 表示模型自行选择 4~12）
seed: -1~2^32-1            # 可选（-1 表示随机）
camera_fixed: true|false   # 可选（默认 false）
watermark: true|false      # 可选（默认 false）
```

创建响应示例：

```json
{
  "success": true,
  "message": "Seedance 任务创建成功",
  "data": {
    "id": "cgt-2025******-****"
  }
}
```

```http
GET /api/v1/seedance/task/{task_id}
```

查询响应示例（data 对齐 Ark 返回，并额外补充 s3_video_url）：

```json
{
  "success": true,
  "message": "任务状态: succeeded",
  "data": {
    "id": "cgt-2025******-****",
    "model": "seedance-1-5-pro-251215",
    "status": "succeeded",
    "content": {
      "video_url": "https://ark-content-generation-cn-beijing.tos-cn-beijing.volces.com/xxx"
    },
    "seed": 10,
    "resolution": "720p",
    "ratio": "16:9",
    "duration": 5,
    "framespersecond": 24,
    "service_tier": "default",
    "execution_expires_after": 172800,
    "generate_audio": true,
    "usage": {
      "completion_tokens": 108900,
      "total_tokens": 108900
    },
    "created_at": 1743414619,
    "updated_at": 1743414673,
    "s3_video_url": "https://..."
  }
}
```

### 查询任务状态

```http
GET /api/v1/task/{task_id}
```

响应示例：

```json
{
  "success": true,
  "message": "任务状态: SUCCEEDED",
  "data": {
    "task_id": "xxx",
    "task_status": "SUCCEEDED",
    "video_url": "https://...",
    "s3_video_url": "https://...",
    "usage": {
      "SR": 720,
      "output_video_duration": 5
    },
    "submit_time": "2025-12-29 16:01:37",
    "end_time": "2025-12-29 16:03:40"
  }
}
```

## 费用计算

UI会根据以下规则自动计算视频生成费用：

- **1080P**: $0.15/秒
- **720P**: $0.1/秒

费用 = 价格 × 视频时长（秒）

示例：720P 5秒视频 = $0.1 × 5 = $0.50

## 数据库

应用使用SQLite记录所有视频生成任务：

- **位置**: `data/video_tasks.db`
- **记录内容**: 任务ID、类型、请求参数、文件URLs、创建时间
- **自动创建**: 应用启动时自动初始化

查看数据库：

```bash
sqlite3 data/video_tasks.db
.tables
SELECT * FROM video_tasks;
```

## 开发指南

### 项目依赖

```txt
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
httpx[socks]>=0.26.0
boto3>=1.34.0
sqlalchemy>=2.0.23
pyyaml>=6.0.1
python-multipart>=0.0.6
Pillow>=10.2.0
```

### 添加新功能

1. 在 `app/models/request.py` 定义请求模型
2. 在 `app/services/` 实现业务逻辑
3. 在 `app/api/endpoints/` 添加API端点
4. 在 `app/main.py` 注册路由

### 运行测试

```bash
# 启动服务
python -m app.main

# 访问测试UI
open http://localhost:9992/ui
```

## 故障排查

### 1. 数据库初始化失败

```bash
# 检查data目录权限
chmod 755 data

# 手动删除数据库重新创建
rm data/video_tasks.db
python -m app.main
```

### 2. S3上传失败

- 检查AWS凭证是否正确
- 检查S3 Bucket权限
- 检查网络连接

### 3. DashScope API调用失败

- 检查API Key是否正确
- 检查region配置是否匹配
- 查看错误日志

## License

MIT License

## 联系方式

如有问题，请提Issue或联系开发团队。
