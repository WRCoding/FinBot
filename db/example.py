from db.services import TransactionService
from db.base import init_db
from datetime import datetime, timedelta

# 初始化数据库（创建表）
init_db()

# 创建服务实例
service = TransactionService()

# 创建交易记录
service.create({
    "amount": "1000.00",
    "publisher": "张三"
})
service.create({
    "amount": "7689.00",
    "publisher": "李四",
    "remark": "支出"
})

# 查询张三的所有交易
transactions = service.get_by_publisher("张三")
print("\n查询张三的所有交易:")
for t in transactions:
    print(f"ID: {t.id}, 金额: {t.amount}, 时间: {t.transaction_time}, 发布者: {t.publisher}")

# 查询最近24小时的交易
yesterday = datetime.utcnow() - timedelta(days=1)
recent_transactions = service.get_by_time_range(
    start_time=yesterday
)
print("\n查询最近24小时的交易:")
for t in recent_transactions:
    print(f"ID: {t.id}, 金额: {t.amount}, 时间: {t.transaction_time}, 发布者: {t.publisher}")

# 查询1000-2000元之间的交易
amount_range_transactions = service.get_by_amount_range(
    min_amount="1000.00",
    max_amount="2000.00"
)
print("\n查询1000-2000元之间的交易:")
for t in amount_range_transactions:
    print(f"ID: {t.id}, 金额: {t.amount}, 时间: {t.transaction_time}, 发布者: {t.publisher}")

# 获取最新的5条交易记录
latest_transactions = service.get_latest_transactions(limit=5)
print("\n获取最新的5条交易记录:")
for t in latest_transactions:
    print(f"ID: {t.id}, 金额: {t.amount}, 时间: {t.transaction_time}, 发布者: {t.publisher}")

# 获取张三的交易总数
count = service.get_publisher_transaction_count("张三")
print("\n获取张三的交易总数:")
print(count)