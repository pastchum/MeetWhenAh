# Bot Tests

This directory contains all tests for the MeetWhenAh Telegram bot.

## Quick Start

**Run tests from the project root directory:**
```bash
# From /Users/kaungzinye/Documents/SWE/MeetWhenAh/
./scripts/run-tests.sh
```

## Test Files

- `conftest.py` - Pytest configuration and shared fixtures
- `factories.py` - Test data factories for creating consistent test objects
- `test_mini_app_url.py` - Unit tests for URL generation
- `test_handlers_url_generation.py` - Unit tests for handler URL generation

## Running Tests

### Method 1: Test Script (Recommended)
```bash
# From project root
./scripts/run-tests.sh                    # All tests
./scripts/run-tests.sh --coverage         # With coverage
./scripts/run-tests.sh --markers "unit"   # Unit tests only
```

### Method 2: Makefile
```bash
# From project root
cd bot
make test                                # All tests
make test-coverage                       # With coverage
make test-unit                          # Unit tests only
```

### Method 3: Direct pytest
```bash
# From project root
cd bot
source venv/bin/activate
python -m pytest tests/ -v
```

## Test Categories

- **Unit tests** (`@pytest.mark.unit`) - Fast, isolated tests
- **Integration tests** (`@pytest.mark.integration`) - With dependencies
- **E2E tests** (`@pytest.mark.e2e`) - Full system tests

## Writing Tests

See [../docs/testing-guide.md](../docs/testing-guide.md) for detailed guidelines.

## Common Commands

```bash
# Run specific test file
python -m pytest tests/test_mini_app_url.py -v

# Run specific test
python -m pytest tests/test_mini_app_url.py::TestMiniAppURL::test_development_with_local_webapp -v

# Debug mode
python -m pytest tests/test_mini_app_url.py -v -s --pdb

# Coverage report
python -m pytest tests/ --cov=. --cov-report=html:htmlcov
```
