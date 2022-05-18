import pytest
from django.utils import timezone
from django.utils.datetime_safe import datetime
from events.class_models.event_models import Colors
from events.class_tests.create_events import TITLE
from reminders.class_models.reminder_models import ReminderType


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
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 14, 0, 0, tzinfo=timezone.utc
    )
    pytest.date_time_start = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 13, 0, 0, tzinfo=timezone.utc
    )
    pytest.reminder_date_time = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 14, 0, 0, tzinfo=timezone.utc
    )

    pytest.reminder_creation_url = '/event/create/'
    pytest.reminder_update_url = '/event/update/{}'.format(1)
    pytest.reminder_creation_html_path = "events/create_event.html"

    pytest.exist_reminder_error = 'reminder already exists'
    pytest.past_date_time_error = "date time should be bigger than the current date_time"


@pytest.fixture
def signed_up_user_details():
    return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}


@pytest.fixture
def sign_in(client, signed_up_user_details):
    return client.post('/login/', data=signed_up_user_details)


@pytest.fixture
def valid_event_data_and_reminder():
    return {'title': TITLE, 'date_time_start': pytest.date_time_start,
            'date_time_end': pytest.date_time_end, 'color': Colors.BLACK,
            'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}
