import json

import anthropic
from openai.types.chat import ChatCompletion
from typing import Dict, Any, Callable, List

from ai.core.base import AIService, AIResponse
from ai.core.config import AIConfig
from config import CLAUDE
from util import date_util


class ClaudeService(AIService):

    def __init__(self):
        self.api_key = CLAUDE
        self.client = anthropic.Anthropic(base_url="https://oa.api2d.net", api_key=self.api_key)
        self.tool_callbacks = {}  # 用于存储工具回调函数

    def register_tool_callback(self, tool_name: str, callback: Callable, params: List[str]):
        """
        注册工具回调函数

        参数:
            tool_name (str): 工具名称
            callback (Callable): 回调函数
        """
        self.tool_callbacks[tool_name] = {'method': callback, 'params': params}

    def chat(self, query: str, sys_prompt: str = AIConfig.get_system_prompt(), json_format: bool = True,
             **kwargs) -> AIResponse:
        tool_list = [
            {
                "name": "get_date_transactions",
                "description": "获取指定范围内的交易数据",
                "input_schema": {
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
        ]
        print(f'query: {query}')
        # You have access to tools, but only use them when necessary. If a tool is not required, respond as normal
        messages = [{"role": "user", "content": query}]
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            tools=tool_list,
            system=sys_prompt,
            messages=messages
        )
        print(f'response: {response}')
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_use = response.content[-1]
            tool_name = tool_use.name
            tool_input = tool_use.input
            print(f'tool_name: {tool_name}, tool_input: {tool_input}')

            # 调用相应的回调函数处理工具请求
            if tool_name in self.tool_callbacks:
                func = self.tool_callbacks[tool_name]['method']
                params = self.tool_callbacks[tool_name]['params']
                p_dict = {}
                for p in params:
                    p_dict[p] = tool_input[p]
                result = func(**p_dict)
                too_response = {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": f'交易数据如下,请结合所给的数据进行分析回答: 100'
                        }
                    ]
                }
                messages.append(too_response)

                print(f'messages: {messages[1]}')
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1024,
                    tools=tool_list,
                    system=sys_prompt,
                    messages=messages
                )
            return AIResponse(content=response.content[0].text, raw_response=response)

    def is_available(self) -> bool:
        pass

    def get_response(self, messages) -> ChatCompletion:
        pass

    def get_date_transactions(self, start_time: str, end_time: str):
        print(f'start_time: {start_time}, end_time: {end_time}')
        pass

if __name__ == '__main__':
    service = ClaudeService()
    service.register_tool_callback("get_date_transactions", service.get_date_transactions,['start_time', 'end_time'])
    service.complex_chat('昨天花费了多少钱')
