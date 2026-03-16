from sqlalchemy import select

from src.db.schema import admin, student

from .sql import Repository


class AdminRepository(Repository):
    async def get_ids(self) -> list[int]:
        stmt = select(admin.c.id)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [row.id for row in result.all()]

    async def get_telegram_ids(self) -> list[int]:
        stmt = select(student.c.telegram_id).join(admin, admin.c.id == student.c.id)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [row.telegram_id for row in result.all()]
