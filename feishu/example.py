import os
from pathlib import Path

from db import init_db
from db.services import TransactionService
from config import APP_ID, APP_SECRET
from feishu.message import FeishuMessageSender
from feishu.table import FeishuTable
from util import common_util
from util.common_util import find_project_root

# sender = FeishuMessageSender(
#     app_id=APP_ID,
#     app_secret=APP_SECRET
# )
# init_db()
#
# # 创建服务实例
# service = TransactionService()

table = FeishuTable(APP_ID, APP_SECRET)
# table_name = table.get_table_name()
# project_root = common_util.find_project_root()
# file_path = os.path.join(project_root, table_name + '.csv', )
# print(file_path)
print(table.get_file_path())
# print(data)
# msg = '\n'.join([
#                 f"类型: {t.type}, 金额: {t.amount}"
#                 for t in data
#             ])

# print(msg)