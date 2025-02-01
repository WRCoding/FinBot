import os
from typing import Optional

class AIConfig:
    """AI服务配置管理类"""
    @staticmethod
    def get_api_key(key_name: str) -> Optional[str]:
        """获取环境变量中的API密钥"""
        return os.getenv(key_name)

    @staticmethod
    def get_openai_api_key() -> Optional[str]:
        return AIConfig.get_api_key("OPENAI_API_KEY")

    @staticmethod
    def get_deepseek_api_key() -> Optional[str]:
        return AIConfig.get_api_key("DEEPSEEK_API_KEY")

    @staticmethod
    def get_system_prompt() -> str:
        system_prompt = '''
        你是一名XML智能解析机器人,你可以把用户上传的XML内容按照如下要求去解析
        1.解析出XML里面的，发布者，标题，交易时间，交易金额，交易类型，备注附言等（如有）
        2.按照JSON的格式进行输出，我只需要最终的结果，不需要中间的过程

        输出示例：
        1.{
          "标题": "xxx",
          "amount": 199,
          "transaction_time": "2025-01-28 13:23:08",
          "publisher": "交通银行",
          "type": "支出",
          "remark": "网上支付 财付通 中铁网络"
        }
        2.{
          "标题": "xxx",
          "amount": 19,
          "transaction_time": "2025-01-28 13:23:08",
          "publisher": "交通银行",
          "type": "收入",
          "remark": " "
        }
        '''
        return system_prompt