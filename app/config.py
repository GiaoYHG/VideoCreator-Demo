"""
配置管理模块
从 YAML 配置文件中读取配置
"""
from pathlib import Path
from typing import Literal

import yaml


class Settings:
    """应用配置类"""

    def __init__(self, config_file: str = "config.yaml"):
        """
        从 YAML 文件加载配置

        Args:
            config_file: 配置文件路径，默认为项目根目录下的 config.yaml
        """
        # 确定配置文件路径（项目根目录）
        project_root = Path(__file__).parent.parent
        config_path = project_root / config_file

        if not config_path.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {config_path}\n"
                f"请复制 config.yaml.example 为 config.yaml 并填入实际配置"
            )

        # 读取 YAML 配置
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # DashScope API 配置
        dashscope = config_data.get("dashscope", {})
        self.dashscope_api_key: str = dashscope.get("api_key", "")
        self.dashscope_region: Literal["beijing", "singapore"] = dashscope.get("region", "singapore")

        # Seedance API 配置（字节跳动方舟 Ark）
        seedance = config_data.get("seedance", {}) or {}
        self.seedance_api_key: str = seedance.get("api_key", "")
        self.seedance_base_url: str = seedance.get("base_url", "https://ark.cn-beijing.volces.com")

        # OpenAI API 配置（Sora）
        openai = config_data.get("openai", {}) or {}
        self.openai_api_key: str = openai.get("api_key", "")
        self.openai_base_url: str = openai.get("base_url", "https://api.openai.com")

        # Google Gemini API 配置（Veo）
        google = config_data.get("google", {}) or {}
        self.google_api_key: str = google.get("api_key", "")

        # AWS S3 配置
        s3 = config_data.get("s3", {})
        self.s3_access_key_id: str = s3.get("access_key_id", "")
        self.s3_secret_access_key: str = s3.get("secret_access_key", "")
        self.s3_bucket_name: str = s3.get("bucket_name", "")
        self.s3_region: str = s3.get("region", "us-east-1")
        self.s3_endpoint_url: str = s3.get("endpoint_url", "")  # 可选，用于自定义S3兼容服务

        # S3 路径配置
        s3_paths = s3.get("paths", {})
        self.s3_image_path: str = s3_paths.get("images", "video-creator/images/")
        self.s3_audio_path: str = s3_paths.get("audios", "video-creator/audios/")
        self.s3_reference_video_path: str = s3_paths.get("reference_videos", "video-creator/reference-videos/")
        self.s3_output_video_path: str = s3_paths.get("output_videos", "video-creator/output-videos/")
        self.s3_url_expiration: int = s3.get("url_expiration", 86400)

        # 应用配置
        app = config_data.get("app", {})
        self.app_port: int = app.get("port", 8000)
        self.app_host: str = app.get("host", "0.0.0.0")
        self.debug: bool = app.get("debug", False)
        self.log_level: str = app.get("log_level", "INFO")

        # 数据库配置
        database = config_data.get("database", {})
        database_path = database.get("path", "data/video_tasks.db")
        # 转换为绝对路径
        self.database_path: str = str((project_root / database_path).resolve())

        # 验证必需配置
        self._validate()

    def _validate(self):
        """验证必需的配置项"""
        required_fields = {
            "dashscope_api_key": self.dashscope_api_key,
            "s3_access_key_id": self.s3_access_key_id,
            "s3_secret_access_key": self.s3_secret_access_key,
            "s3_bucket_name": self.s3_bucket_name,
        }

        missing = [name for name, value in required_fields.items() if not value]
        if missing:
            raise ValueError(
                f"缺少必需的配置项: {', '.join(missing)}\n"
                f"请在 config.yaml 中填入这些配置"
            )

        # 验证 region
        if self.dashscope_region not in ["beijing", "singapore"]:
            raise ValueError(f"dashscope.region 必须是 'beijing' 或 'singapore'，当前值: {self.dashscope_region}")

    @property
    def dashscope_base_url(self) -> str:
        """根据region返回DashScope API的base URL"""
        if self.dashscope_region == "beijing":
            return "https://dashscope.aliyuncs.com"
        return "https://dashscope-intl.aliyuncs.com"


# 全局配置实例
settings = Settings()
