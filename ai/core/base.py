from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from openai.types.chat import ChatCompletion

from ai.core.config import AIConfig


class AIResponse:
    """AI响应的统一封装类"""
    def __init__(self, content: str, raw_response: Optional[Dict[str, Any]] = None):
        self.content = content
        self.raw_response = raw_response or {}

class AIService(ABC):
    """AI服务的抽象基类"""
    @abstractmethod
    def simple_chat(self, prompt: str, sys_prompt: str = AIConfig.get_system_prompt(), json_format: bool = True, **kwargs) -> AIResponse:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_response(self, messages) -> ChatCompletion:
        pass