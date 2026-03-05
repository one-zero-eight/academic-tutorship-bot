from sqlalchemy import Column, Integer, MetaData, String, Table

metadata = MetaData()


tutor_profiles = Table(
    "tutor_profiles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("full_name", String, nullable=False),
    Column("username", String, nullable=True),
    Column("discipline", String, nullable=False),
    Column("photo_id", String, nullable=False),
    Column("about", String, nullable=True),
)


tutors = Table(
    "tutors",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tg_id", Integer, unique=True, nullable=False),
    Column("username", String, nullable=True),
    Column("first_name", String, nullable=True),
    Column("last_name", String, nullable=True),
)


meetings = Table(
    "meetings",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("status", Integer, nullable=False),
    Column("tutor_id", Integer, nullable=True),
    Column("date", Integer, nullable=True),
    Column("description", String, nullable=True),
    Column("duration", Integer, nullable=True),
    Column("room", String, nullable=True),
    Column("attendance", String, nullable=True),
)
