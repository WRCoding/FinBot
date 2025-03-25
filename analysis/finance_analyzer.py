from typing import List

import pandas as pd
import os
import re

from config import APP_SECRET, APP_ID
from feishu.table import FeishuTable
from util import date_util


class FinanceAnalyzer:
    """财务数据分析类，用于读取和分析账本CSV数据"""
    
    def __init__(self, file_path=None):
        """
        初始化财务分析器
        
        参数:
            file_path (str, optional): CSV文件路径
        """
        # 设置pandas显示选项，显示所有行和列
        pd.set_option('display.max_rows', None)  # 显示所有行
        pd.set_option('display.max_columns', None)  # 显示所有列
        pd.set_option('display.width', None)  # 设置显示宽度为无限制
        pd.set_option('display.max_colwidth', None)  # 设置列宽为无限制
        self.df = None
        if file_path:
            self.load_data(file_path)
        else:
            self.table = FeishuTable(APP_ID, APP_SECRET)
            self.load_data(self.table.get_file_path())
    def load_data(self, file_path):
        """
        从CSV文件加载数据
        
        参数:
            file_path (str): CSV文件路径
        
        返回:
            pandas.DataFrame: 加载的数据
        """
        if not os.path.exists(file_path):
            self.table.export_table()
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取CSV文件
        self.df = pd.read_csv(file_path, encoding='utf-8')
        
        # 清理数据
        self._clean_data()
        
        return self.df
    
    def _clean_data(self):
        """清理和转换数据"""
        if self.df is None:
            return
        
        # 删除空列
        self.df = self.df.iloc[:, :4]  # 只保留前4列
        
        # 重命名列
        self.df.columns = ['时间', '类型', '金额', '备注']
        
        # 转换时间列为日期时间格式,%Y年%m月%d日 %H:%M:%S
        self.df['时间'] = pd.to_datetime(self.df['时间'], format='%Y年%m月%d日 %H:%M:%S')
        
        # 转换金额为数值类型
        self.df['金额'] = pd.to_numeric(self.df['金额'])
        
        # 提取备注中的商家信息

    def get_today_summary(self, date_str: str = None) -> List[dict]:
        """
        获取指定日期的收支情况和与前一天的支出差值
        
        参数:
            date_str (str, optional): 指定日期，格式为'YYYYMMDD'，例如'20250301'。如果不指定，则使用昨天的日期。
        
        返回:
            List[dict]: 包含指定日期收支信息的字典列表
        """
        if self.df is None:
            return []
        
        # 处理日期
        if date_str:
            try:
                target_date = pd.to_datetime(date_str, format='%Y%m%d').date()
            except ValueError:
                return [{"error": "日期格式错误，请使用'YYYYMMDD'格式，例如'20250301'"}]
        else:
            target_date = pd.Timestamp.now().date() - pd.Timedelta(days=1)
        
        previous_date = target_date - pd.Timedelta(days=1)
        
        # 添加日期列
        self.df['日期'] = self.df['时间'].dt.date
        
        # 获取目标日期的数据
        target_data = self.df[self.df['日期'] == target_date]
        target_income = round(target_data[target_data['类型'] == '收入']['金额'].sum(), 2)
        target_expense = round(target_data[target_data['类型'] == '支出']['金额'].sum(), 2)
        
        # 获取前一天的数据
        previous_data = self.df[self.df['日期'] == previous_date]
        previous_expense = round(previous_data[previous_data['类型'] == '支出']['金额'].sum(), 2)
        
        # 计算支出差值
        expense_diff = round(target_expense - previous_expense, 2)
        
        return [{
            "income": f"{target_income:.2f}",
            "expenses": f"{target_expense:.2f}",
            "diff": f'多支出{expense_diff:.2f}' if expense_diff > 0 else f'少支出{abs(expense_diff):.2f}',
            "date": target_date.strftime('%Y-%m-%d')
        }]
    
    def get_date_transactions(self, start_time: str = None, end_time: str = None) -> List[dict]:
        """
        获取指定日期范围内的所有交易数据
        
        参数:
            start_time (str, optional): 开始日期，格式为'YYYYMMDD'，例如'20250301'。如果不指定，则使用当天的日期。
            end_time (str, optional): 结束日期，格式为'YYYYMMDD'，例如'20250305'。如果不指定，则只查询开始日期的数据。
        
        返回:
            List[dict]: 包含指定日期范围内所有交易记录的字典列表
        """
        if self.df is None:
            return []
        
        # 确保日期列存在
        if '日期' not in self.df.columns:
            self.df['日期'] = self.df['时间'].dt.date
        
        # 处理开始日期
        if start_time:
            try:
                start_date = pd.to_datetime(start_time, format='%Y%m%d').date()
            except ValueError:
                return [{"error": "开始日期格式错误，请使用'YYYYMMDD'格式，例如'20250301'"}]
        else:
            start_date = pd.Timestamp.now().date()
        
        # 处理结束日期
        if end_time:
            try:
                end_date = pd.to_datetime(end_time, format='%Y%m%d').date()
                if end_date < start_date:
                    return [{"error": "结束日期不能早于开始日期"}]
            except ValueError:
                return [{"error": "结束日期格式错误，请使用'YYYYMMDD'格式，例如'20250305'"}]
            
            # 获取日期范围内的数据
            target_data = self.df[(self.df['日期'] >= start_date) & (self.df['日期'] <= end_date)]
        else:
            # 如果没有指定结束日期，则只查询开始日期的数据
            target_data = self.df[self.df['日期'] == start_date]
        
        # 如果没有数据，返回空列表
        if target_data.empty:
            return []
        
        # 按时间排序（从早到晚）
        target_data = target_data.sort_values(by='时间')
        
        # 将数据转换为字典列表
        transactions = []
        for _, row in target_data.iterrows():
            transactions.append({
                "date": row['时间'],
                "type": row['类型'],
                "amount": f"{row['金额']:.2f}",
                "remark": row['备注'] if '备注' in row else ""
            })
        
        return transactions

    def chat_with_ai(self, question: str):
        from ai.services.manager import AIManager
        from ai.providers.claude_service import ClaudeService
        from finbot import FinBot

        robot = FinBot()
        
        # 实例化Claude服务
        claude_service = ClaudeService()
        
        # 注册工具回调函数
        claude_service.register_tool_callback("get_date_transactions", self.get_date_transactions, ['start_time', 'end_time'])
        sys_prompt = f'''
        你是一名智能数据分析助理,能够根据用户的交易数据来回答用户的问题。
                            1.今天的日期是: {date_util.get_date(format='%Y-%m-%d')}
                            2.涉及到金额计算的,你应该多次验证,避免计算出错
                            3.同时规定每周一为一个星期的开始,每周日为一个星期的结束
                            4.你可以通过tools来获取记账数据
                            5.最后结果不需要把每条数据都罗列出来
                            6.仅服务于交易数据的分析查询，不回应其他无关问题
        '''

        
        # 使用complex_chat方法进行对话，该方法支持工具调用
        response = claude_service.chat(query=question, sys_prompt=sys_prompt)
        print(response)
        # 发送响应
        robot.send_text_msg(response.content)

if __name__ == '__main__':
    a = FinanceAnalyzer()
    a.chat_with_ai("DS 前两天花费了多少钱")