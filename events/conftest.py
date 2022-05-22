import pytest
from django.utils import timezone
from django.utils.datetime_safe import datetime
from events.class_models.event_models import Colors
from reminders.class_models.reminder_models import ReminderType
from events.class_tests.create_events import DATE_TIME_START, DATE_TIME_END, COLOR, TITLE


# define constants
def pytest_configure():

    pytest.current_date = datetime.now()

    pytest.event_date_time_end = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 14, 0, 0, tzinfo=timezone.utc
    )
    pytest.event_date_time_start = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 13, 0, 0, tzinfo=timezone.utc
    )

    pytest.CREATE_EVENT_URL = "/event/create/"
    pytest.CREATE_EVENT_TEMPLATE = 'events/create_event.html'
    pytest.LOGIN_PAGE_TEMPLATE = 'login/register_login.html'

    pytest.valid_event_date_time_start = DATE_TIME_START
    pytest.valid_event_date_time_end = DATE_TIME_END
    pytest.valid_event_color = COLOR
    pytest.valid_event_title = TITLE


@pytest.fixture
def signed_up_user_details():
    return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}


@pytest.fixture
def sign_in(client, signed_up_user_details):
    return client.post('/login/', data=signed_up_user_details)


@pytest.fixture
def valid_event_data_and_reminder():
    return {'title': TITLE, 'date_time_start': pytest.event_date_time_start,
            'date_time_end': pytest.event_date_time_end, 'color': Colors.BLACK,
            'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}
