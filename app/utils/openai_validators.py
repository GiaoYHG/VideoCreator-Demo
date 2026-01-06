"""
OpenAI 文件验证器
用于 OpenAI Sora 视频生成的 input_reference 图片校验
"""

from typing import Tuple

import io
from fastapi import UploadFile
from PIL import Image, ImageOps

from app.utils.exceptions import FileValidationException


class OpenAIFileValidator:
    """OpenAI input_reference 图片验证器（尽量宽松，避免误拒绝）"""

    SUPPORTED_IMAGE_FORMATS = {"jpeg", "jpg", "png", "webp", "bmp", "tiff", "gif"}
    MAX_IMAGE_SIZE = 30 * 1024 * 1024  # 30MB

    @staticmethod
    def _parse_size(size: str) -> tuple[int, int]:
        try:
            raw = (size or "").strip().lower()
            w_str, h_str = raw.split("x", 1)
            w = int(w_str)
            h = int(h_str)
            if w <= 0 or h <= 0:
                raise ValueError
            return w, h
        except Exception:
            raise FileValidationException(f"size 格式错误: {size}（期望如 720x1280）")

    @staticmethod
    def crop_and_resize_to_size(image_bytes: bytes, *, size: str) -> Tuple[bytes, str, str]:
        """
        将参考图片做「居中裁剪 + 缩放」以匹配目标输出 size（宽x高）。
        输出统一为 PNG（避免透明通道/格式差异问题）。
        """
        target_w, target_h = OpenAIFileValidator._parse_size(size)

        try:
            img = Image.open(io.BytesIO(image_bytes))
            img = ImageOps.exif_transpose(img)

            # 居中裁剪以匹配目标宽高比
            src_w, src_h = img.size
            if src_w <= 0 or src_h <= 0:
                raise FileValidationException("图片尺寸无效")

            target_ratio = target_w / target_h
            src_ratio = src_w / src_h

            if src_ratio > target_ratio:
                new_w = int(round(src_h * target_ratio))
                left = max(0, (src_w - new_w) // 2)
                box = (left, 0, min(src_w, left + new_w), src_h)
            else:
                new_h = int(round(src_w / target_ratio))
                top = max(0, (src_h - new_h) // 2)
                box = (0, top, src_w, min(src_h, top + new_h))

            img = img.crop(box)

            # 缩放到目标 size
            resample = getattr(Image, "Resampling", Image).LANCZOS
            img = img.resize((target_w, target_h), resample=resample)

            # 输出 PNG
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA")

            out = io.BytesIO()
            img.save(out, format="PNG", optimize=True)
            content = out.getvalue()

            if len(content) > OpenAIFileValidator.MAX_IMAGE_SIZE:
                raise FileValidationException(
                    f"处理后的图片大小超过限制（最大 {OpenAIFileValidator.MAX_IMAGE_SIZE / 1024 / 1024}MB）"
                )

            return content, "png", "image/png"

        except FileValidationException:
            raise
        except Exception as e:
            raise FileValidationException(f"图片预处理失败: {str(e)}")

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
