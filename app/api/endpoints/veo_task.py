"""
Veo 3.1（Google Gemini API）任务端点
提供：创建 / 查询 / 延长（extend）
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Path, UploadFile, status

from app.models.response import BaseResponse
from app.services.veo_video_service import veo_video_service
from app.utils.exceptions import (
    ConfigurationException,
    FileValidationException,
    GoogleVeoAPIException,
    S3UploadException,
)
from app.utils.veo_validators import VeoFileValidator


router = APIRouter(prefix="/api/v1/veo", tags=["Veo(Gemini)"])


_ALLOWED_MODELS = {"veo-3.1-fast-generate-preview", "veo-3.1-generate-preview"}
_ALLOWED_ASPECT_RATIOS = {"16:9", "9:16"}
_ALLOWED_RESOLUTIONS = {"720p", "1080p", "4k"}
_ALLOWED_DURATIONS = {4, 6, 8}
_ALLOWED_PERSON_GENERATION = {"allow_all", "allow_adult"}

# Veo 3.1 价格表（美元/秒）
_VEO_PRICING_PER_SECOND = {
    "veo-3.1-generate-preview": {
        "720p": 0.40,
        "1080p": 0.40,
        "4k": 0.60,
    },
    "veo-3.1-fast-generate-preview": {
        "720p": 0.15,
        "1080p": 0.15,
        "4k": 0.35,
    },
}


def _calculate_price(model: str, resolution: str, duration_seconds: int) -> float:
    """
    计算 Veo 视频生成价格

    Args:
        model: 模型名称
        resolution: 分辨率 (720p/1080p/4k)
        duration_seconds: 视频时长（秒）

    Returns:
        价格（美元）
    """
    pricing = _VEO_PRICING_PER_SECOND.get(model, {})
    price_per_second = pricing.get(resolution, 0.0)
    return price_per_second * duration_seconds


def _validate_model(model: str) -> str:
    model = (model or "").strip()
    if model not in _ALLOWED_MODELS:
        raise FileValidationException(f"model 不支持: {model}")
    return model


def _validate_prompt(prompt: str) -> str:
    prompt = (prompt or "").strip()
    if not prompt:
        raise FileValidationException("prompt 不能为空")
    return prompt


def _validate_negative_prompt(negative_prompt: Optional[str]) -> Optional[str]:
    if negative_prompt is None:
        return None
    v = str(negative_prompt).strip()
    return v or None


def _normalize_person_generation(value: str, *, has_any_image: bool, is_extend: bool) -> str:
    raw = (value or "").strip() or "auto"
    if raw == "auto":
        return "allow_all" if is_extend or not has_any_image else "allow_adult"

    if raw not in _ALLOWED_PERSON_GENERATION:
        raise FileValidationException(f"person_generation 不支持: {raw}（仅支持 auto/allow_all/allow_adult）")

    # 文档约束（Veo 3.1）：文生/扩展仅 allow_all；图生/插值/参考图仅 allow_adult
    if is_extend and raw != "allow_all":
        raise FileValidationException("extend 模式下 person_generation 仅支持 allow_all")
    if not is_extend:
        if has_any_image and raw != "allow_adult":
            raise FileValidationException("包含图片输入时 person_generation 仅支持 allow_adult")
        if (not has_any_image) and raw != "allow_all":
            raise FileValidationException("纯文生视频时 person_generation 仅支持 allow_all")

    return raw


@router.post("/task", response_model=BaseResponse, summary="创建 Veo 视频任务")
async def create_veo_task(
    model: str = Form("veo-3.1-fast-generate-preview", description="模型（默认 veo-3.1-fast-generate-preview）"),
    prompt: str = Form(..., description="文本提示词（必填）"),
    negative_prompt: Optional[str] = Form(None, description="反向提示词（可选）"),
    first_frame: Optional[UploadFile] = File(None, description="首帧图片（可选）"),
    last_frame: Optional[UploadFile] = File(None, description="尾帧图片（可选，需与首帧一起使用）"),
    reference_images: Optional[List[UploadFile]] = File(None, description="参考图片（可选，最多3张，仅限16:9）"),
    aspect_ratio: str = Form("16:9", description="宽高比（16:9 / 9:16）"),
    resolution: str = Form("720p", description="分辨率（720p / 1080p / 4k；1080p 和 4k 仅支持 8 秒）"),
    duration_seconds: int = Form(8, description="时长（秒）：4/6/8（参考图片、1080p、4k 必须为 8）"),
    person_generation: str = Form("auto", description="人物生成策略（auto/allow_all/allow_adult）"),
):
    try:
        model = _validate_model(model)
        prompt = _validate_prompt(prompt)
        negative_prompt = _validate_negative_prompt(negative_prompt)

        aspect_ratio = (aspect_ratio or "").strip()
        if aspect_ratio not in _ALLOWED_ASPECT_RATIOS:
            raise FileValidationException(f"aspect_ratio 不支持: {aspect_ratio}（仅支持 16:9/9:16）")

        resolution = (resolution or "").strip().lower()
        if resolution not in _ALLOWED_RESOLUTIONS:
            raise FileValidationException(f"resolution 不支持: {resolution}（仅支持 720p/1080p/4k）")

        if duration_seconds not in _ALLOWED_DURATIONS:
            raise FileValidationException("duration_seconds 仅支持 4/6/8")

        if last_frame and not first_frame:
            raise FileValidationException("传入 last_frame 时必须同时传入 first_frame")

        ref_files = reference_images or []
        if len(ref_files) > 3:
            raise FileValidationException("reference_images 最多 3 张")

        uses_interpolation = bool(last_frame)
        uses_reference_images = len(ref_files) > 0

        # Veo 3.1 最新文档约束：
        # 1. 1080p 和 4k 分辨率仅支持 8 秒时长
        # 2. 参考图片必须 duration_seconds=8 且仅支持 16:9
        # 3. 插值（首尾帧）不强制要求 8 秒（除非使用高分辨率）

        # 高分辨率约束
        if resolution in ("1080p", "4k") and duration_seconds != 8:
            raise FileValidationException(f"{resolution} 分辨率仅支持 8 秒时长（duration_seconds=8）")

        # 参考图片约束
        if uses_reference_images:
            if duration_seconds != 8:
                raise FileValidationException("使用 reference_images 时，duration_seconds 必须为 8")
            if aspect_ratio != "16:9":
                raise FileValidationException("使用 reference_images 时，aspect_ratio 仅支持 16:9")

        has_any_image = bool(first_frame or last_frame or uses_reference_images)
        person_generation = _normalize_person_generation(
            person_generation,
            has_any_image=has_any_image,
            is_extend=False,
        )

        first_image = None
        last_image = None
        ref_images = None

        if first_frame:
            first_image = await VeoFileValidator.validate_image_to_pil(first_frame)
        if last_frame:
            last_image = await VeoFileValidator.validate_image_to_pil(last_frame)
        if ref_files:
            ref_images = [await VeoFileValidator.validate_image_to_pil(f) for f in ref_files]

        # 计算价格（每秒价格 × 时长）
        estimated_price_usd = _calculate_price(model, resolution, duration_seconds)

        request_data = {
            "provider": "veo",
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "duration_seconds": duration_seconds,
            "person_generation": person_generation,
            "has_first_frame": bool(first_frame),
            "has_last_frame": bool(last_frame),
            "reference_images_count": len(ref_files),
            "estimated_price_usd": estimated_price_usd,
        }

        result = await veo_video_service.create_video_task(
            model=model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration_seconds=duration_seconds,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            person_generation=person_generation,
            first_frame=first_image,
            last_frame=last_image,
            reference_images=ref_images,
            request_data=request_data,
        )

        return BaseResponse(success=True, message="Veo 任务创建成功", data=result)

    except FileValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except ConfigurationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except GoogleVeoAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except S3UploadException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"},
        )


@router.post("/task/{operation_name:path}/extend", response_model=BaseResponse, summary="延长 Veo 视频")
async def extend_veo_task(
    operation_name: str = Path(..., description="源 operation.name（必须是 Veo 生成的视频）"),
    model: str = Form("veo-3.1-fast-generate-preview", description="模型（默认 veo-3.1-fast-generate-preview）"),
    prompt: str = Form(..., description="新的提示词（必填）"),
    negative_prompt: Optional[str] = Form(None, description="反向提示词（可选）"),
    person_generation: str = Form("auto", description="人物生成策略（extend 模式仅 allow_all）"),
):
    try:
        operation_name = (operation_name or "").strip()
        if not operation_name:
            raise FileValidationException("operation_name 不能为空")

        model = _validate_model(model)
        prompt = _validate_prompt(prompt)
        negative_prompt = _validate_negative_prompt(negative_prompt)

        person_generation = _normalize_person_generation(
            person_generation,
            has_any_image=False,
            is_extend=True,
        )
        # 当前 SDK 示例的 extend 只需 video + prompt + (resolution=720p)
        # person_generation 作为 request_data 记录；是否透传到 SDK 视后续需要再加

        # 计算扩展视频的价格（固定 720p，延长 7 秒）
        estimated_price_usd = _calculate_price(model, "720p", 7)

        request_data = {
            "provider": "veo",
            "action": "extend",
            "source_operation_name": operation_name,
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "person_generation": person_generation,
            "estimated_price_usd": estimated_price_usd,
            "resolution": "720p",  # 扩展固定为 720p
        }

        result = await veo_video_service.extend_video_task(
            source_operation_name=operation_name,
            model=model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            person_generation=person_generation,
            request_data=request_data,
        )

        return BaseResponse(success=True, message="Veo 延长任务创建成功", data=result)

    except FileValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except ConfigurationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except GoogleVeoAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"},
        )


@router.get("/task/{operation_name:path}", response_model=BaseResponse, summary="查询 Veo 任务状态")
async def query_veo_task(
    operation_name: str = Path(..., description="operation.name（创建任务返回的 id）"),
):
    try:
        operation_name = (operation_name or "").strip()
        if not operation_name:
            raise FileValidationException("operation_name 不能为空")

        result = await veo_video_service.query_task_status(operation_name)
        status_value = result.get("status") if isinstance(result, dict) else None
        return BaseResponse(success=True, message=f"任务状态: {status_value or 'UNKNOWN'}", data=result)

    except FileValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except ConfigurationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except GoogleVeoAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"},
        )
