from datetime import datetime
import json


from analysis import FinanceAnalyzer
from db.services import TransactionService
from config import APP_ID, APP_SECRET, WX_ID
from feishu.table import FeishuTable
from util.date_util import get_date


class MessageParser:
    def __init__(self):
        self.analyzer = FinanceAnalyzer()
        self.service = TransactionService()
        self.feishu_table = FeishuTable(APP_ID, APP_SECRET)

    def clean_text(self, text):
        """清理文本内容"""
        if text is None:
            return ""
        return text.strip()
    
    def insert_feishu(self, values):
        """向飞书表格插入数据"""
        self.feishu_table.insert_data(values)
    
    def parse_msg_xml(self, content):
        from ai.services.manager import AIManager

        """解析XML消息内容"""
        try:
            ai_manager = AIManager()
            response = ai_manager.simple_chat(content)
            data = json.loads(response.content)
            print("response:", response.content)
            if data['publisher'] and data['publisher'].endswith('银行') and data['标题'] == '交易提醒':
                data['transaction_time'] = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
                data.pop('标题')
                self.service.create(data)
                values = [[data['transaction_time'], data['type'], data['amount'], data['remark']]]
                self.insert_feishu(values)
                return data
            print("不符合条件，跳过解析。")
            return None
    
        except Exception as e:
            print(f"Error with : {str(e)}")
            return None
    
    def parse_msg_self(self, content: str):
        from finbot import FinBot
        """解析自定义消息内容"""
        data = []
        finBot = FinBot()
        # 处理AI对话
        if content.startswith('@DS'):
            self.analyzer.chat_with_ai(content)
            return
        
        # 处理命令匹配
        match content:
            # case '#全部数据':
            #     data = self.service.get_all_transactions(desc=False)
            case '#昨日数据':
                data = self.analyzer.get_date_transactions(start_time=get_date(-1))
            case '#今日数据':
                data = self.analyzer.get_date_transactions(start_time=get_date())
    
        # 处理汇总命令
        if content.startswith('#汇总@'):
            params = content.split('@')
            data = self.analyzer.get_today_summary(date_str=params[1])
            
        # 检查数据是否为空
        if not data:
            finBot.send_text_msg('没有数据')
            return
    
        # 分批发送数据
        self._send_batch_data(data, finBot)
    
    def _send_batch_data(self, data, finBot):
        """分批发送数据"""
        batch_size = 3  # 每批包含的交易数量
        start_index = 0
        
        while start_index < len(data):
            current_batch = data[start_index:start_index + batch_size]
            batch_messages = []
            
            # 获取当前批次的数据
            for transaction in current_batch:
                transaction_lines = self._format_transaction(transaction)
                batch_messages.append("\n".join(transaction_lines))
                
            msg = "\n".join(batch_messages)
            finBot.send_text_msg(msg)

            # 更新start_index以指向下一个批次的起始位置
            start_index += batch_size
    
    def _format_transaction(self, transaction):
        """格式化交易数据"""
        transaction_lines = []
        
        if type(transaction) is dict:
            if 'date' in transaction:
                transaction_lines.append(f"时间: {transaction['date']}")
            if 'type' in transaction:
                transaction_lines.append(f"类型: {transaction['type']}")
            if 'amount' in transaction:
                transaction_lines.append(f"金额：{transaction['amount']}")
            if 'income' in transaction:
                transaction_lines.append(f"收入: {transaction['income']}")
            if 'expenses' in transaction:
                transaction_lines.append(f"支出: {transaction['expenses']}")
            if 'diff' in transaction:
                transaction_lines.append(f"与前一日对比: {transaction['diff']}")
            if 'remark' in transaction:
                transaction_lines.append(f"备注: {transaction['remark']}")
        
        # 添加分隔线
        transaction_lines.append("---------------------------------")
        
        return transaction_lines


# 为了保持向后兼容，提供与原始函数相同的接口
# def clean_text(text):
#     parser = MessageParser()
#     return parser.clean_text(text)
#
# def insert_feishu(values):
#     parser = MessageParser()
#     parser.insert_feishu(values)
#
# def parse_msg_xml(content):
#     parser = MessageParser()
#     return parser.parse_msg_xml(content)
#
# def parse_msg_self(content: str, wcf: Wcf):
#     parser = MessageParser()
#     parser.parse_msg_self(content, wcf)

# if __name__ == '__main__':
#     with open('msg.xml', mode='r', encoding='utf-8') as f:
#         file_content = f.read()
#     parse_msg_xml(file_content)
