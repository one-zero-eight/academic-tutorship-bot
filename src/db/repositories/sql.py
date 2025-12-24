from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.db.schema import tutors
from src.domain.repositories import Tutor, TutorsRepository


class SQLTutorsRepository(TutorsRepository):
    connection_string: str
    engine: AsyncEngine

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

        self.engine = create_async_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            future=True,
        )

    async def exists(
        self,
        *,
        id: int | None = None,
        tg_id: int | None = None,
        username: str | None = None,
        tutor: Tutor | None = None,
    ) -> bool:
        where = self._where_clause(id, tg_id, username, tutor)

        stmt = select(tutors.c.id).where(where).limit(1)

        async with self.engine.connect() as conn:
            result = await conn.execute(stmt)
            return result.first() is not None

    async def get(
        self,
        *,
        id: int | None = None,
        tg_id: int | None = None,
        username: str | None = None,
    ) -> Tutor:
        where = self._where_clause(id, tg_id, username, tutor=None)
        stmt = select(tutors).where(where).limit(1)

        async with self.engine.connect() as conn:
            result = await conn.execute(stmt)
            row = result.first()
            if row is None:
                raise LookupError("Tutor not found")
            return self._row_to_tutor(row)

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[Tutor]:
        stmt = select(tutors).order_by(tutors.c.id).offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        async with self.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [self._row_to_tutor(row) for row in result.fetchall()]

    async def create(
        self,
        *,
        tg_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Tutor:
        stmt = insert(tutors).values(
            tg_id=tg_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        async with self.engine.begin() as conn:
            try:
                result = await conn.execute(stmt)
                if result.rowcount == 0 or result.inserted_primary_key is None:
                    raise ValueError("Failed to insert tutor")
                db_id = result.inserted_primary_key[0]
            except IntegrityError as e:
                if "UNIQUE constraint failed: tutors.tg_id" in str(e):
                    raise ValueError(f"Tutor with tg_id {tg_id} already exists")
                raise

        return Tutor(id=db_id, tg_id=tg_id, username=username, first_name=first_name, last_name=last_name)

    async def update(self, tutor: Tutor) -> None:
        stmt = (
            update(tutors)
            .where(tutors.c.id == tutor.id)
            .values(
                tg_id=tutor.tg_id,
                username=tutor.username,
                first_name=tutor.first_name,
                last_name=tutor.last_name,
            )
        )

        async with self.engine.begin() as conn:
            result = await conn.execute(stmt)
            if result.rowcount == 0:
                raise LookupError("Tutor not found for update")

    async def remove(
        self,
        *,
        id: int | None = None,
        tg_id: int | None = None,
        username: str | None = None,
        tutor: Tutor | None = None,
    ) -> Tutor:
        where = self._where_clause(id, tg_id, username, tutor)

        select_stmt = select(tutors).where(where).limit(1)
        delete_stmt = delete(tutors).where(where)

        async with self.engine.connect() as conn:
            # SELECT
            result = await conn.execute(select_stmt)
            row = result.fetchone()
            if row is None:
                raise LookupError("Tutor not found")
            deleted_tutor = self._row_to_tutor(row)

            # DELETE
            result = await conn.execute(delete_stmt)
            if result.rowcount == 0:
                raise LookupError("Tutor not found")

        return deleted_tutor

    async def dispose(self):
        await self.engine.dispose()

    def _where_clause(
        self,
        id: int | None,
        tg_id: int | None,
        username: str | None,
        tutor: Tutor | None,
    ):
        if id is not None:
            return tutors.c.id == id
        if tg_id is not None:
            return tutors.c.tg_id == tg_id
        if username is not None:
            return tutors.c.username == username
        if tutor is not None:
            return tutors.c.id == tutor.id
        raise ValueError("At least one of id / telegram_id / tutor must be provided")

    def _row_to_tutor(self, row) -> Tutor:
        return Tutor(
            id=row.id,
            tg_id=row.tg_id,
            username=row.username,
            first_name=row.first_name,
            last_name=row.last_name,
        )
