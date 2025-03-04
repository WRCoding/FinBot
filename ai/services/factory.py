from typing import Dict, Optional, Type
from ..core.base import AIService
from ..core.provider import AIProvider
from ..providers.deepseek_service import DeepseekService

class AIServiceFactory:
    """AI服务工厂类"""
    _services: Dict[AIProvider, Type[AIService]] = {
        AIProvider.DEEPSEEK: DeepseekService,
    }
    
    @classmethod
    def get_service(cls, provider: Optional[AIProvider] = None) -> AIService:
        """
        获取AI服务实例
        :param provider: 指定的服务提供商，如果为None则按优先级尝试
        :return: AI服务实例
        """
        if provider:
            service_class = cls._services.get(provider)
            if not service_class:
                raise ValueError(f"Unsupported AI provider: {provider}")
            return service_class()
        
        # 如果没有指定provider，按优先级尝试
        for provider in AIProvider.get_priority_list():
            service_class = cls._services[provider]
            service = service_class()
            if service.is_available():
                return service
        
        raise RuntimeError("No available AI service found") 