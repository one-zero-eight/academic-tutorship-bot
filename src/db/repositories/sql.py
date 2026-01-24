from sqlalchemy import (
    Row,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.db.schema import meetings, tutors
from src.domain.models import Email, Meeting, MeetingStatus, Tutor
from src.domain.repositories import MeetingsRepository, TutorsRepository


class SQLDatabase:
    _connection_string: str
    _engine: AsyncEngine
    _disposed: bool = False

    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._engine = create_async_engine(
            connection_string,
            pool_size=5,
            max_overflow=10,
            future=True,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def dispose(self):
        if not self._disposed:
            self._disposed = True
            return await self._engine.dispose()


class SQLTutorsRepository(TutorsRepository):
    _db: SQLDatabase

    def __init__(self, db: SQLDatabase):
        self._db = db

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

        async with self._db.engine.connect() as conn:
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

        async with self._db.engine.connect() as conn:
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

        async with self._db.engine.connect() as conn:
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

        async with self._db.engine.begin() as conn:
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

        async with self._db.engine.begin() as conn:
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
        stmt = delete(tutors).where(where).returning(tutors)

        async with self._db.engine.begin() as conn:
            result = await conn.execute(stmt)
            row = result.fetchone()
            if row is None:
                raise LookupError("Tutor not found")
            return self._row_to_tutor(row)

    async def dispose(self):
        await self._db.dispose()

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

    def _row_to_tutor(self, row: Row) -> Tutor:
        return Tutor(
            id=row.id,
            tg_id=row.tg_id,
            username=row.username,
            first_name=row.first_name,
            last_name=row.last_name,
        )


class SQLMeetingsRepository(MeetingsRepository):
    _db: SQLDatabase

    def __init__(self, db: SQLDatabase):
        self._db = db

    async def create(self, *, title: str) -> Meeting:
        # NOTE: creating tmp_meeting here to ensure default values from model definition
        tmp_meeting = Meeting(id=0, title=title)
        stmt = insert(meetings).values(
            title=tmp_meeting.title, duration=tmp_meeting.duration, status=tmp_meeting.status.value
        )

        async with self._db.engine.begin() as conn:
            try:
                result = await conn.execute(stmt)
                if result.rowcount == 0 or result.inserted_primary_key is None:
                    raise ValueError("Failed to insert meeting")
                db_id = result.inserted_primary_key[0]
            except IntegrityError as e:
                print(e)

        return Meeting(id=db_id, title=title)

    async def save(self, meeting: Meeting):
        stmt = (
            update(meetings)
            .where(meetings.c.id == meeting.id)
            .values(
                title=meeting.title,
                status=meeting.status.value,
                description=meeting.description,
                date=meeting.date,
                duration=meeting.duration,
                tutor_id=meeting.tutor.id if meeting.tutor else None,
                room=meeting.room,
                attendance=";".join(meeting._attendance) if meeting._attendance else None,
            )
        )

        async with self._db.engine.begin() as conn:
            result = await conn.execute(stmt)
            if result.rowcount == 0:
                raise LookupError("Meeting not found for update")

    async def get(self, *, id: int) -> Meeting:
        stmt = (
            select(meetings, tutors)
            .join(tutors, meetings.c.tutor_id == tutors.c.id, isouter=True)
            .where(meetings.c.id == id)
            .limit(1)
        )

        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            row = result.first()
            if row is None:
                raise LookupError("Meeting not found")
            return self._row_to_meeting(row)

    async def list(
        self,
        *,
        tutor_id: int | None = None,
        status: MeetingStatus | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[Meeting]:
        stmt = (
            select(meetings, tutors)
            .join(tutors, meetings.c.tutor_id == tutors.c.id, isouter=True)
            .order_by(meetings.c.id)
            .offset(offset)
        )
        if tutor_id is not None:
            stmt = stmt.where(meetings.c.tutor_id == tutor_id)
        if status is not None:
            stmt = stmt.where(meetings.c.status == status.value)
        if limit:
            stmt = stmt.limit(limit)

        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [self._row_to_meeting(row) for row in result.fetchall()]

    async def remove(self, *, id: int | None = None, meeting: Meeting | None = None):
        where = self._where_clause(id, meeting)
        stmt = delete(meetings).where(where)
        async with self._db.engine.begin() as conn:
            result = await conn.execute(stmt)
            if result.rowcount < 1:
                raise LookupError("Meeting not found")

    async def dispose(self):
        await self._db.dispose()

    def _where_clause(
        self,
        id: int | None,
        meeting: Meeting | None,
    ):
        if id is not None:
            return meetings.c.id == id
        if meeting is not None:
            return meetings.c.id == meeting.id
        raise ValueError("Either id or meeting must be provided")

    def _row_to_meeting(self, row: Row) -> Meeting:
        meeting = Meeting(id=row.meetings_id, title=row.meetings_title)
        meeting._status = MeetingStatus(row.meetings_status)
        meeting.date = row.meetings_date
        meeting.description = row.meetings_description
        meeting.duration = row.meetings_duration
        meeting.room = row.meetings_room
        if row.tutors_id is not None:
            tutor = Tutor(
                id=row.tutors_id,
                tg_id=row.tutors_tg_id,
                username=row.tutors_username,
                first_name=row.tutors_first_name,
                last_name=row.tutors_last_name,
            )
            meeting.assign_tutor(tutor)
        if row.meetings_attendance:
            meeting._attendance = [Email(e) for e in row.meetings_attendance.split(";")]
        return meeting
