# -*- coding: utf-8 -*-

import logging
import re
import time
import xml.etree.ElementTree as ET
from queue import Empty
from threading import Thread

from wcferry import Wcf, WxMsg

import schedule

from parse_msg import parse_msg_xml, parse_msg_self


class FinBot:

    def __init__(self, wcf: Wcf) -> None:
        self.wcf = wcf
        self.LOG = logging.getLogger("Robot")
        self.wxid = self.wcf.get_self_wxid()
        self.allContacts = self.getAllContacts()


    def processMsg(self, msg: WxMsg, wcf: Wcf) -> None:
        """当接收到消息的时候，会调用本方法。如果不实现本方法，则打印原始消息。
        此处可进行自定义发送的内容,如通过 msg.content 关键字自动获取当前天气信息，并发送到对应的群组@发送者
        群号：msg.roomid  微信ID：msg.sender  消息内容：msg.content
        content = "xx天气信息为："
        receivers = msg.roomid
        self.sendTextMsg(content, receivers, msg.sender)
        """
        # self_wxid = wcf.get_self_wxid()
        content = msg.content if msg.type == 1 else ''
        print(f'id: {msg.id}, sender: {msg.sender}, type: {msg.type}, content: {content}')
        # if msg.type == 1 and self_wxid == msg.sender:
        #     parse_msg_self(msg.content, self_wxid, wcf)
        if msg.type == 49:
            parse_msg_xml(msg.content)

    def enableReceivingMsg(self) -> None:
        def innerProcessMsg(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    # self.LOG.info(msg)
                    self.processMsg(msg, wcf)
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
