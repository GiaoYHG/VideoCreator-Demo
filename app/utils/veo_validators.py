"""
Veo 文件验证器
用于 Veo 3.1 的图片输入校验（首帧/尾帧/参考图）
"""

from __future__ import annotations

import base64
import io
from typing import Any

from fastapi import UploadFile
from PIL import Image, ImageOps

from app.utils.exceptions import ConfigurationException, FileValidationException


class VeoFileValidator:
    """Veo 图片验证器（尽量宽松）"""

    SUPPORTED_IMAGE_FORMATS = {"jpeg", "jpg", "png", "webp", "bmp", "tiff", "gif"}
    MAX_IMAGE_SIZE = 30 * 1024 * 1024  # 30MB

    @staticmethod
    async def validate_image_to_pil(file: UploadFile) -> Any:
        """
        验证并转换图片为 Google Gemini SDK 可接受的格式
        返回 types.Image 对象（包含 base64 编码和 mimeType）
        """
        content = await file.read()
        if len(content) > VeoFileValidator.MAX_IMAGE_SIZE:
            raise FileValidationException(
                f"图片文件大小超过限制（最大 {VeoFileValidator.MAX_IMAGE_SIZE / 1024 / 1024}MB）"
            )

        try:
            # 验证图片是否可以正常解析
            img = Image.open(io.BytesIO(content))
            img = ImageOps.exif_transpose(img)
            file_format = (img.format or "").lower()
            if file_format == "jpg":
                file_format = "jpeg"
            if file_format and file_format not in VeoFileValidator.SUPPORTED_IMAGE_FORMATS:
                raise FileValidationException(
                    f"不支持的图片格式: {file_format}，支持: {', '.join(sorted(VeoFileValidator.SUPPORTED_IMAGE_FORMATS))}"
                )
            img.load()

            # 将 PIL Image 转换为字节流（使用原始格式或 PNG）
            output_format = file_format if file_format in {"jpeg", "png", "webp"} else "png"
            img_bytes = io.BytesIO()

            # 如果是 RGBA 模式且要保存为 JPEG，需要先转换为 RGB
            if output_format == "jpeg" and img.mode in ("RGBA", "LA", "P"):
                # 创建白色背景
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                rgb_img.save(img_bytes, format="JPEG", quality=95)
            else:
                img.save(img_bytes, format=output_format.upper())

            img_bytes.seek(0)
            image_data = img_bytes.read()

            # 使用 Google Gemini SDK 的 types.Image 来构造图片对象
            try:
                from google.genai import types  # type: ignore

                # 构造符合 API 要求的图片对象
                mime_type = f"image/{output_format}"
                return types.Image(
                    image_bytes=image_data,
                    mime_type=mime_type,
                )
            except Exception as e:
                raise ConfigurationException(
                    "缺少依赖 google-genai（用于 Veo 3.1）",
                    details={"pip": "pip install google-genai", "error": str(e)},
                )

        except Exception as e:
            if isinstance(e, (FileValidationException, ConfigurationException)):
                raise
            raise FileValidationException(f"图片文件解析失败: {str(e)}")

