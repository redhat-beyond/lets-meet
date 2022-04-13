import pytest
from django.utils import timezone
from datetime import datetime
from events.models import EventParticipant
from events.tests import new_event, user0  # noqa: F401
from events.tests import event_participant_creator as participant0  # noqa: F401
from django.core.exceptions import ValidationError
from ..models import Reminder, ReminderType, time_format

METHOD_0 = ReminderType.EMAIL
MESSAGES_0 = 'This is a test text.'
TIME_0 = datetime(2023, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)

JOIN_MEETING = 'Joined Meeting in {minutes} minutes'
PAST_DATE_TIME_ERROR = "{} is not a valid date_time"
EXIST_REMINDER_ERROR = 'reminder already exists'


@pytest.fixture
def reminder_0(participant0):  # noqa: F811
    return Reminder(participant_id=participant0, method=METHOD_0, messages=MESSAGES_0, date_time=TIME_0)


@pytest.fixture
def persist_reminder(reminder_0):
    return save_reminder(reminder_0)


def create_reminder(participant_id, method, messages, date_time):
    return Reminder(participant_id=participant_id, method=method, messages=messages, date_time=date_time)


def save_reminder(reminder):
    reminder.participant_id.user_id.save()
    reminder.participant_id.event_id.save()
    reminder.participant_id.save()
    reminder.save()
    return reminder


@pytest.mark.django_db
class TestReminder:

    def test_persist_reminder(self, persist_reminder):
        assert persist_reminder in Reminder.objects.all()

    def test_delete_reminder(self, persist_reminder):
        persist_reminder.delete()
        assert persist_reminder not in Reminder.objects.all()

    def test_exist_reminder(self):
        assert Reminder.objects.filter(
            participant_id=EventParticipant.objects.get(event_id__title="event1",
                                                        user_id__username="testUser1")
        )
        assert Reminder.objects.filter(
            participant_id=EventParticipant.objects.get(event_id__title="event1",
                                                        user_id__username="testUser2")
        )
        assert Reminder.objects.filter(
            participant_id=EventParticipant.objects.get(event_id__title="event2",
                                                        user_id__username="testUser3")
        )

    def test_reminder_with_invalid_time(self, participant0, date_time=TIME_0):  # noqa: F811
        date_time = datetime(2022, 3, 22, 12, 12, 12, 0, tzinfo=timezone.utc)
        expected = f'{time_format(date_time)} should be bigger than current.'

        with pytest.raises(ValidationError, match=expected):
            save_reminder(
                create_reminder(participant0, METHOD_0, MESSAGES_0, date_time)
            )

    def test_invalid_reminder_exist_twice(self, persist_reminder):
        with pytest.raises(Exception, match=EXIST_REMINDER_ERROR):
            persist_reminder.save()
