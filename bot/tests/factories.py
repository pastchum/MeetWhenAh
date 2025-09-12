"""
Test data factories for creating consistent test objects.
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock
import uuid


class TelegramMessageFactory:
    """Factory for creating Telegram message objects for testing"""
    
    @staticmethod
    def create_message(
        user_id=12345,
        username="testuser",
        chat_id=67890,
        chat_type="private",
        text="/test",
        message_id=111,
        thread_id=None
    ):
        """Create a mock Telegram message"""
        message = MagicMock()
        message.from_user.id = user_id
        message.from_user.username = username
        message.from_user.first_name = "Test"
        message.from_user.last_name = "User"
        message.chat.id = chat_id
        message.chat.type = chat_type
        message.message_thread_id = thread_id
        message.message_id = message_id
        message.text = text
        message.date = datetime.now(timezone.utc)
        return message
    
    @staticmethod
    def create_group_message(**kwargs):
        """Create a group message"""
        return TelegramMessageFactory.create_message(
            chat_type="group",
            **kwargs
        )
    
    @staticmethod
    def create_private_message(**kwargs):
        """Create a private message"""
        return TelegramMessageFactory.create_message(
            chat_type="private",
            **kwargs
        )


class TelegramCallbackQueryFactory:
    """Factory for creating Telegram callback query objects for testing"""
    
    @staticmethod
    def create_callback_query(
        user_id=12345,
        username="testuser",
        data="test:data",
        chat_id=67890,
        message_id=111,
        thread_id=None
    ):
        """Create a mock Telegram callback query"""
        callback_query = MagicMock()
        callback_query.from_user.id = user_id
        callback_query.from_user.username = username
        callback_query.from_user.first_name = "Test"
        callback_query.from_user.last_name = "User"
        callback_query.data = data
        callback_query.id = f"callback_{uuid.uuid4().hex[:8]}"
        
        # Mock message within callback query
        callback_query.message = MagicMock()
        callback_query.message.chat.id = chat_id
        callback_query.message.message_id = message_id
        callback_query.message.message_thread_id = thread_id
        
        return callback_query


class UserDataFactory:
    """Factory for creating user data objects for testing"""
    
    @staticmethod
    def create_user(
        uuid_str=None,
        tele_id="12345",
        tele_user="testuser",
        initialised=True,
        created_at=None
    ):
        """Create user data"""
        return {
            'uuid': uuid_str or str(uuid.uuid4()),
            'tele_id': tele_id,
            'tele_user': tele_user,
            'initialised': initialised,
            'created_at': created_at or datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def create_multiple_users(count=3):
        """Create multiple user data objects"""
        return [
            UserDataFactory.create_user(
                tele_id=str(10000 + i),
                tele_user=f"user{i}"
            )
            for i in range(count)
        ]


class EventDataFactory:
    """Factory for creating event data objects for testing"""
    
    @staticmethod
    def create_event(
        event_id=None,
        event_name="Test Event",
        event_description="Test Description",
        creator_uuid=None,
        start_date="2024-01-01",
        end_date="2024-01-02"
    ):
        """Create event data"""
        return {
            'event_id': event_id or str(uuid.uuid4()),
            'event_name': event_name,
            'event_description': event_description,
            'event_type': 'general',
            'start_date': start_date,
            'end_date': end_date,
            'start_hour': '09:00:00',
            'end_hour': '17:00:00',
            'creator': creator_uuid or str(uuid.uuid4()),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'min_participants': 2,
            'min_duration': 2,
            'max_duration': 4,
            'is_reminders_enabled': True,
            'timezone': 'Asia/Singapore'
        }
    
    @staticmethod
    def create_event_creation_data(
        event_name="Test Event",
        event_details="Test Description",
        start="2024-01-01",
        end="2024-01-02"
    ):
        """Create event creation data (from webapp)"""
        return {
            'event_name': event_name,
            'event_details': event_details,
            'start': start,
            'end': end
        }


class AvailabilityDataFactory:
    """Factory for creating availability data objects for testing"""
    
    @staticmethod
    def create_availability(
        user_uuid=None,
        event_id=None,
        date="2024-01-01",
        start_time="09:00",
        end_time="17:00"
    ):
        """Create availability data"""
        return {
            'user_uuid': user_uuid or str(uuid.uuid4()),
            'event_id': event_id or str(uuid.uuid4()),
            'date': date,
            'start_time': start_time,
            'end_time': end_time
        }
    
    @staticmethod
    def create_multiple_availability_slots(
        user_uuid=None,
        event_id=None,
        dates=None,
        start_time="09:00",
        end_time="17:00"
    ):
        """Create multiple availability slots"""
        if dates is None:
            dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
        
        return [
            AvailabilityDataFactory.create_availability(
                user_uuid=user_uuid,
                event_id=event_id,
                date=date,
                start_time=start_time,
                end_time=end_time
            )
            for date in dates
        ]


class MembershipDataFactory:
    """Factory for creating membership data objects for testing"""
    
    @staticmethod
    def create_membership(
        event_id=None,
        user_uuid=None,
        joined_at=None,
        emoji_icon="👋"
    ):
        """Create membership data"""
        return {
            'event_id': event_id or str(uuid.uuid4()),
            'user_uuid': user_uuid or str(uuid.uuid4()),
            'joined_at': joined_at or datetime.now(timezone.utc).isoformat(),
            'emoji_icon': emoji_icon
        }


class BotFactory:
    """Factory for creating bot objects for testing"""
    
    @staticmethod
    def create_bot(username="test_bot"):
        """Create a mock bot"""
        bot = MagicMock()
        bot.get_me.return_value.username = username
        bot.reply_to.return_value = MagicMock(message_id=111)
        bot.send_message.return_value = MagicMock(message_id=111)
        bot.edit_message_text.return_value = True
        bot.answer_callback_query.return_value = True
        return bot


class EnvironmentFactory:
    """Factory for creating environment configurations for testing"""
    
    @staticmethod
    def create_development_env(
        bot_username="test_dev_bot",
        use_local_webapp=True,
        localhost_port="3000"
    ):
        """Create development environment variables"""
        return {
            'ENVIRONMENT': 'development',
            'BOT_USERNAME': bot_username,
            'WEBAPP_URL': 'https://meet-when-ah.vercel.app',
            'USE_LOCAL_WEBAPP': str(use_local_webapp).lower(),
            'LOCALHOST_PORT': localhost_port
        }
    
    @staticmethod
    def create_staging_env(bot_username="meeting_the_stage_bot"):
        """Create staging environment variables"""
        return {
            'ENVIRONMENT': 'staging',
            'BOT_USERNAME': bot_username,
            'WEBAPP_URL': 'https://meet-when-ah.vercel.app',
            'USE_LOCAL_WEBAPP': 'false'
        }
    
    @staticmethod
    def create_production_env(bot_username="MeetWhenAhBot"):
        """Create production environment variables"""
        return {
            'ENVIRONMENT': 'production',
            'BOT_USERNAME': bot_username,
            'WEBAPP_URL': 'https://meet-when-ah.vercel.app',
            'USE_LOCAL_WEBAPP': 'false'
        }
