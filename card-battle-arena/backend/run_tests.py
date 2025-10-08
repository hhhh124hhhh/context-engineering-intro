#!/usr/bin/env python3
"""
Test runner script for the Card Battle Arena backend.

This script provides a convenient way to run tests with different configurations
and generate coverage reports.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


def install_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")
    dependencies = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "httpx",
        "faker"
    ]

    for dep in dependencies:
        result = run_command([sys.executable, "-m", "pip", "install", dep])
        if result != 0:
            print(f"Failed to install {dep}")
            return False

    print("Dependencies installed successfully.")
    return True


def run_tests(test_path=None, coverage=False, verbose=False, parallel=False):
    """Run the test suite."""

    # Ensure we're in the correct directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Set up environment variables for testing
    env = os.environ.copy()
    env["TESTING"] = "1"
    env["DATABASE_URL"] = "sqlite:///./test.db"
    env["SECRET_KEY"] = "test-secret-key-for-testing-only"

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]

    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("tests/")

    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])

    if verbose:
        cmd.append("-v")

    if parallel:
        cmd.extend(["-n", "auto"])

    # Add pytest configuration
    cmd.extend([
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "--disable-warnings"  # Disable warnings
    ])

    # Run the tests
    result = run_command(cmd)

    if coverage and result == 0:
        print("\nCoverage report generated in htmlcov/index.html")

    return result


def run_specific_tests(test_type):
    """Run specific types of tests."""

    test_paths = {
        "unit": "tests/test_*.py",
        "integration": "tests/integration/",
        "api": "tests/test_api.py",
        "auth": "tests/test_auth.py",
        "game": "tests/test_game_engine.py",
        "matchmaking": "tests/test_matchmaking.py"
    }

    if test_type not in test_paths:
        print(f"Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_paths.keys())}")
        return 1

    return run_tests(test_paths[test_type], coverage=True, verbose=True)


def lint_code():
    """Run code linting."""
    print("Running code linting...")

    # Check if ruff is installed
    try:
        result = run_command([sys.executable, "-m", "ruff", "check", "app/", "tests/"])
        if result != 0:
            print("Linting issues found.")
            return result
    except FileNotFoundError:
        print("Ruff not installed. Install with: pip install ruff")
        return 1

    print("Linting passed.")
    return 0


def format_code():
    """Run code formatting."""
    print("Running code formatting...")

    # Check if black is installed
    try:
        result = run_command([sys.executable, "-m", "black", "app/", "tests/", "--check"])
        if result != 0:
            print("Code formatting issues found. Run 'black app/ tests/' to fix.")
            return result
    except FileNotFoundError:
        print("Black not installed. Install with: pip install black")
        return 1

    print("Code formatting is correct.")
    return 0


def clean_test_artifacts():
    """Clean up test artifacts."""
    print("Cleaning up test artifacts...")

    artifacts = [
        "test.db",
        "test.db-journal",
        ".pytest_cache",
        "htmlcov",
        ".coverage"
    ]

    for artifact in artifacts:
        path = Path(artifact)
        if path.exists():
            if path.is_dir():
                import shutil
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"Removed {artifact}")

    print("Cleanup completed.")


def generate_test_data():
    """Generate test data for development."""
    print("Generating test data...")

    # This would create sample data for testing
    # For now, just create the test database
    try:
        from app.core.database import init_db
        import asyncio

        async def create_test_data():
            await init_db()
            print("Test database created.")

        asyncio.run(create_test_data())
        return 0
    except Exception as e:
        print(f"Failed to create test data: {e}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test runner for Card Battle Arena")
    parser.add_argument(
        "command",
        choices=[
            "install", "test", "coverage", "lint", "format", "clean",
            "unit", "integration", "api", "auth", "game", "matchmaking",
            "generate-data"
        ],
        help="Command to run"
    )
    parser.add_argument(
        "--path",
        help="Specific test path to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )

    args = parser.parse_args()

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Handle commands
    if args.command == "install":
        return install_dependencies()

    elif args.command == "test":
        return run_tests(
            test_path=args.path,
            coverage=False,
            verbose=args.verbose,
            parallel=args.parallel
        )

    elif args.command == "coverage":
        return run_tests(
            test_path=args.path,
            coverage=True,
            verbose=args.verbose,
            parallel=args.parallel
        )

    elif args.command == "lint":
        return lint_code()

    elif args.command == "format":
        return format_code()

    elif args.command == "clean":
        clean_test_artifacts()
        return 0

    elif args.command == "generate-data":
        return generate_test_data()

    elif args.command in ["unit", "integration", "api", "auth", "game", "matchmaking"]:
        return run_specific_tests(args.command)

    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())