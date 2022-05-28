import pytest
from django.core import mail
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from reminders.models import ReminderType
from events.views import CreateMeetingView
from django.forms import formset_factory
from events.planner import EventPlanner
from pytest_django.asserts import assertTemplateUsed
from events.models import (
    Event, Colors, EventParticipant
)
from events.forms import (
    OptionalMeetingDateForm,
    BaseOptionalMeetingDateFormSet
)


LOGIN_HTML_PATH = 'login/register_login.html'
UPDATE_MEETING_URL = '/event/update_meeting'
SHOW_MEETING_URL = "/event/show_meeting"
SHOW_MEETING_DETAILS_HTML_PATH = "meetings/show_meeting.html"
CREATE_AND_UPDATE_MEETING_HTML_PATH = "meetings/create_meeting.html"
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
ADD_PARTICIPANTS_URL = '/event/add_participants/'
DELETE_PARTICIPANT_URL = "/event/delete_participant/"
MEETING_CREATION_URL = '/event/meeting/'
TITLE = "test meeting"
EVENT_DATE_TIME_START = timezone.now() + timedelta(hours=3)
EVENT_DATE_TIME_END = timezone.now() + timedelta(hours=4)
COLOR = Colors.BLACK
OPTIONAL_MEETING_DATE_START = timezone.now() + timedelta(days=1)
OPTIONAL_MEETING_DATE_END = timezone.now() + timedelta(days=2)


@pytest.fixture(autouse=True)
def email_backend_setup():
    settings.EMAIL_BACKEND = EMAIL_BACKEND


@pytest.fixture
def signed_up_user_details():
    return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}


@pytest.fixture
def sign_in(client, signed_up_user_details):
    return client.post('/login/', data=signed_up_user_details)


@pytest.fixture
def valid_event_data():
    return {
        "title": TITLE,
        "date_time_start": EVENT_DATE_TIME_START,
        "date_time_end": EVENT_DATE_TIME_END,
        "color": COLOR,
    }


@pytest.fixture
def update_optional_meeting_data():
    return {
        'optional_meetings-TOTAL_FORMS': '1',
        'optional_meetings-INITIAL_FORMS': '0',
        'optional_meetings-0-date_time_start': timezone.now() + timedelta(hours=2),
        'optional_meetings-0-date_time_end': OPTIONAL_MEETING_DATE_END,
    }


@pytest.fixture
def valid_optional_meeting_data():
    return {
        'optional_meetings-TOTAL_FORMS': '1',
        'optional_meetings-INITIAL_FORMS': '0',
        'optional_meetings-0-date_time_start': OPTIONAL_MEETING_DATE_START,
        'optional_meetings-0-date_time_end': OPTIONAL_MEETING_DATE_END,
    }


@pytest.fixture
def valid_participant_data():
    return {
        'participants-TOTAL_FORMS': '1',
        'participants-INITIAL_FORMS': '0',
        'participants-0-participant_email': 'testUser2@mta.ac.il',
    }


@pytest.fixture
def adding_participants_data():
    return {
        'participants-TOTAL_FORMS': '2',
        'participants-INITIAL_FORMS': '0',
        'participants-0-participant_email': 'testUser2@mta.ac.il',
        'participants-1-participant_email': 'testUser3@mta.ac.il',
    }


@pytest.fixture
def valid_meeting_data(valid_event_data, valid_optional_meeting_data, valid_participant_data):
    meeting_data = {}
    meeting_data.update(valid_event_data)
    meeting_data.update(valid_optional_meeting_data)
    meeting_data.update(valid_participant_data)
    meeting_data.update({"method": ReminderType.WEBSITE})
    return meeting_data


@pytest.mark.django_db
class TestUpdateMeeting:

    def update_meeting_data(self, valid_event_data, optional_meeting_data, adding_participants_data):
        updated_meeting = {}
        updated_meeting.update(valid_event_data)
        updated_meeting.update(optional_meeting_data)
        updated_meeting.update(adding_participants_data)
        updated_meeting.update({"method": ReminderType.WEBSITE})
        return updated_meeting

    @pytest.mark.parametrize(
        'url, html_path', [
            (f"{UPDATE_MEETING_URL}/{3}", CREATE_AND_UPDATE_MEETING_HTML_PATH),
            (f"{SHOW_MEETING_URL}/{3}", SHOW_MEETING_DETAILS_HTML_PATH),
        ],
        ids=[
            "render update meeting template",
            "render show meeting details template"
        ]
    )
    def test_render_update_meeting_template(self, client, sign_in, url, html_path):
        response = client.get(url)
        assert response.status_code == 200
        assertTemplateUsed(response, html_path)

    @pytest.mark.parametrize(
        'url', [f"{UPDATE_MEETING_URL}/{3}", f"{SHOW_MEETING_URL}/{3}"],
        ids=[
            "render update meeting template",
            "render show meeting details template"
        ]
    )
    def test_unauthorized_user_redirected_to_login_page(self, client, url):
        response = client.get(url)
        assert response.status_code == 302
        response = client.get(response.url)
        assert response.status_code == 200
        assertTemplateUsed(response, LOGIN_HTML_PATH)

    def test_adding_new_participant_to_meeting(self, client, sign_in, valid_event_data,
                                               valid_meeting_data, valid_optional_meeting_data,
                                               adding_participants_data):
        response = client.post(MEETING_CREATION_URL, data=valid_meeting_data)
        meeting_id = Event.objects.get(title=TITLE).id
        updated_data = self.update_meeting_data(
            valid_event_data, valid_optional_meeting_data, adding_participants_data
        )
        response = client.post(f"{ADD_PARTICIPANTS_URL}{meeting_id}", data=updated_data)
        assert response.status_code == 302
        assert response.url == "/main/"
        return meeting_id

    def test_removing_participant_from_meeting(self, client, sign_in, valid_meeting_data,
                                               valid_optional_meeting_data, adding_participants_data,
                                               valid_event_data):
        meeting_id = self.test_adding_new_participant_to_meeting(
            client, sign_in, valid_event_data, valid_meeting_data,
            valid_optional_meeting_data, adding_participants_data
        )
        event_participant_id_to_delete = EventParticipant.objects.get(event_id=meeting_id, user_id=3).id
        updated_data = self.update_meeting_data(valid_event_data, valid_optional_meeting_data, adding_participants_data)
        client.post(f"{DELETE_PARTICIPANT_URL}{event_participant_id_to_delete}", data=updated_data)
        with pytest.raises(EventParticipant.DoesNotExist):
            EventParticipant.objects.get(id=event_participant_id_to_delete)

    def test_email_sended_to_added_participant(self, client, sign_in, valid_event_data,
                                               valid_meeting_data, valid_optional_meeting_data,
                                               adding_participants_data):
        self.test_adding_new_participant_to_meeting(
            client, sign_in, valid_event_data, valid_meeting_data,
            valid_optional_meeting_data, adding_participants_data
        )
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Invitation to meeting"

    def test_changing_timeout(self, sign_in, client, update_optional_meeting_data,
                              valid_event_data, adding_participants_data, valid_meeting_data):
        client.post(MEETING_CREATION_URL, data=valid_meeting_data)
        meeting = Event.objects.get(title=TITLE)
        updated_optional_meeting_date = update_optional_meeting_data
        updated_data = self.update_meeting_data(
            valid_event_data, updated_optional_meeting_date, adding_participants_data
        )
        client.post(f"{UPDATE_MEETING_URL}/{meeting.id}", data=updated_data)
        expected_time = CreateMeetingView().get_creation_time(
            meeting, self.get_formset(update_optional_meeting_data)
        ) + timedelta(hours=1)
        res = EventPlanner.get_timeout(meeting)
        res = res.replace(microsecond=0, second=0)
        expected_time = expected_time.replace(microsecond=0, second=0)
        assert expected_time == res

    @staticmethod
    def get_formset(update_optional_meeting_data):
        OptionalMeetingDateFormSet = formset_factory(
            OptionalMeetingDateForm, formset=BaseOptionalMeetingDateFormSet,
            max_num=10, extra=0
        )
        data = update_optional_meeting_data
        optional_meeting_formset = OptionalMeetingDateFormSet(data)
        return optional_meeting_formset
