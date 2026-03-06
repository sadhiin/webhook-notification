from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query

from app.db.repository import create_message, get_latest_messages
from app.schemas.message import CreateMessageRequest, CreateMessageResponse, Message
from app.services.provider import call_provider_async

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.get("", response_model=List[Message])
async def get_messages(limit: int = Query(default=10, ge=1, le=100)):
    try:
        return await get_latest_messages(limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("", response_model=CreateMessageResponse)
async def create_message_endpoint(
    request: CreateMessageRequest,
    background_tasks: BackgroundTasks,
):
    try:
        message = await create_message(request.text)
        message_uuid = message["message_uuid"]
        background_tasks.add_task(call_provider_async, message_uuid, request.text)
        return CreateMessageResponse(id=message_uuid, text=request.text, status=0)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
