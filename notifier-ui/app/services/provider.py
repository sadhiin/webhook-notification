import logging

import httpx

from app.core.config import settings
from app.db.repository import update_message_status
from app.realtime.manager import manager


async def call_provider_async(message_uuid: str, text: str) -> None:
    logging.info("Starting async call to provider for message %s", message_uuid)

    provider_payload = {
        "message_id": message_uuid,
        "text": text,
        "callback_url": settings.callback_url,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.provider_sim_url}/api/send",
                json=provider_payload,
                timeout=10.0,
            )
            logging.info("Provider response: %s - %s", response.status_code, response.text)
        except Exception as exc:
            logging.error("Error calling provider for message %s: %s", message_uuid, exc)


async def process_provider_callback(request_data: dict) -> None:
    status_value = request_data.get("status")
    if status_value == "completed":
        new_status = 1
    elif status_value == "error" or request_data.get("error"):
        new_status = 2
    else:
        new_status = 0

    await update_message_status(request_data["message_id"], new_status)

    await manager.broadcast_message_update(
        {
            "message_uuid": request_data["message_id"],
            "status": new_status,
            "provider_job_id": request_data.get("provider_job_id"),
            "error": request_data.get("error"),
        }
    )
