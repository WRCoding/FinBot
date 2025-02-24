from abc import ABC, abstractmethod
from typing import Dict
from db.services import TransactionService
from feishu.message import FeishuMessageSender
from util.date_util import get_date
class MessageHandler(ABC):
    def __init__(self, service: TransactionService, msg_sender: FeishuMessageSender):
        self.service = service
        self.msg_sender = msg_sender
    
    @abstractmethod
    def handle(self, open_id: str, **kwargs) -> None:
        pass

class AllTransactionsHandler(MessageHandler):
    def handle(self, open_id: str, **kwargs) -> None:
        transactions = self.service.get_all_transactions()
        template = self.service.transfer_template(transactions)
        self.msg_sender.send_message(open_id, 'interactive', template.to_json())

class YesterdayTransactionsHandler(MessageHandler):
    def handle(self, open_id: str, **kwargs) -> None:
        transactions = self.service.get_transactions_by_date(get_date(-1))
        template = self.service.transfer_template(transactions)
        self.msg_sender.send_message(open_id, 'interactive', template.to_json())

class TodayTransactionsHandler(MessageHandler):
    def handle(self, open_id: str, **kwargs) -> None:
        transactions = self.service.get_transactions_by_date(get_date())
        template = self.service.transfer_template(transactions)
        self.msg_sender.send_message(open_id, 'interactive', template.to_json())

class DateRangeTransactionsHandler(MessageHandler):
    def handle(self, open_id: str, **kwargs) -> None:
        transactions = self.service.get_transactions_by_date(kwargs['start_date'], kwargs['end_date'])
        template = self.service.transfer_template(transactions)
        self.msg_sender.send_message(open_id, 'interactive', template.to_json())

class MessageHandlerFactory:
    _handlers: Dict[str, type[MessageHandler]] = {
        'all': AllTransactionsHandler,
        'yesterday': YesterdayTransactionsHandler,
        'today': TodayTransactionsHandler,
        'date_range': DateRangeTransactionsHandler
    }

    @classmethod
    def get_handler(cls, key: str, service: TransactionService, msg_sender: FeishuMessageSender) -> MessageHandler:
        handler_class = cls._handlers.get(key)
        if not handler_class:
            raise ValueError(f'未知的操作类型: {key}')
        return handler_class(service, msg_sender) 