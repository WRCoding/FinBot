import json
from typing import List, Callable

from openai import OpenAI
from openai.types.chat import ChatCompletion

from config import DEEP_SEEK
from ..core.base import AIService, AIResponse
from ..core.config import AIConfig


class DeepseekService(AIService):
    """Deepseek服务实现"""

    def get_response(self, messages, json_format: bool=True, tools: List=None) -> ChatCompletion:
        try:
            params = {
                "model": "deepseek-chat",
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 1.0,
                "stream": False,
            }
            
            if json_format:
                params["response_format"] = {"type": "json_object"}
            if tools:
                params["tools"] = tools
            
            response = self.client.chat.completions.create(**params)
            return response
        except Exception as e:
            print(f"Deepseek service error: {str(e)}")
            raise
        pass

    def __init__(self):
        self.api_key = DEEP_SEEK
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        self.tool_callbacks = {}  # 用于存储工具回调函数

    def register_tool_callback(self, tool_name: str, callback: Callable, params: List[str]):
        """
        注册工具回调函数

        参数:
            tool_name (str): 工具名称
            callback (Callable): 回调函数
        """
        self.tool_callbacks[tool_name] = {'method': callback, 'params': params}

    def chat(self, query: str, sys_prompt: str = AIConfig.get_system_prompt(),
             json_format: bool=True,tools: List=None,  **kwargs) -> AIResponse:
        if not self.is_available():
            raise RuntimeError("Deepseek API key not found")
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_date_transactions",
                    "description": "获取指定范围内的交易数据",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_time": {
                                "type": "string",
                                "description": "范围的起始时间,时间格式转换为YYYYmmdd 例如20250301",
                            },
                            "end_time": {
                                "type": "string",
                                "description": "范围的终止时间,时间格式转换为YYYYmmdd 例如20250310",
                            }
                        },
                        "required": ["start_time", "end_time"],
                    },
                }
            }
        ]
        msg = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": query},
        ]
        response = self.get_response(msg, json_format=json_format, tools=tools)
        msg.append(response.choices[0].message)
        if response.choices[0].finish_reason == 'tool_calls':
            tool_call = response.choices[0].message.tool_calls[0]
            tool_id = tool_call.id
            method = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f'tool_name: {method}, tool_input: {arguments}')
            func = self.tool_callbacks[method]['method']
            params = self.tool_callbacks[method]['params']
            p_dict = {}
            for param in params:
                p_dict[param] = arguments[param]
            result = func(**p_dict)
            tool_resp = {
                "role": "tool",
                "tool_call_id": tool_id,
                "content": f'交易数据如下,请结合所给的数据进行分析回答: {result}'
            }
            msg.append(tool_resp)
            response = self.get_response(msg, json_format=json_format, tools=tools)

        return AIResponse(
            content=response.choices[0].message.content
        )

    def is_available(self) -> bool:
        return bool(self.api_key)
