from fastapi import APIRouter, HTTPException

from app.schemas.message import ProviderCallbackRequest
from app.services.provider import process_provider_callback

router = APIRouter(prefix="/api", tags=["callbacks"])


@router.post("/provider-callback")
async def provider_callback(request: ProviderCallbackRequest):
    try:
        await process_provider_callback(request.model_dump())
        return {"status": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
