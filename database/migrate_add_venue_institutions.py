"""
数据库迁移脚本 - 添加 venue 和 institutions 字段
为 ArxivPaper 表添加会议/期刊和机构信息字段
"""
import sqlite3
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


def migrate_database():
    """执行数据库迁移"""
    db_path = config.DATABASE_PATH

    print(f"开始迁移数据库: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(arxiv_papers)")
        columns = [col[1] for col in cursor.fetchall()]

        # 添加 venue 字段
        if 'venue' not in columns:
            print("添加 venue 字段...")
            cursor.execute("ALTER TABLE arxiv_papers ADD COLUMN venue VARCHAR(200)")
            print("✓ venue 字段添加成功")
        else:
            print("venue 字段已存在，跳过")

        # 添加 venue_year 字段
        if 'venue_year' not in columns:
            print("添加 venue_year 字段...")
            cursor.execute("ALTER TABLE arxiv_papers ADD COLUMN venue_year INTEGER")
            print("✓ venue_year 字段添加成功")
        else:
            print("venue_year 字段已存在，跳过")

        # 添加 institutions 字段
        if 'institutions' not in columns:
            print("添加 institutions 字段...")
            cursor.execute("ALTER TABLE arxiv_papers ADD COLUMN institutions JSON")
            print("✓ institutions 字段添加成功")
        else:
            print("institutions 字段已存在，跳过")

        conn.commit()
        print("\n✅ 数据库迁移完成！")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

    return True


if __name__ == "__main__":
    success = migrate_database()
    sys.exit(0 if success else 1)
