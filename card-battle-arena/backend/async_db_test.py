#!/usr/bin/env python3
"""
异步数据库连接测试脚本
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

async def test_async_connection():
    try:
        # 从环境变量获取数据库URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ 未找到DATABASE_URL环境变量")
            return False
        
        print(f"正在连接到数据库: {database_url}")
        
        # 导入异步数据库模块
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # 创建异步引擎
        engine = create_async_engine(database_url)
        print("✅ 成功创建数据库引擎")
        
        # 测试数据库连接
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            print(f"✅ 数据库连接成功，测试查询返回: {value}")
            
        # 关闭引擎
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("正在测试异步数据库连接...")
    try:
        result = asyncio.run(test_async_connection())
        if result:
            print("🎉 异步数据库连接测试通过!")
        else:
            print("💥 异步数据库连接测试失败!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)