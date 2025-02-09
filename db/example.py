from db.services import TransactionService
from db.base import init_db
from datetime import datetime, timedelta

# 初始化数据库（创建表）
init_db()

# 创建服务实例
service = TransactionService()


data = service.get_transactions_count_by_type()
# print(data)
# msg = '\n'.join([
#                 f"类型: {t.type}, 金额: {t.amount}"
#                 for t in data
#             ])
# print(msg)

a_data = service.get_yesterday_transactions_by_type()
msg = '\n'.join([
                f"类型: {t.type}, 金额: {t.amount}"
                for t in a_data
            ])
print(msg)