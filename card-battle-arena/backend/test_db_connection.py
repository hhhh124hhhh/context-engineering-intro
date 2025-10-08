#!/usr/bin/env python3
"""
测试数据库连接的脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.database.postgres import AsyncSessionLocal, engine
    from sqlalchemy import text
    print("✅ 成功导入数据库模块")
    
    async def test_connection():
        try:
            # 测试数据库连接
            async with AsyncSessionLocal() as session:
                result = await session.execute(text("SELECT 1"))
                value = result.scalar()
                print(f"✅ 数据库连接成功，测试查询返回: {value}")
                return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    if __name__ == "__main__":
        print("正在测试数据库连接...")
        result = asyncio.run(test_connection())
        if result:
            print("🎉 数据库连接测试通过!")
        else:
            print("💥 数据库连接测试失败!")
            sys.exit(1)
            
except Exception as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)