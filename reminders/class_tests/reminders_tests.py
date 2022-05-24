from django.forms import ValidationError
import pytest
from django.core import mail
from datetime import datetime
from django.utils import timezone
from events.models import EventParticipant
from django.db.utils import IntegrityError
from main.utilities import send_reminder_email
from reminders.models import Reminder, ReminderType


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

    def test_new_reminder_0(self, reminder_0, participant0):
        assert reminder_0.participant_id == participant0
        assert reminder_0.method == pytest.valid_method
        assert reminder_0.messages == pytest.message
        assert reminder_0.date_time == pytest.valid_date_time

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

    def test_reminder_with_invalid_time(self, participant0):
        date_time = datetime(2022, 3, 22, 12, 12, 12, 0, tzinfo=timezone.utc)

        with pytest.raises(ValidationError, match=pytest.past_date_time_error):
            save_reminder(
                reminder=create_reminder(participant0, pytest.valid_method, pytest.message, date_time)
            )

    def test_reminder_exist_twice(self):
        event_participant = EventParticipant.objects.get(event_id__title="event1", user_id__username="testUser2")
        event_date_time = datetime(2022, 8, 24, 13, 13, 13, 0, tzinfo=timezone.utc)
        method = ReminderType.WEBSITE

        with pytest.raises(IntegrityError, match=pytest.exist_reminder_error):
            create_reminder(event_participant, method, pytest.message, event_date_time).save()

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
        send_reminder_email("message", EventParticipant.objects.get(id=1))
        assert len(mail.outbox) == 1
