from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from openai.types.chat import ChatCompletion

from ai.core.config import AIConfig


class AIResponse:
    """AI响应的统一封装类"""
    def __init__(self, content: str, raw_response: Any = None):
        self.content = content
        self.raw_response = raw_response

class AIService(ABC):
    """AI服务的抽象基类"""
    @abstractmethod
    def chat(self, content: str, sys_prompt: str = AIConfig.get_system_prompt(), json_format: bool = True, **kwargs) -> AIResponse:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_response(self, messages) -> ChatCompletion:
        pass