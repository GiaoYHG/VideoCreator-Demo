# 前端对接（简要）

默认本地地址：`http://localhost:9992`（以实际部署端口为准），Swagger：`/docs`
快速操作页：`/ui`

## 通用响应结构

- 成功：`{ "success": true, "message": "...", "data": {...} }`
- 失败（非2xx）：`{ "detail": { "success": false, "message": "...", "details": ... } }`

## 基本流程

1. 调用生成接口创建任务，拿到 `task_id`
2. 按 15 秒间隔轮询 `GET /api/v1/task/{task_id}` 获取状态
3. `SUCCEEDED` 后使用 `oss_video_url`（优先）或 `video_url` 播放/下载

> 说明：`video_url` 为 DashScope 临时链接（约 24 小时有效）；`oss_video_url` 为转存到自有 OSS 后返回的签名 URL（有效期由后端 `oss.url_expiration` 配置决定）。

## 接口一览

### 1) 文生视频（T2V）

- `POST /api/v1/video/t2v`
- `Content-Type: multipart/form-data`

表单字段（常用）：
- `prompt`（必填，string）
- `audio`（可选，file：wav/mp3）
- `size`（可选，string，默认 `1920*1080`，如 `1280*720`）
- `duration`（可选，int，默认 5）
- `model`（可选，默认 `wan2.6-t2v`）
- `negative_prompt`（可选，string）
- `prompt_extend`（可选，bool，默认 true）
- `shot_type`（可选，`single`/`multi`，默认 `single`）
- `audio_enable`（可选，bool，默认 true）
- `watermark`（可选，bool，默认 false）
- `seed`（可选，int）

成功返回 `data`：
- `task_id` / `task_status` / `request_id`

### 2) 图生视频（I2V）

- `POST /api/v1/video/i2v`
- `Content-Type: multipart/form-data`

表单字段（常用）：
- `image`（必填，file：jpg/png/bmp/webp）
- `audio`（可选，file：wav/mp3）
- `prompt`（可选，string）
- `resolution`（可选，`720P`/`1080P`，默认 `1080P`）
- 其余字段同 T2V（`model` 默认 `wan2.6-i2v`）

### 3) 参考生视频（R2V）

- `POST /api/v1/video/r2v`
- `Content-Type: multipart/form-data`

表单字段（常用）：
- `reference_videos`（必填，file，最多 3 个；FormData 里同名多次 append）
- `prompt`（必填，string；用 `character1`/`character2` 引用参考角色）
- `duration`（必选，R2V 只支持 5 或 10）
- `size`（可选，默认 `1920*1080`）
- `audio_enable`（可选，bool，默认 true；提取参考视频音色）
- 其余字段同 T2V（`model` 默认 `wan2.6-r2v`）

### 4) 查询任务状态

- `GET /api/v1/task/{task_id}`

成功返回 `data`（关键字段）：
- `task_status`: `PENDING` / `RUNNING` / `SUCCEEDED` / `FAILED` / `CANCELED` / `UNKNOWN`
- `video_url`: DashScope 临时 URL（`SUCCEEDED` 时可能返回）
- `oss_video_url`: 转存到自有 OSS 后的签名 URL（`SUCCEEDED` 时可能返回）
- `usage.size`: 分辨率（如 `1280*720`）
- `error_message` / `error_code`: 失败原因（`FAILED` 时）

## 前端示例（fetch）

```js
const BASE_URL = 'http://localhost:9992';

async function createT2V({ prompt, size = '1280*720' }) {
  const form = new FormData();
  form.append('prompt', prompt);
  form.append('size', size);
  form.append('duration', '5');
  form.append('prompt_extend', 'true');

  const res = await fetch(`${BASE_URL}/api/v1/video/t2v`, { method: 'POST', body: form });
  const json = await res.json();
  if (!res.ok) throw new Error(json?.detail?.message ?? json?.message ?? '请求失败');
  return json.data.task_id;
}

async function pollTask(taskId) {
  while (true) {
    const res = await fetch(`${BASE_URL}/api/v1/task/${taskId}`);
    const json = await res.json();
    if (!res.ok) throw new Error(json?.detail?.message ?? json?.message ?? '查询失败');

    const data = json.data;
    if (data.task_status === 'SUCCEEDED') return data.oss_video_url ?? data.video_url;
    if (data.task_status === 'FAILED') throw new Error(data.error_message ?? 'FAILED');
    await new Promise(r => setTimeout(r, 15000));
  }
}
```
