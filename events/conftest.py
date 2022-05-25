import pytest
from datetime import datetime
from django.utils import timezone
from events.class_models.event_models import Colors
from reminders.class_models.reminder_models import ReminderType


# define constants
def pytest_configure():

    pytest.current_date = datetime.now()

    pytest.event_date_time_end = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 14, 0, 0, tzinfo=timezone.utc
    )
    pytest.event_date_time_start = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 13, 0, 0, tzinfo=timezone.utc
    )

    pytest.reminder_date_time = pytest.event_date_time_start

    pytest.create_event_url = "/event/create/"
    pytest.create_event_template = 'events/create_event.html'
    pytest.login_page_template = 'login/register_login.html'
    pytest.update_event_url = '/event/update/'

    pytest.valid_event_date_time_start = "2012-11-11 11:11"
    pytest.valid_event_date_time_end = "2012-12-12 12:12"
    pytest.valid_event_color = Colors.BLACK
    pytest.valid_event_title = 'new_form'

    pytest.updated_event_title = 'updated_event'
    pytest.updated_event_date_time_start = "2012-12-12 12:12"
    pytest.updated_event_date_time_end = "2012-12-12 13:13"
    pytest.updated_event_color = Colors.WHITE


@pytest.fixture
def signed_up_user_details():
    return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}


@pytest.fixture
def sign_in(client, signed_up_user_details):
    return client.post('/login/', data=signed_up_user_details)


@pytest.fixture
def valid_event_data_and_reminder():
    return {'title':  pytest.valid_event_title, 'date_time_start': pytest.event_date_time_start,
            'date_time_end': pytest.event_date_time_end, 'color': pytest.valid_event_color,
            'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}


@pytest.fixture
def updated_event_data_and_reminder():
    return {'title': pytest.updated_event_title, 'date_time_start': pytest.updated_event_date_time_start,
            'date_time_end': pytest.updated_event_date_time_end, 'color': pytest.updated_event_color,
            'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}
