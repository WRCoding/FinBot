from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from db.models import Transaction
from db.service import BaseDBService
from db.session import get_db
from sqlalchemy import func

from feishu.config import TEMPLATE_ID
from feishu.template import TemplateVariable, Template, TemplateData


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

    def transfer_template(self, transactions: List[Transaction], template_id: str = TEMPLATE_ID, version: str = "1.0.4") -> Template:
        """将交易记录转换为模板对象

        Args:
            transactions: 交易记录列表
            template_id: 模板ID
            version: 模板版本

        Returns:
            Template: 转换后的模板对象
        """
        transaction_list = [
            {
                "type": transaction.type,
                "amount": transaction.amount,
                "transaction_time": transaction.transaction_time,
                "remark": transaction.remark
            } for transaction in transactions
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

    def get_transactions_by_date(self, start_date: str, end_date: str = None) -> List[Transaction]:
        """获取指定日期范围的交易记录
        
        Args:
            start_date: 开始日期，格式为'YYYY年MM月DD日'
            end_date: 结束日期，格式为'YYYY年MM月DD日'，如果不传则只查询start_date当天的数据
            
        Returns:
            List[Transaction]: 交易记录列表
        """
        with get_db() as db:
            if end_date is None:
                # 如果没有传入end_date，则查询start_date当天的数据
                stmt = (
                    select(self.model)
                    .where(self.model.transaction_time.like(f"{start_date}%"))
                    .order_by(self.model.transaction_time.desc())
                )
            else:
                # 查询日期范围内的数据
                stmt = (
                    select(self.model)
                    .where(
                        and_(
                            self.model.transaction_time > start_date,
                            self.model.transaction_time < end_date
                        )
                    )
                    .order_by(self.model.transaction_time.desc())
                )
            
            result = list(db.scalars(stmt))
            for obj in result:
                db.refresh(obj)
            return result
