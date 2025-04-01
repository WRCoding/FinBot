import signal

from wcferry import Wcf

from db import init_db
from finbot import FinBot
from feishu import start_feishu_bot
from scheduler.jobs.daily_summary_task import DailySummaryTask
from scheduler.jobs.update_csv_task import UpdateCsvTask
from scheduler.task_manager import TaskManager
from web.api import start_web

init_db()
start_feishu_bot()
def start_fin_bot():
    robot = FinBot()
    task_manager = TaskManager()
    server = start_web()
    def handler(sig, frame):
        task_manager.shutdown()
        robot.clean()
        server.shutdown()
        exit(0)

    task_manager.register_task(DailySummaryTask())
    task_manager.register_task(UpdateCsvTask())
    signal.signal(signal.SIGINT, handler)


    robot.LOG.info(f"FinBot成功启动···")


    task_manager.start()
    robot.enableReceivingMsg()  # 加队列
    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()

start_fin_bot()

