from typing import List

import pandas as pd
import os
import re

from config import APP_SECRET, APP_ID
from feishu.table import FeishuTable


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
    
    def get_date_transactions(self, date_str: str = None) -> List[dict]:
        """
        获取指定日期的所有交易数据
        
        参数:
            date_str (str, optional): 指定日期，格式为'YYYYMMDD'，例如'20250301'。如果不指定，则使用昨天的日期。
        
        返回:
            List[dict]: 包含指定日期所有交易记录的字典列表
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
            target_date = pd.Timestamp.now().date()
        
        # 确保日期列存在
        if '日期' not in self.df.columns:
            self.df['日期'] = self.df['时间'].dt.date
        
        # 获取目标日期的数据
        target_data = self.df[self.df['日期'] == target_date]
        
        # 如果没有数据，返回空列表
        if target_data.empty:
            return []
        
        # 按时间排序（从早到晚）
        target_data = target_data.sort_values(by='时间')
        
        # 将数据转换为字典列表
        transactions = []
        for _, row in target_data.iterrows():
            transactions.append({
                "date": row['时间'].strftime('%H:%M:%S'),
                "type": row['类型'],
                "amount": f"{row['金额']:.2f}",
                "remark": row['备注'] if '备注' in row else ""
            })
        
        return transactions
