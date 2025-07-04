#!/usr/bin/env python3
"""
日志清理脚本
可以手动运行或通过cron定期执行
"""

import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.log_manager import LogManager
import logging

# 配置简单的日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """主函数"""
    log_manager = LogManager()
    
    print("🧹 开始日志清理...")
    
    # 获取当前状态
    print("\n📊 当前状态:")
    stats = log_manager.get_log_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 执行维护
    print("\n🔧 执行维护...")
    result = log_manager.run_maintenance(archive_days=7, cleanup_days=90)
    
    if result["error"]:
        print(f"❌ 维护失败: {result['error']}")
        return 1
    else:
        print("✅ 维护完成:")
        print(f"  📦 归档: {result['archived']} 个文件")
        print(f"  🗑️ 清理: {result['cleaned']} 个文件")
    
    # 获取维护后状态
    print("\n📊 维护后状态:")
    stats_after = log_manager.get_log_stats()
    for key, value in stats_after.items():
        print(f"  {key}: {value}")
    
    print("\n🎉 日志清理完成!")
    return 0

if __name__ == "__main__":
    exit(main())
