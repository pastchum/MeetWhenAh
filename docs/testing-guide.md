# Testing Guide for MeetWhenAh Bot

This guide explains the testing structure and best practices for the MeetWhenAh Telegram bot project.

## Testing Structure

```
bot/
├── tests/
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── factories.py             # Test data factories
│   ├── test_mini_app_url.py     # Unit tests for URL generation
│   └── test_handlers_url_generation.py  # Unit tests for handlers
├── pytest.ini                  # Pytest configuration
└── requirements.txt            # Testing dependencies
```

## Quick Reference

**🚀 Run tests from project root:**
```bash
# Basic test run
./scripts/run-tests.sh

# With coverage
./scripts/run-tests.sh --coverage

# Unit tests only
./scripts/run-tests.sh --markers "unit"
```

**📁 Directory structure:**
```
MeetWhenAh/                    ← Run tests from here
├── scripts/run-tests.sh       ← Main test script
├── bot/
│   ├── tests/                 ← Test files
│   ├── Makefile              ← Alternative test commands
│   └── pytest.ini            ← Pytest configuration
└── docs/testing-guide.md     ← This file
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- **Fast** (< 1 second each)
- **Isolated** (no external dependencies)
- **Focused** (test single functions/classes)
- Examples: URL generation, parameter validation, data transformation

### Integration Tests (`@pytest.mark.integration`)
- **Medium speed** (1-10 seconds each)
- **With dependencies** (database, external services)
- **Focused** (test component interactions)
- Examples: Service layer tests, database operations

### End-to-End Tests (`@pytest.mark.e2e`)
- **Slow** (> 10 seconds each)
- **Full system** (complete user workflows)
- **Realistic** (actual Telegram API calls)
- Examples: Complete bot conversation flows

## Running Tests

### Where to Run Tests From

**Always run tests from the project root directory:**
```bash
# You should be here:
MeetWhenAh/

# NOT here:
MeetWhenAh/bot/
```

### Method 1: Using the Test Script (Recommended)

**From project root:**
```bash
# Run all tests
./scripts/run-tests.sh

# Run with coverage
./scripts/run-tests.sh --coverage

# Run only unit tests
./scripts/run-tests.sh --markers "unit"

# Run with HTML report
./scripts/run-tests.sh --html --coverage
```

### Method 2: Using Makefile

**From project root:**
```bash
# Navigate to bot directory first
cd bot

# Run all tests
make test

# Run with coverage
make test-coverage

# Run only unit tests
make test-unit

# Run with HTML report
make test-html
```

### Method 3: Direct pytest (Advanced)

**From project root:**
```bash
# Navigate to bot directory
cd bot

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run tests
python -m pytest tests/ -v
```

### Advanced Options
```bash
# Run tests in parallel
./scripts/run-tests.sh --parallel

# Verbose output
./scripts/run-tests.sh --verbose

# Run specific test categories
./scripts/run-tests.sh --markers "unit and not slow"

# Get help
./scripts/run-tests.sh --help
```

## Test Data Factories

Use factories to create consistent test data:

```python
from tests.factories import (
    TelegramMessageFactory,
    UserDataFactory,
    EventDataFactory
)

# Create test message
message = TelegramMessageFactory.create_message(
    user_id=12345,
    username="testuser"
)

# Create test user data
user_data = UserDataFactory.create_user(
    tele_id="12345",
    tele_user="testuser"
)

# Create test event data
event_data = EventDataFactory.create_event(
    event_name="Test Event"
)
```

## Fixtures

Use fixtures for common test setup:

```python
def test_handler_with_fixtures(mock_telegram_message, mock_bot, mock_database_service):
    """Test using fixtures"""
    # Your test code here
    pass
```

## Mocking

Mock external dependencies:

```python
@patch('services.database_service.getEntry')
def test_database_operation(mock_get_entry):
    """Test with mocked database service"""
    mock_get_entry.return_value = {'id': '123'}
    # Your test code here
```

## Test Naming Conventions

- **Test files**: `test_*.py`
- **Test classes**: `Test*`
- **Test functions**: `test_*`
- **Descriptive names**: `test_should_generate_correct_url_when_environment_is_development`

## Writing Good Tests

### 1. Follow AAA Pattern
```python
def test_url_generation():
    # Arrange
    os.environ['ENVIRONMENT'] = 'development'
    
    # Act
    url = get_mini_app_url("test", param="value")
    
    # Assert
    assert "test_dev_bot" in url
    assert "param%3Dvalue" in url
```

### 2. Test Edge Cases
```python
def test_empty_parameters():
    """Test handling of empty parameters"""
    url = get_mini_app_url("test", empty_param="")
    assert "empty_param%3D" in url

def test_unicode_parameters():
    """Test handling of Unicode parameters"""
    url = get_mini_app_url("test", unicode_param="测试")
    assert "unicode_param%3D" in url
```

### 3. Use Descriptive Assertions
```python
# Good
assert "test_dev_bot" in url, f"Expected bot username in URL, got: {url}"

# Better
assert url == "https://t.me/test_dev_bot/meetwhenah?startapp=test=param%3Dvalue"
```

## Coverage Goals

- **Unit tests**: 90%+ coverage
- **Integration tests**: 70%+ coverage
- **Overall**: 80%+ coverage

## Continuous Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Scheduled nightly runs

## Debugging Tests

### Run Single Test
```bash
cd bot
source venv/bin/activate
python -m pytest tests/test_mini_app_url.py::TestMiniAppURL::test_development_with_local_webapp -v
```

### Debug Mode
```bash
python -m pytest tests/test_mini_app_url.py -v -s --pdb
```

### Show Test Output
```bash
python -m pytest tests/test_mini_app_url.py -v -s
```

## Best Practices

1. **Keep tests fast** - Unit tests should run in milliseconds
2. **Make tests independent** - Each test should work in isolation
3. **Use meaningful names** - Test names should describe what's being tested
4. **Test one thing at a time** - Each test should have a single responsibility
5. **Use factories** - Don't duplicate test data creation
6. **Mock external dependencies** - Don't make real API calls in tests
7. **Test edge cases** - Empty values, None, special characters
8. **Keep tests simple** - Complex tests are hard to maintain

## Common Patterns

### Testing URL Generation
```python
def test_url_generation():
    os.environ.update(EnvironmentFactory.create_development_env())
    url = get_mini_app_url("test", param="value")
    assert "test_dev_bot" in url
    assert "param%3Dvalue" in url
```

### Testing Handlers
```python
@patch('utils.mini_app_url.get_mini_app_url')
def test_handler_generates_url(mock_get_url):
    mock_get_url.return_value = "https://test.com"
    # Test handler logic
    mock_get_url.assert_called_once_with("test", param="value")
```

### Testing Error Cases
```python
def test_missing_bot_username():
    os.environ.pop('BOT_USERNAME', None)
    with pytest.raises(ValueError, match="BOT_USERNAME not set"):
        get_mini_app_url("test")
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the bot directory
2. **Environment issues**: Check that virtual environment is activated
3. **Mock issues**: Ensure mocks are properly configured
4. **Database issues**: Use database fixtures for integration tests

### Getting Help

- Check test output for specific error messages
- Use `-v` flag for verbose output
- Use `--pdb` for debugging
- Check pytest documentation for advanced features
