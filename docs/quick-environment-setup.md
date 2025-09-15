# Quick Environment Setup Reference

This is a quick reference for setting up the three environments for MeetWhenAh bot.

## 🚀 Quick Setup Checklist

### 1. Create Environment Files

```bash
# Create environment files in the bot directory
touch bot/.env.development
touch bot/.env.staging
touch bot/.env.production
```

### 2. Fill in Bot Tokens

| Environment | Bot Username | Token Source |
|-------------|--------------|--------------|
| Development | `your_dev_bot_username` | Your existing dev bot |
| Staging | `meeting_the_stage_bot` | Create new bot with @BotFather |
| Production | `MeetWhenAhBot` | Create new bot with @BotFather |

### 3. Set Webhook URLs

| Environment | Webhook URL |
|-------------|-------------|
| Development | `https://your-dev-domain.com/webhook` |
| Staging | `https://your-staging-domain.com/webhook` |
| Production | `https://your-production-domain.com/webhook` |

### 4. GitHub Secrets

Add these to your GitHub repository secrets:

```
STAGING_BOT_TOKEN=your_staging_bot_token_here
PRODUCTION_BOT_TOKEN=your_production_bot_token_here
COOLIFY_STAGING_WEBHOOK=https://your-coolify-staging-webhook-url
COOLIFY_PRODUCTION_WEBHOOK=https://your-coolify-production-webhook-url
```

### 5. Coolify Projects

Create two projects in Coolify:

- **Staging Project**: Deploy from `develop` branch
- **Production Project**: Deploy from `main` branch

### 6. ngrok Setup (For Local Webapp Development)

If you want to test local webapp changes:

```bash
# Install ngrok
npm install -g ngrok

# Start your local webapp
cd webapp && npm run dev

# In another terminal, start ngrok
ngrok http 3000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
# Update BotFather Mini App URL to this ngrok URL
```

## 📋 Environment File Templates

### Development (.env.development)

#### Option A: Production Webapp (Recommended)
```bash
ENVIRONMENT=development
BOT_USERNAME=your_dev_bot_username
TOKEN=your_dev_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
USE_WEBHOOK=true
WEBHOOK_URL=https://your-dev-domain.com/webhook
```

#### Option B: Local Webapp with Tunneling
```bash
ENVIRONMENT=development
BOT_USERNAME=your_dev_bot_username
TOKEN=your_dev_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=true
LOCALHOST_PORT=3000
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
USE_WEBHOOK=true
WEBHOOK_URL=https://your-dev-domain.com/webhook
```

### Staging (.env.staging)
```bash
ENVIRONMENT=staging
BOT_USERNAME=meeting_the_stage_bot
TOKEN=your_staging_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
USE_WEBHOOK=true
WEBHOOK_URL=https://your-staging-domain.com/webhook
```

### Production (.env.production)
```bash
ENVIRONMENT=production
BOT_USERNAME=MeetWhenAhBot
TOKEN=your_production_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
USE_WEBHOOK=true
WEBHOOK_URL=https://your-production-domain.com/webhook
```

## 🔧 Bot Creation Commands

### Staging Bot
```
/newbot
Bot name: MeetWhenAh Staging
Username: meeting_the_stage_bot
```

### Production Bot
```
/newbot
Bot name: MeetWhenAh
Username: MeetWhenAhBot
```

## 🚀 Development Workflow

### Option A: Production Webapp Development (Recommended)
1. **Setup**: Use production webapp configuration
2. **BotFather**: Set Mini App URL to `https://meet-when-ah.vercel.app`
3. **Development**: Focus on bot functionality
4. **Testing**: Test with production webapp

### Option B: Local Webapp Development
1. **Setup**: Use local webapp configuration
2. **Tunneling**: Start ngrok tunnel (`ngrok http 3000`)
3. **BotFather**: Set Mini App URL to ngrok URL
4. **Development**: Test webapp changes locally
5. **Testing**: Test with local webapp via tunnel

## 🚀 Deployment Flow

1. **Development**: Work locally with your dev bot
2. **Push to `develop`**: Automatically deploys to staging
3. **Push to `main`**: Automatically deploys to production

## ✅ Verification

After setup, verify each environment:

```bash
# Test development
cd bot
ENVIRONMENT=development python -c "from utils.mini_app_url import get_mini_app_url; print(get_mini_app_url('test'))"

# Test staging
ENVIRONMENT=staging python -c "from utils.mini_app_url import get_mini_app_url; print(get_mini_app_url('test'))"

# Test production
ENVIRONMENT=production python -c "from utils.mini_app_url import get_mini_app_url; print(get_mini_app_url('test'))"
```

## 🆘 Troubleshooting

- **Bot not responding**: Check token and webhook URL
- **Tests failing**: Run `cd bot && python -m pytest tests/ -v`
- **Deployment failing**: Check Coolify webhook URLs and GitHub secrets
- **Wrong environment**: Verify `ENVIRONMENT` variable in your .env file

## 📚 Additional Resources

For detailed setup instructions, see:
- [Development Setup Guide](./development-setup.md) - Local development with HTTPS
- [Environment Configuration Guide](./environment-configuration.md) - Complete environment setup
- [CI/CD Setup Guide](./ci-cd-setup.md) - Automated deployment pipeline
- [Testing Guide](./testing-guide.md) - Test suite and running tests
