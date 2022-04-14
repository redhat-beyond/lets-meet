from django.http import HttpRequest
from .class_tests.event_tests import *  # noqa: F403 F401
from .class_tests.participant_test import *  # noqa: F403 F401
from .class_models.meeting_models import *  # noqa: F403 F401
from .class_models.participant_model import EventParticipant  # noqa: F403 F401
from .class_models.event_models import Event  # noqa: F403 F401
from .forms import EventCreationForm
from users import models
import pytest

# form preferences -> new event preferences
TITLE = 'new_form'
LOCATION = 'new_form_location'
DESCRIPTION = 'new_form_description'
DATE_TIME_START = "11:11 PM 11-Nov-2011"
DATE_TIME_END = "12:12 PM 12-Dec-2012"

# form's 'test user' preferences -> new event creator preferences
NAME = "form_test_user"
EMAIL = "form_test_user@gmail.com"
PASSWORD = "form_test_U$er123"
PHONE_NUM = "+972544651893"


@pytest.fixture
def form_user():
    return models.User(email=EMAIL, phone_number=PHONE_NUM, password=PASSWORD, username=NAME)


@pytest.fixture
def persist_form_user(form_user):
    form_user.save()
    return form_user


class TestCreateEventForm:

    @pytest.fixture
    def test_title_is_required(self, form_user):
        request = HttpRequest()
        request.POST = {
            "location": LOCATION,
            "description": DESCRIPTION,
            "date_time_start": DATE_TIME_START,
            "date_time_end": DATE_TIME_END,
        }
        new_form = EventCreationForm(request.POST, user_id=form_user)
        assert not new_form.is_valid()

    def test_start_date_time_is_required(self, form_user):
        request = HttpRequest()
        request.POST = {
            "title": TITLE,
            "location": LOCATION,
            "description": DESCRIPTION,
            "date_time_end": DATE_TIME_END,
        }
        new_form = EventCreationForm(request.POST, user_id=form_user)
        assert not new_form.is_valid()

    def test_end_date_time_is_required(self, form_user):
        request = HttpRequest()
        request.POST = {
            "title": TITLE,
            "location": LOCATION,
            "description": DESCRIPTION,
            "date_time_start": DATE_TIME_START,
        }
        new_form = EventCreationForm(request.POST, user_id=form_user)
        assert not new_form.is_valid()

    @pytest.fixture
    def test_only_date_times_and_title_required(self, form_user):
        request = HttpRequest()
        request.POST = {
            "title": TITLE,
            "date_time_start": DATE_TIME_START,
            "date_time_end": DATE_TIME_END,
        }
        new_form = EventCreationForm(request.POST, user_id=form_user)
        assert new_form.is_valid()

    @pytest.fixture
    def persist_new_form(self, form_user):
        request = HttpRequest()
        request.POST = {
            "title": TITLE,
            "location": LOCATION,
            "description": DESCRIPTION,
            "date_time_start": DATE_TIME_START,
            "date_time_end": DATE_TIME_END,
        }
        new_form = EventCreationForm(request.POST, user_id=form_user)
        assert new_form.is_valid()
        new_form.save(True)
        return new_form

    @pytest.mark.django_db
    def test_event_created(self, persist_new_form):
        assert Event.objects.get(title=TITLE)

    @pytest.mark.django_db
    def test_event_participant_created(self, persist_new_form):
        assert EventParticipant.objects.filter(event_id=Event.objects.get(title=TITLE))
