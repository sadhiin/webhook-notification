import asyncpg


class DatabasePool:
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def connect(self, database_url: str) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(database_url, min_size=1, max_size=10)

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Database pool is not initialized")
        return self._pool


db_pool = DatabasePool()
