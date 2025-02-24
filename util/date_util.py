from datetime import datetime, timedelta

def get_date(count: int=0):
    # 获取今天的日期
    today = datetime.now()
    # 计算昨天的日期
    cal_date = today + timedelta(days=count)
    # 格式化输出
    formatted_date = cal_date.strftime('%Y年%m月%d日')
    return formatted_date