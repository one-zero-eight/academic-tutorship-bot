import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    SmallInteger,
    String,
    Table,
    Text,
)

metadata = MetaData()


student = Table(
    "student",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("telegram_id", BigInteger, unique=True, nullable=False),
    Column("language", String(2), nullable=False, default="en", server_default="en"),
    Column("first_name", String(128)),
    Column("last_name", String(128)),
    Column("username", String(36), unique=True),
    Column("email_id", Integer, ForeignKey("email.id", onupdate="RESTRICT", ondelete="RESTRICT"), nullable=False),
    Column("notification_bot_status", SmallInteger, nullable=False, default=1, server_default="1"),
    Column("saw_guide", Boolean, nullable=False, default=False, server_default="false"),
)


email = Table(
    "email",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("value", String(256), unique=True, nullable=False),
)


settings = Table(
    "settings",
    metadata,
    Column("id", Integer, ForeignKey("student.id", ondelete="CASCADE"), primary_key=True),
    Column("receive_notifications", Boolean, nullable=False, default=True),
)


admin = Table(
    "admin",
    metadata,
    Column("id", Integer, ForeignKey("student.id", ondelete="CASCADE"), primary_key=True),
)


tutor = Table(
    "tutor",
    metadata,
    Column("id", Integer, ForeignKey("student.id", ondelete="CASCADE"), primary_key=True),
    Column("profile_name", String(256), nullable=True),
    Column("about", Text, nullable=True),
    Column("photo_id", Integer, ForeignKey("photo.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True),
)


photo = Table(
    "photo",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("telegram_file_id", String(255), nullable=False),
    Column("file_path", String(4096), nullable=False),
)


discipline = Table(
    "discipline",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(256), nullable=False),
    Column("year", SmallInteger, nullable=False),
    Column("language", String(2), nullable=False),
)


student_discipline = Table(
    "student_discipline",
    metadata,
    Column("student_id", Integer, ForeignKey("student.id", ondelete="CASCADE"), primary_key=True),
    Column("discipline_id", Integer, ForeignKey("discipline.id", ondelete="CASCADE"), primary_key=True),
)


tutor_discipline = Table(
    "tutor_discipline",
    metadata,
    Column("tutor_id", Integer, ForeignKey("tutor.id", ondelete="CASCADE"), primary_key=True),
    Column("discipline_id", Integer, ForeignKey("discipline.id", ondelete="CASCADE"), primary_key=True),
)


meeting = Table(
    "meeting",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("status", SmallInteger, nullable=False, default=0, server_default="0"),
    Column("title", String(256), nullable=False),
    Column("discipline_id", ForeignKey("discipline.id", ondelete="SET NULL"), nullable=False),
    Column("created_datetime", DateTime, nullable=False, default=datetime.datetime.now),
    Column("creator_id", Integer, ForeignKey("student.id", ondelete="SET NULL"), nullable=False),
    Column("duration", Integer, nullable=False, default=5400),
    Column("description", Text, nullable=True),
    Column("room", String(32), nullable=True),
    Column("datetime", DateTime, nullable=True),
    Column("tutor_id", Integer, ForeignKey("tutor.id"), nullable=True),
)


attendance = Table(
    "attendance",
    metadata,
    Column("email_id", Integer, ForeignKey("email.id", ondelete="CASCADE"), primary_key=True),
    Column("meeting_id", Integer, ForeignKey("meeting.id", ondelete="CASCADE"), primary_key=True),
)
