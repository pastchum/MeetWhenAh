import os
import pytest
from unittest.mock import patch, MagicMock
from utils.mini_app_url import get_mini_app_url, get_webapp_url


@pytest.mark.unit
class TestMiniAppURL:
    """Test Mini App URL generation with different environments and parameters"""
    
    def test_development_with_local_webapp(self):
        """Test development environment with local webapp enabled"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_dev_bot',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3000'
        })
        
        # Test datepicker URL
        url = get_mini_app_url("datepicker", token="test_token_123")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=datepicker=test_token_123"
        assert url == expected
        
        # Test confirm URL
        url = get_mini_app_url("confirm", event_id="event_456")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=confirm=event_456"
        assert url == expected
        
        # Test share URL
        url = get_mini_app_url("share", token="share_token_789")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=share=share_token_789"
        assert url == expected
        
        # Test dragselector URL
        url = get_mini_app_url("dragselector", event_id="drag_event_101")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=dragselector=drag_event_101"
        assert url == expected
    
    def test_development_with_different_port(self):
        """Test development environment with custom port"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_dev_bot',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3001'
        })
        
        url = get_mini_app_url("datepicker", token="test_token")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=datepicker=test_token"
        assert url == expected
    
    def test_development_without_local_webapp(self):
        """Test development environment without local webapp (uses production)"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_dev_bot',
            'USE_LOCAL_WEBAPP': 'false'
        })
        
        url = get_mini_app_url("datepicker", token="test_token")
        expected = "https://t.me/test_dev_bot/meetwhenah?startapp=datepicker=test_token"
        assert url == expected
    
    def test_staging_environment(self):
        """Test staging environment"""
        os.environ.update({
            'ENVIRONMENT': 'staging',
            'BOT_USERNAME': 'meeting_the_stage_bot'
        })
        
        url = get_mini_app_url("confirm", event_id="staging_event")
        expected = "https://t.me/meeting_the_stage_bot/meetwhenah?startapp=confirm=staging_event"
        assert url == expected
    
    def test_production_environment(self):
        """Test production environment"""
        os.environ.update({
            'ENVIRONMENT': 'production',
            'BOT_USERNAME': 'MeetWhenAhBot'
        })
        
        url = get_mini_app_url("share", token="prod_token")
        expected = "https://t.me/MeetWhenAhBot/meetwhenah?startapp=share=prod_token"
        assert url == expected
    
    def test_missing_bot_username(self):
        """Test error when BOT_USERNAME is not set"""
        os.environ.update({
            'ENVIRONMENT': 'development'
            # BOT_USERNAME not set
        })
        
        with pytest.raises(ValueError, match="BOT_USERNAME not set for environment: development"):
            get_mini_app_url("datepicker", token="test")
    
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
    
    def test_multiple_parameters(self):
        """Test URL generation with multiple parameters"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': 'test_bot'
        })
        
        url = get_mini_app_url("test", param1="value1", param2="value2")
        expected = "https://t.me/test_bot/meetwhenah?startapp=test=param1%3Dvalue1%26param2%3Dvalue2"
        assert url == expected


class TestWebappURL:
    """Test direct webapp URL generation"""
    
    def setup_method(self):
        """Set up test environment variables"""
        self.original_env = os.environ.copy()
    
    def teardown_method(self):
        """Restore original environment variables"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_development_with_local_webapp(self):
        """Test development with local webapp"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3000'
        })
        
        url = get_webapp_url("datepicker", token="test_token")
        expected = "https://localhost:3000/datepicker?token=test_token"
        assert url == expected
    
    def test_development_with_custom_port(self):
        """Test development with custom port"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3001'
        })
        
        url = get_webapp_url("confirm", event_id="test_event")
        expected = "https://localhost:3001/confirm?event_id=test_event"
        assert url == expected
    
    def test_production_webapp_url(self):
        """Test production webapp URL"""
        os.environ.update({
            'ENVIRONMENT': 'production',
            'WEBAPP_URL': 'https://meet-when-ah.vercel.app'
        })
        
        url = get_webapp_url("share", token="prod_token")
        expected = "https://meet-when-ah.vercel.app/share?token=prod_token"
        assert url == expected
    
    def test_default_webapp_url(self):
        """Test default webapp URL when not specified"""
        os.environ.update({
            'ENVIRONMENT': 'production'
        })
        
        url = get_webapp_url("dashboard")
        expected = "https://meet-when-ah.vercel.app/dashboard"
        assert url == expected
    
    def test_staging_webapp_url(self):
        """Test staging webapp URL uses Vercel preview"""
        os.environ.update({
            'ENVIRONMENT': 'staging'
        })
        
        url = get_webapp_url("dashboard")
        expected = "https://meet-when-ah-git-staging.vercel.app/dashboard"
        assert url == expected
    
    def test_dashboard_webapp_url_with_token(self):
        """Test dashboard webapp URL with token parameter"""
        os.environ.update({
            'ENVIRONMENT': 'development',
            'USE_LOCAL_WEBAPP': 'true',
            'LOCALHOST_PORT': '3000'
        })
        
        url = get_webapp_url("dashboard", token="test_token")
        expected = "https://localhost:3000/dashboard?token=test_token"
        assert url == expected
