from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from db.models import Transaction
from db.service import BaseDBService
from db.session import get_db
from sqlalchemy import func


class TransactionService(BaseDBService[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    def get_by_publisher(self, publisher: str, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """根据发布者查询交易记录"""
        with get_db() as db:
            stmt = (
                select(self.model)
                .where(self.model.publisher == publisher)
                .offset(skip)
                .limit(limit)
                .order_by(self.model.transaction_time.desc())
            )
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result

    def get_by_time_range(
            self,
            start_time: Optional[datetime] = None,
            end_time: Optional[datetime] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[Transaction]:
        """根据时间范围查询交易记录"""
        with get_db() as db:
            conditions = []
            if start_time:
                conditions.append(self.model.transaction_time >= start_time)
            if end_time:
                conditions.append(self.model.transaction_time <= end_time)

            stmt = (
                select(self.model)
                .where(and_(*conditions))
                .offset(skip)
                .limit(limit)
                .order_by(self.model.transaction_time.desc())
            )
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result

    def get_by_amount_range(
            self,
            min_amount: Optional[str] = None,
            max_amount: Optional[str] = None,
            skip: int = 0,
            limit: int = 100
    ) -> List[Transaction]:
        """根据金额范围查询交易记录"""
        with get_db() as db:
            conditions = []
            if min_amount:
                conditions.append(self.model.amount >= min_amount)
            if max_amount:
                conditions.append(self.model.amount <= max_amount)

            stmt = (
                select(self.model)
                .where(and_(*conditions))
                .offset(skip)
                .limit(limit)
                .order_by(self.model.transaction_time.desc())
            )
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result

    def get_latest_transactions(self, limit: int = 10) -> List[Transaction]:
        """获取最新的交易记录"""
        with get_db() as db:
            stmt = (
                select(self.model)
                .order_by(self.model.transaction_time.desc())
                .limit(limit)
            )
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result

    def get_all_transactions(self) -> List[Transaction]:
        """获取最新的交易记录"""
        with get_db() as db:
            stmt = (
                select(self.model)
                .order_by(self.model.transaction_time.desc())
            )
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result

    def get_transactions_count_by_type(self):
        """按类型统计交易记录数量"""
        with get_db() as db:
            result = db.query(Transaction.type, func.sum(Transaction.amount).label("amount"), Transaction.transaction_time, Transaction.remark).group_by(
                Transaction.type).all()
            return result

    def get_publisher_transaction_count(self, publisher: str) -> int:
        """获取发布者的交易总数"""
        with get_db() as db:
            stmt = (
                select(self.model)
                .where(self.model.publisher == publisher)
            )
            return len(list(db.scalars(stmt)))


    def get_yesterday_transactions_by_type(self) -> List[dict]:
        """统计上一日不同类型的交易总金额"""
        with get_db() as db:
            from sqlalchemy import func, cast, Float
            from datetime import datetime, timedelta

            # 获取昨天的日期范围
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_start = (today - timedelta(days=2)).strftime('%Y年%m月%d日')
            yesterday_end = today.strftime('%Y年%m月%d日')

            stmt = (
                select(
                    self.model.type,
                    func.sum(cast(self.model.amount, Float)).label('total_amount')
                )
                .where(
                    self.model.transaction_time >= yesterday_start,
                    self.model.transaction_time < yesterday_end
                )
                .group_by(self.model.type)
            )

            result = db.execute(stmt)
            return [
                {
                    "type": row.type or "未分类",
                    "total_amount": float(row.total_amount) if row.total_amount else 0.0
                }
                for row in result
            ]
