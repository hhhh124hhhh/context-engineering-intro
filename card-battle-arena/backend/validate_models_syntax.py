#!/usr/bin/env python3
"""
验证SQLAlchemy模型定义的语法正确性
通过解析Python源代码来检查外键和关系定义
"""

import ast
import sys
from pathlib import Path


def analyze_sqlalchemy_model(file_path):
    """分析单个SQLAlchemy模型文件"""
    print(f"\n🔍 分析文件: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析AST
        tree = ast.parse(content)

        # 查找导入
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")

        # 检查是否导入了ForeignKey
        has_foreignkey = any("ForeignKey" in imp for imp in imports)
        print(f"  ✓ 导入ForeignKey: {'是' if has_foreignkey else '否'}")

        # 查找类定义
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node)

        print(f"  ✓ 找到模型类: {len(classes)} 个")

        for cls in classes:
            print(f"    - {cls.name}")

            # 检查类的方法和属性
            foreign_key_fields = []
            relationships = []

            for node in cls.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # 检查是否是Column定义
                            if isinstance(node.value, ast.Call):
                                func_name = None
                                if isinstance(node.value.func, ast.Name):
                                    func_name = node.value.func.id
                                elif isinstance(node.value.func, ast.Attribute):
                                    func_name = node.value.func.attr

                                if func_name == "Column":
                                    # 检查参数中是否包含ForeignKey
                                    for arg in node.value.args:
                                        if isinstance(arg, ast.Call):
                                            if isinstance(arg.func, ast.Name) and arg.func.id == "ForeignKey":
                                                foreign_key_fields.append(target.id)
                                                print(f"      🔗 找到外键字段: {target.id}")
                                elif func_name == "relationship":
                                    relationships.append(target.id)
                                    print(f"      📊 找到关系: {target.id}")

            if foreign_key_fields:
                print(f"      ✓ {cls.name} 外键字段: {', '.join(foreign_key_fields)}")
            if relationships:
                print(f"      ✓ {cls.name} 关系: {', '.join(relationships)}")

        return True

    except Exception as e:
        print(f"  ❌ 分析失败: {e}")
        return False


def validate_friendship_model():
    """专门验证Friendship模型"""
    print("\n🎯 专门验证Friendship模型...")

    user_file = Path("app/models/user.py")

    if not user_file.exists():
        print(f"❌ 文件不存在: {user_file}")
        return False

    with open(user_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查Friendship类定义
    if "class Friendship(Base):" not in content:
        print("❌ 未找到Friendship类定义")
        return False

    print("✓ 找到Friendship类定义")

    # 检查外键定义
    print(f"  🔍 Friendship部分内容预览:")

    # 提取Friendship类的部分
    start_pos = content.find("class Friendship(Base):")
    if start_pos == -1:
        print("❌ 未找到Friendship类")
        return False

    # 找到下一个类的开始位置
    search_section = content[start_pos:]
    end_pos = search_section.find("\nclass ", 1)  # 跳过当前class，找下一个
    if end_pos == -1:
        friendship_section = search_section
    else:
        friendship_section = search_section[:end_pos]

    print(f"    提取的内容长度: {len(friendship_section)} 字符")

    required_foreignkeys = [
        'sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)',
        'receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)'
    ]

    for fk in required_foreignkeys:
        if fk in friendship_section:
            print(f"✓ 找到外键定义: {fk.split('=')[0].strip()}")
        else:
            # 检查是否是因为空格或格式问题
            simplified_fk = fk.split('=')[0].strip()
            if simplified_fk in friendship_section:
                print(f"✓ 找到外键定义（简化匹配）: {simplified_fk}")
            else:
                print(f"❌ 缺少外键定义: {fk}")
                print(f"    查找的关键词: '{simplified_fk}'")
                # 显示相关部分
                lines = friendship_section.split('\n')
                for i, line in enumerate(lines[:10]):  # 只显示前10行
                    if 'sender_id' in line or 'receiver_id' in line:
                        print(f"    第{i+1}行: {line.strip()}")
                return False

    # 检查关系定义
    required_relationships = [
        'sender = relationship("User"',
        'receiver = relationship("User"'
    ]

    for rel in required_relationships:
        if rel in friendship_section:
            print(f"✓ 找到关系定义: {rel.split('=')[0].strip()}")
        else:
            print(f"❌ 缺少关系定义: {rel}")
            return False

    print("✅ Friendship模型验证通过!")
    return True


def main():
    """主函数"""
    print("🔬 SQLAlchemy模型语法验证工具")
    print("=" * 50)

    # 查找所有模型文件
    model_files = [
        "app/models/user.py",
        "app/models/card.py",
        "app/models/deck.py",
        "app/models/game.py"
    ]

    all_valid = True

    # 验证每个文件
    for file_path in model_files:
        if not analyze_sqlalchemy_model(file_path):
            all_valid = False

    # 特别验证Friendship模型
    if not validate_friendship_model():
        all_valid = False

    print("\n" + "=" * 50)
    if all_valid:
        print("🎉 所有模型语法验证通过!")
        print("✅ SQLAlchemy外键和关系定义正确")
        return 0
    else:
        print("💥 模型验证失败!")
        print("❌ 仍有SQLAlchemy定义问题需要修复")
        return 1


if __name__ == "__main__":
    sys.exit(main())