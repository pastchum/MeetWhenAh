"""
Pytest configuration and shared fixtures for MeetWhenAh Bot tests.
"""
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import tempfile
import shutil


@pytest.fixture(scope="session")
def test_session():
    """Session-level fixture for test setup"""
    # Set test environment variables
    os.environ.update({
        'ENVIRONMENT': 'test',
        'BOT_USERNAME': 'test_bot',
        'WEBAPP_URL': 'https://test-webapp.example.com',
        'USE_LOCAL_WEBAPP': 'false',
        'LOCALHOST_PORT': '3000'
    })
    yield
    # Cleanup after all tests


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment before each test"""
    # Store original environment
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_telegram_message():
    """Create a mock Telegram message object"""
    message = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.from_user.last_name = "User"
    message.chat.id = 67890
    message.chat.type = 'private'
    message.message_thread_id = None
    message.message_id = 111
    message.text = "/test"
    message.date = datetime.now(timezone.utc)
    return message


@pytest.fixture
def mock_telegram_group_message():
    """Create a mock Telegram group message object"""
    message = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.from_user.first_name = "Test"
    message.from_user.last_name = "User"
    message.chat.id = 67890
    message.chat.type = 'group'
    message.message_thread_id = None
    message.message_id = 111
    message.text = "/test"
    message.date = datetime.now(timezone.utc)
    return message


@pytest.fixture
def mock_telegram_callback_query():
    """Create a mock Telegram callback query object"""
    callback_query = MagicMock()
    callback_query.from_user.id = 12345
    callback_query.from_user.username = "testuser"
    callback_query.from_user.first_name = "Test"
    callback_query.from_user.last_name = "User"
    callback_query.data = "test:data"
    callback_query.id = "callback_123"
    
    # Mock message within callback query
    callback_query.message = MagicMock()
    callback_query.message.chat.id = 67890
    callback_query.message.message_id = 111
    callback_query.message.message_thread_id = None
    
    return callback_query


@pytest.fixture
def mock_bot():
    """Create a mock Telegram bot object"""
    bot = MagicMock()
    bot.get_me.return_value.username = "test_bot"
    bot.reply_to.return_value = MagicMock(message_id=111)
    bot.send_message.return_value = MagicMock(message_id=111)
    bot.edit_message_text.return_value = True
    bot.answer_callback_query.return_value = True
    return bot


@pytest.fixture
def mock_supabase():
    """Create a mock Supabase client"""
    supabase = MagicMock()
    supabase.rpc.return_value.execute.return_value.data = []
    return supabase


@pytest.fixture
def mock_database_service():
    """Create a mock database service"""
    with patch('services.database_service.getEntry') as mock_get, \
         patch('services.database_service.setEntry') as mock_set, \
         patch('services.database_service.updateEntry') as mock_update, \
         patch('services.database_service.getEntries') as mock_get_all, \
         patch('services.database_service.deleteEntry') as mock_delete:
        
        # Configure default return values
        mock_get.return_value = None
        mock_set.return_value = True
        mock_update.return_value = True
        mock_get_all.return_value = []
        mock_delete.return_value = True
        
        yield {
            'getEntry': mock_get,
            'setEntry': mock_set,
            'updateEntry': mock_update,
            'getEntries': mock_get_all,
            'deleteEntry': mock_delete
        }


@pytest.fixture
def mock_user_service():
    """Create a mock user service"""
    with patch('services.user_service.getUser') as mock_get_user, \
         patch('services.user_service.setUser') as mock_set_user, \
         patch('services.user_service.updateUsername') as mock_update_username:
        
        # Configure default return values
        mock_get_user.return_value = {
            'uuid': 'test-user-uuid',
            'tele_id': '12345',
            'tele_user': 'testuser',
            'initialised': True
        }
        mock_set_user.return_value = True
        mock_update_username.return_value = True
        
        yield {
            'getUser': mock_get_user,
            'setUser': mock_set_user,
            'updateUsername': mock_update_username
        }


@pytest.fixture
def mock_event_service():
    """Create a mock event service"""
    with patch('services.event_service.getEvent') as mock_get_event, \
         patch('services.event_service.create_event') as mock_create_event, \
         patch('services.event_service.confirmEvent') as mock_confirm_event, \
         patch('services.event_service.join_event') as mock_join_event:
        
        # Configure default return values
        mock_get_event.return_value = {
            'event_id': 'test-event-123',
            'event_name': 'Test Event',
            'event_description': 'Test Description',
            'creator': 'test-creator-uuid'
        }
        mock_create_event.return_value = 'test-event-123'
        mock_confirm_event.return_value = True
        mock_join_event.return_value = True
        
        yield {
            'getEvent': mock_get_event,
            'create_event': mock_create_event,
            'confirmEvent': mock_confirm_event,
            'join_event': mock_join_event
        }


@pytest.fixture
def mock_share_service():
    """Create a mock share service"""
    with patch('services.share_service.put_ctx') as mock_put_ctx:
        mock_put_ctx.return_value = 'test-token-123'
        yield {'put_ctx': mock_put_ctx}


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_event_data():
    """Sample event data for testing"""
    return {
        'event_name': 'Test Event',
        'event_details': 'Test Description',
        'start': '2024-01-01',
        'end': '2024-01-02'
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'uuid': 'test-user-uuid',
        'tele_id': '12345',
        'tele_user': 'testuser',
        'initialised': True,
        'created_at': '2024-01-01T00:00:00Z'
    }


@pytest.fixture
def sample_availability_data():
    """Sample availability data for testing"""
    return [
        {
            'user_uuid': 'test-user-uuid',
            'event_id': 'test-event-123',
            'date': '2024-01-01',
            'start_time': '09:00',
            'end_time': '17:00'
        }
    ]


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, with dependencies)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (slowest, full system)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 1 second"
    )
    config.addinivalue_line(
        "markers", "network: Tests that require network access"
    )
    config.addinivalue_line(
        "markers", "database: Tests that require database access"
    )
    config.addinivalue_line(
        "markers", "telegram: Tests that interact with Telegram API"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add unit marker to tests in test_mini_app_url.py
        if "test_mini_app_url" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests with "integration" in name
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker to tests with "slow" in name
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Add network marker to tests that might use network
        if any(keyword in item.nodeid for keyword in ["telegram", "api", "http"]):
            item.add_marker(pytest.mark.network)
