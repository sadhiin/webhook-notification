from pydantic import BaseModel


class SendRequest(BaseModel):
    message_id: str
    text: str
    callback_url: str


class SendResponse(BaseModel):
    accepted: bool
