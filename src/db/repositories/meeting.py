from collections.abc import Sequence

from sqlalchemy import (
    Row,
    and_,
    delete,
    exists,
    insert,
    select,
    update,
)

from src.db.schema import admin, attendance, discipline, email, meeting, settings, student, student_discipline, tutor
from src.domain.models import Discipline, Meeting, MeetingStatus

from .sql import Repository


class MeetingRepository(Repository):
    async def create(self, title: str, discipline_id: int, creator_telegram_id: int) -> Meeting:
        is_tutor = is_admin = False
        creator_tutor_stmt = (
            select(student.c.id).select_from(student.join(tutor)).where(student.c.telegram_id == creator_telegram_id)
        )
        creator_admin_stmt = (
            select(student.c.id).select_from(student.join(admin)).where(student.c.telegram_id == creator_telegram_id)
        )
        async with self._db.engine.begin() as conn:
            result = await conn.execute(creator_tutor_stmt)
            creator_id = None
            if tutor_id := result.scalar_one_or_none():
                creator_id = tutor_id
                is_tutor = True
            result = await conn.execute(creator_admin_stmt)
            if admin_id := result.scalar_one_or_none():
                creator_id = admin_id
                is_admin = True
            if is_tutor:  # automatically assign tutor as meeting's tutor
                stmt = (
                    insert(meeting)
                    .values(title=title, discipline_id=discipline_id, creator_id=creator_id, tutor_id=creator_id)
                    .returning(meeting.c.id)
                )
            elif is_admin:  # admins can create meetings without tutor
                stmt = (
                    insert(meeting)
                    .values(title=title, discipline_id=discipline_id, creator_id=creator_id)
                    .returning(meeting.c.id)
                )
            else:
                raise PermissionError("Only tutors and admins can create meetings")
            result = await conn.execute(stmt)
            id = result.scalar_one()
        return await self.get(id)

    async def update(self, meeting_: Meeting, attrs: list[str] | None = None):
        data = meeting_.model_dump(by_alias=True, exclude={"discipline", "created_at", "duration_human"})
        if attrs:
            changed = {key: data[key] for key in attrs if key in data}
        else:
            changed = data
        stmt = update(meeting).where(meeting.c.id == meeting_.id).values(**changed)
        async with self._db.engine.begin() as conn:
            await conn.execute(stmt)

    async def get(self, id: int) -> Meeting:
        disc = discipline
        stmt = (
            select(
                meeting,
                disc.c.id.label("d_id"),
                disc.c.name.label("d_name"),
                disc.c.year.label("d_year"),
                disc.c.language.label("d_language"),
            )
            .select_from(meeting.join(discipline, meeting.c.discipline_id == discipline.c.id))
            .where(meeting.c.id == id)
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            if not (row := result.first()):
                raise LookupError("Meeting not found")
            return self._row_to_meeting(row)

    async def get_list(
        self, status_range: MeetingStatus | tuple[MeetingStatus, MeetingStatus], tutor_id: int | None = None
    ) -> list[Meeting]:
        disc = discipline
        stmt = select(
            meeting,
            disc.c.id.label("d_id"),
            disc.c.name.label("d_name"),
            disc.c.year.label("d_year"),
            disc.c.language.label("d_language"),
        ).select_from(meeting.join(discipline, meeting.c.discipline_id == discipline.c.id))
        if isinstance(status_range, MeetingStatus):
            status = status_range
            stmt = stmt.where(meeting.c.status == status.value)
        elif isinstance(status_range, tuple):
            status_from, status_to = status_range
            stmt = stmt.where(and_(meeting.c.status >= status_from, meeting.c.status <= status_to))
        if tutor_id:
            stmt = stmt.where(meeting.c.tutor_id == tutor_id)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [self._row_to_meeting(r) for r in result.all()]

    async def has_attendance(self, id: int) -> bool:
        stmt = select(exists().select_from(attendance)).where(attendance.c.meeting_id == id)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return bool(result.scalar())

    async def get_attendance(self, id: int) -> list[str]:
        stmt = select(email.c.value).select_from(attendance.join(email)).where(attendance.c.meeting_id == id)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return self._rows_to_emails(result.all())

    async def set_attendance(self, id: int, emails: list[str]):
        await self.ensure_emails_exist(emails)
        emails_stmt = select(email.c.id).where(email.c.value.in_(emails))
        delete_old_stmt = delete(attendance).where(attendance.c.meeting_id == id)
        async with self._db.engine.begin() as conn:
            result = await conn.execute(emails_stmt)
            email_ids = [row.id for row in result.all()]
            await conn.execute(delete_old_stmt)
            insert_new_stmt = insert(attendance).values(
                [{"email_id": email_id, "meeting_id": id} for email_id in email_ids]
            )
            await conn.execute(insert_new_stmt)

    async def ensure_emails_exist(self, emails: list[str]):
        select_existing_stmt = select(email.c.value).where(email.c.value.in_(emails))
        async with self._db.engine.begin() as conn:
            result = await conn.execute(select_existing_stmt)
            existing = [row.value for row in result.all()]
            non_existing = [{"value": e} for e in emails if e not in existing]
            if non_existing:
                insert_new_stmt = insert(email).values(non_existing)
                await conn.execute(insert_new_stmt)

    async def add_attendee(self, id: int, email_: str):
        await self.ensure_emails_exist([email_])
        exists_stmt = select(
            exists()
            .select_from(attendance.join(email, email.c.id == attendance.c.email_id))
            .where(and_(email.c.value == email_, attendance.c.meeting_id == id))
        )
        async with self._db.engine.begin() as conn:
            result = await conn.execute(exists_stmt)
            already_attending = bool(result.scalar())
            if already_attending:
                raise FileExistsError("The attendee is already noted")
            email_stmt = select(email.c.id).where(email.c.value == email_)
            result = await conn.execute(email_stmt)
            email_id = result.scalar_one()
            insert_stmt = insert(attendance).values(meeting_id=id, email_id=email_id)
            await conn.execute(insert_stmt)

    async def remove(self, id: int):
        stmt = delete(meeting).where(meeting.c.id == id)
        async with self._db.engine.begin() as conn:
            await conn.execute(stmt)

    async def get_interested_student_ids(self, id: int, *, notifications_only: bool = True) -> list[int]:
        sd = student_discipline
        discipline_id = (await self.get(id)).discipline.id
        stmt = select(sd.c.student_id).where(sd.c.discipline_id == discipline_id)
        if notifications_only:
            stmt = stmt.join(settings, settings.c.id == sd.c.student_id).where(settings.c.receive_notifications)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [row.student_id for row in result.all()]

    def _row_to_meeting(self, row: Row) -> Meeting:
        return Meeting(
            id=row.id,
            title=row.title,
            discipline=Discipline(id=row.d_id, name=row.d_name, year=row.d_year, language=row.d_language),
            creator_id=row.creator_id,
            created_at=row.created_datetime,
            status=MeetingStatus(row.status),
            duration=row.duration,
            description=row.description,
            room=row.room,
            datetime=row.datetime,
            tutor_id=row.tutor_id,
        )

    def _rows_to_emails(self, rows: Sequence[Row]) -> list[str]:
        emails = []
        for row in rows:
            emails.append(row.value)
        return emails
