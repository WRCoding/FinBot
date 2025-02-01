from typing import Optional
from ..core.base import AIResponse
from ..core.provider import AIProvider
from .factory import AIServiceFactory

class AIManager:
    """AI服务管理器"""
    def __init__(self, preferred_provider: Optional[AIProvider] = None):
        self.preferred_provider = preferred_provider
        
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """
        生成AI响应
        :param prompt: 提示词
        :param kwargs: 其他参数
        :return: AI响应
        """
        if self.preferred_provider:
            try:
                service = AIServiceFactory.get_service(self.preferred_provider)
                return service.generate(prompt, **kwargs)
            except Exception as e:
                print(f"Error with preferred provider {self.preferred_provider}: {str(e)}")
        
        # 尝试所有可用的服务
        last_error = None
        for provider in AIProvider.get_priority_list():
            try:
                service = AIServiceFactory.get_service(provider)
                return service.generate(prompt, **kwargs)
            except Exception as e:
                print(f"Error with provider {provider}: {str(e)}")
                last_error = e
                continue
        
        raise RuntimeError(f"All AI services failed. Last error: {str(last_error)}") 