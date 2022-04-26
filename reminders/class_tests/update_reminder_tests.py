import pytest
from datetime import datetime
from django.utils import timezone
from reminders.models import Reminder, ReminderType
from reminders.forms import ReminderUpdateForm
from events.models import Event, EventParticipant, Colors
from pytest_django.asserts import assertTemplateUsed

# from users.tests import sign_in_user


NONE_METHOD = None
INVALID_METHOD = "undefined"
VALID_METHOD = ReminderType.EMAIL
CURRENT_DATE = datetime.now()
MESSAGE = "Joined Meeting in 15 minutes"
VALID_DATE_TIME = datetime(CURRENT_DATE.year, CURRENT_DATE.month, CURRENT_DATE.day,
                           12, 0, 0, tzinfo=timezone.utc)
INVALID_DATE_TIME = datetime(CURRENT_DATE.year - 1, CURRENT_DATE.month, CURRENT_DATE.day,
                             12, 0, 0, tzinfo=timezone.utc)

DATE_TIME_END = datetime(CURRENT_DATE.year, CURRENT_DATE.month, CURRENT_DATE.day,
                         13, 0, 0, tzinfo=timezone.utc)
DATE_TIME_START = datetime(CURRENT_DATE.year, CURRENT_DATE.month, CURRENT_DATE.day,
                           15, 0, 0, tzinfo=timezone.utc)
REMINDER_DATE_TIME = datetime(CURRENT_DATE.year, CURRENT_DATE.month, CURRENT_DATE.day,
                              14, 0, 0, tzinfo=timezone.utc)


REMINDER_CREATION_URL = '/event/update/{}'.format(1)
REMINDER_CREATION_HTML_PATH = "events/create_event.html"


@pytest.mark.django_db
class TestUpdateReminder:

    @pytest.fixture
    def signed_up_user_details(self):
        return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}

    @pytest.fixture
    def sign_in(self, client, signed_up_user_details):
        return client.post('/login/', data=signed_up_user_details)

    @pytest.fixture
    def get_event_participant(self):
        return EventParticipant.objects.get(id=1)
 
    @pytest.fixture
    def valid_event_data(self):
        reminder = Event.objects.get(id=1)
        return {'title': reminder.title, 'date_time_start': reminder.date_time_start,
                'date_time_end': reminder.date_time_end, 'color': Colors.RED,
                'date_time': REMINDER_DATE_TIME, 'method': ReminderType.EMAIL}

    @pytest.mark.parametrize("invalid_user_credentials", [
        # method cannot be None
        {'participant_id': None, 'date_time': VALID_DATE_TIME, 'messages': MESSAGE, 'method': NONE_METHOD},
        # method can be only from ReminderType
        {'participant_id': None, 'date_time': VALID_DATE_TIME, 'messages': MESSAGE, 'method': INVALID_METHOD},
        # datetime should be greater then the present time
        {'participant_id': None, 'date_time': INVALID_DATE_TIME, 'messages': MESSAGE, 'method': VALID_METHOD}
    ], ids=["method is none", "method is not from ReminderType", "date is before the current time"])
    def test_create_reminder(self, get_event_participant, invalid_user_credentials):
        invalid_user_credentials['participant_id'] = get_event_participant

        form = ReminderUpdateForm(data=invalid_user_credentials)

        with pytest.raises(ValueError):
            if form.is_valid():
                form.save
            else:
                raise ValueError()

    def test_update_reminder_form(self, client, sign_in):
        response = client.get(REMINDER_CREATION_URL)
        assert response.status_code == 200
        assert isinstance(response.context['reminder_form'], ReminderUpdateForm)

    def test_renders_update_reminder_template(self, client, sign_in):
        response = client.get(REMINDER_CREATION_URL)
        assert response.status_code == 200
        print(response)
        assertTemplateUsed(response, REMINDER_CREATION_HTML_PATH)

    def test_post_valid_update_reminder(self, client, sign_in, valid_event_data):
        original_reminder = Reminder.objects.get(id=1)
        response = client.post(REMINDER_CREATION_URL, data=valid_event_data)
        assert response.status_code == 200
        assert original_reminder.method != Reminder.objects.get(id=1).method
