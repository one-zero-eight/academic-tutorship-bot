from src.config import settings

from .admin import AdminRepository
from .discipline import DisciplineRepository
from .meeting import MeetingRepository
from .sql import SQLDatabase
from .student import StudentRepository
from .tutor import TutorRepository

db = SQLDatabase(settings.db_url.get_secret_value())
student_repo = StudentRepository(db)
tutor_repo = TutorRepository(db)
admin_repo = AdminRepository(db)
meeting_repo = MeetingRepository(db)
discipline_repo = DisciplineRepository(db)
