# Quick Start Guide

## For New Developers

### 1. Run Setup Script

**macOS/Linux:**
```bash
./scripts/setup-dev.sh
```

**Windows:**
```cmd
scripts\setup-dev.bat
```

### 2. Configure Your Bot

1. Edit `bot/.env.development` with your bot credentials
2. Go to [@BotFather](https://t.me/BotFather)
3. `/mybots` → Your Bot → Mini App
4. Set URL to: `https://localhost:3000` (or your chosen port)

### 3. Start Development

**Terminal 1 (Webapp):**
```bash
cd webapp
npm run dev
```

**Terminal 2 (Bot):**
```bash
cd bot
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
python main.py
```

### 4. Run Tests

**From project root directory:**
```bash
# Run all tests
./scripts/run-tests.sh

# Run with coverage
./scripts/run-tests.sh --coverage

# Run only unit tests
./scripts/run-tests.sh --markers "unit"
```

**Or using Makefile:**
```bash
cd bot
make test-coverage
```

## Environment Variables

| Variable | Kaung's Value | Pat's Value |
|----------|------------|----------------|
| `BOT_USERNAME` | `kzynmeetsme_bot` | `meetwhenahdev_bot` |
| `TOKEN` | Kaung's dev token | Pat's dev token |
| `LOCALHOST_PORT` | `3000` | `3001` (or any free port) |

## Common Issues

### Port Already in Use
Change `LOCALHOST_PORT=3001` in `.env.development` and update BotFather URL

### Certificate Errors
```bash
mkcert -uninstall
mkcert -install
mkcert localhost 127.0.0.1 ::1
```

### Bot Not Responding
- Check token in `.env.development`
- Ensure bot is running without errors
- Verify BotFather Mini App URL

## Development Modes

### Local Webapp Testing
```bash
USE_LOCAL_WEBAPP=true
```
Bot uses your local HTTPS webapp

### Production Webapp Testing
```bash
USE_LOCAL_WEBAPP=false
```
Bot uses production webapp

## Need Help?

See [development-setup.md](development-setup.md) for detailed instructions.
