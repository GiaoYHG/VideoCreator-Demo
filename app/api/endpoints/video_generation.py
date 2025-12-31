"""
视频生成API端点
处理图生视频、文生视频、参考生视频的HTTP请求
"""
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.models.request import I2VRequest, T2VRequest, R2VRequest
from app.models.response import BaseResponse
from app.services.s3_service import s3_service
from app.services.video_service import video_service
from app.utils.exceptions import (
    FileValidationException,
    S3UploadException,
    DashScopeAPIException
)
from app.utils.validators import FileValidator

router = APIRouter(prefix="/api/v1/video", tags=["视频生成"])


@router.post("/i2v", response_model=BaseResponse, summary="图生视频")
async def create_i2v_video(
    image: UploadFile = File(..., description="首帧图片文件（JPEG/PNG/BMP/WEBP，分辨率360-2000像素，最大10MB）"),
    audio: Optional[UploadFile] = File(None, description="自定义音频文件（可选，wav/mp3，3-30秒，最大15MB）"),
    prompt: Optional[str] = Form(None, description="视频描述文本（可选），支持中英文，最长1500字符"),
    negative_prompt: Optional[str] = Form(None, description="反向提示词，用于限制视频画面中不希望出现的内容"),
    model: str = Form("wan2.6-i2v", description="模型名称"),
    resolution: str = Form("1080P", description="分辨率档位。wan2.6支持720P/1080P，wan2.5支持480P/720P/1080P"),
    duration: int = Form(5, description="视频时长（秒）。wan2.6支持5/10/15秒，wan2.5支持5/10秒，其他模型固定5秒或支持3/4/5秒"),
    prompt_extend: bool = Form(True, description="是否智能改写prompt，开启后提升短prompt效果但增加耗时"),
    shot_type: Optional[str] = Form("single", description="镜头类型: single/multi。仅wan2.6支持且prompt_extend=true时生效。优先级：shot_type > prompt"),
    audio_enable: bool = Form(True, description="是否自动配音（audio_url优先级更高）。仅wan2.6/wan2.5支持"),
    watermark: bool = Form(False, description="是否添加水印"),
    seed: Optional[int] = Form(None, ge=0, le=2147483647, description="随机种子[0, 2147483647]")
):
    """
    创建图生视频任务

    根据首帧图像和文本描述生成视频。

    **图片要求**：
    - 格式：JPEG、JPG、PNG（不支持透明通道）、BMP、WEBP
    - 分辨率：宽度和高度均在 [360, 2000] 像素范围内
    - 文件大小：不超过10MB

    **音频要求**：
    - 格式：wav、mp3
    - 时长：3～30秒
    - 文件大小：不超过15MB
    - 超限处理：音频长度超过duration时自动截取，不足时超出部分为无声视频

    **模型支持情况**：
    - wan2.6-i2v: 支持720P/1080P，duration支持5/10/15秒，支持多镜头叙事
    """
    try:
        # 1. 验证并上传图片
        img_content, img_ext = await FileValidator.validate_image(image)
        img_path, img_url = await s3_service.upload_file(img_content, "image", img_ext)

        # 2. 如果有音频，验证并上传
        audio_url = None
        if audio:
            audio_content, audio_ext = await FileValidator.validate_audio(audio)
            audio_path, audio_url = await s3_service.upload_file(audio_content, "audio", audio_ext)

        # 3. 构建请求对象
        request = I2VRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model=model,
            resolution=resolution,
            duration=duration,
            prompt_extend=prompt_extend,
            shot_type=shot_type,
            audio=audio_enable,
            watermark=watermark,
            seed=seed
        )

        # 4. 调用业务逻辑服务
        result = await video_service.create_i2v_video(request, img_url, audio_url)

        return BaseResponse(
            success=True,
            message="图生视频任务创建成功",
            data=result.model_dump()
        )

    except FileValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except S3UploadException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except DashScopeAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"}
        )


@router.post("/t2v", response_model=BaseResponse, summary="文生视频")
async def create_t2v_video(
    audio: Optional[UploadFile] = File(None, description="自定义音频文件（可选）"),
    prompt: str = Form(..., description="视频描述文本，支持中英文，最长1500字符"),
    negative_prompt: Optional[str] = Form(None, description="反向提示词，用于限制视频画面中不希望出现的内容"),
    model: str = Form("wan2.6-t2v", description="模型名称"),
    size: str = Form("1920*1080", description="分辨率，格式: 宽*高（必须是具体数值，如1280*720，不能是1:1或480P）"),
    duration: int = Form(5, description="视频时长（秒）。wan2.6支持5/10/15秒，wan2.5支持5/10秒，其他模型固定5秒"),
    prompt_extend: bool = Form(True, description="是否智能改写prompt，开启后提升短prompt效果但增加耗时"),
    shot_type: Optional[str] = Form("single", description="镜头类型: single/multi。仅wan2.6支持且prompt_extend=true时生效。优先级：shot_type > prompt"),
    audio_enable: bool = Form(True, description="是否自动配音（audio_url优先级更高）。仅wan2.6/wan2.5支持"),
    watermark: bool = Form(False, description="是否添加水印"),
    seed: Optional[int] = Form(None, ge=0, le=2147483647, description="随机种子[0, 2147483647]")
):
    """
    创建文生视频任务
    **支持的分辨率档位**：
    - 720P: 1280*720（16:9）、720*1280（9:16）、960*960（1:1）、1088*832（4:3）、832*1088（3:4）
    - 1080P: 1920*1080（16:9）、1080*1920（9:16）、1440*1440（1:1）、1632*1248（4:3）、1248*1632（3:4）
    """
    try:
        # 1. 如果有音频，验证并上传
        audio_url = None
        if audio:
            audio_content, audio_ext = await FileValidator.validate_audio(audio)
            audio_path, audio_url = await s3_service.upload_file(audio_content, "audio", audio_ext)

        # 2. 构建请求对象
        request = T2VRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model=model,
            size=size,
            duration=duration,
            prompt_extend=prompt_extend,
            shot_type=shot_type,
            audio=audio_enable,
            watermark=watermark,
            seed=seed
        )

        # 3. 调用业务逻辑服务
        result = await video_service.create_t2v_video(request, audio_url)

        return BaseResponse(
            success=True,
            message="文生视频任务创建成功",
            data=result.model_dump()
        )

    except FileValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except S3UploadException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except DashScopeAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"}
        )


@router.post("/r2v", response_model=BaseResponse, summary="参考生视频")
async def create_r2v_video(
    reference_videos: List[UploadFile] = File(..., description="参考视频文件（最多3个）"),
    prompt: str = Form(..., description="视频描述文本。通过character1、character2引用参考角色"),
    negative_prompt: Optional[str] = Form(None, description="反向提示词"),
    model: str = Form("wan2.6-r2v", description="模型名称"),
    size: str = Form("1920*1080", description="分辨率，格式: 宽*高。支持720P/1080P档位的多种宽高比"),
    duration: int = Form(5, description="视频时长（秒），仅支持5或10秒"),
    shot_type: Optional[str] = Form("single", description="镜头类型: single/multi。优先级：shot_type > prompt"),
    audio_enable: bool = Form(True, description="是否自动为视频添加音频（提取参考视频音色）"),
    watermark: bool = Form(False, description="是否添加水印"),
    seed: Optional[int] = Form(None, ge=0, le=2147483647, description="随机种子[0, 2147483647]")
):
    """
    创建参考生视频任务

    根据参考视频中的角色形象和音色生成新视频，保持角色一致性。

    **角色引用说明**：
    - 通过 "character1、character2" 引用参考角色
    - 第1个视频对应character1，第2个对应character2，以此类推
    - 每个参考视频仅包含一个角色

    **示例prompt**: "character1对character2说: 你好！character2回答: 很高兴见到你！"
    """
    try:
        # 1. 验证参考视频数量
        if len(reference_videos) > 3:
            raise FileValidationException("参考视频最多只能上传3个")

        # 2. 验证duration参数（R2V只支持5或10秒）
        if duration not in [5, 10]:
            raise FileValidationException(f"R2V模型的duration参数只支持5或10秒，当前值: {duration}")

        # 3. 验证并上传所有参考视频
        reference_video_urls = []
        for video in reference_videos:
            video_content, video_ext = await FileValidator.validate_video(video)
            video_path, video_url = await s3_service.upload_file(video_content, "video", video_ext)
            reference_video_urls.append(video_url)

        # 4. 构建请求对象
        request = R2VRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model=model,
            size=size,
            duration=duration,
            shot_type=shot_type,
            audio=audio_enable,
            watermark=watermark,
            seed=seed
        )

        # 5. 调用业务逻辑服务
        result = await video_service.create_r2v_video(request, reference_video_urls)

        return BaseResponse(
            success=True,
            message="参考生视频任务创建成功",
            data=result.model_dump()
        )

    except FileValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except S3UploadException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except DashScopeAPIException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"success": False, "message": e.message, "details": e.details}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": f"服务器内部错误: {str(e)}"}
        )
