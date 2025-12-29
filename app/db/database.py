"""
数据库连接和会话管理
使用同步SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 创建Base类
Base = declarative_base()

# 创建同步引擎
engine = None
SessionLocal = None


def init_db():
    """初始化数据库"""
    global engine, SessionLocal

    # 创建SQLite引擎（同步）
    database_url = f"sqlite:///{settings.database_path}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # SQLite特有配置
        echo=False  # 设置为True可以看到SQL日志
    )

    # 创建会话工厂
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    print(f"✅ Database initialized at: {settings.database_path}")


def get_session():
    """获取数据库会话"""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return SessionLocal()
