import pytest
from users.models import User
from events.models import Event, EventParticipant, OptionalMeetingDates
from events.views import CreateMeetingView
from events.tests import valid_event_data, EVENT_DATE_TIME_START, EVENT_DATE_TIME_END  # noqa: F401
from events.forms import EventCreationForm
from datetime import datetime
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed

OPTIONAL_MEETING_DATE_START = datetime(2023, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
OPTIONAL_MEETING_DATE_END = datetime(2023, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)
OPTIONAL_MEETING_DATE_START_IN_THE_PAST = datetime(2019, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
OPTIONAL_MEETING_DATE_END_IN_THE_PAST = datetime(2019, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)
MEETING_CREATOR_EMAIL = 'testUser1@mta.ac.il'
USER2_EMAIL = 'testUser2@mta.ac.il'
MEETING_CREATION_URL = '/event/meeting/'
MEETING_CREATION_HTML_PATH = "meetings/create_meeting.html"
LOGIN_HTML_PATH = 'login/register_login.html'


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
        'participants-0-participant_email': USER2_EMAIL,
    }


@pytest.mark.django_db
class TestCreateMeetingForm:
    @pytest.fixture
    def signed_up_user_details(self):
        return {'email': MEETING_CREATOR_EMAIL, 'password': 'PasswordU$er123'}

    @pytest.fixture
    def sign_in(self, client, signed_up_user_details):
        return client.post('/login/', data=signed_up_user_details)

    def test_meeting_created(self, sign_in, valid_optional_meeting_data, valid_participant_data,
                             valid_event_data, client):  # noqa:F811
        user_id = User.objects.get(pk=1)
        request = client.get(MEETING_CREATION_URL)
        view = TestCreateMeetingForm.create_meeting_view(user_id, valid_event_data, valid_optional_meeting_data,
                                                         valid_participant_data)
        assert request.status_code == 200
        assert view.create_event_form.is_valid()
        event_instance = view.create_event_form.save()
        event_creator = EventParticipant.objects.get(event_id=event_instance, user_id=user_id)
        TestCreateMeetingForm.assert_validation_on_formset(event_creator, event_instance, request, view)
        TestCreateMeetingForm.assert_all_created_models_are_saved(event_instance, event_creator)

    @pytest.mark.parametrize('invalid_participant_data, expected_error', [
        (
                # user does not exist
                {'participants-TOTAL_FORMS': '2', 'participants-INITIAL_FORMS': '0',
                 'participants-0-participant_email': USER2_EMAIL,
                 'participants-1-participant_email': 'DoesNotexist@mta.ac.il'
                 },
                "There is not user with the email: DoesNotexist@mta.ac.il"
        ),
        (
                # event creator included participant
                {'participants-TOTAL_FORMS': '1', 'participants-INITIAL_FORMS': '0',
                 'participants-0-participant_email': MEETING_CREATOR_EMAIL},
                "You can't add yourself as participant"
        ),
        (
                # empty participant
                {
                    'participants-TOTAL_FORMS': '0', 'participants-INITIAL_FORMS': '0',
                    'participants-0-participant_email': ''
                },
                "You have to enter at least one participant in the meeting"
        ),

    ], ids=[
        "user does not exist",
        "event creator email included in participant",
        "empty participant",
    ]
                             )
    def test_invalid_participant_formset(self, invalid_participant_data, expected_error):
        user_id = User.objects.get(pk=1)
        view = TestCreateMeetingForm.create_meeting_view(user_id, participant_data=invalid_participant_data)
        assert not view.meeting_participants_formset.is_valid()
        assert expected_error in view.meeting_participants_formset.non_form_errors()

    @pytest.mark.parametrize("invalid_optional_meeting_data,expected_error,is_formset_error", [
        # blank end date
        (
                {'optional_meetings-TOTAL_FORMS': '1', 'optional_meetings-INITIAL_FORMS': '0',
                 'optional_meetings-0-date_time_start': OPTIONAL_MEETING_DATE_START,
                 'optional_meetings-0-date_time_end': '',
                 },
                "'Ending date cannot be blank'", False
        ),
        (
                # blank start date
                {'optional_meetings-TOTAL_FORMS': '1', 'optional_meetings-INITIAL_FORMS': '0',
                 'optional_meetings-0-date_time_start': '',
                 'optional_meetings-0-date_time_end': OPTIONAL_MEETING_DATE_END,
                 },
                "Starting date cannot be blank", False
        ),
        (
                # dates not unique
                {'optional_meetings-TOTAL_FORMS': '2', 'optional_meetings-INITIAL_FORMS': '0',
                 'optional_meetings-0-date_time_start': OPTIONAL_MEETING_DATE_START,
                 'optional_meetings-0-date_time_end': OPTIONAL_MEETING_DATE_END,
                 'optional_meetings-1-date_time_start': OPTIONAL_MEETING_DATE_START,
                 'optional_meetings-1-date_time_end': OPTIONAL_MEETING_DATE_END,
                 },
                "The optional meeting dates should be different", True
        ),
        (
                # dates in the past
                {'optional_meetings-TOTAL_FORMS': '1', 'optional_meetings-INITIAL_FORMS': '0',
                 'optional_meetings-0-date_time_start': OPTIONAL_MEETING_DATE_START_IN_THE_PAST,
                 'optional_meetings-0-date_time_end': OPTIONAL_MEETING_DATE_END_IN_THE_PAST,
                 },
                "Meeting can be set only one hour later from now", True
        )
    ], ids=[
        "blank end date",
        "blank start date",
        "dates not unique",
        "dates in the past",
    ]
                             )
    def test_invalid_optional_meeting_formset(self, invalid_optional_meeting_data, expected_error, is_formset_error):
        view = TestCreateMeetingForm.create_meeting_view(optional_meeting_data=invalid_optional_meeting_data)
        assert not view.optional_meetings_formset.is_valid()
        if is_formset_error:
            assert expected_error in view.optional_meetings_formset.non_form_errors()
        else:
            assert expected_error in f'{view.optional_meetings_formset.errors}'

    def test_render_meeting_template(self, client, sign_in):
        response = client.get(MEETING_CREATION_URL)
        assert response.status_code == 200
        assertTemplateUsed(response, MEETING_CREATION_HTML_PATH)

    def test_unauthorized_user_redirected_to_login_page(self, client):
        response = client.get(MEETING_CREATION_URL)
        assert response.status_code == 302
        response = client.get(response.url)
        assert response.status_code == 200
        assertTemplateUsed(response, LOGIN_HTML_PATH)

    @staticmethod
    def create_meeting_view(user_id=None, event_data=None, optional_meeting_data=None,
                            participant_data=None):
        view = CreateMeetingView()
        view.create_event_form = EventCreationForm(data=event_data, user_id=user_id)
        view.optional_meetings_formset = view.OptionalMeetingDateFormSet(prefix='optional_meetings',
                                                                         data=optional_meeting_data)
        view.meeting_participants_formset = view.MeetingParticipantsFormset(prefix='participants', user_id=user_id,
                                                                            data=participant_data)
        return view

    @staticmethod
    def assert_all_created_models_are_saved(event_instance, event_creator):
        assert Event.objects.get(pk=event_instance.id)
        assert EventParticipant.objects.get(event_id=event_instance,
                                            user_id=User.objects.get(email=USER2_EMAIL))
        assert OptionalMeetingDates.objects.get(event_creator_id=event_creator,
                                                date_time_start=OPTIONAL_MEETING_DATE_START,
                                                date_time_end=OPTIONAL_MEETING_DATE_END)
        # dates on event are included as optional date
        assert OptionalMeetingDates.objects.get(event_creator_id=event_creator,
                                                date_time_start=EVENT_DATE_TIME_START,
                                                date_time_end=EVENT_DATE_TIME_END)

    @staticmethod
    def assert_validation_on_formset(event_creator, event_instance, request, view):
        assert view.check_optional_meeting_dates_formset(
            event_instance, event_creator, view.optional_meetings_formset)
        assert view.check_participant_formset(request, event_instance, view.meeting_participants_formset)
