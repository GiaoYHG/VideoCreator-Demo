"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.endpoints import video_generation, task_query, ui, seedance_task, sora_video
from app.utils.exceptions import VideoCreatorException
from app.db import init_db

# 创建FastAPI应用实例
app = FastAPI(
    title="视频生成服务 API",
    description="""
    基于阿里云DashScope通义万相的视频生成服务

    ## 功能特性
    - 图生视频 (Image-to-Video, I2V)
    - 文生视频 (Text-to-Video, T2V)
    - 参考生视频 (Reference-to-Video, R2V)
    - 统一任务查询接口

    ## 工作流程
    1. 调用视频生成接口（/api/v1/video/i2v 或 /t2v 或 /r2v）
    2. 获取 task_id
    3. 使用 task_id 定时调用查询接口（/api/v1/task/{task_id}）
    4. 当状态为 SUCCEEDED 时，获取视频URL
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug
)

# 配置CORS（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(video_generation.router)
app.include_router(task_query.router)
app.include_router(seedance_task.router)
app.include_router(sora_video.router)
app.include_router(ui.router)


# 启动事件：初始化数据库
@app.on_event("startup")
def startup_event():
    """应用启动时初始化数据库"""
    init_db()


@app.get("/", tags=["健康检查"])
async def root():
    """根路径，返回服务信息"""
    return {
        "service": "视频生成服务",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "dashscope_region": settings.dashscope_region,
        "s3_region": settings.s3_region,
        "s3_bucket": settings.s3_bucket_name
    }


# 全局异常处理
@app.exception_handler(VideoCreatorException)
async def video_creator_exception_handler(request, exc: VideoCreatorException):
    """处理自定义业务异常"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """处理未捕获的异常"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "details": str(exc) if settings.debug else None
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
