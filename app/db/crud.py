"""
数据库CRUD操作
"""
import json
from typing import Optional, List
from app.db.database import get_session
from app.db.models import VideoTask


def create_video_task(
    task_id: str,
    task_type: str,
    request_id: str,
    request_data: dict,
    img_url: Optional[str] = None,
    audio_url: Optional[str] = None,
    reference_video_urls: Optional[List[str]] = None
) -> Optional[VideoTask]:
    """
    创建视频任务记录

    Args:
        task_id: 任务ID
        task_type: 任务类型（I2V/T2V/R2V）
        request_id: DashScope请求ID
        request_data: 完整的请求参数字典
        img_url: 图片URL（I2V使用）
        audio_url: 音频URL（可选）
        reference_video_urls: 参考视频URLs列表（R2V使用）

    Returns:
        VideoTask: 创建的任务对象，失败返回None
    """
    session = get_session()
    try:
        # 将请求数据转换为JSON字符串
        request_data_json = json.dumps(request_data, ensure_ascii=False)

        # 将参考视频URLs转换为JSON字符串
        reference_video_urls_json = None
        if reference_video_urls:
            reference_video_urls_json = json.dumps(reference_video_urls, ensure_ascii=False)

        # 创建任务对象
        video_task = VideoTask(
            task_id=task_id,
            task_type=task_type,
            request_id=request_id,
            request_data=request_data_json,
            img_url=img_url,
            audio_url=audio_url,
            reference_video_urls=reference_video_urls_json
        )

        # 添加到会话并提交
        session.add(video_task)
        session.commit()
        session.refresh(video_task)

        print(f"✅ Task recorded: {task_id} ({task_type})")
        return video_task

    except Exception as e:
        session.rollback()
        print(f"❌ Failed to record task {task_id}: {str(e)}")
        return None

    finally:
        session.close()


def get_video_task_by_id(task_id: str) -> Optional[VideoTask]:
    """
    根据任务ID获取视频任务记录

    Args:
        task_id: 任务ID

    Returns:
        VideoTask: 任务对象，如果不存在返回None
    """
    session = get_session()
    try:
        task = session.query(VideoTask).filter(VideoTask.task_id == task_id).first()
        if task and task.request_data:
            # 将JSON字符串转换回字典
            try:
                task.request_data = json.loads(task.request_data)
            except (json.JSONDecodeError, TypeError):
                pass
        return task
    except Exception as e:
        print(f"❌ Failed to get task {task_id}: {str(e)}")
        return None
    finally:
        session.close()
