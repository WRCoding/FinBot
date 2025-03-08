from pyexpat.errors import messages

from openai.types.chat import ChatCompletion

from config import DEEP_SEEK
from ..core.base import AIService, AIResponse
from ..core.config import AIConfig
from openai import OpenAI, NotGiven


class DeepseekService(AIService):
    """Deepseek服务实现"""

    def get_response(self, messages, json_format: bool=True) -> ChatCompletion:
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=1024,
                temperature=1.0,
                stream=False,
                response_format={
                    'type': 'json_object'
                } if json_format else NotGiven,
            )
            # TODO: 实现Deepseek的API调用
            # 这里需要根据实际的Deepseek API文档实现
            return response
        except Exception as e:
            print(f"Deepseek service error: {str(e)}")
            raise
        pass

    def __init__(self):
        self.api_key = DEEP_SEEK
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def simple_chat(self, content: str, sys_prompt: str = AIConfig.get_system_prompt(),
                    json_format: bool=True,  **kwargs) -> AIResponse:
        if not self.is_available():
            raise RuntimeError("Deepseek API key not found")

        msg = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": content},
        ]
        response = self.get_response(msg, json_format=json_format)
        return AIResponse(
            content=response.choices[0].message.content
        )

    def is_available(self) -> bool:
        return bool(self.api_key)
