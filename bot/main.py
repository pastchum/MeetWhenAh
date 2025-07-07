from telegram.telegram_bot import initialise_bot
from webhook.server import app

def main():
    initialise_bot()
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    main()