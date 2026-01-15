"""
Veo 业务逻辑服务
负责：参数组合 -> 调用 Veo API -> 记录任务 -> 查询并转存 S3
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from app.db.crud import create_video_task, get_video_task_by_id
from app.services.s3_service import s3_service
from app.services.veo_service import veo_service


class VeoVideoService:
    async def create_video_task(
        self,
        *,
        model: str,
        prompt: str,
        negative_prompt: Optional[str],
        duration_seconds: int,
        aspect_ratio: str,
        resolution: str,
        person_generation: str,
        first_frame: Optional[Any],
        last_frame: Optional[Any],
        reference_images: Optional[List[Any]],
        request_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        # 记录开始时间
        start_time = time.time()

        op_name = await veo_service.generate_videos(
            model=model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration_seconds=duration_seconds,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            person_generation=person_generation,
            first_frame=first_frame,
            last_frame=last_frame,
            reference_images=reference_images,
        )

        # 添加创建时间戳到 request_data
        request_data["created_at"] = start_time

        try:
            create_video_task(
                task_id=op_name,
                task_type="VEO",
                request_id="",
                request_data=request_data,
            )
        except Exception as e:
            print(f"Warning: Failed to record veo task to database: {e}")

        # 获取价格信息
        estimated_price_usd = request_data.get("estimated_price_usd", 0.0)

        return {
            "id": op_name,
            "estimated_price_usd": estimated_price_usd,
            "model": model,
            "resolution": resolution,
        }

    async def extend_video_task(
        self,
        *,
        source_operation_name: str,
        model: str,
        prompt: str,
        negative_prompt: Optional[str],
        person_generation: str,
        request_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        # 记录开始时间
        start_time = time.time()

        op_name = await veo_service.extend_videos(
            source_operation_name=source_operation_name,
            model=model,
            prompt=prompt,
            negative_prompt=negative_prompt,
            person_generation=person_generation,
        )

        # 添加创建时间戳到 request_data
        request_data["created_at"] = start_time

        try:
            create_video_task(
                task_id=op_name,
                task_type="VEO_EXT",
                request_id="",
                request_data=request_data,
            )
        except Exception as e:
            print(f"Warning: Failed to record veo extend task to database: {e}")

        # 获取价格信息
        estimated_price_usd = request_data.get("estimated_price_usd", 0.0)

        return {
            "id": op_name,
            "estimated_price_usd": estimated_price_usd,
            "model": model,
            "resolution": "720p",  # 扩展固定为 720p
        }

    async def query_task_status(self, operation_name: str) -> Dict[str, Any]:
        info = await veo_service.get_operation_info(operation_name=operation_name)
        data: Dict[str, Any] = dict(info)

        # 尝试从数据库获取任务信息（包含价格和创建时间）
        try:
            task = get_video_task_by_id(operation_name)
            if task and task.request_data:
                data["estimated_price_usd"] = task.request_data.get("estimated_price_usd", 0.0)
                data["model"] = task.request_data.get("model", "")
                data["resolution"] = task.request_data.get("resolution", "")

                # 计算耗时
                created_at = task.request_data.get("created_at")
                if created_at:
                    current_time = time.time()
                    elapsed_seconds = int(current_time - created_at)
                    data["elapsed_seconds"] = elapsed_seconds
                    data["elapsed_time_formatted"] = _format_duration(elapsed_seconds)
        except Exception as e:
            print(f"Warning: Failed to get task info from database: {e}")

        status_raw = str(data.get("status") or "").lower()
        if status_raw == "succeeded":
            try:
                video_bytes = await veo_service.download_video_bytes(operation_name=operation_name)
                _, s3_url = await s3_service.upload_file(video_bytes, "output_video", "mp4")
                data["s3_video_url"] = s3_url
            except Exception:
                pass

        return data


def _format_duration(seconds: int) -> str:
    """格式化时间为易读格式"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}分{secs}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"


veo_video_service = VeoVideoService()
