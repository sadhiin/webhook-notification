import os
import logging
import httpx
from database import update_message_status
from websocket_manager import manager


PROVIDER_SIM_URL = os.getenv("PROVIDER_SIM_URL", "http://provider-sim:8000")


async def call_provider_async(message_uuid: str, text: str):
    logging.info(f"Starting async call to provider for message {message_uuid}")
    
    async with httpx.AsyncClient() as client:
        provider_payload = {
            "message_id": message_uuid,
            "text": text,
            "callback_url": "http://notifier-ui:8000/api/provider-callback"
        }
        
        try:
            logging.info(f"Calling provider-sim at {PROVIDER_SIM_URL}/api/send with payload: {provider_payload}")
            response = await client.post(
                f"{PROVIDER_SIM_URL}/api/send",
                json=provider_payload,
                timeout=10.0
            )
            logging.info(f"Provider response: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error calling provider: {e}")
            pass


async def process_provider_callback(request_data: dict):
    """Process provider callback and broadcast updates"""
    if request_data["status"] == "completed":
        new_status = 1
    elif request_data["status"] == "error" or request_data.get("error"):
        new_status = 2
    else:
        new_status = 0
    
    await update_message_status(request_data["message_id"], new_status)
    
    # Broadcast the update to all connected clients
    await manager.broadcast_message_update({
        "message_uuid": request_data["message_id"],
        "status": new_status,
        "provider_job_id": request_data.get("provider_job_id"),
        "error": request_data.get("error")
    })