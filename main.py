import signal

from fastapi import FastAPI
from wcferry import Wcf

from finbot import FinBot

app = FastAPI()

def start_fin_bot():
    wcf = Wcf(debug=True)

    def handler(sig, frame):
        wcf.cleanup()  # 退出前清理环境
        exit(0)

    signal.signal(signal.SIGINT, handler)

    robot = FinBot(wcf)
    robot.LOG.info(f"FinBot成功启动···")

    robot.enableReceivingMsg()  # 加队列
    # 让机器人一直跑
    robot.keepRunningAndBlockProcess()

start_fin_bot()
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

