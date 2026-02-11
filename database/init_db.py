"""
数据库初始化脚本
运行此脚本以创建数据库表
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import DatabaseManager
import config


def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")

    db_manager = DatabaseManager(config.DATABASE_PATH)
    db_manager.create_tables()

    print(f"数据库初始化完成！数据库路径: {config.DATABASE_PATH}")
    print("所有表已创建成功。")


if __name__ == "__main__":
    init_database()
