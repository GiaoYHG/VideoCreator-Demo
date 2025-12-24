"""
文件验证器
验证上传文件的格式、大小、分辨率等
"""
from typing import Tuple
from fastapi import UploadFile
from PIL import Image
import io

from app.utils.exceptions import FileValidationException


class FileValidator:
    """文件验证器类"""

    # 支持的文件格式
    SUPPORTED_IMAGE_FORMATS = {"jpeg", "jpg", "png", "bmp", "webp"}
    SUPPORTED_AUDIO_FORMATS = {"wav", "mp3"}
    SUPPORTED_VIDEO_FORMATS = {"mp4", "mov"}

    # 文件大小限制（字节）
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_AUDIO_SIZE = 15 * 1024 * 1024  # 15MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

    # 图片分辨率限制
    MIN_IMAGE_DIMENSION = 360
    MAX_IMAGE_DIMENSION = 2000

    @staticmethod
    async def validate_image(file: UploadFile) -> Tuple[bytes, str]:
        """
        验证图片文件

        Args:
            file: 上传的图片文件

        Returns:
            Tuple[bytes, str]: (文件内容, 文件扩展名)

        Raises:
            FileValidationException: 验证失败
        """
        # 读取文件内容
        content = await file.read()
        file_size = len(content)

        # 验证文件大小
        if file_size > FileValidator.MAX_IMAGE_SIZE:
            raise FileValidationException(
                f"图片文件大小超过限制（最大 {FileValidator.MAX_IMAGE_SIZE / 1024 / 1024}MB）"
            )

        # 验证文件格式
        try:
            image = Image.open(io.BytesIO(content))
            file_format = image.format.lower() if image.format else ""

            if file_format not in FileValidator.SUPPORTED_IMAGE_FORMATS:
                raise FileValidationException(
                    f"不支持的图片格式: {file_format}，"
                    f"支持的格式: {', '.join(FileValidator.SUPPORTED_IMAGE_FORMATS)}"
                )

            # 验证分辨率
            width, height = image.size
            if (width < FileValidator.MIN_IMAGE_DIMENSION or
                width > FileValidator.MAX_IMAGE_DIMENSION or
                height < FileValidator.MIN_IMAGE_DIMENSION or
                height > FileValidator.MAX_IMAGE_DIMENSION):
                raise FileValidationException(
                    f"图片分辨率不符合要求（宽度和高度需在 {FileValidator.MIN_IMAGE_DIMENSION}-"
                    f"{FileValidator.MAX_IMAGE_DIMENSION} 像素之间），当前: {width}x{height}"
                )

        except Exception as e:
            if isinstance(e, FileValidationException):
                raise
            raise FileValidationException(f"图片文件解析失败: {str(e)}")

        return content, file_format

    @staticmethod
    async def validate_audio(file: UploadFile) -> Tuple[bytes, str]:
        """
        验证音频文件

        Args:
            file: 上传的音频文件

        Returns:
            Tuple[bytes, str]: (文件内容, 文件扩展名)

        Raises:
            FileValidationException: 验证失败
        """
        # 读取文件内容
        content = await file.read()
        file_size = len(content)

        # 验证文件大小
        if file_size > FileValidator.MAX_AUDIO_SIZE:
            raise FileValidationException(
                f"音频文件大小超过限制（最大 {FileValidator.MAX_AUDIO_SIZE / 1024 / 1024}MB）"
            )

        # 从文件名获取扩展名
        if not file.filename:
            raise FileValidationException("无效的文件名")

        file_ext = file.filename.split(".")[-1].lower()

        if file_ext not in FileValidator.SUPPORTED_AUDIO_FORMATS:
            raise FileValidationException(
                f"不支持的音频格式: {file_ext}，"
                f"支持的格式: {', '.join(FileValidator.SUPPORTED_AUDIO_FORMATS)}"
            )

        return content, file_ext

    @staticmethod
    async def validate_video(file: UploadFile) -> Tuple[bytes, str]:
        """
        验证视频文件

        Args:
            file: 上传的视频文件

        Returns:
            Tuple[bytes, str]: (文件内容, 文件扩展名)

        Raises:
            FileValidationException: 验证失败
        """
        # 读取文件内容
        content = await file.read()
        file_size = len(content)

        # 验证文件大小
        if file_size > FileValidator.MAX_VIDEO_SIZE:
            raise FileValidationException(
                f"视频文件大小超过限制（最大 {FileValidator.MAX_VIDEO_SIZE / 1024 / 1024}MB）"
            )

        # 从文件名获取扩展名
        if not file.filename:
            raise FileValidationException("无效的文件名")

        file_ext = file.filename.split(".")[-1].lower()

        if file_ext not in FileValidator.SUPPORTED_VIDEO_FORMATS:
            raise FileValidationException(
                f"不支持的视频格式: {file_ext}，"
                f"支持的格式: {', '.join(FileValidator.SUPPORTED_VIDEO_FORMATS)}"
            )

        return content, file_ext
