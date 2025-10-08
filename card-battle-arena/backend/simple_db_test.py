#!/usr/bin/env python3
"""
简单的数据库连接测试脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

try:
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    import asyncio
    print("✅ 成功导入SQLAlchemy模块")
    
    # 从环境变量获取数据库URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ 未找到DATABASE_URL环境变量")
        sys.exit(1)
    
    print(f"正在连接到数据库: {database_url}")
    
    # 创建异步引擎
    engine = create_async_engine(database_url)
    print("✅ 成功创建数据库引擎")
    
    async def test_connection():
        try:
            # 测试数据库连接
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                value = result.scalar()
                print(f"✅ 数据库连接成功，测试查询返回: {value}")
                return True
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
        finally:
            # 关闭引擎
            await engine.dispose()
    
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
    import traceback
    traceback.print_exc()
    sys.exit(1)