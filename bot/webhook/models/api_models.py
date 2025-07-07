from pydantic import BaseModel
from typing import List, Optional

class AvailabilityRequest(BaseModel):
    username: str
    event_id: str
    availability_data: Optional[List[dict]] = None

class EventResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    message: Optional[str] = None

class AvailabilityResponse(BaseModel):
    status: str
    data: Optional[List[dict]] = None
    message: Optional[str] = None 