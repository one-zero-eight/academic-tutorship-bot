from sqlalchemy import Row, delete, insert, select

from src.db.schema import discipline
from src.domain.models import Discipline

from .sql import Repository


class DisciplineRepository(Repository):
    async def get_languages(self) -> list[str]:
        stmt = select(discipline.c.language).distinct().order_by(discipline.c.language)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [row.language for row in result.all()]

    async def get_years(self, language: str) -> list[int]:
        stmt = select(discipline.c.year).distinct().where(discipline.c.language == language).order_by(discipline.c.year)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [row.year for row in result.all()]

    async def get_semesters(self, language: str, year: int) -> list[int]:
        stmt = (
            select(discipline.c.semester)
            .distinct()
            .where(
                discipline.c.language == language,
                discipline.c.year == year,
            )
            .order_by(discipline.c.semester)
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [row.semester for row in result.all()]

    async def get_list(self, language: str, year: int, semester: int) -> list[Discipline]:
        stmt = (
            select(discipline)
            .where(
                discipline.c.language == language,
                discipline.c.year == year,
                discipline.c.semester == semester,
            )
            .order_by(discipline.c.name)
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [self._row_to_discipline(row) for row in result.all()]

    async def get_full_list(self) -> list[Discipline]:
        stmt = select(discipline).order_by(discipline.c.id)
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [self._row_to_discipline(row) for row in result.all()]

    async def create(self, language: str, year: int, semester: int, name: str) -> Discipline:
        stmt = (
            insert(discipline).values(language=language, year=year, semester=semester, name=name).returning(discipline)
        )
        async with self._db.engine.begin() as conn:
            result = await conn.execute(stmt)
            if not (row := result.first()):
                raise ValueError("Could not insert discipline")
            return self._row_to_discipline(row)

    async def delete(self, id: int | None = None, name: str | None = None) -> Discipline | None:
        if name is not None:
            select_stmt = select(discipline).where(discipline.c.name == name).limit(1)
        elif id is not None:
            select_stmt = select(discipline).where(discipline.c.id == id).limit(1)
        else:
            return None
        async with self._db.engine.begin() as conn:
            result = await conn.execute(select_stmt)
            if not (row := result.first()):
                return None
            found_discipline = self._row_to_discipline(row)
            delete_stmt = delete(discipline).where(discipline.c.id == found_discipline.id)
            await conn.execute(delete_stmt)
        return found_discipline

    def _row_to_discipline(self, row: Row) -> Discipline:
        return Discipline(id=row.id, name=row.name, year=row.year, semester=row.semester, language=row.language)
