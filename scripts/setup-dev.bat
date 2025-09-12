@echo off
REM Development Setup Script for MeetWhenAh (Windows)
REM This script helps set up local HTTPS development environment

echo 🚀 Setting up MeetWhenAh development environment...

REM Check if mkcert is installed
where mkcert >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ mkcert is not installed. Please install it first:
    echo    Windows: choco install mkcert
    echo    Or download from: https://github.com/FiloSottile/mkcert/releases
    pause
    exit /b 1
)

REM Navigate to webapp directory
cd webapp

REM Install local CA if not already installed
echo 📜 Installing local CA...
mkcert -install

REM Generate certificates
echo 🔐 Generating HTTPS certificates...
mkcert localhost 127.0.0.1 ::1

REM Check if certificates were created
if not exist "localhost+2.pem" (
    echo ❌ Failed to generate certificates
    pause
    exit /b 1
)

echo ✅ Certificates generated successfully!

REM Go back to root directory
cd ..

REM Check if .env.development exists
if not exist "bot\.env.development" (
    echo 📝 Creating .env.development file...
    (
        echo ENVIRONMENT=development
        echo BOT_USERNAME=your_dev_bot_username
        echo TOKEN=your_dev_bot_token_here
        echo WEBAPP_URL=https://meet-when-ah.vercel.app
        echo USE_LOCAL_WEBAPP=true
        echo LOCALHOST_PORT=3000
    ) > bot\.env.development
    echo ⚠️  Please edit bot\.env.development with your bot credentials
) else (
    echo ✅ .env.development already exists
)

REM Install dependencies
echo 📦 Installing dependencies...

REM Install webapp dependencies
cd webapp
if not exist "node_modules" (
    echo Installing webapp dependencies...
    npm install
)
cd ..

REM Install bot dependencies
cd bot
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing bot dependencies...
pip install -r requirements.txt

cd ..

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit bot\.env.development with your bot credentials
echo 2. Configure your bot in BotFather:
echo    - Go to @BotFather
echo    - /mybots → Your Bot → Mini App
echo    - Set URL to: https://localhost:3000
echo.
echo 3. Start development servers:
echo    Terminal 1: cd webapp ^&^& npm run dev
echo    Terminal 2: cd bot ^&^& venv\Scripts\activate ^&^& python main.py
echo.
echo 📚 For detailed instructions, see docs\development-setup.md
pause
