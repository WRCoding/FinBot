# -*- coding: utf-8 -*-
from wcferry import Wcf

from finbot import FinBot
from message_parser import MessageParser
from scheduler.base_task import BaseTask
from util.date_util import get_date
from config import WX_ID


class DailySummaryTask(BaseTask):
    """
    每日汇总任务，每天早上8点执行
    """
    
    def __init__(self):
        super().__init__(
            task_id="daily_summary",
            description="每日汇总，发送前一天的汇总信息"
        )
        self.msg_parser = MessageParser()
        
    def execute(self, *args, **kwargs):
        """
        执行任务，发送每日汇总信息
        """
        # 获取前一天的日期
        date = get_date(count=-1, format='%Y%m%d')
        content = f'#汇总@{date}'

        
        # 发送汇总消息
        self.msg_parser.parse_msg_self(content)
        return f"已发送{date}的每日汇总"
    
    def get_cron_config(self):
        """
        获取cron配置，每天早上8点执行
        """
        return {
            "hour": "8",
            "minute": "0"
        } 