from datetime import datetime, timedelta

def get_yesterday_date():
    # 获取今天的日期
    today = datetime.now()
    # 计算昨天的日期
    yesterday = today - timedelta(days=1)
    # 格式化输出
    formatted_yesterday = yesterday.strftime('%Y年%m月%d日')
    return formatted_yesterday