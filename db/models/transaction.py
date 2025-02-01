from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from db.base import Base

class Transaction(Base):
    """交易模型"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="主键ID")
    amount = Column(String(50), nullable=False, index=True, comment="交易金额")
    transaction_time = Column(String(100), nullable=False, index=True, comment="交易时间")
    publisher = Column(String(100), nullable=False, index=True, comment="发布者")
    remark = Column(String(100), nullable=True, index=True, comment="备注")
    type = Column(String(10), nullable=True, index=True, comment="类型")

    def __repr__(self):
        return f"<Transaction(id={self.id if '_sa_instance_state' in self.__dict__ else None})>" 