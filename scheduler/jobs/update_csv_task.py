from typing import Any, Dict

from config import APP_ID, APP_SECRET
from feishu.table import FeishuTable
from scheduler.base_task import BaseTask


class UpdateCsvTask(BaseTask):

    def __init__(self):
        super().__init__(
            task_id="update_csv",
            description="每日更新CSV数据"
        )

    def get_cron_config(self):
        """
                获取cron配置，每天早上1点执行
                """
        return {
            "hour": "1",
            "minute": "0"
        }

    def execute(self, *args, **kwargs):
        table = FeishuTable(APP_ID, APP_SECRET)
        table.export_table()
        return f"已经更新最新的CSV数据"
