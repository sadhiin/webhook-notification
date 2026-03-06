import logging

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.callbacks import router as callbacks_router
from app.api.routes.messages import router as messages_router
from app.api.routes.ws import router as ws_router
from app.core.config import settings
from app.db.pool import db_pool

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")


@app.on_event("startup")
async def on_startup() -> None:
    await db_pool.connect(settings.database_url)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await db_pool.disconnect()


@app.get("/")
async def read_root():
    return FileResponse(f"{settings.static_dir}/index.html")


app.include_router(messages_router)
app.include_router(callbacks_router)
app.include_router(ws_router)
