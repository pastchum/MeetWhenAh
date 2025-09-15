# Environment Configuration Guide

This guide explains how to set up different environments (development, staging, production) for the MeetWhenAh bot.

## Overview

The bot supports three environments with different configurations:

- **Development**: Local development with HTTPS support
- **Staging**: Testing environment with restricted access
- **Production**: Live environment for all users

## Environment Files

### Development Environment (.env.development)

```bash
# Development Environment Configuration
ENVIRONMENT=development

# Bot Configuration
BOT_USERNAME=your_dev_bot_username
TOKEN=your_dev_bot_token_here

# Webapp Configuration
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=true
LOCALHOST_PORT=3000

# Database Configuration (Supabase)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Webhook Configuration
USE_WEBHOOK=true
WEBHOOK_URL=https://your-domain.com/webhook

# Optional: Additional Development Settings
DEBUG=true
LOG_LEVEL=debug
```

### Staging Environment (.env.staging)

```bash
# Staging Environment Configuration
ENVIRONMENT=staging

# Bot Configuration
BOT_USERNAME=meeting_the_stage_bot
TOKEN=your_staging_bot_token_here

# Webapp Configuration
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false

# Database Configuration (Supabase)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Webhook Configuration
USE_WEBHOOK=true
WEBHOOK_URL=https://your-staging-domain.com/webhook

# Optional: Additional Staging Settings
DEBUG=false
LOG_LEVEL=info
```

### Production Environment (.env.production)

```bash
# Production Environment Configuration
ENVIRONMENT=production

# Bot Configuration
BOT_USERNAME=MeetWhenAhBot
TOKEN=your_production_bot_token_here

# Webapp Configuration
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false

# Database Configuration (Supabase)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Webhook Configuration
USE_WEBHOOK=true
WEBHOOK_URL=https://your-production-domain.com/webhook

# Optional: Additional Production Settings
DEBUG=false
LOG_LEVEL=warning
```

## Environment-Specific Settings

### Bot Configuration

| Environment | Bot Username | Access Level |
|-------------|--------------|--------------|
| Development | `your_dev_bot_username` | Developer only |
| Staging | `meeting_the_stage_bot` | Developer + testers |
| Production | `MeetWhenAhBot` | All users |

### Webapp Configuration

| Environment | URL | Local Development |
|-------------|-----|-------------------|
| Development | `https://meet-when-ah.vercel.app` or `https://localhost:3000` | `USE_LOCAL_WEBAPP=true` |
| Staging | `https://meet-when-ah.vercel.app` | `USE_LOCAL_WEBAPP=false` |
| Production | `https://meet-when-ah.vercel.app` | `USE_LOCAL_WEBAPP=false` |

### Database Configuration

All environments use the same Supabase instance:
- **SUPABASE_URL**: Your Supabase project URL
- **SUPABASE_KEY**: Your Supabase anon key

## Setup Instructions

### 1. Create Environment Files

```bash
# Create environment files in the bot directory
touch bot/.env.development
touch bot/.env.staging
touch bot/.env.production
```

### 2. Fill in Your Values

For each environment file, replace the placeholder values:

- `your_dev_bot_username` → Your development bot username
- `your_dev_bot_token_here` → Your development bot token
- `your_staging_bot_token_here` → Your staging bot token
- `your_production_bot_token_here` → Your production bot token
- `your_supabase_url_here` → Your Supabase project URL
- `your_supabase_key_here` → Your Supabase anon key
- `https://your-domain.com/webhook` → Your webhook URL

### 3. Bot Setup

#### Development Bot
1. Create a bot with @BotFather
2. Get the bot token
3. Set webhook for local development

#### Staging Bot
1. Create bot: `meeting_the_stage_bot`
2. Restrict access to developers and testers
3. Set webhook for staging domain

#### Production Bot
1. Create bot: `MeetWhenAhBot`
2. Open access to all users
3. Set webhook for production domain

### 4. Webhook Setup

Each environment needs its own webhook URL:

- **Development**: `https://your-dev-domain.com/webhook`
- **Staging**: `https://your-staging-domain.com/webhook`
- **Production**: `https://your-production-domain.com/webhook`

## CI/CD Integration

The environment configuration integrates with the CI/CD pipeline:

- **Development**: Local development with `USE_LOCAL_WEBAPP=true`
- **Staging**: Deploys on `develop` branch push
- **Production**: Deploys on `main` branch push

For detailed setup instructions, see:
- [Development Setup Guide](./development-setup.md) - Local development with HTTPS
- [CI/CD Setup Guide](./ci-cd-setup.md) - Automated deployment pipeline

## Security Notes

- Never commit `.env` files to version control
- Use GitHub Secrets for sensitive values in CI/CD
- Rotate bot tokens regularly
- Use different webhook URLs for each environment
- Restrict staging bot access to authorized users only

## Troubleshooting

### Common Issues

1. **Wrong Bot Username**: Ensure `BOT_USERNAME` matches your actual bot username
2. **Invalid Token**: Verify the bot token is correct and active
3. **Webhook Issues**: Check that webhook URL is accessible and properly configured
4. **Database Connection**: Verify Supabase URL and key are correct

### Debug Mode

Enable debug mode in development:

```bash
DEBUG=true
LOG_LEVEL=debug
```

This will provide detailed logging for troubleshooting.
