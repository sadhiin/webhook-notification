import os
import uuid
from typing import List
import asyncpg


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://notifier_user:notifier_pass@localhost:5432/notifier_db")


async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)


async def get_latest_messages(limit: int = 10) -> List[dict]:
    conn = await get_db_connection()
    try:
        rows = await conn.fetch(
            """SELECT message_id, message_uuid::text, status, text, created_at, updated_at
            FROM messages 
            ORDER BY created_at DESC 
            LIMIT $1""", limit
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()


async def create_message(text: str) -> dict:
    conn = await get_db_connection()
    try:
        message_uuid = str(uuid.uuid4())
        row = await conn.fetchrow(
            """INSERT INTO messages (message_uuid, text) 
            VALUES ($1, $2) 
            RETURNING message_id, message_uuid::text, status, text, created_at, updated_at""",
            message_uuid, text
        )
        return dict(row)
    finally:
        await conn.close()

async def update_message_status(message_uuid: str, status: str) -> dict:
    conn = await get_db_connection()
    try:
        row = await conn.fetchrow(
            """UPDATE messages 
            SET status = $1, updated_at = NOW() 
            WHERE message_uuid::text = $2 
            RETURNING message_id, message_uuid::text, status, text, created_at, updated_at""",
            status, message_uuid
        )
        return dict(row) if row else None
    finally:
        await conn.close()

