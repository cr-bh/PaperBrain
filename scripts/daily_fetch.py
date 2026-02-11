#!/usr/bin/env python3
"""
Auto-Scholar 定时抓取脚本
可通过 cron job 或任务计划程序定时执行

使用方法:
  python scripts/daily_fetch.py

定时配置示例 (Linux/Mac cron):
  # 每天早上 8 点执行
  0 8 * * * cd /path/to/paperbrain && python scripts/daily_fetch.py >> logs/daily_fetch.log 2>&1

定时配置示例 (Windows 任务计划程序):
  1. 打开"任务计划程序"
  2. 创建基本任务
  3. 触发器: 每天早上 8:00
  4. 操作: 启动程序
     - 程序: python
     - 参数: scripts/daily_fetch.py
     - 起始于: C:\\path\\to\\paperbrain
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.scheduler import daily_scheduler
from services.report_generator import report_generator
from database.db_manager import db_manager
from datetime import datetime


def main():
    """主函数"""
    print(f"\n{'='*70}")
    print(f"Auto-Scholar 定时任务")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")

    try:
        # 执行流水线
        daily_scheduler.run_daily_pipeline(max_results=200)

        # 生成报告
        print("\n📄 生成 HTML 报告...")
        yesterday = datetime.now()
        papers = db_manager.get_arxiv_papers_by_date(yesterday, min_score=5.0)

        if papers:
            report_path = report_generator.generate_daily_report(papers, yesterday)
            print(f"✓ 报告已生成: {report_path}")
        else:
            print("⚠️  没有符合条件的论文，跳过报告生成")

        print(f"\n{'='*70}")
        print("✅ 定时任务执行成功")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n❌ 定时任务执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
