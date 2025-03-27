from fastapi import FastAPI
from pydantic import BaseModel

from config import HOST, PORT


class Item(BaseModel):
    msg: str


app = FastAPI()


@app.post("/send/msg/")
def create_item(item: Item):
    print(item.msg)

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    config = uvicorn.Config(app, host=HOST, port=PORT)
    server = uvicorn.Server(config)
    server.run()
    # server.shutdown()
