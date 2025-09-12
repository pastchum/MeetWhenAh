"""
Simple tests that don't require network access or complex imports.
"""
import os
import pytest
from utils.mini_app_url import get_mini_app_url, get_webapp_url


@pytest.mark.unit
class TestSimpleURLGeneration:
    """Simple tests for URL generation without network dependencies"""
    
    def test_basic_mini_app_url(self):
        """Test basic Mini App URL generation"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_bot'
        })
        
        url = get_mini_app_url("test", param="value")
        expected = "https://t.me/test_bot/meetwhenah?startapp=test=value"
        assert url == expected
    
    def test_development_with_local_webapp(self):
        """Test development environment with local webapp"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_bot',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3000'
        })
        
        url = get_mini_app_url("datepicker", token="test_token")
        expected = "https://t.me/test_bot/meetwhenah?startapp=datepicker=test_token"
        assert url == expected
    
    def test_production_environment(self):
        """Test production environment"""
        os.environ.update({
            'ENVIRONMENT': 'production',
            'BOT_USERNAME': 'MeetWhenAhBot'
        })
        
        url = get_mini_app_url("confirm", event_id="test_event")
        expected = "https://t.me/MeetWhenAhBot/meetwhenah?startapp=confirm=test_event"
        assert url == expected
    
    def test_webapp_url_generation(self):
        """Test direct webapp URL generation"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3000'
        })
        
        url = get_webapp_url("test", param="value")
        expected = "https://localhost:3000/test?param=value"
        assert url == expected
    
    def test_url_encoding(self):
        """Test URL encoding of special characters"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_bot'
        })
        
        url = get_mini_app_url("test", special="value with spaces & symbols!")
        expected = "https://t.me/test_bot/meetwhenah?startapp=test=value with spaces & symbols!"
        assert url == expected
    
    def test_missing_bot_username(self):
        """Test error when BOT_USERNAME is missing"""
        os.environ.pop('BOT_USERNAME', None)
        os.environ['ENVIRONMENT'] = 'development'
        
        with pytest.raises(ValueError, match="BOT_USERNAME not set"):
            get_mini_app_url("test")
    
    def test_no_parameters(self):
        """Test URL generation without parameters"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_bot'
        })
        
        url = get_mini_app_url("dashboard")
        expected = "https://t.me/test_bot/meetwhenah?startapp=dashboard"
        assert url == expected
    
    def test_dashboard_with_token(self):
        """Test dashboard URL generation with token parameter"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_bot'
        })
        
        url = get_mini_app_url("dashboard", token="test_token_123")
        expected = "https://t.me/test_bot/meetwhenah?startapp=dashboard=test_token_123"
        assert url == expected