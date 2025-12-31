"""
自定义异常类
定义业务逻辑中可能出现的各种异常
"""
from typing import Any, Optional


class VideoCreatorException(Exception):
    """基础异常类"""

    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class S3UploadException(VideoCreatorException):
    """S3 上传异常"""
    pass


class DashScopeAPIException(VideoCreatorException):
    """DashScope API调用异常"""
    pass


class SeedanceAPIException(VideoCreatorException):
    """Seedance API调用异常"""
    pass


class FileValidationException(VideoCreatorException):
    """文件验证异常"""
    pass


class TaskNotFoundException(VideoCreatorException):
    """任务未找到异常"""
    pass


class ConfigurationException(VideoCreatorException):
    """配置错误异常"""
    pass
