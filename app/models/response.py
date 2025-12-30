"""
响应模型
定义API接口的响应数据结构
"""
from typing import Optional, Literal, Any

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """基础响应模型"""

    success: bool = Field(description="请求是否成功")
    message: str = Field(description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class VideoGenerationResponse(BaseModel):
    """视频生成响应模型"""

    task_id: str = Field(description="任务ID，用于后续查询")
    task_status: Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN"] = Field(
        description="任务状态"
    )
    request_id: str = Field(description="请求ID")


class TaskUsage(BaseModel):
    """任务资源使用情况"""

    duration: Optional[int] = Field(None, description="总时长（秒）")
    input_video_duration: Optional[int] = Field(None, description="输入视频时长（秒）")
    output_video_duration: Optional[int] = Field(None, description="输出视频时长（秒）")
    video_count: Optional[int] = Field(None, description="视频数量")
    SR: Optional[int] = Field(None, description="分辨率档位")
    size: Optional[str] = Field(None, description="生成视频的分辨率（宽*高），等同于parameters.size")


class TaskQueryResponse(BaseModel):
    """任务查询响应模型"""

    task_id: str = Field(description="任务ID")
    task_status: Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELED", "UNKNOWN"] = Field(
        description="任务状态"
    )
    request_id: str = Field(description="请求ID")
    submit_time: Optional[str] = Field(None, description="提交时间")
    scheduled_time: Optional[str] = Field(None, description="调度时间")
    end_time: Optional[str] = Field(None, description="结束时间")
    orig_prompt: Optional[str] = Field(None, description="原始prompt")
    actual_prompt: Optional[str] = Field(None, description="改写后的prompt")
    video_url: Optional[str] = Field(None, description="生成的视频URL（临时，24小时有效）")
    s3_video_url: Optional[str] = Field(None, description="转存到S3的视频URL（签名URL，有效期取决于s3.url_expiration）")
    usage: Optional[TaskUsage] = Field(None, description="资源使用情况")
    error_code: Optional[str] = Field(None, description="错误代码")
    error_message: Optional[str] = Field(None, description="错误消息")


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""

    file_url: str = Field(description="文件的公网访问URL")
    file_path: str = Field(description="文件在S3中的路径")
    file_size: int = Field(description="文件大小（字节）")
