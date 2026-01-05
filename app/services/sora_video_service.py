"""
Sora 业务逻辑服务（OpenAI Videos API）
负责：创建/Remix/查询任务并在完成后转存到 S3
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.db.crud import create_video_task
from app.services.openai_video_service import openai_video_service
from app.services.s3_service import s3_service


_DONE_STATUSES = {"completed", "succeeded"}


class SoraVideoService:
    async def create_video_task(
        self,
        *,
        prompt: str,
        model: str,
        seconds: str,
        size: str,
        input_reference: Optional[tuple[str, bytes, str]] = None,
        request_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        response = await openai_video_service.create_video(
            prompt=prompt,
            model=model,
            seconds=seconds,
            size=size,
            input_reference=input_reference,
        )

        video_id = response.get("id")
        if video_id:
            try:
                create_video_task(
                    task_id=video_id,
                    task_type="SORA",
                    request_id="",
                    request_data=request_data,
                )
            except Exception as e:
                print(f"Warning: Failed to record sora task to database: {e}")

        return response

    async def remix_video_task(
        self,
        *,
        video_id: str,
        prompt: str,
        request_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        response = await openai_video_service.remix_video(video_id=video_id, prompt=prompt)

        new_id = response.get("id")
        if new_id:
            try:
                create_video_task(
                    task_id=new_id,
                    task_type="SORA_REMIX",
                    request_id="",
                    request_data=request_data,
                )
            except Exception as e:
                print(f"Warning: Failed to record sora remix task to database: {e}")

        return response

    async def query_video_task(self, *, video_id: str) -> Dict[str, Any]:
        response = await openai_video_service.retrieve_video(video_id=video_id)
        data: Dict[str, Any] = dict(response)

        status = str(data.get("status") or "").lower()
        if status in _DONE_STATUSES:
            try:
                video_bytes = await openai_video_service.download_video_content(video_id=video_id)
                _, s3_url = await s3_service.upload_file(video_bytes, "output_video", "mp4")
                data["s3_video_url"] = s3_url
            except Exception:
                # 转存失败不影响返回元数据
                pass

        return data


sora_video_service = SoraVideoService()

