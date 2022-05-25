import pytest
from json import loads
from users.models import User
from users.tests import persist_user  # noqa: F401
from events.forms import EventCreationForm
from events.models import Event, Colors, EventParticipant
from datetime import datetime
from django.utils import timezone

# form preferences -> new event preferences
TITLE = 'new_form'
LOCATION = 'new_form_location'
DESCRIPTION = 'new_form_description'
EVENT_DATE_TIME_START = datetime(2023, 11, 11, 12, 12, 12, 0, tzinfo=timezone.utc)
EVENT_DATE_TIME_END = datetime(2023, 11, 11, 14, 12, 12, 0, tzinfo=timezone.utc)
COLOR = Colors.BLACK


@pytest.fixture
def valid_event_data():
    return {
        "title": TITLE,
        "location": LOCATION,
        "description": DESCRIPTION,
        "date_time_start": EVENT_DATE_TIME_START,
        "date_time_end": EVENT_DATE_TIME_END,
        "color": COLOR,
        }


@pytest.mark.django_db
class TestCreateEventForm:

    @pytest.mark.parametrize("invalid_data", [
            # title cannot be None
            {'title': None, 'date_time_start': EVENT_DATE_TIME_START,
             'date_time_end': EVENT_DATE_TIME_END, 'color': COLOR},
            # title cannot be blank
            {'title': "", 'date_time_start': EVENT_DATE_TIME_START,
             'date_time_end': EVENT_DATE_TIME_END, 'color': COLOR},
            # date_time_start cannot be None
            {'title': TITLE, 'date_time_start': None,
             'date_time_end': EVENT_DATE_TIME_END, 'color': COLOR},
            # date_time_end cannot be None
            {'title': TITLE, 'date_time_start': EVENT_DATE_TIME_START,
             'date_time_end': None, 'color': COLOR},
            # date_time_end must be bigger than date_time_start
            {'title': TITLE, 'date_time_start': EVENT_DATE_TIME_END,
             'date_time_end': EVENT_DATE_TIME_START, 'color': COLOR},
            # date_time_end cannot be equal to date_time_start
            {'title': TITLE, 'date_time_start': EVENT_DATE_TIME_START,
             'date_time_end': EVENT_DATE_TIME_START, 'color': COLOR},
        ], ids=[
            "title is none",
            "title is blank",
            "star time is none",
            "end time is none",
            "end time is not bigger then start time",
            "start time and end time are equal"
        ]
    )
    def test_event_creation_form_errors(self, invalid_data, persist_user):  # noqa: F811
        form = EventCreationForm(data=invalid_data, user_id=persist_user)

        with pytest.raises(ValueError):
            if form.is_valid():
                form.save
            else:
                raise ValueError()

    def test_event_created(self, valid_event_data, persist_user):  # noqa: F811
        form = EventCreationForm(data=valid_event_data, user_id=persist_user)
        new_event = form.save()
        assert Event.objects.get(pk=new_event.id)

    def test_event_participant_created(self, valid_event_data, persist_user):  # noqa: F811
        form = EventCreationForm(data=valid_event_data, user_id=persist_user)
        new_event = form.save()
        assert EventParticipant.objects.get(event_id=Event.objects.get(pk=new_event.id), user_id=persist_user)

    def test_user_not_exists_when_saving_form(self, valid_event_data, user0):
        form = EventCreationForm(data=valid_event_data, user_id=user0)
        with pytest.raises(User.DoesNotExist):
            if form.is_valid():
                form.save()
            else:
                assert False

    @pytest.fixture
    def signed_up_user_details(self):
        return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}

    @pytest.fixture
    def sign_in(self, client, signed_up_user_details):
        return client.post('/login/', data=signed_up_user_details)

    @pytest.mark.parametrize("event_id, result", [
            (1, "success"),
            (2, "fail"),
        ], ids=[
            "test valid delete event",
            "test invalid delete event",
        ]
     )
    def test_delete_event(self, client, sign_in, event_id, result):
        response = client.get(f"/event/delete_event/{event_id}")
        assert response.status_code == 200
        assert loads(response.content)["result"] == result
