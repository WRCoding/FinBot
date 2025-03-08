import signal

from fastapi import FastAPI
from wcferry import Wcf

from db import init_db
from finbot import FinBot
from feishu import start_feishu_bot
from scheduler.jobs.daily_summary_task import DailySummaryTask
from scheduler.jobs.update_csv_task import UpdateCsvTask
from scheduler.task_manager import TaskManager

init_db()
start_feishu_bot()
def start_fin_bot():
    wcf = Wcf(debug=True)
    task_manager = TaskManager()
    def handler(sig, frame):
        task_manager.shutdown()
        wcf.cleanup()  # 退出前清理环境
        exit(0)

    task_manager.register_task(DailySummaryTask(wcf=wcf))
    task_manager.register_task(UpdateCsvTask())
    signal.signal(signal.SIGINT, handler)
    print(wcf.get_msg_types())
    robot = FinBot(wcf)
    robot.LOG.info(f"FinBot成功启动···")


    task_manager.start()
    robot.enableReceivingMsg()  # 加队列
    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()

start_fin_bot()

