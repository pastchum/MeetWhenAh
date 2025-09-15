# Development Setup Guide

This guide will help you set up local development with HTTPS for Telegram Mini App testing.

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- Telegram Bot Token
- macOS, Windows, or Linux

## Step 1: Development Workflow Overview

There are two ways to develop locally:

### Option A: Use Production Webapp (Recommended for Bot Development)
- Bot uses production webapp (`https://meet-when-ah.vercel.app`)
- Fastest setup, works immediately
- Good for testing bot functionality and webapp integration

### Option B: Use Local Webapp with Tunneling (For Webapp Development)
- Bot uses your local webapp via tunneling service (ngrok)
- Required for testing webapp changes locally
- More complex setup but allows full local development

## Step 2: HTTPS Setup for Local Development (Option B Only)

### Install mkcert (Certificate Authority)

**macOS:**
```bash
brew install mkcert
```

**Windows:**
```bash
choco install mkcert
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install libnss3-tools
wget -O mkcert https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
chmod +x mkcert
sudo mv mkcert /usr/local/bin/
```

### Generate Local Certificates

```bash
# Navigate to webapp directory
cd webapp

# Install the local CA
mkcert -install

# Generate certificates for localhost
mkcert localhost 127.0.0.1 ::1
```

This creates two files:
- `localhost+2.pem` (certificate)
- `localhost+2-key.pem` (private key)

## Step 3: Environment Configuration

### Create Environment File

Create `.env.development` in the `bot/` directory:

```bash
# Create the environment file
touch bot/.env.development
```

### Option A: Production Webapp Configuration (Recommended)

Edit `bot/.env.development` for production webapp:

```bash
# Development Environment Configuration
ENVIRONMENT=development

# Bot Configuration
BOT_USERNAME=your_dev_bot_username
TOKEN=your_dev_bot_token_here

# Webapp Configuration
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false

# Database Configuration (Supabase)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Webhook Configuration
USE_WEBHOOK=false
# WEBHOOK_URL not needed for local development (uses polling)

# Optional: Additional Development Settings
DEBUG=true
LOG_LEVEL=debug
```

### Option B: Local Webapp Configuration (For Webapp Development)

Edit `bot/.env.development` for local webapp with tunneling:

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
USE_WEBHOOK=false
# WEBHOOK_URL not needed for local development (uses polling)

# Optional: Additional Development Settings
DEBUG=true
LOG_LEVEL=debug
```

### Configure Your Dev Bot

#### For Option A (Production Webapp):
1. Go to [@BotFather](https://t.me/BotFather) on Telegram
2. Use `/mybots` command
3. Select your dev bot
4. Choose "Bot Settings" → "Mini App"
5. Set URL to: `https://meet-when-ah.vercel.app`

#### For Option B (Local Webapp with Tunneling):
1. Go to [@BotFather](https://t.me/BotFather) on Telegram
2. Use `/mybots` command
3. Select your dev bot
4. Choose "Bot Settings" → "Mini App"
5. Set URL to: `https://your-ngrok-url.ngrok.io` (see Step 4 for setup)

## Step 4: Start Development Servers

### Option A: Production Webapp Development

#### Terminal 1: Start Bot Only
```bash
cd bot
pip install -r requirements.txt  # If first time
python main.py
```

**Testing:**
1. Message your dev bot on Telegram
2. Use `/create` command
3. Click "Create Event" button
4. The Mini App will open the production webapp

### Option B: Local Webapp Development with Tunneling

#### Install ngrok
```bash
# Install ngrok globally
npm install -g ngrok

# Or download from https://ngrok.com/download
```

#### Terminal 1: Start Local Webapp (HTTPS)
```bash
cd webapp
npm install  # If first time
npm run dev
```

Your webapp will be available at `https://localhost:3000`

#### Terminal 2: Start ngrok Tunnel
```bash
# Expose your local webapp to the internet
ngrok http 3000
```

This will give you a URL like: `https://abc123.ngrok.io`

#### Terminal 3: Start Bot
```bash
cd bot
pip install -r requirements.txt  # If first time
python main.py
```

**Testing:**
1. Update BotFather Mini App URL to your ngrok URL (e.g., `https://abc123.ngrok.io`)
2. Message your dev bot on Telegram
3. Use `/create` command
4. Click "Create Event" button
5. The Mini App will open your local webapp via ngrok

## Troubleshooting

### Certificate Issues

If you get certificate errors:

```bash
# Reinstall certificates
mkcert -uninstall
mkcert -install
mkcert localhost 127.0.0.1 ::1
```

### Port Conflicts

If port 3000 is busy:

1. Change `LOCALHOST_PORT=3001` in `.env.development`
2. Update BotFather Mini App URL to `https://localhost:3001`
3. Restart both servers

### Bot Not Responding

1. Check your bot token in `.env.development`
2. Ensure bot is running without errors
3. Check BotFather Mini App URL configuration

### ngrok Issues

If using local webapp with ngrok:

1. **ngrok URL not working**:
   - Ensure ngrok is running: `ngrok http 3000`
   - Check that your local webapp is running on port 3000
   - Update BotFather Mini App URL to the new ngrok URL

2. **ngrok URL changes frequently**:
   - Free ngrok URLs change on restart
   - Consider ngrok paid plan for static URLs
   - Or use production webapp for stable development

3. **ngrok connection issues**:
   - Check internet connection
   - Try restarting ngrok
   - Use `ngrok http 3000 --log=stdout` for debugging

## Development Workflow

### For Bot Development (Recommended)

1. Use **Option A** configuration (`USE_LOCAL_WEBAPP=false`)
2. Bot uses production webapp
3. Focus on bot functionality, handlers, and business logic
4. Fastest setup, works immediately

### For Webapp Development

1. Use **Option B** configuration (`USE_LOCAL_WEBAPP=true`)
2. Set up ngrok tunnel to expose local webapp
3. Update BotFather Mini App URL to ngrok URL
4. Changes to webapp code will hot-reload
5. Test webapp changes with real bot integration

### Switching Between Modes

To switch between development modes:

```bash
# Switch to production webapp
sed -i 's/USE_LOCAL_WEBAPP=true/USE_LOCAL_WEBAPP=false/' bot/.env.development

# Switch to local webapp
sed -i 's/USE_LOCAL_WEBAPP=false/USE_LOCAL_WEBAPP=true/' bot/.env.development
```

**Remember to update BotFather Mini App URL when switching!**

## Webhook vs Polling for Local Development

**Local Development Uses Polling**:
- **`USE_WEBHOOK=false`**: Bot polls Telegram for updates (recommended for local development)
- **`WEBHOOK_URL`**: Not needed - bot automatically polls for updates
- **Why polling?**: Simpler local development, no HTTPS webhook setup needed
- **Ngrok**: Only needed if testing local webapp (`USE_LOCAL_WEBAPP=true`), not for bot polling

**Production/Staging Uses Webhooks**:
- **`USE_WEBHOOK=true`**: Bot receives updates via HTTP webhook
- **`WEBHOOK_URL`**: Required - tells Telegram where to send updates
- **Why webhook?**: More efficient, scales better, required for production

**Common Confusion**:
- **Bot webhook** ≠ **Webapp hosting**
- **Bot polling** works fine locally without HTTPS
- **Webapp** always needs HTTPS (Telegram Mini App requirement)

## Environment Variables Reference

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Current environment | `development` | ✅ |
| `BOT_USERNAME` | Your dev bot username | `yourname_dev_bot` | ✅ |
| `TOKEN` | Your dev bot token | `123456789:ABC...` | ✅ |
| `WEBAPP_URL` | Production webapp URL | `https://meet-when-ah.vercel.app` | ✅ |
| `USE_LOCAL_WEBAPP` | Use local webapp for testing | `true` or `false` | ✅ |
| `LOCALHOST_PORT` | Port for local webapp | `3000`, `3001`, etc. | ✅ |
| `SUPABASE_URL` | Supabase project URL | `https://xxx.supabase.co` | ✅ |
| `SUPABASE_KEY` | Supabase anon key | `eyJhbGciOiJIUzI1NiIs...` | ✅ |
| `USE_WEBHOOK` | Enable webhook mode | `false` (local), `true` (prod) | ✅ |
| `WEBHOOK_URL` | Webhook endpoint URL | Not needed for local | ❌ (local) |
| `DEBUG` | Enable debug mode | `true` or `false` | ❌ |
| `LOG_LEVEL` | Logging level | `debug`, `info`, `warning` | ❌ |

## Quick Commands

### Option A: Production Webapp Development
```bash
# Start bot only
cd bot && python main.py
```

### Option B: Local Webapp Development
```bash
# Start webapp
cd webapp && npm run dev

# Start ngrok tunnel (in another terminal)
ngrok http 3000

# Start bot (in another terminal)
cd bot && python main.py
```

### Utility Commands
```bash
# Reset certificates (if using local webapp)
mkcert -uninstall && mkcert -install && mkcert localhost 127.0.0.1 ::1

# Switch to production webapp mode
sed -i 's/USE_LOCAL_WEBAPP=true/USE_LOCAL_WEBAPP=false/' bot/.env.development

# Switch to local webapp mode
sed -i 's/USE_LOCAL_WEBAPP=false/USE_LOCAL_WEBAPP=true/' bot/.env.development
```

## CI/CD Integration

This development setup integrates with the CI/CD pipeline:

- **Local Development**: Use your dev bot with `USE_LOCAL_WEBAPP=true`
- **Staging Deployment**: 
  - Push to `staging` branch
  - GitHub Actions runs tests
  - If tests pass: Coolify deploys bot API + Vercel creates webapp preview
- **Production Deployment**: 
  - Push to `main` branch
  - GitHub Actions runs tests
  - If tests pass: Coolify deploys bot API + Vercel deploys webapp to main URL

For more details, see:
- [Environment Configuration Guide](./environment-configuration.md)
- [CI/CD Setup Guide](./ci-cd-setup.md)

## Need Help?

- Check the terminal output for error messages
- Ensure all environment variables are set correctly
- Verify BotFather Mini App URL matches your localhost port
- Make sure both webapp and bot servers are running
- Review the [Environment Configuration Guide](./environment-configuration.md) for complete setup
