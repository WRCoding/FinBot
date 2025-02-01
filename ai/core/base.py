from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AIResponse:
    """AI响应的统一封装类"""
    def __init__(self, content: str, raw_response: Optional[Dict[str, Any]] = None):
        self.content = content
        self.raw_response = raw_response or {}

class AIService(ABC):
    """AI服务的抽象基类"""
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass 