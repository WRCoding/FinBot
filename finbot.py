# -*- coding: utf-8 -*-

import logging
import time
from queue import Empty
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler
from wcferry import Wcf, WxMsg

import schedule

from config import WX_ID
from parse_msg import parse_msg_xml, parse_msg_self
from util.date_util import get_date


class FinBot:

    def __init__(self, wcf: Wcf) -> None:
        self.wcf = wcf
        self.LOG = logging.getLogger("Robot")
        self.wxid = self.wcf.get_self_wxid()
        self.allContacts = self.getAllContacts()

    def processMsg(self, msg: WxMsg) -> None:
        """当接收到消息的时候，会调用本方法。如果不实现本方法，则打印原始消息。
        此处可进行自定义发送的内容,如通过 msg.content 关键字自动获取当前天气信息，并发送到对应的群组@发送者
        群号：msg.roomid  微信ID：msg.sender  消息内容：msg.content
        content = "xx天气信息为："
        receivers = msg.roomid
        self.sendTextMsg(content, receivers, msg.sender)
        """
        content = msg.content if msg.type == 1 else ''
        print(f'id: {msg.id}, sender: {msg.sender}, type: {msg.type}, content: {content}')
        if msg.type == 1 and msg.sender == WX_ID:
            parse_msg_self(msg.content, self.wcf)
        if msg.type == 49:
            parse_msg_xml(msg.content)

    def enableReceivingMsg(self) -> None:
        def innerProcessMsg(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    # self.LOG.info(msg)
                    self.processMsg(msg)
                except Empty:
                    continue  # Empty message
                except Exception as e:
                    self.LOG.error(f"Receiving message error: {e}")

        # print(f'消息类型: ${self.wcf.get_msg_types()}')
        self.wcf.enable_receiving_msg()
        Thread(target=innerProcessMsg, name="GetMessage", args=(self.wcf,), daemon=True).start()

    def getAllContacts(self) -> dict:
        """
        获取联系人（包括好友、公众号、服务号、群成员……）
        格式: {"wxid": "NickName"}
        """
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName FROM Contact;")
        return {contact["UserName"]: contact["NickName"] for contact in contacts}

    def keepRunningAndBlockProcess(self) -> None:
        """
        保持机器人运行，不让进程退出
        """
        while True:
            schedule.run_pending()
            time.sleep(1)

    def send_daily_summary(self) -> None:
        date = get_date(count=-1, format='%Y%m%d')
        content = f'#汇总@{date}'
        parse_msg_self(content, self.wcf)

    def start_scheduler(self) -> None:
        scheduler = BackgroundScheduler()

        # 添加每天早上8点执行的任务
        scheduler.add_job(
            self.send_daily_summary,
            trigger='cron',
            hour=8,
            minute=0
        )

        # 启动调度器
        scheduler.start()
