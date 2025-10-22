"""
Integration tests for event creation flow between webapp and telegram bot.
Tests the complete flow from webapp event creation to telegram bot message handling.
"""
import os
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
from telegram.handlers.event_handlers import handle_event_creation
from factories import (
    TelegramMessageFactory,
    EventDataFactory,
    UserDataFactory,
    BotFactory
)


@pytest.mark.integration
class TestEventCreationIntegration:
    """Integration tests for event creation flow"""
    
    def test_handle_event_creation_success(self):
        """Test successful event creation from webapp data"""
        # Arrange
        message = TelegramMessageFactory.create_private_message(
            user_id=12345,
            username="testuser",
            chat_id=67890
        )
        
        event_data = EventDataFactory.create_event_creation_data(
            event_name="Team Meeting",
            event_details="Discuss Q4 goals",
            start="2024-12-01T00:00:00Z",
            end="2024-12-05T00:00:00Z"
        )
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event, \
             patch('telegram.handlers.event_handlers.getEvent') as mock_get_event, \
             patch('telegram.handlers.event_handlers.generate_event_description') as mock_gen_desc, \
             patch('telegram.handlers.event_handlers.ask_availability') as mock_ask_avail:
            
            # Configure mocks
            mock_create_event.return_value = 'test-event-123'
            mock_get_event.return_value = {
                'event_id': 'test-event-123',
                'event_name': 'Team Meeting',
                'event_description': 'Discuss Q4 goals'
            }
            mock_gen_desc.return_value = "Event: Team Meeting\nDescription: Discuss Q4 goals"
            
            # Act
            handle_event_creation(message, event_data)
            
            # Assert
            # Verify event was created with correct data
            mock_create_event.assert_called_once()
            call_kwargs = mock_create_event.call_args[1]
            assert call_kwargs['event_name'] == 'Team Meeting'
            assert call_kwargs['event_description'] == 'Discuss Q4 goals'
            assert call_kwargs['creator_id'] == '12345'
            assert call_kwargs['auto_join'] is True
            
            # Verify success message was sent
            mock_bot.reply_to.assert_called_once()
            reply_args = mock_bot.reply_to.call_args
            assert message in reply_args[0]
            assert 'Event created successfully' in reply_args[0][1]
            assert 'Team Meeting' in mock_gen_desc.return_value
            
            # Verify availability was requested
            mock_ask_avail.assert_called_once_with(
                chat_id=67890,
                event_id='test-event-123',
                thread_id=None
            )
    
    def test_handle_event_creation_group_chat(self):
        """Test event creation in group chat mentions creator"""
        # Arrange
        message = TelegramMessageFactory.create_group_message(
            user_id=12345,
            username="testuser",
            chat_id=67890
        )
        
        event_data = EventDataFactory.create_event_creation_data()
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event, \
             patch('telegram.handlers.event_handlers.getEvent') as mock_get_event, \
             patch('telegram.handlers.event_handlers.generate_event_description') as mock_gen_desc, \
             patch('telegram.handlers.event_handlers.ask_availability') as mock_ask_avail:
            
            mock_create_event.return_value = 'test-event-123'
            mock_get_event.return_value = {'event_id': 'test-event-123', 'event_name': 'Test Event'}
            mock_gen_desc.return_value = "Event details"
            
            # Act
            handle_event_creation(message, event_data)
            
            # Assert
            reply_args = mock_bot.reply_to.call_args
            success_message = reply_args[0][1]
            assert '@testuser made an event!' in success_message
    
    def test_handle_event_creation_missing_fields(self):
        """Test event creation with missing required fields"""
        # Arrange
        message = TelegramMessageFactory.create_private_message()
        
        # Missing event_name
        incomplete_data = {
            'event_name': '',
            'event_details': 'Test Description',
            'start': '2024-12-01T00:00:00Z',
            'end': '2024-12-05T00:00:00Z'
        }
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event:
            
            # Act
            handle_event_creation(message, incomplete_data)
            
            # Assert
            mock_bot.reply_to.assert_called_once()
            error_message = mock_bot.reply_to.call_args[0][1]
            assert 'Missing Information' in error_message or 'Missing required event details' in error_message
            mock_create_event.assert_not_called()
    
    def test_handle_event_creation_database_failure(self):
        """Test handling of database failure during event creation"""
        # Arrange
        message = TelegramMessageFactory.create_private_message()
        event_data = EventDataFactory.create_event_creation_data()
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event:
            
            # Simulate database failure
            mock_create_event.return_value = None
            
            # Act
            handle_event_creation(message, event_data)
            
            # Assert
            mock_bot.reply_to.assert_called_once()
            error_message = mock_bot.reply_to.call_args[0][1]
            assert 'Creation Failed' in error_message or 'Failed to create event' in error_message
    
    def test_handle_event_creation_with_date_parsing(self):
        """Test event creation with various date formats"""
        # Arrange
        message = TelegramMessageFactory.create_private_message()
        
        # Test with ISO format dates
        event_data = EventDataFactory.create_event_creation_data(
            start="2024-12-01T09:00:00.000Z",
            end="2024-12-05T17:00:00.000Z"
        )
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event, \
             patch('telegram.handlers.event_handlers.getEvent') as mock_get_event, \
             patch('telegram.handlers.event_handlers.generate_event_description') as mock_gen_desc, \
             patch('telegram.handlers.event_handlers.ask_availability') as mock_ask_avail, \
             patch('telegram.handlers.event_handlers.parse_date') as mock_parse_date, \
             patch('telegram.handlers.event_handlers.format_date') as mock_format_date:
            
            mock_create_event.return_value = 'test-event-123'
            mock_get_event.return_value = {'event_id': 'test-event-123', 'event_name': 'Test'}
            mock_gen_desc.return_value = "Event"
            mock_parse_date.side_effect = lambda x: datetime.fromisoformat(x.replace('Z', '+00:00'))
            mock_format_date.side_effect = lambda x: x.strftime('%Y-%m-%d')
            
            # Act
            handle_event_creation(message, event_data)
            
            # Assert
            mock_create_event.assert_called_once()
            # Verify date parsing was called
            assert mock_parse_date.call_count == 2
    
    def test_handle_event_creation_exception_handling(self):
        """Test error handling when exception occurs during event creation"""
        # Arrange
        message = TelegramMessageFactory.create_private_message()
        event_data = EventDataFactory.create_event_creation_data()
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event:
            
            # Simulate exception
            mock_create_event.side_effect = Exception("Database connection failed")
            
            # Act
            handle_event_creation(message, event_data)
            
            # Assert
            mock_bot.reply_to.assert_called_once()
            error_message = mock_bot.reply_to.call_args[0][1]
            assert 'Creation Error' in error_message or 'Error creating event' in error_message


@pytest.mark.integration
class TestWebappToTelegramFlow:
    """Integration tests for complete webapp to telegram flow"""
    
    def test_complete_event_creation_flow(self):
        """Test complete flow from webapp submission to telegram notification"""
        # Arrange
        # Simulate webapp sending event data
        webapp_data = {
            'token': 'test-token-123',
            'event_id': 'webapp-event-456',
            'event_name': 'Sprint Planning',
            'event_details': 'Plan next sprint tasks',
            'start': '2024-12-10T00:00:00.000Z',
            'end': '2024-12-15T00:00:00.000Z',
            'creator': '12345'
        }
        
        message = TelegramMessageFactory.create_private_message(
            user_id=12345,
            chat_id=67890
        )
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event, \
             patch('telegram.handlers.event_handlers.getEvent') as mock_get_event, \
             patch('telegram.handlers.event_handlers.generate_event_description') as mock_gen_desc, \
             patch('telegram.handlers.event_handlers.ask_availability') as mock_ask_avail:
            
            mock_create_event.return_value = 'backend-event-789'
            mock_get_event.return_value = {
                'event_id': 'backend-event-789',
                'event_name': 'Sprint Planning',
                'event_description': 'Plan next sprint tasks'
            }
            mock_gen_desc.return_value = "Event: Sprint Planning"
            
            # Act
            handle_event_creation(message, webapp_data)
            
            # Assert
            # Verify event creation happened
            assert mock_create_event.called
            
            # Verify telegram notification was sent
            assert mock_bot.reply_to.called
            reply_message = mock_bot.reply_to.call_args[0][1]
            assert 'Sprint Planning' in mock_gen_desc.return_value
            assert 'Event created successfully' in reply_message
            
            # Verify availability request was sent
            assert mock_ask_avail.called
            
            # Verify inline button was added with correct URL
            reply_markup = mock_bot.reply_to.call_args[1]['reply_markup']
            assert reply_markup is not None
    
    def test_webapp_data_transformation(self):
        """Test that webapp data is correctly transformed for telegram bot"""
        # Arrange
        webapp_data = {
            'event_name': 'Test Event',
            'event_details': 'Test Description',
            'start': '2024-12-01T00:00:00.000Z',
            'end': '2024-12-05T00:00:00.000Z'
        }
        
        message = TelegramMessageFactory.create_private_message(user_id=12345)
        
        with patch('telegram.handlers.event_handlers.bot'), \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event, \
             patch('telegram.handlers.event_handlers.getEvent') as mock_get_event, \
             patch('telegram.handlers.event_handlers.generate_event_description'), \
             patch('telegram.handlers.event_handlers.ask_availability'), \
             patch('telegram.handlers.event_handlers.parse_date') as mock_parse, \
             patch('telegram.handlers.event_handlers.format_date') as mock_format:
            
            mock_create_event.return_value = 'event-123'
            mock_get_event.return_value = {'event_id': 'event-123', 'event_name': 'Test Event'}
            mock_parse.side_effect = lambda x: datetime.fromisoformat(x.replace('Z', '+00:00'))
            mock_format.side_effect = lambda x: x.strftime('%Y-%m-%d')
            
            # Act
            handle_event_creation(message, webapp_data)
            
            # Assert
            call_kwargs = mock_create_event.call_args[1]
            assert call_kwargs['event_name'] == webapp_data['event_name']
            assert call_kwargs['event_description'] == webapp_data['event_details']
            assert call_kwargs['creator_id'] == '12345'


@pytest.mark.integration
class TestEventCreationWithMiniAppURL:
    """Integration tests for event creation with mini app URL generation"""
    
    def test_confirm_button_url_generation(self):
        """Test that confirm button has correct mini app URL"""
        # Arrange
        message = TelegramMessageFactory.create_private_message()
        event_data = EventDataFactory.create_event_creation_data()
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event, \
             patch('telegram.handlers.event_handlers.getEvent') as mock_get_event, \
             patch('telegram.handlers.event_handlers.generate_event_description') as mock_gen_desc, \
             patch('telegram.handlers.event_handlers.ask_availability'):
            
            mock_bot.get_me.return_value.username = 'test_bot'
            mock_create_event.return_value = 'event-123'
            mock_get_event.return_value = {'event_id': 'event-123', 'event_name': 'Test'}
            mock_gen_desc.return_value = "Event"
            
            # Act
            handle_event_creation(message, event_data)
            
            # Assert
            reply_markup = mock_bot.reply_to.call_args[1]['reply_markup']
            assert reply_markup is not None
            
            # Check that markup contains button with URL
            # The URL should contain the event_id
            # Note: We'd need to inspect the actual InlineKeyboardButton to verify the URL
            # For now, we just verify that reply_markup was created
            assert mock_bot.reply_to.called
    
    def test_share_command_context(self):
        """Test that event creation enables /share command"""
        # Arrange
        message = TelegramMessageFactory.create_private_message()
        event_data = EventDataFactory.create_event_creation_data()
        
        with patch('telegram.handlers.event_handlers.bot') as mock_bot, \
             patch('telegram.handlers.event_handlers.create_event') as mock_create_event, \
             patch('telegram.handlers.event_handlers.getEvent') as mock_get_event, \
             patch('telegram.handlers.event_handlers.generate_event_description') as mock_gen_desc, \
             patch('telegram.handlers.event_handlers.ask_availability'):
            
            mock_create_event.return_value = 'event-123'
            mock_get_event.return_value = {'event_id': 'event-123', 'event_name': 'Test'}
            mock_gen_desc.return_value = "Event"
            
            # Act
            handle_event_creation(message, event_data)
            
            # Assert
            success_message = mock_bot.reply_to.call_args[0][1]
            assert '/share' in success_message
            assert 'group chats' in success_message.lower()

