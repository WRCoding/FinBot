from typing import TypeVar, Type, Optional, List, Any, Dict, Generic
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete
from db.session import get_db

# 定义泛型类型
ModelType = TypeVar("ModelType")

class BaseDBService(Generic[ModelType]):
    """
    通用数据库操作服务基类
    用法示例:
    class UserService(BaseDBService[UserModel]):
        def __init__(self):
            super().__init__(UserModel)
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """创建记录"""
        with get_db() as db:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            db.commit()  # 使用commit替代flush
            db.refresh(db_obj)  # 刷新对象以加载所有属性
            return db_obj
    
    def get(self, id: Any) -> Optional[ModelType]:
        """根据ID获取记录"""
        with get_db() as db:
            obj = db.get(self.model, id)
            if obj:
                db.refresh(obj)  # 刷新对象以加载所有属性
            return obj
    
    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取多条记录"""
        with get_db() as db:
            stmt = select(self.model).offset(skip).limit(limit)
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result
    
    def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """更新记录"""
        with get_db() as db:
            stmt = (
                update(self.model)
                .where(self.model.id == id)
                .values(**obj_in)
                .returning(self.model)
            )
            result = db.execute(stmt)
            db.commit()  # 使用commit替代flush
            obj = result.scalar_one_or_none()
            if obj:
                db.refresh(obj)  # 刷新对象以加载所有属性
            return obj
    
    def delete(self, id: Any) -> bool:
        """删除记录"""
        with get_db() as db:
            stmt = delete(self.model).where(self.model.id == id)
            result = db.execute(stmt)
            db.commit()  # 使用commit替代flush
            return result.rowcount > 0
    
    def exists(self, id: Any) -> bool:
        """检查记录是否存在"""
        with get_db() as db:
            return db.query(self.model).filter(self.model.id == id).first() is not None 