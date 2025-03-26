# Meet When Ah? Backend

This is the backend for the Meet When Ah? application, which helps groups find the optimal time to meet based on everyone's availability.

## Features

- Telegram bot integration for creating events and setting availability
- FastAPI server for direct API access
- Smart scheduling algorithm that considers:
  - Sleep hours preferences
  - Contiguous time blocks
  - Partial overlaps in availability
  - Time of day preferences
- User availability patterns saved by event type
- Username tracking and updates

## Getting Started

### Prerequisites

- Python 3.7+
- Firebase account with Firestore database
- Telegram Bot token

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Firebase credentials:
   - Place your Firebase Admin SDK key file in the python-backend directory

4. Set up your environment variables:
   - Create a `.env` file in the python-backend directory
   - Add your Telegram Bot token: `TOKEN=your_telegram_bot_token`

### Running the Backend

There are three ways to run the backend:

1. Run both the Telegram bot and FastAPI server:
   ```
   python run_both.py
   ```

2. Run only the Telegram bot:
   ```
   python telegram.py
   ```

3. Run only the FastAPI server:
   ```
   python start_server.py
   ```

## API Endpoints

The FastAPI server provides these endpoints:

- `GET /api/availability/{username}/{event_id}` - Get a user's availability for an event
- `POST /api/availability` - Update a user's availability for an event
  - Request body:
    ```json
    {
      "username": "kaungzinye",
      "event_id": "event_id_string",
      "availability_data": [
        {"date": "2023-11-15", "time": "1430"},
        {"date": "2023-11-15", "time": "1500"}
      ]
    }
    ```
- `GET /api/event/{event_id}` - Get event details

## Telegram Bot Commands

- `/start` - Create a new event
- `/sleep` - Set your sleep hours to improve scheduling
- `/myavailability` - Check your availability for an event
- `/updateavailability` - Update your availability for an existing event

## Scheduling Algorithm

The scheduling algorithm (`scheduling.py`) finds optimal meeting times by:

1. Identifying contiguous blocks of time when users are available
2. Scoring these blocks based on:
   - Number of participants available
   - Length of the block
   - Time of day (preferring business hours)
   - Avoiding users' sleep hours
3. Selecting the highest-scoring block as the recommended meeting time

## License

MIT