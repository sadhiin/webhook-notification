import asyncio
import logging
import random
import string

import httpx

from app.schemas.callback import CallbackError, CallbackSuccess


def generate_job_id() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))


async def process_message(message_id: str, text: str, callback_url: str) -> None:
    delay = random.uniform(2.0, 5.0)
    logging.info("Processing message %s, sleeping for %.2fs", message_id, delay)
    await asyncio.sleep(delay)

    is_success = random.random() < 0.85
    logging.info("Message %s result: %s", message_id, "success" if is_success else "failure")

    async with httpx.AsyncClient() as client:
        if is_success:
            payload = CallbackSuccess(
                message_id=message_id,
                provider_job_id=generate_job_id(),
            ).model_dump()
        else:
            payload = CallbackError(
                message_id=message_id,
                error="Simulated failure",
            ).model_dump()

        try:
            response = await client.post(callback_url, json=payload, timeout=10.0)
            logging.info("Callback response for %s: %s", message_id, response.status_code)
        except Exception as exc:
            logging.error("Error calling callback for %s: %s", message_id, exc)
