"""
OpenAI 文件验证器
用于 OpenAI Sora 视频生成的 input_reference 图片校验
"""

from typing import Tuple

import io
from fastapi import UploadFile
from PIL import Image

from app.utils.exceptions import FileValidationException


class OpenAIFileValidator:
    """OpenAI input_reference 图片验证器（尽量宽松，避免误拒绝）"""

    SUPPORTED_IMAGE_FORMATS = {"jpeg", "jpg", "png", "webp", "bmp", "tiff", "gif"}
    MAX_IMAGE_SIZE = 30 * 1024 * 1024  # 30MB

    @staticmethod
    async def validate_image(file: UploadFile) -> Tuple[bytes, str, str]:
        content = await file.read()
        if len(content) > OpenAIFileValidator.MAX_IMAGE_SIZE:
            raise FileValidationException(
                f"图片文件大小超过限制（最大 {OpenAIFileValidator.MAX_IMAGE_SIZE / 1024 / 1024}MB）"
            )

        try:
            image = Image.open(io.BytesIO(content))
            file_format = (image.format or "").lower()
            if file_format == "jpeg":
                ext = "jpeg"
            else:
                ext = file_format

            if ext == "jpg":
                ext = "jpeg"

            if ext not in OpenAIFileValidator.SUPPORTED_IMAGE_FORMATS:
                raise FileValidationException(
                    f"不支持的图片格式: {ext}，支持: {', '.join(sorted(OpenAIFileValidator.SUPPORTED_IMAGE_FORMATS))}"
                )

        except Exception as e:
            if isinstance(e, FileValidationException):
                raise
            raise FileValidationException(f"图片文件解析失败: {str(e)}")

        content_type_map = {
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "bmp": "image/bmp",
            "tiff": "image/tiff",
            "gif": "image/gif",
        }
        content_type = content_type_map.get(ext, "application/octet-stream")
        return content, ext, content_type

