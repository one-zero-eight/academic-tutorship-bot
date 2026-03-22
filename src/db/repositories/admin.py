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

    async def sync_with_config(self, admin_telegram_ids: list[int]) -> tuple[list[int], list[int]]:
        """Sync the admin table with the given list of telegram ids.
        Returns a tuple of two lists: (added_telegram_ids, removed_telegram_ids)
        """
        current_admin_telegram_ids = await self.get_telegram_ids()
        to_add = set(admin_telegram_ids) - set(current_admin_telegram_ids)
        to_remove = set(current_admin_telegram_ids) - set(admin_telegram_ids)

        async with self._db.engine.begin() as conn:
            for telegram_id in to_add:
                await conn.execute(
                    admin.insert().values(
                        id=select(student.c.id).where(student.c.telegram_id == telegram_id).scalar_subquery()
                    )
                )
            for telegram_id in to_remove:
                await conn.execute(
                    admin.delete().where(
                        admin.c.id == select(student.c.id).where(student.c.telegram_id == telegram_id).scalar_subquery()
                    )
                )

        return list(to_add), list(to_remove)
