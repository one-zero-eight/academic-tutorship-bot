from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class SQLDatabase:
    _connection_string: str
    _engine: AsyncEngine
    _disposed: bool = False

    def __init__(self, connection_string: str, dumb: bool = False):
        self._connection_string = connection_string
        self._engine = create_async_engine(
            connection_string,
            **(
                {}
                if dumb
                else {
                    "pool_size": 5,
                    "max_overflow": 10,
                    "future": True,
                }
            ),
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def dispose(self):
        if not self._disposed:
            self._disposed = True
            return await self._engine.dispose()


class Repository:
    _db: SQLDatabase

    def __init__(self, db: SQLDatabase):
        self._db = db
