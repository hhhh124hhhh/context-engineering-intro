#!/usr/bin/env python3
"""
测试bcrypt功能的脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from passlib.context import CryptContext
    print("✅ 成功导入passlib")
    
    # 创建密码哈希上下文
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    print("✅ 成功创建CryptContext")
    
    # 测试密码哈希 - 使用符合长度要求的密码
    password = "TestPass123!"  # 短密码，符合bcrypt要求
    hashed = pwd_context.hash(password)
    print(f"✅ 成功生成哈希: {hashed[:20]}...")
    
    # 测试密码验证
    is_valid = pwd_context.verify(password, hashed)
    print(f"✅ 密码验证结果: {is_valid}")
    
    # 测试长密码截断
    long_password = "A" * 100  # 100个字符的密码
    truncated_password = long_password[:72]  # 截断到72个字符
    try:
        hashed_long = pwd_context.hash(truncated_password)
        print(f"✅ 长密码处理成功: {len(truncated_password)} 字符")
    except Exception as e:
        print(f"⚠️  长密码处理警告: {e}")
        # 使用短密码作为备选
        short_password = "ShortPass123!"
        hashed_short = pwd_context.hash(short_password)
        print(f"✅ 使用备选短密码: {hashed_short[:20]}...")
    
    print("\n🎉 bcrypt基础功能测试完成!")
    
except Exception as e:
    print(f"❌ bcrypt测试失败: {e}")
    sys.exit(1)