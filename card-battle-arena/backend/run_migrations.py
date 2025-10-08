#!/usr/bin/env python3
"""
运行数据库迁移的脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def run_migrations():
    try:
        # 导入alembic模块
        from alembic.config import Config
        from alembic import command
        
        # 创建alembic配置
        alembic_cfg = Config("alembic.ini")
        
        # 运行迁移
        print("正在运行数据库迁移...")
        command.upgrade(alembic_cfg, "head")
        print("✅ 数据库迁移完成!")
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = run_migrations()
    if not result:
        sys.exit(1)