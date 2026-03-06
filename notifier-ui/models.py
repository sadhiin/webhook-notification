from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    message_id: int
    message_uuid: str
    status: int
    text: str
    created_at: datetime
    updated_at: datetime


class CreateMessageRequest(BaseModel):
    text: str


class CreateMessageResponse(BaseModel):
    id: str
    text: str
    status: int


class ProviderCallbackRequest(BaseModel):
    message_id: str
    status: str
    provider_job_id: Optional[str] = None
    error: Optional[str] = None