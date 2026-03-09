import pytest

from src.db.repositories import DisciplineRepository, StudentRepository, TutorRepository
from src.domain.models import Tutor
from tests.fixtures import *


@pytest.mark.asyncio
async def test_create(student_repo: StudentRepository, tutor_repo: TutorRepository):
    data = {
        "telegram_id": 2,
        "first_name": "John",
        "last_name": "Gekhtin",
        "username": "testusername",
        "email_": "test.user@innopolis.university",
    }
    student = await student_repo.create(**data)
    tutor = await tutor_repo.create(student.id)
    assert tutor.id == student.id
    assert tutor.profile_name is None
    assert tutor.about is None
    assert tutor.photo is None
    assert await tutor_repo.exists(tutor.telegram_id)


@pytest.mark.asyncio
async def test_update(student_repo: StudentRepository, tutor_repo: TutorRepository):
    # Create student and tutor
    data = {
        "telegram_id": 3,
        "first_name": "Jane",
        "last_name": "Smith",
        "username": "janesmith",
        "email_": "jane.smith@innopolis.university",
    }
    student = await student_repo.create(**data)
    tutor = await tutor_repo.create(student.id)

    # Update tutor
    updated_tutor = Tutor(
        id=tutor.id,
        telegram_id=tutor.telegram_id,
        first_name=tutor.first_name,
        last_name=tutor.last_name,
        username=tutor.username,
        profile_name="Dr. Jane Smith",
        about="Experienced tutor in computer science",
        photo=None,
    )

    await tutor_repo.update(updated_tutor)

    # Verify update
    fetched_tutor = await tutor_repo.get(id=tutor.id)
    assert fetched_tutor.profile_name == "Dr. Jane Smith"
    assert fetched_tutor.about == "Experienced tutor in computer science"


@pytest.mark.asyncio
async def test_update_with_attrs(student_repo: StudentRepository, tutor_repo: TutorRepository):
    # Create student and tutor
    data = {
        "telegram_id": 4,
        "first_name": "Bob",
        "last_name": "Johnson",
        "username": "bobj",
        "email_": "bob.johnson@innopolis.university",
    }
    student = await student_repo.create(**data)
    tutor = await tutor_repo.create(student.id)

    # Update only specific fields
    updated_tutor = Tutor(
        id=tutor.id,
        telegram_id=tutor.telegram_id,
        first_name=tutor.first_name,
        last_name=tutor.last_name,
        username=tutor.username,
        profile_name="Prof. Bob Johnson",
        about="Math and physics tutor",
        photo=None,
    )

    await tutor_repo.update(updated_tutor, ["profile_name"])

    # Verify only profile_name was updated
    fetched_tutor = await tutor_repo.get(id=tutor.id)
    assert fetched_tutor.profile_name == "Prof. Bob Johnson"
    assert fetched_tutor.about is None  # about should not be updated


@pytest.mark.asyncio
async def test_exists(student_repo: StudentRepository, tutor_repo: TutorRepository):
    # Create student and tutor
    data = {
        "telegram_id": 5,
        "first_name": "Alice",
        "last_name": "Wonder",
        "username": "alicew",
        "email_": "alice.wonder@innopolis.university",
    }
    student = await student_repo.create(**data)
    await tutor_repo.create(student.id)

    # Check exists
    assert await tutor_repo.exists(student.telegram_id) is True
    assert await tutor_repo.exists(999999) is False  # Non-existent telegram_id


@pytest.mark.asyncio
async def test_get_by_id(student_repo: StudentRepository, tutor_repo: TutorRepository):
    # Create student and tutor
    data = {
        "telegram_id": 6,
        "first_name": "Charlie",
        "last_name": "Brown",
        "username": "charlieb",
        "email_": "charlie.brown@innopolis.university",
    }
    student = await student_repo.create(**data)
    created_tutor = await tutor_repo.create(student.id)

    # Get by id
    fetched_tutor = await tutor_repo.get(id=created_tutor.id)
    assert fetched_tutor.id == created_tutor.id
    assert fetched_tutor.telegram_id == student.telegram_id
    assert fetched_tutor.first_name == student.first_name
    assert fetched_tutor.last_name == student.last_name


@pytest.mark.asyncio
async def test_get_by_telegram_id(student_repo: StudentRepository, tutor_repo: TutorRepository):
    # Create student and tutor
    data = {
        "telegram_id": 7,
        "first_name": "Diana",
        "last_name": "Prince",
        "username": "dianap",
        "email_": "diana.prince@innopolis.university",
    }
    student = await student_repo.create(**data)
    created_tutor = await tutor_repo.create(student.id)

    # Get by telegram_id
    fetched_tutor = await tutor_repo.get(telegram_id=student.telegram_id)
    assert fetched_tutor.id == created_tutor.id
    assert fetched_tutor.telegram_id == student.telegram_id


@pytest.mark.asyncio
async def test_get_not_found(tutor_repo: TutorRepository):
    with pytest.raises(LookupError, match="Tutor not found"):
        await tutor_repo.get(id=999999)

    with pytest.raises(LookupError, match="Tutor not found"):
        await tutor_repo.get(telegram_id=999999)


@pytest.mark.asyncio
async def test_get_disciplines(student_repo: StudentRepository, tutor_repo: TutorRepository, discipline_repo):
    # Create student and tutor
    data = {
        "telegram_id": 8,
        "first_name": "Eve",
        "last_name": "Adams",
        "username": "evea",
        "email_": "eve.adams@innopolis.university",
    }
    student = await student_repo.create(**data)
    await tutor_repo.create(student.id)

    # Get disciplines (should be empty initially)
    disciplines = await tutor_repo.get_disciplines(student.id)
    assert len(disciplines) == 0


@pytest.mark.asyncio
async def test_set_disciplines(
    student_repo: StudentRepository,
    tutor_repo: TutorRepository,
    discipline_repo: DisciplineRepository,
):
    # Create student and tutor
    data = {
        "telegram_id": 9,
        "first_name": "Frank",
        "last_name": "Miller",
        "username": "frankm",
        "email_": "frank.miller@innopolis.university",
    }
    student = await student_repo.create(**data)
    await tutor_repo.create(student.id)

    # Get some disciplines
    disciplines = [
        await discipline_repo.create("EN", 1, "First Dist"),
        await discipline_repo.create("EN", 2, "Second Dist"),
        await discipline_repo.create("EN", 2, "Third Dist"),
        await discipline_repo.create("RU", 3, "Четвёртая Дисц"),
    ]

    # Set first two disciplines for tutor
    await tutor_repo.set_disciplines(student.id, disciplines[:2])

    # Verify disciplines were set
    tutor_disciplines = await tutor_repo.get_disciplines(student.id)
    assert len(tutor_disciplines) == 2
    assert tutor_disciplines[0].id in [d.id for d in disciplines[:2]]
    assert tutor_disciplines[1].id in [d.id for d in disciplines[:2]]

    # Update with different disciplines
    await tutor_repo.set_disciplines(student.id, disciplines[2:4])

    # Verify old disciplines were removed and new ones added
    tutor_disciplines = await tutor_repo.get_disciplines(student.id)
    assert len(tutor_disciplines) == 2
    assert tutor_disciplines[0].id in [d.id for d in disciplines[2:4]]
    assert tutor_disciplines[1].id in [d.id for d in disciplines[2:4]]


@pytest.mark.asyncio
async def test_get_list(student_repo: StudentRepository, tutor_repo: TutorRepository):
    # Create multiple tutors
    tutors_data = [
        {"telegram_id": 10, "first_name": "Grace", "last_name": "Hopper", "username": "graceh"},
        {"telegram_id": 11, "first_name": "Alan", "last_name": "Turing", "username": "alant"},
        {"telegram_id": 12, "first_name": "Ada", "last_name": "Lovelace", "username": "adal"},
    ]

    for data in tutors_data:
        data["email_"] = f"{data['username']}@innopolis.university"
        student = await student_repo.create(**data)
        await tutor_repo.create(student.id)

    # Get all tutors
    tutors = await tutor_repo.get_list()
    assert len(tutors) >= 3
