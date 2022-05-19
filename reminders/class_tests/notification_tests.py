import pytest
from datetime import datetime
from django.utils import timezone
from django.db import IntegrityError
from django.forms import ValidationError
from events.models import EventParticipant
from reminders.models import Notification
from events.tests import (  # noqa: F401
    new_event, user0,
    event_participant_creator as participant0
)


@pytest.fixture
def persist_notification(notification_0):
    return save_notification(notification_0)


def create_notification(participant_id, seen_time, sent_time, message):
    return Notification(participant_id=participant_id, seen_time=seen_time, sent_time=sent_time, message=message)


def save_notification(notification):
    notification.participant_id.user_id.save()
    notification.participant_id.event_id.save()
    notification.participant_id.save()
    notification.save()
    return notification


@pytest.mark.django_db
class TestNotification:

    def test_persist_notification(self, persist_notification):
        assert persist_notification in Notification.objects.all()

    def test_delete_notification(self, persist_notification):
        persist_notification.delete()
        assert persist_notification not in Notification.objects.all()

    def test_exist_notification(self):
        for event_id, user_id in zip([1, 1, 2], range(1, 4)):
            assert Notification.objects.filter(
                participant_id=EventParticipant.objects.get(
                    event_id__title=f"event{event_id}",
                    user_id__username=f"testUser{user_id}"
                )
            )

    def test_invalid_time(self, event_participant):
        date_time_read = timezone.now()

        with pytest.raises(ValidationError, match=pytest.notification_past_date_time_error):
            create_notification(event_participant, date_time_read, pytest.date_time_end, pytest.message).save()

    def test_duplication_of_notification(self, event_participant):  # noqa: F811
        date_time_sent = datetime(2032, 2, 24, 11, 11, 11, 0, tzinfo=timezone.utc)
        date_time_read = datetime(2033, 3, 24, 11, 11, 11, 0, tzinfo=timezone.utc)

        with pytest.raises(IntegrityError, match=pytest.row_duplication_error):
            create_notification(event_participant, date_time_read, date_time_sent, pytest.message).save()
