from sqlalchemy import Row, insert, select

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

    async def get_list(self, language: str, year: int) -> list[Discipline]:
        stmt = (
            select(discipline)
            .where(discipline.c.language == language, discipline.c.year == year)
            .order_by(discipline.c.name)
        )
        async with self._db.engine.connect() as conn:
            result = await conn.execute(stmt)
            return [self._row_to_discipline(row) for row in result.all()]

    async def create(self, language: str, year: int, name: str) -> Discipline:
        stmt = insert(discipline).values(language=language, year=year, name=name).returning(discipline)
        async with self._db.engine.begin() as conn:
            result = await conn.execute(stmt)
            if not (row := result.first()):
                raise ValueError("Could not insert discipline")
            return self._row_to_discipline(row)

    def _row_to_discipline(self, row: Row) -> Discipline:
        return Discipline(id=row.id, name=row.name, year=row.year, language=row.language)
