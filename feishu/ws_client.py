import lark_oapi as lark
import threading
from lark_oapi.api.application.v6 import P2ApplicationBotMenuV6


from feishu.config import APP_ID, APP_SECRET



## P2ImMessageReceiveV1 为接收消息 v2.0；CustomizedEvent 内的 message 为接收消息 v1.0。
def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    open_id = data.event.sender.sender_id.open_id
    print(
        f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data.event.sender.sender_id.open_id, indent=4)}')

#
def do_message_event(data: P2ApplicationBotMenuV6) -> None:
    # print(f'[ do_customized_event access ], type: message, data: {lark.JSON.marshal(data.event, indent=4)}')
    from db.services import TransactionService
    from feishu.message import FeishuMessageSender
    service = TransactionService()
    template =service.get_transactions_for_template()
    msg_sender = FeishuMessageSender(APP_ID, APP_SECRET)
    resp = msg_sender.send_message(data.event.operator.operator_id.open_id, 'interactive', template.to_json())
    print(resp)


event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p2_application_bot_menu_v6(do_message_event) \
    .build()


def _ws_client_thread():
    cli = lark.ws.Client(APP_ID, APP_SECRET,
                         event_handler=event_handler,
                         log_level=lark.LogLevel.INFO)
    cli.start()


def start():
    ws_thread = threading.Thread(target=_ws_client_thread, name="feishu_ws_client")
    ws_thread.daemon = True  # 设置为守护线程，这样主程序退出时，WebSocket 客户端也会退出
    ws_thread.start()
    return ws_thread  # 返回线程对象，方便调用方管理线程