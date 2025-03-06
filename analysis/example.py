#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
财务分析工具示例脚本
"""

import os
import sys

from ai.core.provider import AIProvider
from ai.services.manager import AIManager
from finance_analyzer import FinanceAnalyzer
from util import date_util
from util.date_util import get_date


def main():
    # 获取当前脚本所在目录
    # 获取项目根目录
    # CSV文件路径

    # 创建分析器实例
    analyzer = FinanceAnalyzer()
    print(analyzer.get_date_transactions(get_date(-1)))
    # user_content = f'''
    # 以下为记账数据 \n
    # {analyzer.df}\n
    # 问题: 昨天比前天花费的多还是少? 如果多是多花费了多少钱，少又是少了多少钱
    # '''
    # print(user_content)
    # sys_prompt = f'''
    # 你是一名智能数据分析助理,能够根据用户的记账数据内容来回答用户的问题。
    #                     1.今天的日期是: {date_util.get_date()}
    #                     2.涉及到金额计算的,你应该多次验证,避免计算出错
    # '''
    # ai_manager = AIManager(preferred_provider=AIProvider.DEEPSEEK)
    # try:
    #     response = ai_manager.simple_chat(prompt=user_content, sys_prompt=sys_prompt, json_format=False)
    #     print("OpenAI response:", response.content)
    # except Exception as e:
    #     print(f"Error with OpenAI: {str(e)}")
    # # 打印摘要信息
    # summary = analyzer.get_summary()
    # print("=== 账本摘要 ===")
    # for key, value in summary.items():
    #     print(f"{key}: {value}")
    # print()
    #
    # # 打印每日摘要
    # daily_summary = analyzer.get_daily_summary()
    # print("=== 每日摘要 ===")
    # print(daily_summary.tail())
    # print()
    #
    #
    # # 打印分类摘要
    # category_summary = analyzer.get_category_summary()
    # print("=== 消费分类摘要 ===")
    # print(category_summary)
    # print()


if __name__ == "__main__":
    main() 