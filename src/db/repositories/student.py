from sqlalchemy import (
    Row,
    delete,
    exists,
    insert,
    select,
)

from src.db.schema import admin, email, settings, student
from src.domain.models import Settings, Student

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
