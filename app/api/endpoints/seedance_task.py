"""
Seedance 任务 API 端点
提供：创建任务 + 查询任务
"""

from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Path, status

from app.models.response import BaseResponse
from app.services.seedance_video_service import seedance_video_service
from app.services.seedance_service import DEFAULT_SEEDANCE_MODEL_ID
from app.utils.exceptions import (
    FileValidationException,
    OSSUploadException,
    SeedanceAPIException,
    ConfigurationException,
)
from app.utils.seedance_validators import SeedanceFileValidator
from app.services.s3_service import oss_service


router = APIRouter(prefix="/api/v1/seedance", tags=["Seedance"])


_ALLOWED_RATIOS = {"16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"}
_ALLOWED_RESOLUTIONS = {"480p", "720p"}


def _build_prompt_text(
    prompt: str,
    *,
    resolution: Optional[str],
    ratio: Optional[str],
    duration: Optional[int],
    seed: Optional[int],
    camera_fixed: bool,
    watermark: bool,
) -> str:
    base = (prompt or "").strip()
    if not base:
        raise FileValidationException("prompt 不能为空")

    params = []
    if resolution:
        normalized = str(resolution).strip().lower()
        if normalized not in _ALLOWED_RESOLUTIONS:
            raise FileValidationException(f"resolution 不支持: {resolution}（仅支持 480p/720p）")
        params.append(f"--rs {normalized}")

    if ratio:
        if ratio not in _ALLOWED_RATIOS:
            raise FileValidationException(f"ratio 不支持: {ratio}")
        params.append(f"--rt {ratio}")

    if duration is not None:
        if duration != -1 and not (4 <= duration <= 12):
            raise FileValidationException("duration 仅支持 -1 或 4~12 的整数")
        params.append(f"--dur {duration}")

    if seed is not None:
        if seed < -1 or seed > 4294967295:
            raise FileValidationException("seed 取值范围为 [-1, 2^32-1]")
        params.append(f"--seed {seed}")

    if camera_fixed:
        params.append("--cf true")

    if watermark:
        params.append("--wm true")

    if not params:
        return base
    return f"{base} {' '.join(params)}"


@router.post("/task", response_model=BaseResponse, summary="创建 Seedance 视频任务")
async def create_seedance_task(
    model: str = Form(DEFAULT_SEEDANCE_MODEL_ID, description="模型 ID（默认 doubao-seedance-1-5-pro-251215）"),
    prompt: str = Form(..., description="文本提示词（必填）"),
    first_frame: Optional[UploadFile] = File(None, description="首帧图片（可选）"),
    last_frame: Optional[UploadFile] = File(None, description="尾帧图片（可选，需与首帧一起使用）"),
    generate_audio: bool = Form(True, description="是否生成同步音频（默认 true）"),
    resolution: Optional[str] = Form(None, description="分辨率（可选，480p/720p；Seedance 1.5 pro 默认 720p）"),
    ratio: Optional[str] = Form(None, description="宽高比（可选，例如 16:9 / 9:16 / adaptive）"),
    duration: Optional[int] = Form(None, description="时长（可选，4~12 或 -1）"),
    seed: Optional[int] = Form(None, description="随机种子（可选，[-1, 2^32-1]）"),
    camera_fixed: bool = Form(False, description="是否固定摄像头（可选，默认 false）"),
    watermark: bool = Form(False, description="是否添加水印（可选，默认 false）"),
):
    try:
        model = (model or "").strip()
        if not model:
            raise FileValidationException("model 不能为空")
        if len(model) > 128:
            raise FileValidationException("model 长度超过限制（最大 128 字符）")

        if last_frame and not first_frame:
            raise FileValidationException("传入 last_frame 时必须同时传入 first_frame")

        first_frame_url = None
        last_frame_url = None

        if first_frame:
            img_content, img_ext = await SeedanceFileValidator.validate_image(first_frame)
            _, first_frame_url = await oss_service.upload_file(img_content, "image", img_ext)

        if last_frame:
            img_content, img_ext = await SeedanceFileValidator.validate_image(last_frame)
            _, last_frame_url = await oss_service.upload_file(img_content, "image", img_ext)

        prompt_text = _build_prompt_text(
            prompt,
            resolution=resolution,
            ratio=ratio,
            duration=duration,
            seed=seed,
            camera_fixed=camera_fixed,
            watermark=watermark,
        )

        request_data = {
            "provider": "seedance",
            "model": model,
            "prompt": prompt,
            "prompt_text": prompt_text,
            "generate_audio": bool(generate_audio),
            "resolution": resolution,
            "ratio": ratio,
            "duration": duration,
            "seed": seed,
            "camera_fixed": bool(camera_fixed),
            "watermark": bool(watermark),
            "first_frame_url": first_frame_url,
            "last_frame_url": last_frame_url,
        }

        result = await seedance_video_service.create_video_task(
            model=model,
            prompt_text=prompt_text,
            first_frame_url=first_frame_url,
            last_frame_url=last_frame_url,
            generate_audio=generate_audio,
            request_data=request_data,
        )

        return BaseResponse(
            success=True,
            message="Seedance 任务创建成功",
            data=result,
        )

    except FileValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except OSSUploadException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except ConfigurationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except SeedanceAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"},
        )


@router.get("/task/{task_id}", response_model=BaseResponse, summary="查询 Seedance 任务状态")
async def query_seedance_task(
    task_id: str = Path(..., description="任务ID（创建任务返回的 id）")
):
    try:
        result = await seedance_video_service.query_task_status(task_id)
        status_value = result.get("status") if isinstance(result, dict) else None
        return BaseResponse(
            success=True,
            message=f"任务状态: {status_value or 'UNKNOWN'}",
            data=result,
        )

    except ConfigurationException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except SeedanceAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"},
        )
