"""Test suite for NotificationManager - sends all possible notifications to a target telegram_id."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from aiogram import Bot, Dispatcher

from src.domain.models import Discipline, Meeting, MeetingStatus, NotificationBotStatus, Settings, Student, Tutor
from src.notifications.notification_manager import NotificationManager

# Target telegram ID for all tests
TELEGRAM_ID = 98765432


@pytest.fixture
def mock_bot():
    """Create a mock bot that tracks sent messages."""
    bot = AsyncMock(spec=Bot)
    bot.send_message = AsyncMock(return_value=MagicMock())
    bot.get_me = AsyncMock(return_value=MagicMock(username="notification_bot"))
    return bot


@pytest.fixture
def mock_dispatcher():
    """Create a mock dispatcher."""
    return MagicMock(spec=Dispatcher)


@pytest_asyncio.fixture
async def notification_manager(mock_bot, mock_dispatcher):
    """Create a NotificationManager instance with mocks."""
    manager = NotificationManager(mock_bot, mock_dispatcher)
    manager.set_control_bot_username("control_bot")
    await manager.load_notification_bot_username()
    return manager


@pytest.fixture
def test_student():
    """Create a test student."""
    return Student(
        id=1,
        telegram_id=TELEGRAM_ID,
        language="en",
        email="student@innopolis.university",
        settings=Settings(receive_notifications=True),
        first_name="John",
        last_name="Doe",
        username="johndoe",
        is_admin=False,
        notification_bot_status=NotificationBotStatus.ACTIVATED,
        saw_guide=True,
    )


@pytest.fixture
def test_tutor():
    """Create a test tutor."""
    return Tutor(
        id=2,
        telegram_id=TELEGRAM_ID,
        username="tutor_user",
        first_name="Jane",
        last_name="Smith",
        profile_name="Dr. Jane Smith",
        about="Experienced tutor",
        photo=None,
    )


@pytest.fixture
def test_admin():
    """Create a test admin (student with admin flag)."""
    return Student(
        id=3,
        telegram_id=TELEGRAM_ID,
        language="en",
        email="admin@innopolis.university",
        settings=Settings(receive_notifications=True),
        first_name="Admin",
        last_name="User",
        username="adminuser",
        is_admin=True,
        notification_bot_status=NotificationBotStatus.ACTIVATED,
        saw_guide=True,
    )


@pytest.fixture
def test_discipline():
    """Create a test discipline."""
    return Discipline(
        id=1,
        name="Advanced Programming",
        year=2,
        language="en",
    )


@pytest.fixture
def test_meeting(test_discipline, test_tutor):
    """Create a test meeting."""
    meeting_data = {
        "id": 1,
        "title": "Async Python Workshop",
        "discipline": test_discipline,
        "creator_id": 1,
        "created_at": datetime.now(),
        "status": MeetingStatus.CREATED,
        "duration": 3600,
        "description": "Learn async programming in Python",
        "room": "Room 101",
        "datetime": datetime.now() + timedelta(days=1),
        "tutor_id": test_tutor.id,
    }
    return Meeting.model_validate(meeting_data)


@pytest.fixture
def test_meeting_announced(test_meeting):
    """Create a meeting in ANNOUNCED status."""
    meeting = test_meeting
    meeting.status = MeetingStatus.ANNOUNCED
    return meeting


@pytest.fixture
def test_meeting_approving(test_meeting):
    """Create a meeting in APPROVING status."""
    meeting = test_meeting
    meeting.status = MeetingStatus.APPROVING
    return meeting


@pytest.fixture
def test_meeting_finished(test_meeting):
    """Create a meeting in FINISHED status."""
    meeting = test_meeting
    meeting.status = MeetingStatus.FINISHED
    return meeting


# ============== Tests ==============


@pytest.mark.asyncio
async def test_send_bot_started(notification_manager, mock_bot):
    """Test send_bot_started notification."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            await notification_manager.send_bot_started()

            # Verify send_message was called
            assert mock_bot.send_message.called
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == TELEGRAM_ID
            assert "started" in call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_send_bot_shutdown(notification_manager, mock_bot):
    """Test send_bot_shutdown notification."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            await notification_manager.send_bot_shutdown()

            assert mock_bot.send_message.called
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == TELEGRAM_ID
            assert "shut down" in call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_send_receive_notification_enabled(notification_manager, mock_bot, test_student):
    """Test notification enabled toggle."""
    with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
        mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
        mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

        await notification_manager.send_receive_notification_toggled(test_student.id, enabled=True)

        assert mock_bot.send_message.called
        call_args = mock_bot.send_message.call_args
        assert call_args[1]["chat_id"] == TELEGRAM_ID
        assert "enabled" in call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_send_receive_notification_disabled(notification_manager, mock_bot, test_student):
    """Test notification disabled toggle."""
    with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
        mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
        mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

        await notification_manager.send_receive_notification_toggled(test_student.id, enabled=False)

        assert mock_bot.send_message.called
        call_args = mock_bot.send_message.call_args
        assert call_args[1]["chat_id"] == TELEGRAM_ID
        assert "disabled" in call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_send_meeting_tutor_assigned(notification_manager, mock_bot, test_meeting, test_tutor):
    """Test meeting tutor assigned notification."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            await notification_manager.send_meeting_tutor_assigned(test_meeting, test_tutor)

            assert mock_bot.send_message.called
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == TELEGRAM_ID
            assert test_meeting.title in call_args[1]["text"]


@pytest.mark.asyncio
async def test_send_meeting_tutor_changed(notification_manager, mock_bot, test_meeting, test_tutor):
    """Test meeting tutor changed notification."""
    old_tutor = Tutor(
        id=99,
        telegram_id=TELEGRAM_ID,
        username="old_tutor",
        first_name="Old",
        last_name="Tutor",
    )
    new_tutor = test_tutor

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            test_meeting.status = MeetingStatus.ANNOUNCED

            await notification_manager.send_meeting_tutor_changed(test_meeting, old_tutor, new_tutor)

            assert mock_bot.send_message.called


@pytest.mark.asyncio
async def test_send_meeting_updated_datetime(notification_manager, mock_bot, test_meeting, test_tutor):
    """Test meeting datetime updated notification."""
    test_meeting.tutor_id = test_tutor.id
    test_meeting.status = MeetingStatus.ANNOUNCED

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_interested_student_ids = AsyncMock(return_value=[])

                await notification_manager.send_meeting_updated(test_meeting, "datetime_")

                assert mock_bot.send_message.called


@pytest.mark.asyncio
async def test_send_meeting_updated_room(notification_manager, mock_bot, test_meeting, test_tutor):
    """Test meeting room updated notification."""
    test_meeting.tutor_id = test_tutor.id
    test_meeting.status = MeetingStatus.ANNOUNCED

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_interested_student_ids = AsyncMock(return_value=[])

                await notification_manager.send_meeting_updated(test_meeting, "room")

                assert mock_bot.send_message.called


@pytest.mark.asyncio
async def test_send_meeting_approve_request(notification_manager, mock_bot, test_meeting, test_tutor):
    """Test meeting approve request notification with buttons."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            await notification_manager.send_meeting_approve_request(test_meeting, test_tutor)

            assert mock_bot.send_message.called
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == TELEGRAM_ID
            assert test_meeting.datetime_.isoformat(sep=" ", timespec="minutes") in call_args[1]["text"]
            # Verify that reply_markup is sent (buttons)
            assert call_args[1]["reply_markup"] is not None


@pytest.mark.asyncio
async def test_send_meeting_approved(notification_manager, mock_bot, test_meeting, test_tutor):
    """Test meeting approved notification."""
    test_meeting.tutor_id = test_tutor.id

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            await notification_manager.send_meeting_approved(test_meeting)

            assert mock_bot.send_message.called
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == TELEGRAM_ID
            assert "approved" in call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_send_meeting_discarded(notification_manager, mock_bot, test_meeting, test_tutor):
    """Test meeting discarded notification."""
    test_meeting.tutor_id = test_tutor.id

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            await notification_manager.send_meeting_discarded(test_meeting, "Conflict with other meetings")

            assert mock_bot.send_message.called
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == TELEGRAM_ID
            assert "discarded" in call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_send_meeting_announced(notification_manager, mock_bot, test_meeting_announced, test_tutor):
    """Test meeting announced notification."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_interested_student_ids = AsyncMock(return_value=[])

                await notification_manager.send_meeting_announced(test_meeting_announced, test_tutor)

                assert mock_bot.send_message.called


@pytest.mark.asyncio
async def test_send_meeting_cancelled(notification_manager, mock_bot, test_meeting_announced):
    """Test meeting cancelled notification."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_interested_student_ids = AsyncMock(return_value=[])

                await notification_manager.send_meeting_cancelled(test_meeting_announced)

                assert mock_bot.send_message.called
                call_args = mock_bot.send_message.call_args
                assert "cancelled" in call_args[1]["text"].lower()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("reminder_kind", "expected_phrase"),
    [
        ("24h", "starts in 24 hours"),
        ("1h", "starts in 1 hour"),
    ],
)
async def test_send_meeting_reminder(
    notification_manager, mock_bot, test_meeting_announced, test_tutor, reminder_kind, expected_phrase
):
    """Test meeting reminder notification."""
    test_meeting_announced.tutor_id = test_tutor.id

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_interested_student_ids = AsyncMock(return_value=[])
                with patch("src.notifications.notification_manager.tutor_repo") as mock_tutor_repo:
                    mock_tutor_repo.get = AsyncMock(return_value=test_tutor)

                    await notification_manager.send_meeting_reminder(
                        test_meeting_announced, reminder_kind=reminder_kind
                    )

                    assert mock_bot.send_message.called
                    call_args = mock_bot.send_message.call_args
                    assert expected_phrase in call_args[1]["text"].lower()
                    assert (
                        test_meeting_announced.datetime_.isoformat(sep=" ", timespec="minutes") in call_args[1]["text"]
                    )


@pytest.mark.asyncio
async def test_send_meeting_started(notification_manager, mock_bot, test_meeting_announced, test_tutor):
    """Test meeting started notification."""
    test_meeting_announced.tutor_id = test_tutor.id
    test_meeting_announced.status = MeetingStatus.CONDUCTING

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_interested_student_ids = AsyncMock(return_value=[])

            with patch("src.notifications.notification_manager.tutor_repo") as mock_tutor_repo:
                mock_tutor_repo.get = AsyncMock(return_value=test_tutor)

                await notification_manager.send_meeting_started(test_meeting_announced)

                assert mock_bot.send_message.called


@pytest.mark.asyncio
async def test_send_meeting_finished(notification_manager, mock_bot, test_meeting_finished, test_tutor):
    """Test meeting finished notification."""
    test_meeting_finished.tutor_id = test_tutor.id

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.tutor_repo") as mock_tutor_repo:
                mock_tutor_repo.get = AsyncMock(return_value=test_tutor)

                await notification_manager.send_meeting_finished(test_meeting_finished)

                assert mock_bot.send_message.called
                call_args = mock_bot.send_message.call_args
                assert "finished" in call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_send_meeting_closed_by_admin(notification_manager, mock_bot, test_meeting_finished, test_tutor):
    """Test meeting closed by admin notification."""
    test_meeting_finished.tutor_id = test_tutor.id
    test_meeting_finished.status = MeetingStatus.CLOSED

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_attendance = AsyncMock(return_value=[1, 2, 3])

                await notification_manager.send_meeting_closed(test_meeting_finished, by_admin=True)

                assert mock_bot.send_message.called


@pytest.mark.asyncio
async def test_send_meeting_closed_by_tutor(notification_manager, mock_bot, test_meeting_finished, test_tutor):
    """Test meeting closed by tutor notification."""
    test_meeting_finished.tutor_id = test_tutor.id
    test_meeting_finished.status = MeetingStatus.CLOSED

    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_attendance = AsyncMock(return_value=[1, 2, 3])

                await notification_manager.send_meeting_closed(test_meeting_finished, by_admin=False)

                assert mock_bot.send_message.called


@pytest.mark.asyncio
async def test_send_tutor_promoted(notification_manager, mock_bot, test_tutor):
    """Test tutor promoted notification."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            await notification_manager.send_tutor_promoted(test_tutor)

            assert mock_bot.send_message.called
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == TELEGRAM_ID
            assert "promoted" in call_args[1]["text"].lower()


@pytest.mark.asyncio
async def test_send_tutor_dismissed(notification_manager, mock_bot, test_tutor):
    """Test tutor dismissed notification."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            await notification_manager.send_tutor_dismissed(test_tutor)

            assert mock_bot.send_message.called
            call_args = mock_bot.send_message.call_args
            assert call_args[1]["chat_id"] == TELEGRAM_ID
            assert "dismissed" in call_args[1]["text"].lower()


# ============== Integration Tests ==============


@pytest.mark.asyncio
async def test_localized_button_labels(notification_manager, mock_bot):
    """Test that buttons are properly localized for en and ru languages."""
    notification_manager.set_control_bot_username("test_control_bot")

    # Test English
    markup_en = notification_manager.gen_approve_discard_request_reply_markup(1, lang="en")
    assert len(markup_en.inline_keyboard) == 1
    assert len(markup_en.inline_keyboard[0]) == 2
    assert "✅" in markup_en.inline_keyboard[0][0].text
    assert "❌" in markup_en.inline_keyboard[0][1].text

    # Test Russian
    markup_ru = notification_manager.gen_approve_discard_request_reply_markup(1, lang="ru")
    assert len(markup_ru.inline_keyboard) == 1
    assert len(markup_ru.inline_keyboard[0]) == 2
    # Russian buttons should have different text
    assert markup_ru.inline_keyboard[0][0].text != markup_en.inline_keyboard[0][0].text


@pytest.mark.asyncio
async def test_all_notifications_send_to_target_telegram_id(
    notification_manager, mock_bot, test_meeting, test_tutor, test_admin
):
    """Verify all notifications are sent to the target TELEGRAM_ID."""
    with patch("src.notifications.notification_manager.admin_repo") as mock_admin_repo:
        mock_admin_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])

        with patch("src.notifications.notification_manager.student_repo") as mock_student_repo:
            mock_student_repo.get_telegram_ids = AsyncMock(return_value=[TELEGRAM_ID])
            mock_student_repo.get_language_by_telegram_ids = AsyncMock(return_value={TELEGRAM_ID: "en"})

            with patch("src.notifications.notification_manager.meeting_repo") as mock_meeting_repo:
                mock_meeting_repo.get_interested_student_ids = AsyncMock(return_value=[])
                mock_meeting_repo.get_attendance = AsyncMock(return_value=[])

            with patch("src.notifications.notification_manager.tutor_repo") as mock_tutor_repo:
                mock_tutor_repo.get = AsyncMock(return_value=test_tutor)

                # Send all notifications
                await notification_manager.send_bot_started()
                await notification_manager.send_bot_shutdown()
                await notification_manager.send_meeting_tutor_assigned(test_meeting, test_tutor)
                await notification_manager.send_meeting_approved(test_meeting)
                await notification_manager.send_tutor_promoted(test_tutor)
                await notification_manager.send_tutor_dismissed(test_tutor)

                # Verify all calls were made to the target TELEGRAM_ID
                call_count = mock_bot.send_message.call_count
                assert call_count > 0

                for call in mock_bot.send_message.call_args_list:
                    assert call[1]["chat_id"] == TELEGRAM_ID
