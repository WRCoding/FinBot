from db import init_db
from db.services import TransactionService
from config import APP_ID, APP_SECRET
from feishu.message import FeishuMessageSender

sender = FeishuMessageSender(
    app_id=APP_ID,
    app_secret=APP_SECRET
)
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