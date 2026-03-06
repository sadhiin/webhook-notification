import logging

from fastapi import BackgroundTasks, FastAPI

from app.schemas.message import SendRequest, SendResponse
from app.services.processor import process_message

logging.basicConfig(level=logging.INFO)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/send", response_model=SendResponse)
async def send_message(request: SendRequest, background_tasks: BackgroundTasks):
    logging.info("Received message: %s - %s", request.message_id, request.text)
    background_tasks.add_task(process_message, request.message_id, request.text, request.callback_url)
    return SendResponse(accepted=True)
