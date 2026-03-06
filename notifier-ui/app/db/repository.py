import uuid
from typing import Any

from app.db.pool import db_pool


async def get_latest_messages(limit: int = 10) -> list[dict[str, Any]]:
    async with db_pool.pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT message_id, message_uuid::text, status, text, created_at, updated_at
            FROM messages
            ORDER BY created_at DESC
            LIMIT $1""",
            limit,
        )
    return [dict(row) for row in rows]


async def create_message(text: str) -> dict[str, Any]:
    async with db_pool.pool.acquire() as conn:
        message_uuid = str(uuid.uuid4())
        row = await conn.fetchrow(
            """INSERT INTO messages (message_uuid, text)
            VALUES ($1, $2)
            RETURNING message_id, message_uuid::text, status, text, created_at, updated_at""",
            message_uuid,
            text,
        )
    return dict(row)


async def update_message_status(message_uuid: str, status: int) -> dict[str, Any] | None:
    async with db_pool.pool.acquire() as conn:
        row = await conn.fetchrow(
            """UPDATE messages
            SET status = $1, updated_at = NOW()
            WHERE message_uuid::text = $2
            RETURNING message_id, message_uuid::text, status, text, created_at, updated_at""",
            status,
            message_uuid,
        )
    return dict(row) if row else None
