from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from .base import engine

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

@contextmanager
def get_db() -> Session:
    """
    获取数据库会话的上下文管理器
    使用方法:
    with get_db() as db:
        db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_db_session() -> Session:
    """
    获取一个新的数据库会话
    注意：使用此方法需要手动关闭会话
    """
    return SessionLocal() 