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

temp = service.get_transactions_for_template()
print(temp.to_escaped_json())