import pytest
from datetime import datetime
from django.utils import timezone
from django.db import IntegrityError
from main.utilities import time_format
from events.models import EventParticipant
from django.core.exceptions import ValidationError
from reminders.models import Reminder, ReminderType
from events.tests import (  # noqa: F401
    new_event, user0,
    event_participant_creator as participant0
)

METHOD_0 = ReminderType.EMAIL
MESSAGES_0 = 'This is a test text.'
TIME_0 = datetime(2023, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)

JOIN_MEETING = 'Joined Meeting in {} minutes'
EXIST_REMINDER_ERROR = 'reminder already exists'
PAST_DATE_TIME_ERROR = "{} is not a valid date_time"


@pytest.fixture
def reminder_0(participant0):  # noqa: F811
    return Reminder(participant_id=participant0, method=METHOD_0, messages=MESSAGES_0, date_time=TIME_0)


@pytest.fixture
def persist_reminder(reminder_0):
    return save_reminder(reminder_0)


def create_reminder(participant_id, date_time, messages, method):
    return Reminder(participant_id=participant_id, date_time=date_time, messages=messages, method=method)


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
            save_reminder(create_reminder(participant0, date_time, MESSAGES_0, METHOD_0))

    def test_invalid_reminder_exist_twice(self):
        participant = EventParticipant.objects.get(event_id__title="event2", user_id__username="testUser3")
        date_time = datetime(2022, 8, 14, 13, 13, 13, 0, tzinfo=timezone.utc)
        message = JOIN_MEETING.format(30)
        reminder_type = ReminderType.WEBSITE

        with pytest.raises(IntegrityError, match=EXIST_REMINDER_ERROR):
            create_reminder(participant, date_time, message, reminder_type).save()
