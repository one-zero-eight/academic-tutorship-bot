from src.config import settings
from src.domain.repositories import MeetingsRepository, TutorsRepository

from .sql import SQLDatabase, SQLMeetingsRepository, SQLTutorsRepository

if conn_string := settings.db_conn_string:
    db = SQLDatabase(conn_string)
    tutors_repo: TutorsRepository = SQLTutorsRepository(db)
    meetings_repo: MeetingsRepository = SQLMeetingsRepository(db)
else:
    raise ImportError("Database Connection String (db_conn_string) is not set in ./settings.yaml")
