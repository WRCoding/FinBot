from parse_msg import parse_msg_self
from util.date_util import get_date

date = get_date(count=-1, format='%Y%m%d')
content = f'#汇总@{date}'
parse_msg_self(content, None)