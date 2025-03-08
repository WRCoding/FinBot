from typing import Optional
from ..core.base import AIResponse
from ..core.config import AIConfig
from ..core.provider import AIProvider
from .factory import AIServiceFactory
from finbot import FinBot

class AIManager:
    """AI服务管理器"""
    def __init__(self, preferred_provider: Optional[AIProvider] = AIProvider.DEEPSEEK):
        self.preferred_provider = preferred_provider
        self.robot = FinBot()  # 获取 FinBot 单例
        
    def simple_chat(self, content: str, sys_prompt: str = AIConfig.get_system_prompt(), json_format: bool = True, **kwargs) -> AIResponse:
        """
        生成AI响应
        :param json_format: 是否输出JSON格式
        :param sys_prompt: 系统提示词
        :param content: 内容
        :param kwargs: 其他参数
        :return: AI响应
        """
        if self.preferred_provider:
            try:
                service = AIServiceFactory.get_service(self.preferred_provider)
                return service.simple_chat(content, sys_prompt, json_format,  **kwargs)
            except Exception as e:
                self.robot.send_text_msg(str(e))
                print(f"Error with preferred provider {self.preferred_provider}: {str(e)}")
        
        # 尝试所有可用的服务
        last_error = None
        for provider in AIProvider.get_priority_list():
            try:
                service = AIServiceFactory.get_service(provider)
                return service.simple_chat(content, **kwargs)
            except Exception as e:
                print(f"Error with provider {provider}: {str(e)}")
                last_error = e
                continue
        self.robot.send_text_msg(str(last_error))
        raise RuntimeError(f"All AI services failed. Last error: {str(last_error)}") 