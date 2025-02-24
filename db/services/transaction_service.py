from typing import List
from sqlalchemy import select, and_
from db.models import Transaction
from db.service import BaseDBService
from db.session import get_db
from sqlalchemy import func

from config import TEMPLATE_ID
from feishu.template import TemplateVariable, Template, TemplateData
from util.date_util import get_date


class TransactionService(BaseDBService[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    def get_all_transactions(self, desc: bool=True) -> List[Transaction]:
        """获取全部的交易记录"""
        with get_db() as db:
            stmt = (
                select(self.model)
                .order_by(self.model.transaction_time.desc() if desc else self.model.transaction_time.asc())
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

    def get_transactions_by_date(self, start_date: str, end_date: str = None, desc: bool=True) -> List[Transaction]:
        """获取指定日期范围的交易记录
        
        Args:
            start_date: 开始日期，格式为'YYYY年MM月DD日'
            end_date: 结束日期，格式为'YYYY年MM月DD日'，如果不传则只查询start_date当天的数据
            desc: 是否倒序输出
        Returns:
            List[Transaction]: 交易记录列表
        """
        with get_db() as db:
            if end_date is None:
                # 如果没有传入end_date，则查询start_date当天的数据
                stmt = (
                    select(self.model)
                    .where(self.model.transaction_time.like(f"{start_date}%"))
                    .order_by(self.model.transaction_time.desc() if desc else self.model.transaction_time.asc())
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

    def get_transactions_summary_by_date(self, start_date: str = get_date(), end_date: str = None) -> List[dict]:
        """获取指定日期范围内按类型分组的交易汇总

        Args:
            start_date: 开始日期，格式为'YYYY年MM月DD日'
            end_date: 结束日期，格式为'YYYY年MM月DD日'，如果不传则只查询start_date当天的数据

        Returns:
            List[dict]: 包含类型和总金额的字典列表
        """
        with get_db() as db:
            from sqlalchemy import func, cast, Float

            base_query = select(
                self.model.type,
                func.sum(cast(self.model.amount, Float)).label('total_amount')
            )

            if end_date is None:
                # 如果没有传入end_date，则查询start_date当天的数据
                stmt = (
                    base_query
                    .where(self.model.transaction_time.like(f"{start_date}%"))
                    .group_by(self.model.type)
                )
            else:
                # 查询日期范围内的数据
                stmt = (
                    base_query
                    .where(
                        and_(
                            self.model.transaction_time > start_date,
                            self.model.transaction_time < end_date
                        )
                    )
                    .group_by(self.model.type)
                )

            results = db.execute(stmt).all()
            return [{"type": type_, "amount": float(total_amount)} for type_, total_amount in results]
