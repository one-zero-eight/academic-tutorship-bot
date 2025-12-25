from sqlalchemy import Column, Integer, MetaData, String, Table

metadata = MetaData()


tutors = Table(
    "tutors",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tg_id", Integer, unique=True, nullable=False),
    Column("username", String, nullable=True),
    Column("first_name", String, nullable=True),
    Column("last_name", String, nullable=True),
)
