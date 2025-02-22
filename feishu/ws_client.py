import lark_oapi as lark
from lark_oapi.api.application.v6 import P2ApplicationBotMenuV6

from feishu.config import APP_ID, APP_SECRET


## P2ImMessageReceiveV1 为接收消息 v2.0；CustomizedEvent 内的 message 为接收消息 v1.0。
def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    open_id = data.event.sender.sender_id.open_id
    print(
        f'[ do_p2_im_message_receive_v1 access ], data: {lark.JSON.marshal(data.event.sender.sender_id.open_id, indent=4)}')


def do_message_event(data: P2ApplicationBotMenuV6) -> None:
    print(f'[ do_customized_event access ], type: message, data: {lark.JSON.marshal(data.event, indent=4)}')


event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p2_application_bot_menu_v6(do_message_event) \
    .build()


def start():
    cli = lark.ws.Client(APP_ID, APP_SECRET,
                         event_handler=event_handler,
                         log_level=lark.LogLevel.DEBUG)
    cli.start()

if __name__ == '__main__':
    start()