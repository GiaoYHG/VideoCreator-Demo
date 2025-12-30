"""
Seedance 文件验证器
用于 Seedance 任务的图片输入校验（与 Wan/DashScope 约束不同）
"""

from typing import Tuple

import io
from fastapi import UploadFile
from PIL import Image

from app.utils.exceptions import FileValidationException


class SeedanceFileValidator:
    """Seedance 文件验证器"""

    SUPPORTED_IMAGE_FORMATS = {"jpeg", "jpg", "png", "webp", "bmp", "tiff", "gif"}

    MAX_IMAGE_SIZE = 30 * 1024 * 1024  # 30MB
    MIN_IMAGE_DIMENSION = 300
    MAX_IMAGE_DIMENSION = 6000
    MIN_ASPECT_RATIO = 0.4
    MAX_ASPECT_RATIO = 2.5

    @staticmethod
    async def validate_image(file: UploadFile) -> Tuple[bytes, str]:
        content = await file.read()
        file_size = len(content)

        if file_size > SeedanceFileValidator.MAX_IMAGE_SIZE:
            raise FileValidationException(
                f"图片文件大小超过限制（最大 {SeedanceFileValidator.MAX_IMAGE_SIZE / 1024 / 1024}MB）"
            )

        try:
            image = Image.open(io.BytesIO(content))
            file_format = (image.format or "").lower()
            if file_format == "jpeg":
                file_ext = "jpeg"
            else:
                file_ext = file_format

            if file_ext not in SeedanceFileValidator.SUPPORTED_IMAGE_FORMATS:
                raise FileValidationException(
                    f"不支持的图片格式: {file_ext}，"
                    f"支持的格式: {', '.join(sorted(SeedanceFileValidator.SUPPORTED_IMAGE_FORMATS))}"
                )

            width, height = image.size
            if (
                width < SeedanceFileValidator.MIN_IMAGE_DIMENSION
                or width > SeedanceFileValidator.MAX_IMAGE_DIMENSION
                or height < SeedanceFileValidator.MIN_IMAGE_DIMENSION
                or height > SeedanceFileValidator.MAX_IMAGE_DIMENSION
            ):
                raise FileValidationException(
                    f"图片分辨率不符合要求（宽高需在 {SeedanceFileValidator.MIN_IMAGE_DIMENSION}-"
                    f"{SeedanceFileValidator.MAX_IMAGE_DIMENSION} 像素之间），当前: {width}x{height}"
                )

            ratio = width / height if height else 0
            if ratio <= 0 or ratio < SeedanceFileValidator.MIN_ASPECT_RATIO or ratio > SeedanceFileValidator.MAX_ASPECT_RATIO:
                raise FileValidationException(
                    "图片宽高比不符合要求（宽/高需在 "
                    f"{SeedanceFileValidator.MIN_ASPECT_RATIO}-"
                    f"{SeedanceFileValidator.MAX_ASPECT_RATIO} 之间），当前: {width}/{height}"
                )

        except Exception as e:
            if isinstance(e, FileValidationException):
                raise
            raise FileValidationException(f"图片文件解析失败: {str(e)}")

        return content, file_ext

