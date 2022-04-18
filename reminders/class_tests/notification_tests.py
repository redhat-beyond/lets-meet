import pytest
from django.utils import timezone
from datetime import datetime
from events.models import EventParticipant
from events.tests import new_event, user0  # noqa: F401
from events.tests import event_participant_creator as participant0  # noqa: F401
from ..models import Notification, ReminderType
from django.db import IntegrityError
from django.core.exceptions import ValidationError

METHOD_0 = ReminderType.EMAIL
MESSAGE_0 = 'Testing 123 and a 4 and a 5.'
SEEN_TIME_0 = datetime(2024, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
SENT_TIME_0 = datetime(2023, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
BAD_SEEN_TIME_0 = datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
JOIN_MEETING = 'Joined Meeting in {} minutes'
PAST_DATE_TIME_ERROR = "{} is not a valid date_time"
EXIST_NOTIFICATION_ERROR = 'reminder already exists'


@pytest.fixture
def notification_0(participant0):  # noqa: F811
    return Notification(participant_id=participant0, seen_time=SEEN_TIME_0, sent_time=SENT_TIME_0,
                        message=MESSAGE_0)


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
        assert Notification.objects.filter(
            participant_id=EventParticipant.objects.get(event_id__title="event1",
                                                        user_id__username="testUser1")
        )
        assert Notification.objects.filter(
            participant_id=EventParticipant.objects.get(event_id__title="event1",
                                                        user_id__username="testUser2")
        )
        assert Notification.objects.filter(
            participant_id=EventParticipant.objects.get(event_id__title="event2",
                                                        user_id__username="testUser3")
        )

    def test_invalid_time(self):
        participant = EventParticipant.objects.get(event_id__title="event2", user_id__username="testUser3")
        date_time_sent = datetime(2000, 2, 24, 11, 11, 11, 0, tzinfo=timezone.utc)
        date_time_read = timezone.now()
        message = JOIN_MEETING.format(35)
        expected = 'sent time should be bigger than the current date'

        with pytest.raises(IntegrityError, match=expected):
            create_notification(participant, date_time_read, date_time_sent, message).save()

    def test_duplication_of_notification(self):  # noqa: F811
        participant = EventParticipant.objects.get(event_id__title="event2", user_id__username="testUser3")
        date_time_sent = datetime(2032, 2, 24, 11, 11, 11, 0, tzinfo=timezone.utc)
        date_time_read = datetime(2033, 3, 24, 11, 11, 11, 0, tzinfo=timezone.utc)
        message = JOIN_MEETING.format(35)
        expected = 'notification already exists'

        with pytest.raises(ValidationError, match=expected):
            create_notification(participant, date_time_read, date_time_sent, message).save()
