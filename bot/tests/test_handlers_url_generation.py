"""
Simple tests for URL generation functionality.
These tests focus on the core URL generation behavior without complex handler mocking.
"""
import os
import pytest
from utils.mini_app_url import get_mini_app_url


@pytest.mark.unit
class TestURLGeneration:
    """Test URL generation for Mini App and Webapp URLs"""
    
    def setup_method(self):
        """Set up test environment"""
        self.original_env = os.environ.copy()
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_dev_bot',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3000'
        })
    
    def teardown_method(self):
        """Restore environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_single_parameter_no_encoding(self):
        """Test that single parameters are not URL encoded (matches original behavior)"""
        url = get_mini_app_url("datepicker", token="test_token_123")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=datepicker=test_token_123"
        assert url == expected
    
    def test_single_parameter_with_special_chars(self):
        """Test that special characters in single parameters are not URL encoded"""
        url = get_mini_app_url("test", param="value with spaces & symbols!")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=test=value with spaces & symbols!"
        assert url == expected
    
    def test_multiple_parameters_url_encoded(self):
        """Test that multiple parameters are properly URL encoded"""
        url = get_mini_app_url("test", param1="value1", param2="value2")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=test=param1%3Dvalue1%26param2%3Dvalue2"
        assert url == expected
    
    def test_empty_parameters(self):
        """Test handling of empty parameters"""
        url = get_mini_app_url("test", empty_param="")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=test="
        assert url == expected
    
    def test_none_parameters(self):
        """Test handling of None parameters"""
        url = get_mini_app_url("test", none_param=None)
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=test=None"
        assert url == expected
    
    def test_unicode_parameters(self):
        """Test handling of Unicode parameters"""
        url = get_mini_app_url("test", unicode_param="测试中文")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=test=测试中文"
        assert url == expected
    
    def test_environment_switching(self):
        """Test that URLs change correctly when switching environments"""
        # Test development
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'dev_bot',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3000'
        })
        
        dev_url = get_mini_app_url("test", param="value")
        assert "dev_bot" in dev_url
        assert "startapp=test=value" in dev_url
        
        # Test staging
        os.environ.update({
            'ENVIRONMENT': 'staging',
            'BOT_USERNAME': 'staging_bot'
        })
        
        staging_url = get_mini_app_url("test", param="value")
        assert "staging_bot" in staging_url
        assert "startapp=test=value" in staging_url
        
        # Test production
        os.environ.update({
            'ENVIRONMENT': 'production',
            'BOT_USERNAME': 'MeetWhenAhBot'
        })
        
        prod_url = get_mini_app_url("test", param="value")
        assert "MeetWhenAhBot" in prod_url
        assert "startapp=test=value" in prod_url
    
    def test_webapp_url_generation(self):
        """Test webapp URL generation"""
        from utils.mini_app_url import get_webapp_url
        
        # Test with parameters
        url = get_webapp_url("datepicker", token="test123")
        expected = "https://localhost:3000/datepicker?token=test123"
        assert url == expected
        
        # Test without parameters
        url = get_webapp_url("dashboard")
        expected = "https://localhost:3000/dashboard"
        assert url == expected
    
    def test_original_handler_patterns(self):
        """Test URL patterns that match the original handler implementations"""
        # Test datepicker pattern (from create command)
        url = get_mini_app_url("datepicker", token="abc123")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=datepicker=abc123"
        assert url == expected
        
        # Test share pattern (from share command)
        url = get_mini_app_url("share", token="def456")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=share=def456"
        assert url == expected
        
        # Test confirm pattern (from event creation)
        url = get_mini_app_url("confirm", event_id="event789")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=confirm=event789"
        assert url == expected
        
        # Test dragselector pattern (from event buttons)
        url = get_mini_app_url("dragselector", event_id="event789")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=dragselector=event789"
        assert url == expected
