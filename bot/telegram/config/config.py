import os
import logging
from dotenv import load_dotenv
import telebot
from telebot.handler_backends import State, StatesGroup
from telebot import apihelper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise ValueError("No TOKEN found in environment variables")

logger.info(f"Initializing bot with token: {TOKEN[:5]}...{TOKEN[-5:]}")

# Enable middleware
apihelper.ENABLE_MIDDLEWARE = True

# Initialize bot with proper configuration
bot = telebot.TeleBot(
    TOKEN,
    parse_mode='HTML',
    skip_pending=True,  # Skip pending messages on startup
    num_threads=4,      # Use multiple threads for better performance
    threaded=True       # Enable threaded mode
)

# Define bot commands
BOT_COMMANDS = [
    telebot.types.BotCommand("/start", "Start the bot and create events"),
    telebot.types.BotCommand("/help", "Show help message"),
    telebot.types.BotCommand("/sleep", "Set your sleep hours"),
    #telebot.types.BotCommand("/myavailability", "Check your availability for an event"),
    #telebot.types.BotCommand("/updateavailability", "Update your availability for an event")
]

# Set commands
try:
    bot.set_my_commands(BOT_COMMANDS)
    logger.info("Bot commands set successfully")
except Exception as e:
    logger.error(f"Failed to set commands: {e}")

# Add a test handler to verify bot is working
@bot.message_handler(commands=['test'])
def test_command(message):
    logger.info(f"Received test command from {message.from_user.username}")
    bot.reply_to(message, "Bot is working!")

# States for conversation handling
class BotStates(StatesGroup):
    waiting_for_sleep_start = State()
    waiting_for_sleep_end = State()
    waiting_for_event_id = State() 