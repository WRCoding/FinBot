import os
import threading

from fastapi import FastAPI
import sys

from uvicorn import Server

from entity.web_msg import WebMsg
from message_parser import MessageParser

# 获取根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将根目录添加到path中
sys.path.append(BASE_DIR)

from config import HOST, PORT

app = FastAPI()


@app.post("/send/msg/")
def create_item(web_msg: WebMsg):
    parser = MessageParser()
    parser.parse_msg_web(web_msg)


@app.get("/")
def read_root():
    return {"Hello": "World"}


def _app_client_thread():
    import uvicorn
    config = uvicorn.Config(app, host=HOST, port=PORT)
    server = uvicorn.Server(config)
    server.run()
    return server


def start_web():
    ws_thread = threading.Thread(target=_app_client_thread, name="feishu_ws_client")
    ws_thread.daemon = True  # 设置为守护线程，这样主程序退出时，WebSocket 客户端也会退出
    ws_thread.start()
    return ws_thread

# if __name__ == "__main__":
# import uvicorn
#
# config = uvicorn.Config(app, host=HOST, port=PORT)
# server = uvicorn.Server(config)
# server.run()
# # server.shutdown()
