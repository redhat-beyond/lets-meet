import pytest
from django.core import mail
from users.models import User
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from events.planner import EventPlanner
from django.forms import formset_factory
from reminders.models import ReminderType
from django.contrib.messages import get_messages
from events.models import (
    OptionalMeetingDates, PossibleParticipant,
    Event, Colors, EventParticipant
)
from events.forms import (
    OptionalMeetingDateForm,
    BaseOptionalMeetingDateFormSet
)

TITLE = "test meeting"
EVENT_DATE_TIME_START = timezone.now() + timedelta(hours=2)
EVENT_DATE_TIME_END = timezone.now() + timedelta(hours=4)
COLOR = Colors.BLACK

OPTIONAL_MEETING_DATE_START = timezone.now() + timedelta(days=1)
OPTIONAL_MEETING_DATE_END = timezone.now() + timedelta(days=2)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.fixture
def valid_event_data():
    return {
        "title": TITLE,
        "date_time_start": EVENT_DATE_TIME_START,
        "date_time_end": EVENT_DATE_TIME_END,
        "color": COLOR,
    }


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
def valid_meeting_data(valid_event_data, valid_optional_meeting_data, valid_participant_data):
    meeting_data = {}
    meeting_data.update(valid_event_data)
    meeting_data.update(valid_optional_meeting_data)
    meeting_data.update(valid_participant_data)
    meeting_data.update({"method": ReminderType.WEBSITE})
    return meeting_data


@pytest.mark.django_db
class TestEventPlanner:

    def create_meeting(self, event_start_time):
        event, time_now = self.create_event(event_start_time)
        creator = self.create_event_participants(event)
        self.create_optional_meeting_date(event, creator)
        return event, time_now

    def create_event(self, event_start_time):
        time_now = timezone.now()
        end_time = time_now + timedelta(hours=7)
        start_time = time_now + timedelta(minutes=event_start_time)
        event = Event(
            title="test meeting",
            date_time_start=start_time,
            date_time_end=end_time
        )
        event.save()
        return event, time_now

    def create_event_participants(self, event):
        user1 = User.objects.get(id=1)
        user2 = User.objects.get(id=2)
        creator = EventParticipant(event_id=event, user_id=user1, is_creator=True)
        creator.save()
        participant = EventParticipant(event_id=event, user_id=user2, is_creator=False)
        participant.save()
        return creator

    def create_optional_meeting_date(self, event, creator):
        OptionalMeetingDates(
            event_creator_id=creator,
            date_time_start=event.date_time_start,
            date_time_end=event.date_time_end
        ).save()

    @pytest.mark.parametrize(
        'event_title, expected_meeting_id', [
            ("event3", 4),
            ("event4", None),
        ],
        ids=["find event3", "event 4 - meeting not found"]
    )
    def test_find_meeting(self, event_title, expected_meeting_id):
        event = Event.objects.get(title=event_title)
        planner = EventPlanner(event)
        expected_meeting_date = None
        if expected_meeting_id:
            expected_meeting_date = OptionalMeetingDates.objects.get(id=expected_meeting_id)
        planner.find_meeting()
        assert expected_meeting_date == planner.chosen_meeting_date

    @pytest.mark.parametrize(
        ('original_event_title, chosen_meeting_id, '
         'expected_meeting_deleted_ids, expected_possible_participants_deleted_ids, '
         'expected_event_participants_deleted_ids'), [
            ("event3", 4, range(3, 6), range(4, 6), [6]),
            ("event1", 1, range(1, 2), range(1, 3), [])
        ],
        ids=[
            "execute event3- event participant with id 6 should be deleted from meeting",
            "execute event1- all the event participant are in the meeting"
        ]
    )
    def test_execute_choice(self, original_event_title, chosen_meeting_id,
                            expected_meeting_deleted_ids, expected_possible_participants_deleted_ids,
                            expected_event_participants_deleted_ids):

        if type(chosen_meeting_id) is int:
            chosen_meeting_date = OptionalMeetingDates.objects.get(id=chosen_meeting_id)
            planner = EventPlanner(Event.objects.get(title=original_event_title))
            planner.chosen_meeting_date = chosen_meeting_date
            planner.update_which_participants_can_and_cant_meet(planner.chosen_meeting_date)
            planner.execute_choice()
        else:
            chosen_meeting_date = chosen_meeting_id

        for meeting_id in expected_meeting_deleted_ids:
            with pytest.raises(OptionalMeetingDates.DoesNotExist):
                OptionalMeetingDates.objects.get(id=meeting_id)

        for participant_id in expected_possible_participants_deleted_ids:
            with pytest.raises(PossibleParticipant.DoesNotExist):
                PossibleParticipant.objects.get(id=participant_id)

        for event_participant_id in expected_event_participants_deleted_ids:
            with pytest.raises(EventParticipant.DoesNotExist):
                EventParticipant.objects.get(id=event_participant_id)

        original_event = Event.objects.get(title=original_event_title)
        assert original_event.date_time_start == chosen_meeting_date.date_time_start
        assert original_event.date_time_end == chosen_meeting_date.date_time_end

    @pytest.mark.parametrize(
        ('original_event_title, chosen_meeting_id, '
         'expected_meeting_deleted_ids, expected_possible_participants_deleted_ids, '
         'expected_event_participants_deleted_ids'),
        [("event3", 4, range(3, 6), range(4, 6), [6])],
        ids=["run on event 3"]
    )
    def test_run(self, original_event_title, chosen_meeting_id,
                 expected_meeting_deleted_ids, expected_possible_participants_deleted_ids,
                 expected_event_participants_deleted_ids):

        original_event = Event.objects.get(title=original_event_title)
        chosen_meeting = OptionalMeetingDates.objects.get(id=chosen_meeting_id)
        planner = EventPlanner(original_event)
        planner.run()
        self.test_execute_choice(
            original_event_title, chosen_meeting,
            expected_meeting_deleted_ids, expected_possible_participants_deleted_ids,
            expected_event_participants_deleted_ids
        )

    def test_email_sended_to_creator_with_algorithm_results(self):
        original_event = Event.objects.get(title="event3")
        planner = EventPlanner(original_event)
        planner.run()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Meeting event3 results"

    def test_email_sended_to_all_participants_when_meeting_created(self, client, sign_in, valid_meeting_data):
        response = client.post("/event/meeting/", data=valid_meeting_data)
        assert response.status_code == 302
        assert response.url == "/main/"
        assert len(mail.outbox) == 1
        return response

    def test_success_message_after_create_meeting(self, client, sign_in, valid_meeting_data):
        response = self.test_email_sended_to_all_participants_when_meeting_created(client, sign_in, valid_meeting_data)
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 4
        assert str(messages[0]) == "The meeting has been created successfully."

    def test_email_sended_to_creator_while_suitable_meeting_not_found(self):
        original_event = Event.objects.get(title="event4")
        EventPlanner(original_event).run()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "No suitable meeting found"

    def test_correct_calculating_timeout(self):
        meeting_start_time_in_minutes = 120
        meeting, time_now = self.create_meeting(meeting_start_time_in_minutes)
        expected_time = time_now + timedelta(hours=1)
        res = EventPlanner.get_timeout(meeting)
        res = res.replace(microsecond=0, second=0)
        expected_time = expected_time.replace(microsecond=0, second=0)
        assert expected_time == res

    @pytest.mark.parametrize(
        ('event_start_time, optional_meeting_start_time'),
        [
            (30, 120),
            (120, 20),
            (45, 15)
        ],
        ids=[
            "set event time less than an hour",
            "set optional meeting time less than an hour",
            "set the event and optional meeting time less than an hour"
        ]
    )
    def test_meeting_can_be_set_at_least_one_hour_from_current_time(self, event_start_time,
                                                                    optional_meeting_start_time):
        event, time_now = self.create_event(event_start_time)
        OptionalMeetingDateFormSet = formset_factory(
            OptionalMeetingDateForm, formset=BaseOptionalMeetingDateFormSet,
            max_num=10, extra=0
        )
        data = {
            'form-INITIAL_FORMS': 1,
            'form-TOTAL_FORMS': 1,
            'form-0-date_time_start': time_now + timedelta(minutes=optional_meeting_start_time),
            'form-0-date_time_end': time_now + timedelta(hours=3),
        }
        optional_meeting_formset = OptionalMeetingDateFormSet(data)
        optional_meeting_formset.set_event_instance(event)
        assert not optional_meeting_formset.is_valid()
        assert "Meeting can be set only one hour later from now" in optional_meeting_formset.non_form_errors()
