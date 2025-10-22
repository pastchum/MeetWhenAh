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

## Where to run tests and how to import

- Always prefer running tests from the project root via `./scripts/run-tests.sh`. The script `cd`'s into `bot/` and sets up the venv, so imports resolve consistently.
- If running `pytest` manually, first `cd bot && source venv/bin/activate`, then run `python -m pytest tests -v`.
- Import style inside tests should follow this pattern:
  - For bot modules: `from telegram.handlers.event_handlers import ...` or `from utils.mini_app_url import ...` if running inside `bot/`.
  - If you intentionally run tests from the project root without `cd bot`, use absolute imports prefixed with `bot.` like `from bot.telegram.handlers.event_handlers import ...` and `from bot.utils.mini_app_url import ...`.
- Our standard is to run tests using the script (which changes into `bot/`), so tests should generally use imports without the `bot.` prefix (e.g., `from telegram...` and `from utils...`).

### Common error and fix

- Error: `ModuleNotFoundError: No module named 'bot'`
  - Cause: Running `pytest` from within `bot/` while using `from bot....` imports.
  - Fix: Either (a) run tests from the project root using `./scripts/run-tests.sh`, or (b) change imports to non-prefixed paths (e.g., `from telegram...`).

- Error: `ModuleNotFoundError: No module named 'telegram'`
  - Cause: Running tests from the project root manually without the script and using non-prefixed imports.
  - Fix: Use the script (recommended), or ensure you `cd bot` before running `pytest`.

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
