import os
import uuid
from datetime import datetime, timedelta

# import from services
from services.database_service import getEntry, setEntry, updateEntry, getEntries

EXPIRY_TIME = 60 * 15 # 15 minutes

def put_ctx(user_id: str, chat_id: str, message_id: str, thread_id: str | None, exp: int = EXPIRY_TIME) -> str:
    token = str(uuid.uuid4().hex)
    expires_at = datetime.now() + timedelta(seconds=exp)
    data = {
        "tele_id": user_id,
        "chat_id": chat_id,
        "thread_id": thread_id,
        "message_id": message_id,
        "expires_at": expires_at
    }
    setEntry("webapp_share_tokens", token, data)
    return token

def get_ctx(token: str) -> dict:
    return getEntry("webapp_share_tokens", token)