# 视频生成服务 API

基于阿里云 DashScope 通义万相（Wan2.6）、字节跳动 Seedance 1.5 pro、OpenAI Sora、Google Veo 3.1 的视频生成服务后端，提供多种视频生成/查询能力，并在成功后自动转存到 S3。

## 功能特性

- ✅ **Wan2.6 (DashScope)**: 图生视频 (I2V) / 文生视频 (T2V) / 参考生视频 (R2V)
- ✅ **Seedance 1.5 pro（Ark）**: 创建/查询任务，支持首帧/首尾帧图生
- ✅ **Sora（OpenAI Videos API）**: 创建/Remix/查询，支持 `input_reference` 图片参考
- ✅ **Veo 3.1（Gemini API）**: 创建/查询/延长（extend），支持首尾帧、最多 3 张参考图、4k 分辨率
- ✅ **任务查询**: Wan2.6 使用统一查询接口；Seedance/Sora/Veo 使用各自查询接口
- ✅ **自动文件上传**: 自动上传到 AWS S3 并生成公网 URL
- ✅ **视频永久存储**: 自动将生成的视频转存到自有 S3
- ✅ **任务记录**: SQLite数据库记录所有任务创建信息
- ✅ **费用统计**: UI 自动计算并显示 Wan2.6/Sora/Veo 费用（Seedance 不计算）
- ✅ **耗时追踪**: 自动记录并显示任务生成耗时（仅成功时显示）
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
│   │       ├── seedance_task.py    # Seedance 创建/查询端点
│   │       ├── sora_video.py       # Sora 创建/Remix/查询端点
│   │       ├── veo_task.py         # Veo 创建/查询/延长端点
│   │       └── ui.py               # 测试 UI 端点
│   ├── services/                    # 业务服务
│   │   ├── s3_service.py           # S3 上传服务
│   │   ├── dashscope_service.py    # DashScope API 服务
│   │   ├── video_service.py        # Wan2.6 业务逻辑服务
│   │   ├── seedance_service.py     # Seedance API 服务
│   │   ├── seedance_video_service.py # Seedance 业务逻辑服务
│   │   ├── openai_video_service.py # OpenAI Videos API 服务
│   │   ├── sora_video_service.py   # Sora 业务逻辑服务
│   │   ├── veo_service.py          # Veo SDK 封装服务
│   │   └── veo_video_service.py    # Veo 业务逻辑服务
│   ├── db/                          # 数据库模块
│   │   ├── database.py             # 数据库连接管理
│   │   ├── models.py               # 数据库模型
│   │   └── crud.py                 # 数据库操作
│   └── utils/                       # 工具类
│       ├── exceptions.py           # 自定义异常
│       ├── validators.py           # 文件验证器（Wan2.6）
│       ├── seedance_validators.py  # Seedance 文件验证器
│       ├── openai_validators.py    # OpenAI 文件验证器
│       └── veo_validators.py       # Veo 文件验证器
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

# 可选：Seedance（Ark）
seedance:
  api_key: your_seedance_api_key_here
  base_url: https://ark.cn-beijing.volces.com

# 可选：OpenAI（Sora）
openai:
  api_key: your_openai_api_key_here
  base_url: https://api.openai.com

# 可选：Google（Veo 3.1）
google:
  api_key: your_google_api_key_here

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
- 字节跳动 Seedance API Key（可选）
- OpenAI API Key（可选）
- Google API Key（可选）

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

### Seedance（Ark）配置（可选）

```yaml
seedance:
  api_key: your_seedance_api_key_here
  base_url: https://ark.cn-beijing.volces.com
```

### OpenAI（Sora）配置（可选）

```yaml
openai:
  api_key: your_openai_api_key_here
  base_url: https://api.openai.com
```

### Google（Veo 3.1）配置（可选）

```yaml
google:
  api_key: your_google_api_key_here
```

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

### Sora（OpenAI Videos API）（创建/Remix/查询）

```http
POST /api/v1/sora/video
Content-Type: multipart/form-data

prompt: string            # 必填
input_reference: <file>   # 可选（仅图片）
model: sora-2|sora-2-pro  # 可选（默认 sora-2）
seconds: 4|8|12           # 可选（默认 4）
size: 720x1280|1280x720  # 可选（sora-2 仅支持这两个；默认 720x1280）
```

说明：若传入 `input_reference`，后端会按所选 `size` 做「居中裁剪 + 缩放」后再请求 OpenAI。
说明：当 `model=sora-2-pro` 时，`size` 还支持 `1024x1792`、`1792x1024`。

创建响应示例（data 对齐 OpenAI 返回）：

```json
{
  "success": true,
  "message": "Sora 任务创建成功",
  "data": {
    "id": "video_123",
    "object": "video",
    "model": "sora-2",
    "status": "queued",
    "progress": 0,
    "created_at": 1712697600,
    "size": "1024x1792",
    "seconds": "8",
    "quality": "standard"
  }
}
```

```http
POST /api/v1/sora/video/{video_id}/remix
Content-Type: multipart/form-data

prompt: string            # 必填
```

```http
GET /api/v1/sora/video/{video_id}
```

查询响应说明：`data` 对齐 OpenAI `retrieve` 返回；当 `status` 为 `completed` 时，后端会下载 `/v1/videos/{id}/content` 并转存到 S3，额外补充 `s3_video_url` 字段。

说明：本项目不提供 OpenAI 的 `List videos` / `Delete video` 两个接口。

### Veo 3.1（Gemini API）（创建/查询/延长）

```http
POST /api/v1/veo/task
Content-Type: multipart/form-data

model: veo-3.1-fast-generate-preview|veo-3.1-generate-preview  # 可选（默认 fast）
prompt: string                 # 必填
negative_prompt: string        # 可选
first_frame: <file>            # 可选（首帧图）
last_frame: <file>             # 可选（尾帧图；有 last_frame 必须同时传 first_frame）
reference_images: <files>      # 可选（参考图，最多 3 张；可重复传 1~3 个字段）
aspect_ratio: 16:9|9:16        # 可选（默认 16:9；使用 reference_images 时仅支持 16:9）
resolution: 720p|1080p|4k      # 可选（默认 1080p；1080p 和 4k 仅支持 8 秒）
duration_seconds: 4|6|8        # 可选（默认 8；使用参考图、1080p、4k 时必须为 8）
person_generation: auto|allow_all|allow_adult  # 可选（默认 auto；按文档规则自动选择）
```

**约束规则**：
- 首帧/尾帧 与 参考图片 **互斥**，只能选择其中一种方式
- `1080p` 和 `4k` 分辨率仅支持 8 秒时长
- 使用 `reference_images` 时必须为 `16:9` + `8秒`
- 插值（首尾帧）支持任意时长（除非使用高分辨率）

创建响应示例：

```json
{
  "success": true,
  "message": "Veo 任务创建成功",
  "data": {
    "id": "models/veo-3.1-fast-generate-preview/operations/xxx",
    "estimated_price_usd": 1.20,
    "model": "veo-3.1-fast-generate-preview",
    "resolution": "720p"
  }
}
```

```http
POST /api/v1/veo/task/{operation_name}/extend
Content-Type: multipart/form-data

model: veo-3.1-fast-generate-preview|veo-3.1-generate-preview  # 可选（默认 fast）
prompt: string                 # 必填（新的提示词）
negative_prompt: string        # 可选
```

**延长说明**：
- 每次延长约 7 秒，最多延长 20 次
- 仅支持 Veo 生成的视频（来自 `operation.response.generated_videos[0].video`）
- 固定输出为 720p 分辨率
- 视频存储期限为 2 天（被引用时重置）

```http
GET /api/v1/veo/task/{operation_name}
```

查询响应示例：

```json
{
  "success": true,
  "message": "任务状态: succeeded",
  "data": {
    "name": "models/veo-3.1-fast-generate-preview/operations/xxx",
    "status": "succeeded",
    "done": true,
    "error": null,
    "estimated_price_usd": 1.20,
    "model": "veo-3.1-fast-generate-preview",
    "resolution": "720p",
    "elapsed_seconds": 135,
    "elapsed_time_formatted": "2分15秒",
    "s3_video_url": "https://..."
  }
}
```

### Wan2.6 查询任务状态

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

UI 会根据以下规则自动计算视频生成费用：

### Wan2.6（DashScope）

- **1080P**: $0.15/秒
- **720P**: $0.1/秒
- **480P及以下**: 免费

**计算公式**: 费用 = 价格/秒 × 视频时长（秒）

**示例**: 720P 5秒视频 = $0.1 × 5 = **$0.50**

### Sora（OpenAI）

- **Sora 2**: $0.10/秒
- **Sora 2 Pro**: $0.30/秒

**计算公式**: 费用 = 价格/秒 × 视频时长（秒）

**示例**: Sora 2 生成 8秒视频 = $0.10 × 8 = **$0.80**

### Veo 3.1（Google Gemini）

| 模型 | 720p | 1080p | 4k |
|------|------|-------|-----|
| **veo-3.1-fast-generate-preview** | $0.15/秒 | $0.15/秒 | $0.35/秒 |
| **veo-3.1-generate-preview** | $0.40/秒 | $0.40/秒 | $0.60/秒 |

**计算公式**: 费用 = 价格/秒 × 视频时长（秒）

**示例**:
- veo-3.1-fast + 720p + 8秒 = $0.15 × 8 = **$1.20**
- veo-3.1-fast + 4k + 8秒 = $0.35 × 8 = **$2.80**
- veo-3.1-generate + 720p + 8秒 = $0.40 × 8 = **$3.20**
- veo-3.1-generate + 4k + 8秒 = $0.60 × 8 = **$4.80**
- 延长视频（7秒，720p，fast）= $0.15 × 7 = **$1.05**

### Seedance（字节跳动）

**暂不计算费用**（价格信息待补充）

---

**注意**：
- 💰 价格会在任务创建时立即显示（预估）
- ⏱️ 耗时仅在任务成功完成时显示（实际总耗时）

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
google-genai>=1.57.0
anyio>=4.0.0
```

### 添加新功能

1. 在 `app/models/request.py` 定义请求模型
2. 在 `app/services/` 实现业务逻辑
3. 在 `app/api/endpoints/` 添加API端点
4. 在 `app/main.py` 注册路由

### Veo 3.1 特性

#### 价格自动计算
- 创建任务时根据 `模型 + 分辨率 + 时长` 自动计算价格
- 价格立即在响应中返回，UI 实时显示
- 支持延长任务的价格计算（固定 7秒 × 720p）

#### 耗时追踪
- 任务创建时记录 Unix 时间戳
- 查询时自动计算耗时（`current_time - created_at`）
- 自动格式化为易读格式（秒/分钟/小时）
- 仅在任务成功完成时显示总耗时

#### 互斥逻辑
- 前端自动处理首帧/尾帧与参考图片的互斥
- 选择首帧/尾帧时自动禁用参考图片上传
- 选择参考图片时自动禁用首帧/尾帧上传
- 按钮视觉反馈（灰色 + 不可点击）

#### 约束自动管理
- 1080p/4k 自动限制为 8 秒
- 参考图片自动限制为 16:9 + 8秒
- 分辨率/宽高比选项动态启用/禁用

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
