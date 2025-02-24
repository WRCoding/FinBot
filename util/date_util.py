from datetime import datetime, timedelta

def get_date(count: int=0, format: str='%Y年%m月%d日') -> str:
    # 获取今天的日期
    today = datetime.now()
    # 计算昨天的日期
    cal_date = today + timedelta(days=count)
    # 格式化输出
    formatted_date = cal_date.strftime(format)
    return formatted_date

def convert_date_format(date_str):
    # 将字符串解析为datetime对象，假设输入格式固定为YYYYMMDD
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    # 格式化datetime对象为所需的字符串格式
    formatted_date = date_obj.strftime('%Y年%m月%d日')
    return formatted_date