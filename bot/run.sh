#OUTDATED, DO NOT USE

#!/bin/bash

# Kill any existing Python processes
pkill -f "python main.py"
pkill -f "python server.py"

# Environment variables
export WEBHOOK_URL="https://deploy.jensenhshoots.com/webhook/bot"
export USE_WEBHOOK=true
export PORT=8000
export PYTHONPATH=/Users/kaungzinye/Documents/SWE/meetWhenAh:/Users/kaungzinye/Documents/SWE/meetWhenAh/bot

# Start the server in the background
cd ../webapp/backend/src && python server.py &
SERVER_PID=$!

# Wait a bit for the server to start
sleep 2

# Start the bot
cd ../../../bot && python main.py &
BOT_PID=$!

# Function to handle cleanup
cleanup() {
    echo "Cleaning up..."
    kill $SERVER_PID
    kill $BOT_PID
    exit
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait 