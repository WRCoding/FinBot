import os

from fastapi import FastAPI
from pydantic import BaseModel



import sys
# 获取根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将根目录添加到path中
sys.path.append(BASE_DIR)

from config import HOST, PORT
class Item(BaseModel):
    remark: str
    msg:str


app = FastAPI()


@app.post("/send/msg/")
def create_item(item: Item):
    print(f'remark: {item.remark}, msg: {item.msg}')

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config(app, host=HOST, port=PORT)
    server = uvicorn.Server(config)
    server.run()
    # server.shutdown()
