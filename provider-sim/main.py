import asyncio
import logging
import random
import string
from typing import Optional
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import httpx

logging.basicConfig(level=logging.INFO)

app = FastAPI()

class SendRequest(BaseModel):
    message_id: str
    text: str
    callback_url: str

class SendResponse(BaseModel):
    accepted: bool

class CallbackSuccess(BaseModel):
    message_id: str
    status: str = "completed"
    provider_job_id: str

class CallbackError(BaseModel):
    message_id: str
    status: str = "error"
    error: str

def generate_job_id() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

async def process_message(message_id: str, text: str, callback_url: str):
    delay = random.uniform(2.0, 5.0)
    logging.info(f"Processing message {message_id}, sleeping for {delay:.2f}s")
    await asyncio.sleep(delay)
    
    is_success = random.random() < 0.85
    logging.info(f"Message {message_id} result: {'success' if is_success else 'failure'}")
    
    async with httpx.AsyncClient() as client:
        if is_success:
            payload = CallbackSuccess(
                message_id=message_id,
                provider_job_id=generate_job_id()
            ).dict()
        else:
            payload = CallbackError(
                message_id=message_id,
                error="Simulated failure"
            ).dict()
        
        try:
            logging.info(f"Calling callback {callback_url} with payload: {payload}")
            response = await client.post(callback_url, json=payload, timeout=10.0)
            logging.info(f"Callback response: {response.status_code}")
        except Exception as e:
            logging.error(f"Error calling callback: {e}")
            pass

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/send", response_model=SendResponse)
async def send_message(request: SendRequest, background_tasks: BackgroundTasks):
    logging.info(f"Received message: {request.message_id} - {request.text}")
    background_tasks.add_task(process_message, request.message_id, request.text, request.callback_url)
    return SendResponse(accepted=True)