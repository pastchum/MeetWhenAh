# Development Setup Guide

This guide will help you set up local development with HTTPS for Telegram Mini App testing.

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- Telegram Bot Token
- macOS, Windows, or Linux

## Step 1: HTTPS Setup for Local Development

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

## Step 2: Environment Configuration

### Create Environment File

Create `.env.development` in the `bot/` directory:

```bash
# Copy from template
cp bot/config/environment_template.py bot/.env.development
```

Edit `bot/.env.development` with your values:

```bash
ENVIRONMENT=development
BOT_USERNAME=your_dev_bot_username
TOKEN=your_dev_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=true
LOCALHOST_PORT=3000  # Change this to your preferred port (3001, 3002, etc.)
```

### Configure Your Dev Bot

1. Go to [@BotFather](https://t.me/BotFather) on Telegram
2. Use `/mybots` command
3. Select your dev bot
4. Choose "Bot Settings" → "Mini App"
5. Set URL to: `https://localhost:3000` (or your chosen port)

## Step 3: Start Development Servers

### Terminal 1: Start Webapp (HTTPS)

```bash
cd webapp
npm install  # If first time
npm run dev
```

Your webapp will be available at `https://localhost:3000`

### Terminal 2: Start Bot

```bash
cd bot
pip install -r requirements.txt  # If first time
python main.py
```

## Step 4: Testing

1. Message your dev bot on Telegram
2. Use `/create` command
3. Click "Create Event" button
4. The Mini App should open with HTTPS (no browser warnings)

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

## Development Workflow

### For Webapp Development

1. Set `USE_LOCAL_WEBAPP=true` in `.env.development`
2. Bot will use your local HTTPS webapp
3. Changes to webapp code will hot-reload

### For Production Testing

1. Set `USE_LOCAL_WEBAPP=false` in `.env.development`
2. Bot will use production webapp
3. Test with real production data

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Current environment | `development` |
| `BOT_USERNAME` | Your dev bot username | `yourname_dev_bot` |
| `TOKEN` | Your dev bot token | `123456789:ABC...` |
| `WEBAPP_URL` | Production webapp URL | `https://meet-when-ah.vercel.app` |
| `USE_LOCAL_WEBAPP` | Use local webapp for testing | `true` or `false` |
| `LOCALHOST_PORT` | Port for local webapp | `3000`, `3001`, etc. |

## Quick Commands

```bash
# Start everything
cd webapp && npm run dev &
cd bot && python main.py

# Stop everything
# Ctrl+C in both terminals

# Reset certificates
mkcert -uninstall && mkcert -install && mkcert localhost 127.0.0.1 ::1
```

## Need Help?

- Check the terminal output for error messages
- Ensure all environment variables are set correctly
- Verify BotFather Mini App URL matches your localhost port
- Make sure both webapp and bot servers are running
