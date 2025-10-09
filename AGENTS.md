# AGENTS.md - Development Commands & Guidelines

## Build/Lint/Test Commands
- **Run all tests**: `python -m pytest tests/` or `python run_tests.py test`
- **Run single test**: `python -m pytest tests/test_file.py::test_function -v`
- **Run with coverage**: `python run_tests.py coverage`
- **Lint code**: `ruff check . && black --check .`
- **Format code**: `black . && ruff --fix .`
- **Type checking**: `mypy app/`

## Code Style Guidelines
- **Language**: Python 3.11+ with type hints
- **Formatting**: Black (88 char line length), Ruff for linting
- **Imports**: Group stdlib, third-party, local imports with isort
- **Naming**: snake_case for functions/vars, PascalCase for classes
- **Error handling**: Use custom exceptions, proper logging with structlog
- **Testing**: pytest with async support, 80%+ coverage requirement
- **Documentation**: Google-style docstrings, type hints required

## Project Structure
- Use FastAPI for web APIs, SQLAlchemy for database
- Follow modular design with clear separation of concerns
- Always use virtual environment (venv_linux for Python)
- Include unit tests for all new features
- Validate with pydantic models for data integrity