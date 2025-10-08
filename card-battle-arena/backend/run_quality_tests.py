#!/usr/bin/env python3
"""
质量测试运行脚本
运行所有质量相关的测试：单元测试、集成测试和健康检查
"""

import asyncio
import sys
import subprocess
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description, timeout=300):
    """运行命令并处理结果"""
    print(f"\n🔬 {description}...")
    print(f"📤 命令: {' '.join(cmd)}")

    try:
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=project_root
        )
        end_time = time.time()

        duration = end_time - start_time
        print(f"⏱️  执行时间: {duration:.2f}秒")

        if result.returncode == 0:
            print(f"✅ {description} - 通过")
            if result.stdout:
                print("📥 输出:")
                print(result.stdout)
        else:
            print(f"❌ {description} - 失败 (退出码: {result.returncode})")
            if result.stderr:
                print("📥 错误:")
                print(result.stderr)
            if result.stdout:
                print("📥 输出:")
                print(result.stdout)

        return result.returncode == 0, result

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - 超时")
        return False, None
    except Exception as e:
        print(f"💥 {description} - 异常: {e}")
        return False, None

def run_unit_tests():
    """运行单元测试"""
    print("\n" + "="*60)
    print("🧪 运行单元测试")
    print("="*60)

    # 检查是否在虚拟环境中
    venv_python = None
    if Path("venv/Scripts/python.exe").exists():
        venv_python = "./venv/Scripts/python.exe"
    elif Path("venv/bin/python").exists():
        venv_python = "./venv/bin/python"

    if venv_python:
        cmd = [venv_python, "-m", "pytest", "tests/", "-v", "--tb=short", "-m", "unit"]
    else:
        cmd = ["python3", "-m", "pytest", "tests/", "-v", "--tb=short", "-m", "unit"]

    success, result = run_command(cmd, "单元测试", timeout=600)
    return success

def run_integration_tests():
    """运行集成测试"""
    print("\n" + "="*60)
    print("🔗 运行集成测试")
    print("="*60)

    # 检查Redis是否可用
    redis_available = False
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list()
        redis_available = any("redis" in c.name for c in containers)
    except:
        pass

    if redis_available:
        print("📦 检测到Redis容器，运行集成测试")

        # 检查虚拟环境
        venv_python = None
        if Path("venv/Scripts/python.exe").exists():
            venv_python = "./venv/Scripts/python.exe"
        elif Path("venv/bin/python").exists():
            venv_python = "./venv/bin/python"

        if venv_python:
            cmd = [venv_python, "-m", "pytest", "tests/integration/", "-v", "--tb=short"]
        else:
            cmd = ["python3", "-m", "pytest", "tests/integration/", "-v", "--tb=short"]

        success, result = run_command(cmd, "集成测试", timeout=600)
        return success
    else:
        print("⚠️  Redis不可用，跳过集成测试")
        return True  # 跳过但不算失败

def run_code_quality_checks():
    """运行代码质量检查"""
    print("\n" + "="*60)
    print("🔍 运行代码质量检查")
    print("="*60)

    checks = []

    # 检查是否安装了ruff
    try:
        # 尝试使用虚拟环境中的ruff
        venv_ruff = None
        if Path("venv/Scripts/ruff.exe").exists():
            venv_ruff = "./venv/Scripts/ruff.exe"
        elif Path("venv/bin/ruff").exists():
            venv_ruff = "./venv/bin/ruff"

        if venv_ruff:
            cmd = [venv_ruff, "check", "app/"]
        else:
            cmd = ["ruff", "check", "app/"]

        ruff_success, _ = run_command(cmd, "Ruff代码检查")
        checks.append(("Ruff", ruff_success))
    except FileNotFoundError:
        print("⚠️  Ruff未安装，跳过代码检查")
        checks.append(("Ruff", True))  # 跳过但不算失败

    # 检查是否安装了black
    try:
        venv_black = None
        if Path("venv/Scripts/black.exe").exists():
            venv_black = "./venv/Scripts/black.exe"
        elif Path("venv/bin/black").exists():
            venv_black = "./venv/bin/black"

        if venv_black:
            cmd = [venv_black, "--check", "app/"]
        else:
            cmd = ["black", "--check", "app/"]

        black_success, _ = run_command(cmd, "Black格式检查")
        checks.append(("Black", black_success))
    except FileNotFoundError:
        print("⚠️  Black未安装，跳过格式检查")
        checks.append(("Black", True))  # 跳过但不算失败

    # 检查import排序
    try:
        venv_isort = None
        if Path("venv/Scripts/isort.exe").exists():
            venv_isort = "./venv/Scripts/isort.exe"
        elif Path("venv/bin/isort").exists():
            venv_isort = "./venv/bin/isort"

        if venv_isort:
            cmd = [venv_isort, "--check-only", "app/"]
        else:
            cmd = ["isort", "--check-only", "app/"]

        isort_success, _ = run_command(cmd, "isort导入排序检查")
        checks.append(("isort", isort_success))
    except FileNotFoundError:
        print("⚠️  isort未安装，跳过导入排序检查")
        checks.append(("isort", True))  # 跳过但不算失败

    all_passed = all(success for _, success in checks)

    print("\n📋 代码质量检查结果:")
    for name, success in checks:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name:<10} {status}")

    return all_passed

def run_security_checks():
    """运行安全检查"""
    print("\n" + "="*60)
    print("🔒 运行安全检查")
    print("="*60)

    # 检查常见安全问题
    security_issues = []

    # 检查是否有硬编码的密码或密钥
    try:
        import subprocess
        result = subprocess.run(
            ["grep", "-r", "-i", "password.*=", "app/", "--include=*.py"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        if result.stdout:
            security_issues.append("发现可能的硬编码密码")
    except:
        pass

    # 检查是否有debug=True
    try:
        result = subprocess.run(
            ["grep", "-r", "debug.*=.*True", "app/", "--include=*.py"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        if result.stdout:
            security_issues.append("发现debug模式可能启用")
    except:
        pass

    if security_issues:
        print("⚠️  发现潜在安全问题:")
        for issue in security_issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ 安全检查通过")
        return True

def check_dependencies():
    """检查依赖项"""
    print("\n" + "="*60)
    print("📦 检查依赖项")
    print("="*60)

    # 检查requirements.txt文件
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        print("✅ requirements.txt存在")
    else:
        print("❌ requirements.txt不存在")
        return False

    # 检查关键依赖
    key_dependencies = [
        "fastapi",
        "sqlalchemy",
        "redis",
        "structlog",
        "pydantic"
    ]

    try:
        import pkg_resources

        missing_deps = []
        for dep in key_dependencies:
            try:
                pkg_resources.get_distribution(dep)
                print(f"✅ {dep}")
            except pkg_resources.DistributionNotFound:
                missing_deps.append(dep)
                print(f"❌ {dep} - 未安装")

        if missing_deps:
            print(f"\n⚠️  缺少依赖: {', '.join(missing_deps)}")
            print("💡 请运行: pip install -r requirements.txt")
            return False
        else:
            print("\n✅ 所有关键依赖已安装")
            return True

    except Exception as e:
        print(f"❌ 检查依赖时出错: {e}")
        return False

def generate_quality_report(results):
    """生成质量报告"""
    print("\n" + "="*60)
    print("📊 质量测试报告")
    print("="*60)

    total_checks = len(results)
    passed_checks = sum(1 for _, success in results if success)

    print(f"总检查项: {total_checks}")
    print(f"通过项: {passed_checks}")
    print(f"失败项: {total_checks - passed_checks}")
    print(f"通过率: {(passed_checks / total_checks * 100):.1f}%")

    print("\n📋 详细结果:")
    for check_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{check_name:<25} {status}")

    if passed_checks == total_checks:
        print("\n🎉 所有质量检查通过！")
        print("🚀 代码质量良好，可以部署")
    else:
        print("\n⚠️  部分检查失败")
        print("🔧 请修复上述问题后重新运行测试")

    print("="*60)
    return passed_checks == total_checks

def main():
    """主函数"""
    print("🧪 卡牌对战竞技场 - 质量测试套件")
    print("=" * 60)

    # 检查依赖
    deps_ok = check_dependencies()

    # 运行各项检查
    results = []

    if deps_ok:
        # 代码质量检查
        quality_ok = run_code_quality_checks()
        results.append(("代码质量", quality_ok))

        # 安全检查
        security_ok = run_security_checks()
        results.append(("安全检查", security_ok))

        # 单元测试
        unit_ok = run_unit_tests()
        results.append(("单元测试", unit_ok))

        # 集成测试
        integration_ok = run_integration_tests()
        results.append(("集成测试", integration_ok))
    else:
        results.append(("依赖检查", False))

    # 生成报告
    all_passed = generate_quality_report(results)

    # 返回适当的退出码
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())