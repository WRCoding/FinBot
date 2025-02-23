from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from db.models import Transaction
from db.service import BaseDBService
from db.session import get_db
from sqlalchemy import func

from feishu.config import TEMPLATE_ID
from feishu.message_template import TemplateVariable, Template, TemplateData


class TransactionService(BaseDBService[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    def get_latest_transactions(self, limit: int = 10) -> List[Transaction]:
        """获取最新的交易记录"""
        with get_db() as db:
            stmt = (
                select(self.model.type,
                       self.model.transaction_time,
                       self.model.remark,
                       self.model.amount)
                .order_by(self.model.transaction_time.desc())
                .limit(limit)
            )
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result

    def get_all_transactions(self) -> List[Transaction]:
        """获取全部的交易记录"""
        with get_db() as db:
            stmt = (
                select(self.model)
                .order_by(self.model.transaction_time.desc())
            )
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result

    def get_transactions_count_by_type(self) -> List[Transaction]:
        """按类型统计交易记录数量"""
        with get_db() as db:
            result = db.query(Transaction.type, func.sum(Transaction.amount).label("amount"),
                              Transaction.transaction_time, Transaction.remark).group_by(
                Transaction.type).all()
            return result

    def get_yesterday_transactions_by_type(self) -> List[Transaction]:
        """统计上一日不同类型的交易总金额"""
        with get_db() as db:
            from sqlalchemy import func, cast, Float
            from datetime import datetime, timedelta

            # 获取昨天的日期范围
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_start = (today - timedelta(days=1)).strftime('%Y年%m月%d日')
            yesterday_end = today.strftime('%Y年%m月%d日')

            stmt = (
                select(
                    self.model.type,
                    func.sum(cast(self.model.amount, Float)).label('amount')
                )
                .where(
                    self.model.transaction_time >= yesterday_start,
                    self.model.transaction_time < yesterday_end
                )
                .group_by(self.model.type)
            )

            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)  # 刷新每个对象以加载所有属性
            return result

    def get_transactions_for_template(self, template_id: str = TEMPLATE_ID, version: str = "1.0.4") -> Template:
        """获取交易记录并转换为模板对象"""
        with get_db() as db:
            stmt = (
                select(
                    self.model.type,
                    self.model.amount,
                    self.model.transaction_time,
                    self.model.remark
                )
                .order_by(self.model.transaction_time.desc())
            )
            rows = db.execute(stmt).all()
            transaction_list = [
                {
                    "type": row[0],
                    "amount": row[1],
                    "transaction_time": row[2],
                    "remark": row[3]
                } for row in rows
            ]
            
            return Template(
                type="template",
                data=TemplateData(
                    template_id=template_id,
                    template_version_name=version,
                    template_variable=TemplateVariable(
                        transactions=transaction_list
                    )
                )
            )
