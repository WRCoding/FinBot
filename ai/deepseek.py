from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import openai
from openai import OpenAI
import os
import json
from enum import Enum

class AIProvider(Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    
class AIResponse:
    def __init__(self, content: str, raw_response: dict = None):
        self.content = content
        self.raw_response = raw_response

class AIService(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

class OpenAIService(AIService):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}]
            )
            return AIResponse(
                content=response.choices[0].message.content,
                raw_response=response
            )
        except Exception as e:
            print(f"OpenAI service error: {str(e)}")
            raise

    def is_available(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))

class DeepseekService(AIService):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        try:
            # 这里实现Deepseek的API调用
            # 目前是示例实现，需要根据实际的Deepseek API进行修改
            return AIResponse(
                content="Deepseek response",
                raw_response={}
            )
        except Exception as e:
            print(f"Deepseek service error: {str(e)}")
            raise

    def is_available(self) -> bool:
        return bool(self.api_key)

class AIServiceFactory:
    _services: Dict[AIProvider, AIService] = {
        AIProvider.OPENAI: OpenAIService,
        AIProvider.DEEPSEEK: DeepseekService,
    }
    
    @classmethod
    def get_service(cls, provider: Optional[AIProvider] = None) -> AIService:
        if provider:
            service_class = cls._services.get(provider)
            if not service_class:
                raise ValueError(f"Unsupported AI provider: {provider}")
            return service_class()
        
        # 如果没有指定provider，按优先级尝试
        for provider in AIProvider:
            service_class = cls._services[provider]
            service = service_class()
            if service.is_available():
                return service
        
        raise RuntimeError("No available AI service found")

class AIManager:
    def __init__(self, preferred_provider: Optional[AIProvider] = None):
        self.preferred_provider = preferred_provider
        
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        if self.preferred_provider:
            try:
                service = AIServiceFactory.get_service(self.preferred_provider)
                return service.generate(prompt, **kwargs)
            except Exception as e:
                print(f"Error with preferred provider {self.preferred_provider}: {str(e)}")
        
        # 尝试所有可用的服务
        last_error = None
        for provider in AIProvider:
            try:
                service = AIServiceFactory.get_service(provider)
                return service.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                continue
        
        raise RuntimeError(f"All AI services failed. Last error: {str(last_error)}")

# 使用示例
if __name__ == "__main__":
    # 使用默认优先级
    ai_manager = AIManager()
    try:
        response = ai_manager.generate("Hello, AI!")
        print(response.content)
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # 指定特定提供商
    ai_manager = AIManager(preferred_provider=AIProvider.OPENAI)
    try:
        response = ai_manager.generate("Hello, OpenAI!")
        print(response.content)
    except Exception as e:
        print(f"Error: {str(e)}")
