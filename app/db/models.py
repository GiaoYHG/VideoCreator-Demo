"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.db.database import Base


class VideoTask(Base):
    """视频生成任务模型"""

    __tablename__ = "video_tasks"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 任务标识
    task_id = Column(String(100), unique=True, nullable=False, index=True, comment="任务ID")
    task_type = Column(String(10), nullable=False, index=True, comment="任务类型: I2V/T2V/R2V")
    request_id = Column(String(100), comment="DashScope请求ID")

    # 请求数据（JSON字符串）
    request_data = Column(Text, comment="完整的请求参数JSON")

    # 文件URLs
    img_url = Column(Text, comment="图片URL（I2V使用）")
    audio_url = Column(Text, comment="音频URL（可选）")
    reference_video_urls = Column(Text, comment="参考视频URLs的JSON数组（R2V使用）")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="记录创建时间")

    def __repr__(self):
        return f"<VideoTask(id={self.id}, task_id='{self.task_id}', task_type='{self.task_type}')>"
