"""
Sora（OpenAI Videos API）端点
提供：创建 / Remix / 查询
"""

from typing import Optional

import os

from fastapi import APIRouter, File, Form, HTTPException, Path, UploadFile, status

from app.models.response import BaseResponse
from app.services.sora_video_service import sora_video_service
from app.utils.exceptions import (
    ConfigurationException,
    FileValidationException,
    OpenAIAPIException,
    S3UploadException,
)
from app.utils.openai_validators import OpenAIFileValidator


router = APIRouter(prefix="/api/v1/sora", tags=["Sora(OpenAI)"])


_ALLOWED_MODELS = {"sora-2", "sora-2-pro"}
_ALLOWED_SECONDS = {4, 8, 12}
_ALLOWED_SIZES_BY_MODEL = {
    "sora-2": {"720x1280", "1280x720"},
    "sora-2-pro": {"720x1280", "1280x720", "1024x1792", "1792x1024"},
}


@router.post("/video", response_model=BaseResponse, summary="创建 Sora 视频任务")
async def create_sora_video(
    prompt: str = Form(..., description="文本提示词（必填）"),
    input_reference: Optional[UploadFile] = File(None, description="参考图片（可选）"),
    model: str = Form("sora-2", description="模型（sora-2 / sora-2-pro）"),
    seconds: int = Form(4, description="时长（秒）：4/8/12"),
    size: str = Form("720x1280", description="分辨率：720x1280/1280x720/1024x1792/1792x1024"),
):
    try:
        model = (model or "").strip()
        if model not in _ALLOWED_MODELS:
            raise FileValidationException(f"model 不支持: {model}")
        if seconds not in _ALLOWED_SECONDS:
            raise FileValidationException(f"seconds 不支持: {seconds}（仅支持 4/8/12）")
        size = (size or "").strip()
        allowed_sizes = _ALLOWED_SIZES_BY_MODEL.get(model)
        if not allowed_sizes or size not in allowed_sizes:
            raise FileValidationException(f"size 不支持: {size}（model={model}）")

        prompt = (prompt or "").strip()
        if not prompt:
            raise FileValidationException("prompt 不能为空")

        input_ref_payload = None
        if input_reference:
            content, ext, content_type = await OpenAIFileValidator.validate_image(input_reference)
            content, ext, content_type = OpenAIFileValidator.crop_and_resize_to_size(content, size=size)
            original_name = (input_reference.filename or "input_reference").strip() or "input_reference"
            base = os.path.splitext(original_name)[0] or "input_reference"
            filename = f"{base}.{ext}"
            input_ref_payload = (filename, content, content_type)

        request_data = {
            "provider": "openai",
            "prompt": prompt,
            "model": model,
            "seconds": str(seconds),
            "size": size,
            "has_input_reference": bool(input_reference),
        }

        result = await sora_video_service.create_video_task(
            prompt=prompt,
            model=model,
            seconds=str(seconds),
            size=size,
            input_reference=input_ref_payload,
            request_data=request_data,
        )

        return BaseResponse(success=True, message="Sora 任务创建成功", data=result)

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
    except OpenAIAPIException as e:
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


@router.post("/video/{video_id}/remix", response_model=BaseResponse, summary="Remix Sora 视频任务")
async def remix_sora_video(
    video_id: str = Path(..., description="已完成的视频 ID"),
    prompt: str = Form(..., description="新的提示词（必填）"),
):
    try:
        video_id = (video_id or "").strip()
        if not video_id:
            raise FileValidationException("video_id 不能为空")

        prompt = (prompt or "").strip()
        if not prompt:
            raise FileValidationException("prompt 不能为空")

        request_data = {"provider": "openai", "action": "remix", "video_id": video_id, "prompt": prompt}
        result = await sora_video_service.remix_video_task(video_id=video_id, prompt=prompt, request_data=request_data)
        return BaseResponse(success=True, message="Sora Remix 任务创建成功", data=result)

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
    except OpenAIAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"},
        )


@router.get("/video/{video_id}", response_model=BaseResponse, summary="查询 Sora 任务状态")
async def query_sora_video(
    video_id: str = Path(..., description="视频任务 ID"),
):
    try:
        video_id = (video_id or "").strip()
        if not video_id:
            raise FileValidationException("video_id 不能为空")

        result = await sora_video_service.query_video_task(video_id=video_id)
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
    except OpenAIAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"},
        )
