from config import DEEP_SEEK
from ..core.base import AIService, AIResponse
from ..core.config import AIConfig
from openai import OpenAI


class DeepseekService(AIService):
    """Deepseek服务实现"""

    def __init__(self):
        self.api_key = DEEP_SEEK
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def generate(self, prompt: str, **kwargs) -> AIResponse:
        if not self.is_available():
            raise RuntimeError("Deepseek API key not found")

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": AIConfig.get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
                temperature=0.7,
                stream=False,
                response_format={
                    'type': 'json_object'
                }
            )
            # TODO: 实现Deepseek的API调用
            # 这里需要根据实际的Deepseek API文档实现
            return AIResponse(
                content=response.choices[0].message.content
            )
        except Exception as e:
            print(f"Deepseek service error: {str(e)}")
            raise

    def is_available(self) -> bool:
        return bool(self.api_key)
