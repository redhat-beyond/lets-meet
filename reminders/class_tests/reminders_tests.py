import pytest
from django.core import mail
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from events.models import EventParticipant
from django.db.utils import IntegrityError
from main.utilities import send_reminder_email
from reminders.models import Reminder, ReminderType
from events.tests import (  # noqa: F401
        new_event, user0,
        event_participant_creator as participant0
)


MESSAGES_0 = 'This is a test text.'
METHOD_0 = ReminderType.EMAIL
TIME_0 = datetime(2023, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)

JOIN_MEETING = 'Joined Meeting in {} minutes'

EXIST_REMINDER_ERROR = 'reminder already exists'
PAST_DATE_TIME_ERROR = "date time should be bigger than the current date_time"


@pytest.fixture
def reminder_0(participant0):  # noqa: F811
    return Reminder(participant_id=participant0, method=METHOD_0, messages=MESSAGES_0, date_time=TIME_0)


def test_new_reminder_0(reminder_0, participant0):  # noqa: F811
    assert reminder_0.participant_id == participant0
    assert reminder_0.method == METHOD_0
    assert reminder_0.messages == MESSAGES_0
    assert reminder_0.date_time == TIME_0


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


@pytest.fixture(autouse=True)
def email_backend_setup():
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.mark.django_db
class TestReminder:

    def test_persist_reminder(self, persist_reminder):
        assert persist_reminder in Reminder.objects.all()

    def test_delete_reminder(self, persist_reminder):
        persist_reminder.delete()
        assert persist_reminder not in Reminder.objects.all()

    def test_exist_reminder(self):
        for event_id, user_id in zip([1, 1, 2], range(1, 4)):
            assert Reminder.objects.filter(
                participant_id=EventParticipant.objects.get(
                    event_id__title=f"event{event_id}",
                    user_id__username=f"testUser{user_id}"
                )
            )

    def test_reminder_with_invalid_time(self, participant0):  # noqa: F811
        date_time = datetime(2022, 3, 22, 12, 12, 12, 0, tzinfo=timezone.utc)

        with pytest.raises(IntegrityError, match=PAST_DATE_TIME_ERROR):
            save_reminder(
                create_reminder(participant0, METHOD_0, MESSAGES_0, date_time)
            )

    def test_reminder_exist_twice(self):
        event_participant = EventParticipant.objects.get(event_id__title="event1", user_id__username="testUser2")
        event_date_time = datetime(2022, 8, 24, 13, 13, 13, 0, tzinfo=timezone.utc)
        message = JOIN_MEETING.format(50)
        method = ReminderType.WEBSITE

        with pytest.raises(IntegrityError, match='reminder already exists'):
            create_reminder(event_participant, method, message, event_date_time).save()

    def test_get_earliest_reminder(self):
        expected_reminder = Reminder.objects.get(
            participant_id__event_id__title="event1",
            participant_id__user_id__username="testUser1"
        )
        assert expected_reminder == Reminder.objects.get_next_reminder()

    def test_email_send(self):
        mail.send_mail('subject', 'body.', 'from@example.com', ['to@example.com'])
        assert len(mail.outbox) == 1

    def test_send_reminder_email(self):
        send_reminder_email("message", "user@mail")
        assert len(mail.outbox) == 1
