import pytest
from events.models import EventParticipant


# define constants
def pytest_configure():
    pytest.meeting_vote_url = "/event/meeting_vote/"
    pytest.meeting_vote_html_path = "events/meeting_vote.html"


@pytest.fixture
def signed_up_user_details():
    return {'email': 'testUser2@mta.ac.il', 'password': 'PasswordU$er456'}


@pytest.fixture
def sign_in(client, signed_up_user_details):
    return client.post('/login/', data=signed_up_user_details)


@pytest.fixture
def get_event_participant():
    return EventParticipant.objects.get(id=2)


@pytest.fixture
def valid_meeting_vote_data():
    return {'date_vote': True}
