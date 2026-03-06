from pydantic import BaseModel


class CallbackSuccess(BaseModel):
    message_id: str
    status: str = "completed"
    provider_job_id: str


class CallbackError(BaseModel):
    message_id: str
    status: str = "error"
    error: str
