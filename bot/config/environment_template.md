# Environment Configuration Template
# Copy this to .env files for different environments

# Development Environment (.env.development)
DEVELOPMENT_CONFIG = """
ENVIRONMENT=development
BOT_USERNAME=kzynmeetsme_bot
TOKEN=your_dev_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false
LOCALHOST_PORT=3000
"""

# Staging Environment (.env.staging)
STAGING_CONFIG = """
ENVIRONMENT=staging
BOT_USERNAME=meeting_the_stage_bot
TOKEN=your_staging_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false
"""

# Production Environment (.env.production)
PRODUCTION_CONFIG = """
ENVIRONMENT=production
BOT_USERNAME=MeetWhenAhBot
TOKEN=your_production_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false
"""
