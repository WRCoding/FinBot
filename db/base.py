from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import os

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 数据库文件路径
DB_FILE = os.path.join(BASE_DIR, 'data.db')
DATABASE_URL = f"sqlite:///{DB_FILE}"

def ensure_db_file_exists():
    """确保数据库文件存在"""
    db_dir = os.path.dirname(DB_FILE)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    if not os.path.exists(DB_FILE):
        # 创建空的数据库文件
        open(DB_FILE, 'a').close()
        print(f"数据库文件已创建: {DB_FILE}")

# 确保数据库文件存在
ensure_db_file_exists()

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # 允许多线程访问
    echo=False  # 设置为True可以看到SQL语句
)

# 创建declarative基类
Base = declarative_base()

def init_db():
    """初始化数据库（创建所有表）"""
    Base.metadata.create_all(bind=engine)
    print("数据库表已初始化") 