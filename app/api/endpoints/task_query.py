"""
任务查询API端点
提供统一的任务状态查询接口
"""
from fastapi import APIRouter, HTTPException, status, Path

from app.models.response import BaseResponse
from app.services.video_service import video_service
from app.utils.exceptions import (
    TaskNotFoundException,
    DashScopeAPIException
)

router = APIRouter(prefix="/api/v1/task", tags=["任务查询"])


@router.get("/{task_id}", response_model=BaseResponse, summary="查询任务状态")
async def query_task(
    task_id: str = Path(..., description="任务ID，创建视频任务时返回")
):
    """
    查询视频生成任务的状态

    **任务状态说明：**
    - PENDING: 排队中，继续轮询
    - RUNNING: 处理中，继续轮询
    - SUCCEEDED: 成功，可获取视频URL
    - FAILED: 失败，查看错误信息
    - CANCELED: 已取消
    - UNKNOWN: 任务不存在或已过期（24小时）

    **视频URL说明：**
    - video_url: DashScope临时URL（24小时有效）
    - s3_video_url: 转存到自有S3的URL（签名URL，有效期取决于s3.url_expiration）
    """
    try:
        result = await video_service.query_task_status(task_id)

        return BaseResponse(
            success=True,
            message=f"任务状态: {result.task_status}",
            data=result.model_dump()
        )

    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
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
