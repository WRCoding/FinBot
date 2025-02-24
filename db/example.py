from util.date_util import get_date
from db.services import TransactionService
from db.base import init_db
from datetime import datetime, timedelta

# 初始化数据库（创建表）
init_db()

# 创建服务实例
service = TransactionService()


# print(data)
# msg = '\n'.join([
#                 f"类型: {t.type}, 金额: {t.amount}"
#                 for t in data
#             ])
# print(msg)
# data = service.get_transactions_by_date('2025年02月01日')
# print(data)
# temp = service.transfer_template(service.get_all_transactions())
# print(temp)
print(service.get_transactions_summary_by_date('2025年02月01日'))