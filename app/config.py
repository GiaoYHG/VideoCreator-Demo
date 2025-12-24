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

        # OSS 配置
        oss = config_data.get("oss", {})
        self.oss_access_key_id: str = oss.get("access_key_id", "")
        self.oss_access_key_secret: str = oss.get("access_key_secret", "")
        self.oss_bucket_name: str = oss.get("bucket_name", "")
        self.oss_endpoint: str = oss.get("endpoint", "oss-cn-shanghai.aliyuncs.com")

        # OSS 路径配置
        oss_paths = oss.get("paths", {})
        self.oss_image_path: str = oss_paths.get("images", "video-creator/images/")
        self.oss_audio_path: str = oss_paths.get("audios", "video-creator/audios/")
        self.oss_reference_video_path: str = oss_paths.get("reference_videos", "video-creator/reference-videos/")
        self.oss_output_video_path: str = oss_paths.get("output_videos", "video-creator/output-videos/")
        self.oss_url_expiration: int = oss.get("url_expiration", 86400)

        # 应用配置
        app = config_data.get("app", {})
        self.app_port: int = app.get("port", 8000)
        self.app_host: str = app.get("host", "0.0.0.0")
        self.debug: bool = app.get("debug", False)
        self.log_level: str = app.get("log_level", "INFO")

        # 验证必需配置
        self._validate()

    def _validate(self):
        """验证必需的配置项"""
        required_fields = {
            "dashscope_api_key": self.dashscope_api_key,
            "oss_access_key_id": self.oss_access_key_id,
            "oss_access_key_secret": self.oss_access_key_secret,
            "oss_bucket_name": self.oss_bucket_name,
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
