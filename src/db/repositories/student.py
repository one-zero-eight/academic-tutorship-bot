from sqlalchemy import (
    Row,
    delete,
    exists,
    insert,
    select,
    update,
)

from src.db.schema import admin, discipline, email, settings, student, student_discipline
from src.domain.models import Discipline, Settings, Student

from .sql import Repository


class StudentRepository(Repository):
    async def create(
        self,
        telegram_id: int,
        first_name: str | None,
        last_name: str | None,
        username: str | None,
        email_: str,
    ) -> Student:
        async with self._db.engine.begin() as conn:
            select_email_stmt = select(email).where(email.c.value == email_)
            result = await conn.execute(select_email_stmt)
            email_row = result.first()
            if email_row:
                email_id = email_row.id
            else:
                insert_email_stmt = insert(email).values(value=email_).returning(email.c.id)
                result = await conn.execute(insert_email_stmt)
                email_id = result.scalar_one()
            insert_student_stmt = (
                insert(student)
                .values(
                    telegram_id=telegram_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email_id=email_id,
                )
                .returning(student.c.id)
            )
            result = await conn.execute(insert_student_stmt)
            student_id = result.scalar_one()
            insert_settings_stmt = insert(settings).values(id=student_id)
            await conn.execute(insert_settings_stmt)
        return await self.get(telegram_id)

    async def exists(self, *, telegram_id: int | None = None, email_: str | None = None) -> bool:
        if telegram_id:
            stmt = select(exists().where(student.c.telegram_id == telegram_id))
        elif email_:
            stmt = select(
                exists()
                .select_from(student.join(email, email.c.id == student.c.email_id))
                .where(email.c.value == email_)
            )
        else:
            raise ValueError("Both telegram_id and email_ are None")
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return bool(result.scalar())

    async def get(self, telegram_id: int):
        is_admin_subquery = exists().where(admin.c.id == student.c.id)
        stmt = (
            select(
                student,
                email.c.value.label("email"),
                settings.c.receive_notifications,
                is_admin_subquery.label("is_admin"),
            )
            .select_from(student.join(email).join(settings))
            .where(student.c.telegram_id == telegram_id)
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            row = result.first()
            if row is None:
                raise LookupError("Student not found")
            return self._row_to_student(row)

    async def remove(self, id: int):
        stmt = delete(student).where(student.c.id == id)
        async with self._db.engine.begin() as conn:
            await conn.execute(stmt)

    async def is_admin(self, telegram_id: int):
        stmt = select(
            exists()
            .select_from(admin.join(student, admin.c.id == student.c.id))
            .where(student.c.telegram_id == telegram_id)
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return bool(result.scalar())

    async def get_relevant_disciplines(self, telegram_id: int):
        student_id = await self.get_student_id(telegram_id)
        stmt = (
            select(discipline)
            .select_from(discipline.join(student_discipline, discipline.c.id == student_discipline.c.discipline_id))
            .where(student_discipline.c.student_id == student_id)
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [self._row_to_discipline(row) for row in result.all()]

    async def set_relevant_disciplines(self, telegram_id: int, discipline_ids: list[int]):
        """Clears and sets new relevant disciplines"""
        student_id = await self.get_student_id(telegram_id)
        delete_old_stmt = delete(student_discipline).where(student_discipline.c.student_id == student_id)
        insert_new_stmt = insert(student_discipline).values(
            [{"student_id": student_id, "discipline_id": d_id} for d_id in discipline_ids]
        )
        async with self._db.engine.begin() as conn:
            await conn.execute(delete_old_stmt)
            await conn.execute(insert_new_stmt)

    async def get_student_id(self, telegram_id: int) -> int:
        stmt = select(student.c.id).select_from(student).where(student.c.telegram_id == telegram_id)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return result.scalar_one()

    async def update(self, student_: Student, attrs: list[str] | None = None):
        """Update student in database.

        - Updates STUDENT and SETTINGS tables
        - You may specify which `attrs` to update (to optimize query), otherwise updates all
        """
        student_changed, settings_changed = self.__get_what_changed(student_, attrs)
        student_stmt = update(student).where(student.c.id == student_.id).values(**student_changed)
        settings_stmt = update(settings).where(settings.c.id == student_.id).values(**settings_changed)
        async with self._db.engine.begin() as conn:
            if student_changed:
                await conn.execute(student_stmt)
            if settings_changed:
                await conn.execute(settings_stmt)

    def _row_to_student(self, row: Row) -> Student:
        return Student(
            id=row.id,
            telegram_id=row.telegram_id,
            email=row.email,
            first_name=row.first_name,
            last_name=row.last_name,
            username=row.username,
            is_admin=row.is_admin,
            settings=Settings(receive_notifications=row.receive_notifications),
        )

    def _row_to_discipline(self, row: Row) -> Discipline:
        return Discipline(id=row.id, name=row.name, year=row.year, language=row.language)

    def __get_what_changed(self, student_: Student, attrs: list[str] | None = None) -> tuple[dict, dict]:
        student_data = student_.model_dump()
        del student_data["settings"]
        settings_data = student_.settings.model_dump()
        if attrs:
            student_changed = {key: student_data[key] for key in attrs if key in student_data}
            settings_changed = {key: settings_data[key] for key in attrs if key in settings_data}
        else:
            student_changed = student_data
            settings_changed = settings_data
        return (student_changed, settings_changed)
