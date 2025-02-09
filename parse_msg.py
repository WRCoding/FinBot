from datetime import datetime
import json
import xml.etree.ElementTree as ET
import os

from dateutil import parser
from wcferry import Wcf

from ai.core.provider import AIProvider
from ai.services.manager import AIManager
from db.services import TransactionService


def clean_text(text):
    if text is None:
        return ""
    return text.strip()


def parse_msg_xml(content):
    ai_manager = AIManager()
    try:
        response = ai_manager.generate(content)
        data = json.loads(response.content)
        print("response:", response.content)
        if data['publisher'] and data['publisher'].endswith('银行') and data['标题'] == '交易提醒':
            data['transaction_time'] = datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
            data.pop('标题')
            service = TransactionService()
            service.create(data)
            return data
        print("不符合条件，跳过解析。")
        return None

    except Exception as e:
        print(f"Error with : {str(e)}")
    # 判断条件

def parse_msg_self(content, wcf: Wcf):
    service = TransactionService()
    match content:
        case '#全部数据':
            data = service.get_transactions_count_by_type()
            # 构建消息字符串
            msg = '\n'.join([
                f"类型: {t.type}, 金额: {t.amount}"
                for t in data
            ])
            wcf.send_text(msg, wcf.get_self_wxid())
        case '#昨日数据':
            data = service.get_yesterday_transactions_by_type()
            msg = '\n'.join([
                f"类型: {t['type']}, 金额: {t['total_amount']}"
                for t in data
            ])
            wcf.send_text(msg, wcf.get_self_wxid())
        case '#测试':
            with open('msg.xml', 'r') as f:
                content = f.read()
            wcf.send_xml(wcf.get_self_wxid(), content, 5)

#
# if __name__ == '__main__':
#     with open('msg.xml', mode='r', encoding='utf-8') as f:
#         file_content = f.read()
#     parse_msg_xml(file_content)
