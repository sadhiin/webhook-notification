import logging
from typing import List
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from models import Message, CreateMessageRequest, CreateMessageResponse, ProviderCallbackRequest
from database import get_latest_messages, create_message
from websocket_manager import manager
from services import call_provider_async, process_provider_callback

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/api/messages", response_model=List[Message])
async def get_messages(limit: int = Query(default=10, ge=1, le=100)):
    try:
        messages = await get_latest_messages(limit)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages", response_model=CreateMessageResponse)
async def create_message_endpoint(request: CreateMessageRequest, background_tasks: BackgroundTasks):
    try:
        message = await create_message(request.text)
        message_uuid = message["message_uuid"]
        
        background_tasks.add_task(call_provider_async, message_uuid, request.text)
        
        return CreateMessageResponse(
            id=message_uuid,
            text=request.text,
            status=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for ping/pong or other client messages
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/provider-callback")
async def provider_callback(request: ProviderCallbackRequest):
    try:
        # Convert Pydantic model to dict for service function
        request_dict = request.model_dump()
        await process_provider_callback(request_dict)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))