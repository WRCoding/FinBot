from openai import OpenAI

from config import OPEN_AI
from ..core.base import AIService, AIResponse
from ..core.config import AIConfig


class OpenAIService(AIService):
    """OpenAI服务实现"""

    def __init__(self):
        self.api_key = OPEN_AI
        if self.is_available():
            self.client = OpenAI(api_key=self.api_key, base_url='https://openai.api2d.net/v1')

    def generate(self, prompt: str, **kwargs) -> AIResponse:
        if not self.is_available():
            raise RuntimeError("OpenAI API key not found")

        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", "gpt-4o-mini"),
                messages=[{"role": "system", "content": AIConfig.get_system_prompt()},
                          {"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return AIResponse(
                content=response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI service error: {str(e)}")
            raise

    def is_available(self) -> bool:
        return bool(self.api_key)
