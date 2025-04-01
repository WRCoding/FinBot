from pydantic import BaseModel

class WebMsg(BaseModel):
    remark: str
    msg: str