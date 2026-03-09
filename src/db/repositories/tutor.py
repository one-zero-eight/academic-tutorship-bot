from sqlalchemy import Row, delete, exists, insert, or_, select, update

from src.db.schema import discipline, photo, student, tutor, tutor_discipline
from src.domain.models import Discipline, Photo, Student, Tutor

from .sql import Repository


class TutorRepository(Repository):
    async def create(self, id: int) -> Tutor:
        stmt = insert(tutor).values(id=id)
        async with self._db.engine.begin() as conn:
            await conn.execute(stmt)
        return await self.get(id=id)

    async def update(self, tutor_: Tutor, attrs: list[str] | None = None):
        """Update tutor in database.

        - Updates TUTOR and STUDENT tables
        - You may specify which `attrs` to update (to optimize query), otherwise updates all
        - "photo" is not updated, even if included in `attrs`, use `set_photo`
        """
        changed_student, changed_tutor = self.__get_what_changed(tutor_, attrs)
        tutor_stmt = update(tutor).where(tutor.c.id == tutor_.id).values(**changed_tutor)
        student_stmt = update(student).where(student.c.id == tutor_.id).values(**changed_student)
        async with self._db.engine.begin() as conn:
            if changed_tutor:
                await conn.execute(tutor_stmt)
            if changed_student:
                await conn.execute(student_stmt)

    async def set_photo(self, tutor_id: int, telegram_file_id: int, file_path: str):
        """Inserts photo for tutor in database.

        - DOES NOT store image file storage, do that beforehand
        - Inserts into PHOTO
        - Updates TUTOR.photo_id
        """
        photo_stmt = insert(photo).values(telegram_file_id=telegram_file_id, file_path=file_path).returning(photo.c.id)
        async with self._db.engine.begin() as conn:
            result = await conn.execute(photo_stmt)
            photo_id = result.scalar_one()
            tutor_stmt = update(tutor).values(photo_id=photo_id)
            await conn.execute(tutor_stmt)

    async def unset_photo(self, tutor_id: int):
        stmt = update(tutor).values(photo_id=None)
        async with self._db.engine.begin() as conn:
            await conn.execute(stmt)

    async def exists(self, telegram_id: int) -> bool:
        stmt = select(exists().select_from(tutor.join(student, tutor.c.id == student.c.id))).where(
            student.c.telegram_id == telegram_id
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return bool(result.scalar())

    async def get(self, *, id: int | None = None, telegram_id: int | None = None) -> Tutor:
        tutor_stmt = (
            select(student, tutor, photo.c.telegram_file_id, photo.c.file_path)
            .select_from(
                student.join(tutor, tutor.c.id == student.c.id).join(
                    photo, tutor.c.photo_id == photo.c.id, isouter=True
                )
            )
            .where(or_(student.c.id == id, student.c.telegram_id == telegram_id))
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(tutor_stmt)
            if not (row := result.first()):
                raise LookupError("Tutor not found")
            return self._row_to_tutor(row)

    async def get_disciplines(self, id: int) -> list[Discipline]:
        stmt = select(discipline).join(tutor_discipline).where(tutor_discipline.c.tutor_id == id)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            disciplines = [self._row_to_discipline(r) for r in result.all()]
        return disciplines

    async def set_disciplines(self, id: int, disciplines: list[Discipline]):
        delete_old_stmt = delete(tutor_discipline).where(tutor_discipline.c.tutor_id == id)
        insert_new_stmt = insert(tutor_discipline).values(
            [{"tutor_id": id, "discipline_id": discipline.id} for discipline in disciplines]
        )
        async with self._db.engine.begin() as conn:
            await conn.execute(delete_old_stmt)
            if disciplines:
                await conn.execute(insert_new_stmt)

    async def get_list(self, *, with_profiles_only: bool = False) -> list[Tutor]:
        stmt = select(student, tutor, photo.c.telegram_file_id, photo.c.file_path).select_from(
            student.join(tutor, tutor.c.id == student.c.id).join(photo, tutor.c.photo_id == photo.c.id, isouter=True)
        )
        if with_profiles_only:
            stmt = stmt.where(tutor.c.profile_name.is_not(None))
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            tutors = [self._row_to_tutor(r) for r in result.all()]
        return tutors

    async def remove(self, tutor_: Tutor):
        stmt = delete(tutor).where(tutor.c.id == tutor_.id)
        async with self._db.engine.begin() as conn:
            await conn.execute(stmt)

    def _row_to_tutor(self, row: Row) -> Tutor:
        return Tutor(
            id=row.id,
            telegram_id=row.telegram_id,
            first_name=row.first_name,
            last_name=row.last_name,
            username=row.username,
            profile_name=row.profile_name,
            about=row.about,
            photo=(
                Photo(id=row.photo_id, telegram_file_id=row.telegram_file_id, file_path=row.file_path)
                if row.photo_id
                else None
            ),
        )

    def _row_to_discipline(self, row: Row) -> Discipline:
        return Discipline(
            id=row.id,
            name=row.name,
            year=row.year,
            language=row.language,
        )

    def __get_what_changed(self, tutor_: Tutor, attrs: list[str] | None = None) -> tuple[dict, dict]:
        data = tutor_.model_dump()
        del data["photo"]  # photo not included in update
        if attrs:
            changed = {key: data[key] for key in attrs if key in data}
        else:
            changed = data
        changed_student = {key: changed[key] for key in changed if key in Student.model_fields.keys()}
        changed_tutor = {key: changed[key] for key in changed if key not in changed_student}
        return (changed_student, changed_tutor)
