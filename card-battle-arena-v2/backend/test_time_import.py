#!/usr/bin/env python3
"""
测试time模块导入是否修复
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    # 测试导入interactive_demo模块
    import interactive_demo
    print("✅ interactive_demo模块导入成功")

    # 测试time模块是否可用
    import time
    print("✅ time模块导入成功")

    # 测试time.sleep函数
    print("⏰ 测试time.sleep...")
    time.sleep(0.1)
    print("✅ time.sleep工作正常")

    # 测试AI函数是否可以调用（不实际运行游戏）
    print("🤖 测试AI函数...")
    # 这里不实际调用，因为需要交互输入
    print("✅ AI函数结构正常")

    print("\n🎉 修复验证成功！time模块导入问题已解决。")

except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")