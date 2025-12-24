# Docker 部署到服务器（简要）

本项目已提供 `Dockerfile` 和 `docker-compose.yml`，推荐使用 Docker Compose 部署。

## 1) 本地推送到 GitHub

1. 在 GitHub 创建一个仓库（建议私有）
2. 在项目根目录执行：

```bash
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin git@github.com:<you>/<repo>.git
git push -u origin main
```

> 注意：`backend/config.yaml` 含密钥，已在 `.gitignore` 中忽略；服务器上再创建该文件。

## 2) 服务器拉取代码

```bash
git clone git@github.com:<you>/<repo>.git
cd <repo>
```

## 3) 准备配置文件（服务器上）

```bash
cp backend/config.yaml.example backend/config.yaml
vi backend/config.yaml
```

建议将：
- `app.debug` 设为 `false`
- 填入正确的 `dashscope.api_key` / `dashscope.region` / OSS 配置

## 4) 构建并启动

```bash
docker compose up -d --build
docker compose logs -f video-creator
```

验证：
- `curl http://127.0.0.1:9992/health`
- 浏览器：`http://<server-ip>:9992/ui`

## 5) 更新版本

```bash
git pull
docker compose up -d --build
```

## 端口说明

默认对外端口为 `9992`（见 `docker-compose.yml` 的 `ports`）。如需换端口，改为 `"<外部端口>:9992"` 即可。

