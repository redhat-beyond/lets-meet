import pytest
from datetime import datetime
from django.utils import timezone
from reminders.models import ReminderType
from events.models import EventParticipant, Colors


# define constants
def pytest_configure():

    pytest.current_date = datetime.now()
    pytest.event_date_time_end = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 14, 0, 0, tzinfo=timezone.utc
    )
    pytest.event_date_time_start = datetime(
        pytest.current_date.year, pytest.current_date.month, pytest.current_date.day + 1, 13, 0, 0, tzinfo=timezone.utc
    )

    pytest.create_event_url = "/event/create/"
    pytest.create_event_template = 'events/create_event.html'
    pytest.login_page_template = 'login/register_login.html'
    pytest.update_event_url = '/event/update/'

    pytest.valid_event_date_time_start = "2012-11-11 11:11"
    pytest.valid_event_date_time_end = "2012-12-12 12:12"
    pytest.valid_event_color = Colors.BLACK
    pytest.valid_event_title = 'new_form'
    pytest.home_url = "/main/"

    pytest.login_url = "/login/"
    pytest.meeting_vote_url = "/event/meeting_vote/{}"
    pytest.meeting_vote_html_path = "vote/meeting_vote.html"
    pytest.remove_participant_url = "/event/remove_participant/{}"

    pytest.updated_event_title = 'updated_event'
    pytest.updated_event_date_time_start = "2012-12-12 12:12"
    pytest.updated_event_date_time_end = "2012-12-12 13:13"
    pytest.updated_event_color = Colors.WHITE


@pytest.fixture
def signed_up_user_details():
    return {'email': 'testUser2@mta.ac.il', 'password': 'PasswordU$er456'}


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


@pytest.fixture
def get_event_participant():
    return EventParticipant.objects.get(id=8)


@pytest.fixture
def valid_meeting_vote_data():
    return {'date_vote': True}
