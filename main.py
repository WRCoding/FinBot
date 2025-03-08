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
    # {0: '朋友圈消息', 1: '文字', 3: '图片', 34: '语音', 37: '好友确认', 40: 'POSSIBLEFRIEND_MSG', 42: '名片',
    #  43: '视频', 47: '石头剪刀布 | 表情图片', 48: '位置', 49: '共享实时位置、文件、转账、链接', 50: 'VOIPMSG',
    #  51: '微信初始化', 52: 'VOIPNOTIFY', 53: 'VOIPINVITE', 62: '小视频', 66: '微信红包', 9999: 'SYSNOTICE',
    #  10000: '红包、系统消息', 10002: '撤 回消息', 1048625: '搜狗表情', 16777265: '链接', 436207665: '微信红包',
    #  536936497: '红包封面', 754974769: '视频号视频', 771751985: '视频号名片', 822083633: '引用消息',
    #  922746929: '拍一拍', 973078577: '视频号直播', 974127153: '商品链接', 975175729: '视频号直播',
    #  1040187441: '音乐链接', 1090519089: '文件'}
    print(wcf.get_msg_types())
    robot = FinBot(wcf)
    robot.LOG.info(f"FinBot成功启动···")


    task_manager.start()
    robot.enableReceivingMsg()  # 加队列
    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()

start_fin_bot()

