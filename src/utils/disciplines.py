from collections.abc import Callable

from src.bot.logging_ import log_debug
from src.db.repositories import discipline_repo
from src.domain.models import Discipline


class ParseError(Exception): ...


def parse_add_discipline_command(command: str) -> list[Discipline]:
    if not command.startswith("/add-discipline"):
        raise ParseError("Command not starts from /add-discipline")
    command = " ".join(command.split(" ")[1:])
    to_add = []
    for line in command.split("\n"):
        try:
            discipline = __parse_add_discipline_line(line)
            to_add.append(discipline)
        except ParseError as e:
            log_debug("parse.add-discipline.error", err=str(e))
    return to_add


def __parse_add_discipline_line(line: str) -> Discipline:
    parts = line.split(" ", maxsplit=3)
    if len(parts) < 4:
        raise ParseError(f"Not enough parts in line: {parts}")
    lang, year, sem, name = parts
    lang = lang.lower()
    EXPECTED_LANGS = ["ru", "en"]
    if lang not in EXPECTED_LANGS:
        raise ParseError(f"Unknown language: {lang}, expected: {EXPECTED_LANGS}")
    try:
        year = int(year)
    except ValueError:
        raise ParseError(f"Year is not int: {year}")
    if (year < 0) or (year > 4):
        raise ParseError(f"Year out of bounds: {year}")
    try:
        sem = int(sem)
    except ValueError:
        raise ParseError(f"Semester is not int: {sem}")
    if (sem < 0) or (sem > 3):
        raise ParseError(f"Semester out of bounds: {sem}")
    return Discipline(
        id=-1,
        language=lang.upper(),
        year=year,
        semester=sem,
        name=name,
    )


def parse_del_discipline_command(command: str) -> list[int | str]:
    if not command.startswith("/del-discipline"):
        raise ParseError("Command not starts from /del-discipline")
    command = " ".join(command.split(" ")[1:])
    to_del = []
    for line in command.split("\n"):
        try:
            id_or_name = __parse_del_discipline_line(line)
            to_del.append(id_or_name)
        except ParseError as e:
            log_debug("parse.del-discipline.error", err=str(e))
    return to_del


def __parse_del_discipline_line(line: str) -> int | str:
    parts = line.split(" ")
    id_ = None
    name_ = None
    if len(parts) == 1:
        try:
            id_ = int(parts[0])
        except ValueError:
            name_ = line
    else:
        name_ = line
    if id_ is not None:
        return id_
    elif name_ is not None:
        return name_
    else:
        raise ParseError(f"No name and no id provided: {parts}")


async def add_disciplines(to_add: list[Discipline]) -> list[Discipline]:
    added = []
    for d in to_add:
        try:
            created_d = await discipline_repo.create(language=d.language, year=d.year, semester=d.semester, name=d.name)
            added.append(created_d)
        except Exception as e:
            log_debug("add-disciplines.error", err=str(e))
    return added


async def delete_disciplines(to_del: list[int | str]) -> list[Discipline]:
    deleted = []
    for id_or_name in to_del:
        try:
            if isinstance(id_or_name, str):
                deleted_d = await discipline_repo.delete(name=id_or_name)
            elif isinstance(id_or_name, int):
                deleted_d = await discipline_repo.delete(id=id_or_name)
            else:
                raise ValueError("id_or_name is not of type str or int")
            if deleted_d:
                deleted.append(deleted_d)
        except Exception as e:
            log_debug("del-disciplines.error", err=str(e))
    return deleted


def build_disciplines_added_message(added: list[Discipline], i18n_func: Callable[[str, dict], str]) -> str:
    _ = i18n_func
    output = ""
    output += _("DISCIPLINES_ADDED_TITLE", {}) + "\n"
    for d in added:
        context = {
            "d_id": d.id,
            "d_lang": d.language,
            "d_year": d.year,
            "d_semester": d.semester,
            "d_name": d.name,
        }
        output += _("DISCIPLINES_CONTROL_LIST_ENTRY", context) + "\n"
    return output


def build_disciplines_deleted_message(deleted: list[Discipline], i18n_func: Callable[[str, dict], str]) -> str:
    _ = i18n_func
    output = ""
    output += _("DISCIPLINES_DELETED_TITLE", {}) + "\n"
    for d in deleted:
        context = {
            "d_id": d.id,
            "d_lang": d.language,
            "d_year": d.year,
            "d_semester": d.semester,
            "d_name": d.name,
        }
        output += _("DISCIPLINES_CONTROL_LIST_ENTRY", context) + "\n"
    return output
