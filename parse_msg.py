from datetime import datetime
import json

from wcferry import Wcf, WxMsg

from ai.services.manager import AIManager
from analysis import FinanceAnalyzer
from db.services import TransactionService
from config import APP_ID, APP_SECRET, WX_ID
from feishu.table import FeishuTable
from util.common_util import find_project_root
from util.date_util import get_date


def clean_text(text):
    if text is None:
        return ""
    return text.strip()


def insert_feishu(values):
    table_sender = FeishuTable(APP_ID, APP_SECRET)
    table_sender.insert_data(values)

def parse_video_msg(msg: WxMsg, wcf: Wcf):
    print(wcf.get_audio_msg(id=msg.id, dir=f'{find_project_root()}/'))
    pass

def parse_msg_xml(content):
    ai_manager = AIManager()
    try:
        response = ai_manager.simple_chat(content)
        data = json.loads(response.content)
        print("response:", response.content)
        if data['publisher'] and data['publisher'].endswith('银行') and data['标题'] == '交易提醒':
            data['transaction_time'] = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            data.pop('标题')
            service = TransactionService()
            service.create(data)
            values = [[data['transaction_time'], data['type'], data['amount'], data['remark']]]
            insert_feishu(values)
            return data
        print("不符合条件，跳过解析。")
        return None

    except Exception as e:
        print(f"Error with : {str(e)}")
    # 判断条件


def parse_msg_self(content: str, wcf: Wcf):
    analyzer = FinanceAnalyzer()
    data = []
    if content.startswith('@DS'):
        analyzer.chat_with_ai(content)
        return
    match content:
        # case '#全部数据':
        #     data = service.get_all_transactions(desc=False)
        case '#昨日数据':
            data = analyzer.get_date_transactions(date_str=get_date(-1))
        case '#今日数据':
            data = analyzer.get_date_transactions(date_str=get_date())

    if content.startswith('#汇总@'):
        params = content.split('@')
        data = analyzer.get_today_summary(date_str=params[1])
    if not data:
        wcf.send_text('没有数据', WX_ID)
        return

    batch_size = 3  # 每批包含的交易数量
    start_index = 0
    while start_index < len(data):
        current_batch = data[start_index:start_index + batch_size]
        batch_messages = []
        # 获取当前批次的数据
        for transaction in current_batch:
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
            # else:
            #     # 动态添加各字段信息
            #     if hasattr(transaction, 'type') and transaction.type:
            #         transaction_lines.append(f"类型: {transaction.type}")
            #     if hasattr(transaction, 'amount') and transaction.amount:
            #         transaction_lines.append(f"金额: {transaction.amount}")
            #     if hasattr(transaction, 'transaction_time') and transaction.transaction_time:
            #         transaction_lines.append(f"时间: {transaction.transaction_time}")
            #     if hasattr(transaction, 'remark') and transaction.remark:
            #         transaction_lines.append(f"备注: {transaction.remark}")

            # 添加分隔线
            transaction_lines.append("---------------------------------")

            batch_messages.append("\n".join(transaction_lines))
        msg = "\n".join(batch_messages)
        wcf.send_text(msg, WX_ID)
        # 更新start_index以指向下一个批次的起始位置
        start_index += batch_size
#
# if __name__ == '__main__':
#     with open('msg.xml', mode='r', encoding='utf-8') as f:
#         file_content = f.read()
#     parse_msg_xml(file_content)
