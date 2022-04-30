import pytest
from datetime import datetime
from django.utils import timezone
from django.db import IntegrityError
from events.models import EventParticipant
from reminders.models import Notification
from django.core.exceptions import ValidationError
from events.tests import (  # noqa: F401
    new_event, user0,
    event_participant_creator as participant0
)

<<<<<<< HEAD
=======

MESSAGE_0 = 'Testing 123 and a 4 and a 5.'
JOIN_MEETING = 'Joined Meeting in {} minutes'
SEEN_TIME_0 = datetime(2024, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
SENT_TIME_0 = datetime(2023, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)

ROW_DUPLICATION_ERROR = 'notification already exists'
PAST_DATE_TIME_ERROR = 'seen time cannot be earlier than time of creation.'


@pytest.fixture
def notification_0(participant0):  # noqa: F811
    return Notification(
        participant_id=participant0, seen_time=SEEN_TIME_0, sent_time=SENT_TIME_0, message=MESSAGE_0
    )

>>>>>>> 707a363... Comments And ForEach:

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

    @pytest.fixture
    def event_participant(self):
        return EventParticipant.objects.get(event_id__title="event2", user_id__username="testUser3")

    @pytest.fixture
    def notification_message(self):
        return JOIN_MEETING.format(35)

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

<<<<<<< HEAD
    def test_invalid_time(self, event_participant):
        date_time_read = timezone.now()

        with pytest.raises(IntegrityError, match=pytest.notification_past_date_time_error):
            create_notification(event_participant, date_time_read, pytest.invalid_date_time, pytest.message).save()

    def test_duplication_of_notification(self, event_participant):  # noqa: F811
        date_time_sent = datetime(2032, 2, 24, 11, 11, 11, 0, tzinfo=timezone.utc)
        date_time_read = datetime(2033, 3, 24, 11, 11, 11, 0, tzinfo=timezone.utc)

        with pytest.raises(IntegrityError, match=pytest.row_duplication_error):
            create_notification(event_participant, date_time_read, date_time_sent, pytest.message).save()
=======
    def test_invalid_time(self, event_participant, notification_message):
        date_time_read = datetime(2000, 2, 24, 11, 11, 11, 0, tzinfo=timezone.utc)
        date_time_sent = timezone.now()

        with pytest.raises(ValidationError, match=PAST_DATE_TIME_ERROR):
            create_notification(event_participant, date_time_read, date_time_sent, notification_message).save()

    def test_duplication_of_notification(self, event_participant, notification_message):  # noqa: F811
        date_time_sent = datetime(2032, 2, 24, 11, 11, 11, 0, tzinfo=timezone.utc)
        date_time_read = datetime(2033, 3, 24, 11, 11, 11, 0, tzinfo=timezone.utc)

        with pytest.raises(IntegrityError, match=ROW_DUPLICATION_ERROR):
            create_notification(event_participant, date_time_read, date_time_sent, notification_message).save()
>>>>>>> 707a363... Comments And ForEach:
