from datetime import datetime
import json

from ai.providers.deepseek_service import DeepseekService
from analysis import FinanceAnalyzer
from db.services import TransactionService
from config import APP_ID, APP_SECRET, WX_ID
from entity.web_msg import WebMsg
from feishu.table import FeishuTable
from util.date_util import get_date


class MessageParser:
    # 单例实例
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageParser, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.analyzer = FinanceAnalyzer()
            self.service = TransactionService()
            self.feishu_table = FeishuTable(APP_ID, APP_SECRET)
            self.initialized = True

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
            with open('./msg.xml', 'a+', encoding='utf-8') as f:
                f.write(content + '\n')
            ai_manager = AIManager()
            response = ai_manager.simple_chat(content)
            data = json.loads(response.content)
            # print("response:", response.content)
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

    def parse_msg_web(self, web_msg: WebMsg):
        print(f'remark: {web_msg.remark}, msg: {web_msg.msg}')
        content = web_msg.msg
        if web_msg.remark and ',' in web_msg.remark:
            trans_type = web_msg.remark.split(',')[0]
            content = f'[交易类型:{trans_type}]:{web_msg.msg}'
        ds = DeepseekService()
        sys_prompt = '''
            用户将提供给你一段内容，请你分析内容，并提取其中的关键信息，以 JSON 的形式输出，输出的 JSON 需遵守以下的格式：
                {       
                  "amount": <金额>,
                  "transaction_time": <时间>,
                  "type": <交易类型>,
                  "remark": <备注>
                }
            '''
        response = ds.chat(query=content, sys_prompt=sys_prompt)
        data = json.loads(response.content)
        print("response:", response.content)
        # values = [[data['transaction_time'], data['type'], data['amount'], data['remark']]]
        # self.service.create(data)
        # self.insert_feishu(values)

    def parse_msg_self(self, content: str):
        if content.startswith('#') is False and content.startswith('@AI') is False:
            return
        from finbot import FinBot
        """解析自定义消息内容"""
        data = []
        finBot = FinBot()
        # 处理AI对话
        if content.startswith('@AI'):
            self.analyzer.chat_with_ai(content.split(" ")[1])
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

# if __name__ == '__main__':
#     with open('msg.xml', mode='a+', encoding='utf-8') as f:
#         f.write('\n' + 'dddddd')
