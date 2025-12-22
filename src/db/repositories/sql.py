from sqlalchemy import (
    Column,
    ColumnElement,
    Integer,
    MetaData,
    String,
    Table,
    and_,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.config import settings
from src.domain.repositories import Tutor, TutorsRepository


class SQLTutorsRepository(TutorsRepository):
    connection_string: str
    engine: AsyncEngine
    tutors: Table

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

        self.engine = create_async_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            future=True,
        )

        metadata = MetaData()

        self.tutors = Table(
            "tutors",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("tg_id", Integer, unique=True, nullable=False),
            Column("username", String, nullable=False),
            Column("first_name", String, nullable=False),
            Column("last_name", String, nullable=True),
        )

    async def exists(
        self,
        *,
        id: int | None = None,
        telegram_id: int | None = None,
        tutor: Tutor | None = None,
    ) -> bool:
        where = self._where_clause(id=id, telegram_id=telegram_id, tutor=tutor)

        stmt = select(self.tutors.c.id).where(where).limit(1)

        async with self.engine.connect() as conn:
            result = await conn.execute(stmt)
            return result.first() is not None

    async def get(
        self,
        *,
        id: int | None = None,
        telegram_id: int | None = None,
    ) -> Tutor:
        where = self._where_clause(id=id, telegram_id=telegram_id, tutor=None)
        stmt = select(self.tutors).where(where).limit(1)

        async with self.engine.connect() as conn:
            result = await conn.execute(stmt)
            row = result.first()
            if row is None:
                raise LookupError("Tutor not found")
            return self._row_to_tutor(row)

    async def update(self, tutor: Tutor) -> None:
        stmt = (
            update(self.tutors)
            .where(self.tutors.c.id == tutor.id)
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

    async def dispose(self) -> None:
        await self.engine.dispose()

    def _where_clause(
        self,
        *,
        id: int | None,
        telegram_id: int | None,
        tutor: Tutor | None,
    ):
        conds: list[ColumnElement[bool]] = []
        if id is not None:
            conds.append(self.tutors.c.id == id)
        if telegram_id is not None:
            conds.append(self.tutors.c.tg_id == telegram_id)
        if tutor is not None:
            conds.append(self.tutors.c.id == tutor.id)
        if not conds:
            raise ValueError("At least one of id / telegram_id / tutor must be provided")
        return and_(*conds)

    def _row_to_tutor(self, row) -> Tutor:
        return Tutor(
            id=row.id,
            tg_id=row.tg_id,
            username=row.username,
            first_name=row.first_name,
            last_name=row.last_name,
        )


if conn_string := settings.db_conn_string:
    tutors_repo: TutorsRepository = SQLTutorsRepository(conn_string)
else:
    raise ImportError("Database Connection String (db_conn_string) is not set in ./settings.yaml")
