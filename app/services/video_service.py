"""
视频业务逻辑服务
整合OSS服务和DashScope服务，提供完整的业务流程
"""
from typing import List, Optional

from app.models.request import I2VRequest, T2VRequest, R2VRequest
from app.models.response import (
    VideoGenerationResponse,
    TaskQueryResponse,
    TaskUsage
)
from app.services.dashscope_service import dashscope_service
from app.services.s3_service import oss_service


class VideoService:
    """视频业务逻辑服务类"""

    async def create_i2v_video(
        self,
        request: I2VRequest,
        img_url: str,
        audio_url: Optional[str] = None
    ) -> VideoGenerationResponse:
        """
        创建图生视频任务

        Args:
            request: 图生视频请求参数
            img_url: 图片URL（已上传到OSS）
            audio_url: 音频URL（可选，已上传到OSS）

        Returns:
            VideoGenerationResponse: 视频生成响应
        """
        # 调用DashScope API创建任务
        response = await dashscope_service.create_i2v_task(
            img_url=img_url,
            prompt=request.prompt,
            model=request.model,
            negative_prompt=request.negative_prompt,
            audio_url=audio_url,
            resolution=request.resolution,
            duration=request.duration,
            prompt_extend=request.prompt_extend,
            shot_type=request.shot_type,
            audio=request.audio,
            watermark=request.watermark,
            seed=request.seed
        )

        # 解析响应
        output = response.get("output", {})
        return VideoGenerationResponse(
            task_id=output.get("task_id"),
            task_status=output.get("task_status", "UNKNOWN"),
            request_id=response.get("request_id", "")
        )

    async def create_t2v_video(
        self,
        request: T2VRequest,
        audio_url: Optional[str] = None
    ) -> VideoGenerationResponse:
        """
        创建文生视频任务

        Args:
            request: 文生视频请求参数
            audio_url: 音频URL（可选，已上传到OSS）

        Returns:
            VideoGenerationResponse: 视频生成响应
        """
        # 调用DashScope API创建任务
        response = await dashscope_service.create_t2v_task(
            prompt=request.prompt,
            model=request.model,
            negative_prompt=request.negative_prompt,
            audio_url=audio_url,
            size=request.size,
            duration=request.duration,
            prompt_extend=request.prompt_extend,
            shot_type=request.shot_type,
            audio=request.audio,
            watermark=request.watermark,
            seed=request.seed
        )

        # 解析响应
        output = response.get("output", {})
        return VideoGenerationResponse(
            task_id=output.get("task_id"),
            task_status=output.get("task_status", "UNKNOWN"),
            request_id=response.get("request_id", "")
        )

    async def create_r2v_video(
        self,
        request: R2VRequest,
        reference_video_urls: List[str]
    ) -> VideoGenerationResponse:
        """
        创建参考生视频任务

        Args:
            request: 参考生视频请求参数
            reference_video_urls: 参考视频URL列表（已上传到OSS）

        Returns:
            VideoGenerationResponse: 视频生成响应
        """
        # 调用DashScope API创建任务
        response = await dashscope_service.create_r2v_task(
            prompt=request.prompt,
            reference_video_urls=reference_video_urls,
            model=request.model,
            negative_prompt=request.negative_prompt,
            size=request.size,
            duration=request.duration,
            shot_type=request.shot_type,
            audio=request.audio,
            watermark=request.watermark,
            seed=request.seed
        )

        # 解析响应
        output = response.get("output", {})
        return VideoGenerationResponse(
            task_id=output.get("task_id"),
            task_status=output.get("task_status", "UNKNOWN"),
            request_id=response.get("request_id", "")
        )

    async def query_task_status(self, task_id: str) -> TaskQueryResponse:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            TaskQueryResponse: 任务查询响应

        Raises:
            TaskNotFoundException: 任务不存在
        """
        # 调用DashScope API查询任务
        response = await dashscope_service.query_task(task_id)

        output = response.get("output", {})
        task_status = output.get("task_status", "UNKNOWN")

        # 构建响应
        query_response = TaskQueryResponse(
            task_id=output.get("task_id", task_id),
            task_status=task_status,
            request_id=response.get("request_id", ""),
            submit_time=output.get("submit_time"),
            scheduled_time=output.get("scheduled_time"),
            end_time=output.get("end_time"),
            orig_prompt=output.get("orig_prompt"),
            actual_prompt=output.get("actual_prompt"),
            video_url=output.get("video_url"),
            oss_video_url=None,
            usage=None,
            error_code=output.get("code"),
            error_message=output.get("message")
        )

        # 如果任务成功，处理usage信息（usage在响应顶层，不在output内）
        if "usage" in response:
            usage_data = response["usage"]
            query_response.usage = TaskUsage(
                duration=usage_data.get("duration"),
                input_video_duration=usage_data.get("input_video_duration"),
                output_video_duration=usage_data.get("output_video_duration"),
                video_count=usage_data.get("video_count"),
                SR=usage_data.get("SR"),
                size=usage_data.get("size") or usage_data.get("video_ratio")
            )

        # 如果任务成功且有video_url，自动下载并转存到OSS
        if task_status == "SUCCEEDED" and output.get("video_url"):
            try:
                # 下载视频并上传到自有OSS
                _, oss_url = await oss_service.download_and_upload(
                    output["video_url"],
                    "output_video"
                )
                query_response.oss_video_url = oss_url
            except Exception:
                # 转存失败不影响返回临时URL
                pass

        return query_response


# 全局视频服务实例
video_service = VideoService()
