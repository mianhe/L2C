from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试模式标志
is_testing = bool(os.getenv("TESTING"))

# 数据库URL配置
if is_testing:
    # 测试环境使用命名内存数据库以实现连接共享
    SQLALCHEMY_DATABASE_URL = "sqlite:///file:memdb?mode=memory&cache=shared&uri=true"
else:
    # 生产环境使用文件数据库
    SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=is_testing,  # 在测试模式下启用SQL日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 用于测试的会话实例
_test_db = None

Base = declarative_base()

def init_db():
    """初始化数据库表结构"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """数据库会话依赖"""
    if is_testing:
        # 测试环境使用全局测试会话
        global _test_db
        if _test_db is None:
            logger.warning("测试数据库会话未设置，创建新会话")
            _test_db = SessionLocal()
        try:
            yield _test_db
        finally:
            # 测试会话由测试框架管理，这里不关闭
            pass
    else:
        # 非测试环境，每次请求创建新会话
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

def set_test_db(db):
    """设置测试数据库会话"""
    global _test_db
    _test_db = db
    logger.info("测试数据库会话设置成功") 