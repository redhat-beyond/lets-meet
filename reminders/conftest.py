import pytest
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from reminders.models import Reminder, ReminderType, Notification
from events.models import Event, EventParticipant, Colors
from events.tests import (  # noqa: F401
        new_event, user0,
        event_participant_creator as participant0
)


# define constants
def pytest_configure():
    pytest.invalid_method = "undefined"
    pytest.current_date = datetime.now()
    pytest.valid_method = ReminderType.EMAIL
    pytest.message = "Joined Meeting in 50 minutes"
    pytest.valid_date_time = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 12, 0, 0, tzinfo=timezone.utc
    )
    pytest.invalid_date_time = datetime(
        pytest.current_date.year - 1, pytest.current_date.month, pytest.current_date.day, 12, 0, 0, tzinfo=timezone.utc
    )

    pytest.date_time_end = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 13, 0, 0, tzinfo=timezone.utc
    )
    pytest.date_time_start = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 15, 0, 0, tzinfo=timezone.utc
    )
    pytest.reminder_date_time = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 14, 0, 0, tzinfo=timezone.utc
    )

    pytest.reminder_creation_url = '/event/create/'
    pytest.reminder_update_url = '/event/update/{}'.format(1)
    pytest.reminder_update_url_event2 = '/event/update/{}'.format(2)
    pytest.reminder_creation_html_path = "events/create_event.html"

    pytest.exist_reminder_error = 'reminder already exists'
    pytest.past_date_time_error = "date time should be bigger than the current date_time"

    pytest.row_duplication_error = 'notification already exists'
    pytest.notification_past_date_time_error = 'seen time cannot be earlier than time of creation.'

    pytest.get_notification_url = '/notification/get-notification/'
    pytest.seen_notification_url = '/notification/seen-notification/{}'


@pytest.fixture
def signed_up_user_details():
    return {'email': 'testUser2@mta.ac.il', 'password': 'PasswordU$er456'}


@pytest.fixture
def sign_in(client, signed_up_user_details):
    return client.post('/login/', data=signed_up_user_details)


@pytest.fixture
def signed_up_user3_details():
    return {'email': 'testUser3@mta.ac.il', 'password': 'PasswordU$er789'}


@pytest.fixture
def sign_in_user_3(client, signed_up_user3_details):
    return client.post('/login/', data=signed_up_user3_details)


@pytest.fixture
def get_event_participant():
    return EventParticipant.objects.get(id=1)


@pytest.fixture
def valid_event_data():
    return {'title': "test event", 'date_time_start': pytest.date_time_start,
            'date_time_end': pytest.date_time_end, 'color': Colors.BLACK,
            'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}


@pytest.fixture
def valid_updated_event_data():
    reminder = Event.objects.get(id=1)
    return {'title': reminder.title, 'date_time_start': reminder.date_time_start,
            'date_time_end': reminder.date_time_end, 'color': Colors.RED,
            'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}


@pytest.fixture
def reminder_0(participant0):  # noqa: F811
    return Reminder(
        participant_id=participant0, method=pytest.valid_method,
        messages=pytest.message, date_time=pytest.valid_date_time
    )


@pytest.fixture(autouse=True)
def email_backend_setup():
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.fixture
def notification_0(participant0):  # noqa: F811
    return Notification(
        participant_id=participant0, seen_time=pytest.date_time_start,
        sent_time=pytest.date_time_end, message=pytest.message
    )


@pytest.fixture
def event_participant():
    return EventParticipant.objects.get(event_id__title="event2", user_id__username="testUser3")
