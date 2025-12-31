"""
Seedance 业务逻辑服务
负责：组装请求、调用 Seedance API、记录任务、查询任务并转存 S3
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.db.crud import create_video_task
from app.services.s3_service import s3_service
from app.services.seedance_service import seedance_service


class SeedanceVideoService:
    async def create_video_task(
        self,
        *,
        model: str,
        prompt_text: str,
        first_frame_url: Optional[str],
        last_frame_url: Optional[str],
        generate_audio: bool = True,
        request_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        content = [{"type": "text", "text": prompt_text}]
        if first_frame_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": first_frame_url},
                    "role": "first_frame",
                }
            )
        if last_frame_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": last_frame_url},
                    "role": "last_frame",
                }
            )

        response = await seedance_service.create_task(content, model=model, generate_audio=generate_audio)
        task_id = response.get("id")
        if not task_id:
            raise ValueError("Seedance 返回缺少任务 ID（id）")

        try:
            create_video_task(
                task_id=task_id,
                task_type="SEEDANCE",
                request_id="",
                request_data=request_data,
                img_url=first_frame_url,
                audio_url=None,
                reference_video_urls=None,
            )
        except Exception as e:
            print(f"Warning: Failed to record seedance task to database: {e}")

        # 对齐 Ark 文档：创建任务只返回 id
        return {"id": task_id}

    async def query_task_status(self, task_id: str) -> Dict[str, Any]:
        # 直接对齐 Ark 查询返回结构，并补充 s3_video_url
        response = await seedance_service.query_task(task_id)
        data: Dict[str, Any] = dict(response)

        content = data.get("content") or {}
        if not isinstance(content, dict):
            content = {}
        video_url = content.get("video_url")

        status_raw = (data.get("status") or "").lower()
        if status_raw == "succeeded" and video_url:
            try:
                _, s3_url = await s3_service.download_and_upload(video_url, "output_video")
                data["s3_video_url"] = s3_url
            except Exception:
                pass

        return data


seedance_video_service = SeedanceVideoService()
