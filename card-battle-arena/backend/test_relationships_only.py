#!/usr/bin/env python3
"""
仅测试SQLAlchemy关系定义的语法正确性
不依赖于完整的数据库环境
"""

import sys
import ast
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_relationship_definitions():
    """测试关系定义的语法正确性"""

    print("🔍 测试SQLAlchemy关系定义修复...")

    try:
        # 读取user.py文件内容
        user_file = project_root / "app" / "models" / "user.py"
        with open(user_file, 'r', encoding='utf-8') as f:
            user_content = f.read()

        # 读取game.py文件内容
        game_file = project_root / "app" / "models" / "game.py"
        with open(game_file, 'r', encoding='utf-8') as f:
            game_content = f.read()

        # 检查关键的关系定义修复
        checks = [
            # User模型中的关系定义修复
            ('sent_friendships修复', 'sent_friendships = relationship("Friendship", foreign_keys="[Friendship.sender_id]"'),
            ('received_friendships修复', 'received_friendships = relationship("Friendship", foreign_keys="[Friendship.receiver_id]"'),
            ('chat_messages修复', 'chat_messages = relationship("ChatMessage", foreign_keys="[ChatMessage.sender_id]"'),

            # ChatMessage模型中的关系定义修复
            ('sender关系修复', 'sender = relationship("User", foreign_keys=[sender_id]'),
            ('receiver关系新增', 'receiver = relationship("User", foreign_keys=[receiver_id]'),
        ]

        print("\n📋 检查修复内容:")
        all_passed = True

        for check_name, expected_code in checks:
            if expected_code in user_content or expected_code in game_content:
                print(f"✅ {check_name}: 通过")
            else:
                print(f"❌ {check_name}: 失败 - 未找到预期代码")
                all_passed = False

        # 验证语法正确性
        print("\n🔧 验证Python语法...")
        try:
            ast.parse(user_content)
            print("✅ user.py 语法正确")
        except SyntaxError as e:
            print(f"❌ user.py 语法错误: {e}")
            all_passed = False

        try:
            ast.parse(game_content)
            print("✅ game.py 语法正确")
        except SyntaxError as e:
            print(f"❌ game.py 语法错误: {e}")
            all_passed = False

        if all_passed:
            print("\n🎉 所有关系定义修复验证通过！")
            print("✅ SQLAlchemy关系定义语法正确")
            print("✅ 修复内容完整")
            return True
        else:
            print("\n❌ 部分检查失败，请检查修复内容")
            return False

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🧪 SQLAlchemy关系定义修复验证")
    print("=" * 60)

    success = test_relationship_definitions()

    print("\n" + "=" * 60)
    if success:
        print("✅ 验证成功: 关系定义修复完成")
        print("🚀 可以尝试运行测试账号创建脚本")
    else:
        print("❌ 验证失败: 需要进一步修复")
    print("=" * 60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())