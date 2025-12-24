from src.config import settings
from src.domain.repositories import TutorsRepository

from .sql import SQLTutorsRepository

if conn_string := settings.db_conn_string:
    tutors_repo: TutorsRepository = SQLTutorsRepository(conn_string)
else:
    raise ImportError("Database Connection String (db_conn_string) is not set in ./settings.yaml")
