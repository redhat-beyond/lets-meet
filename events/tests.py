from .class_tests.event_tests import *  # noqa: F403 F401
from .class_tests.participant_test import *  # noqa: F403 F401
from .class_models.meeting_models import *  # noqa: F403 F401
from .class_models.participant_model import EventParticipant
from .class_models.event_models import Event, Colors
from .forms import EventCreationForm
from users import models
from users.class_tests.users_tests import *  # noqa: F401 F403
import pytest

# form preferences -> new event preferences
TITLE = 'new_form'
LOCATION = 'new_form_location'
DESCRIPTION = 'new_form_description'
# DATE_TIME_END = "12:12 PM 12-Dec-2012"
# DATE_TIME_START = "11:11 PM 11-Nov-2011"
DATE_TIME_END = "2012-12-12 12:12"
DATE_TIME_START = "2012-11-11 11:11"
COLOR = Colors.BLACK


@pytest.fixture
def valid_event_data():
    return {
            "title": TITLE,
            "location": LOCATION,
            "description": DESCRIPTION,
            "date_time_start": DATE_TIME_START,
            "date_time_end": DATE_TIME_END,
            "color": COLOR,
        }


@pytest.mark.django_db
class TestCreateEventForm:

    @pytest.mark.parametrize("invalid_data", [
            # title cannot be None
            {'title': None, 'date_time_start': DATE_TIME_START, 'date_time_end': DATE_TIME_END, 'color': COLOR},
            # title cannot be blank
            {'title': "", 'date_time_start': DATE_TIME_START, 'date_time_end': DATE_TIME_END, 'color': COLOR},
            # date_time_start cannot be None
            {'title': TITLE, 'date_time_start': None, 'date_time_end': DATE_TIME_END, 'color': COLOR},
            # date_time_end cannot be None
            {'title': TITLE, 'date_time_start': DATE_TIME_START, 'date_time_end': None, 'color': COLOR},
            # date_time_end must be bigger than date_time_start
            {'title': TITLE, 'date_time_start': DATE_TIME_END, 'date_time_end': DATE_TIME_START, 'color': COLOR},
            # date_time_end cannot be equal to date_time_start
            {'title': TITLE, 'date_time_start': DATE_TIME_START, 'date_time_end': DATE_TIME_START, 'color': COLOR},
        ])
    def test_event_creation_form_errors(self, invalid_data, persist_user):
        form = EventCreationForm(data=invalid_data, user_id=persist_user)

        with pytest.raises(ValueError):
            if form.is_valid():
                form.save
            else:
                raise ValueError()

    def test_event_created(self, valid_event_data, persist_user):
        form = EventCreationForm(data=valid_event_data, user_id=persist_user)
        new_event = form.save()
        assert Event.objects.get(pk=new_event.id)

    def test_event_participant_created(self, valid_event_data, persist_user):
        form = EventCreationForm(data=valid_event_data, user_id=persist_user)
        new_event = form.save()
        assert EventParticipant.objects.get(event_id=Event.objects.get(pk=new_event.id), user_id=persist_user)

    def test_user_not_exists_when_saving_form(self, valid_event_data, user0):
        form = EventCreationForm(data=valid_event_data, user_id=user0)
        with pytest.raises(models.User.DoesNotExist):
            if form.is_valid():
                form.save()
            else:
                assert False
