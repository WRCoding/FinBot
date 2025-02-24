import signal

from fastapi import FastAPI
from wcferry import Wcf

from db import init_db
from finbot import FinBot
from feishu import start_feishu_bot

init_db()
start_feishu_bot()
def start_fin_bot():
    wcf = Wcf(debug=True)

    def handler(sig, frame):
        wcf.cleanup()  # 退出前清理环境
        exit(0)

    signal.signal(signal.SIGINT, handler)

    robot = FinBot(wcf)
    robot.LOG.info(f"FinBot成功启动···")

    robot.start_scheduler()
    robot.enableReceivingMsg()  # 加队列
    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()

start_fin_bot()

