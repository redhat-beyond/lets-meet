import pytest
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from events.models import OptionalMeetingDates, EventParticipant, PossibleParticipant, Event


EVENT_3_TITLE = "event3"
ROW_DUPLICATION_ERROR = "The User is already registered in this possible meeting date"
INVALID_PARTICIPANT_REGISTRATION = "The participant is not part of this event"
MIN_POSSIBLE_EVENT_PARTICIPANT_ID = 4
MAX_POSSIBLE_EVENT_PARTICIPANT_ID = 8
MIN_POSSIBLE_MEETING_PARTICIPANT_ID = 5
MAX_POSSIBLE_MEETING_PARTICIPANT_ID = 7


def create_possible_participant(participant_id, possible_meeting_id):
    return PossibleParticipant(participant_id=participant_id, possible_meeting_id=possible_meeting_id)


@pytest.fixture
def get_possible_meeting():
    possible_meeting = OptionalMeetingDates.objects.get(
        date_time_start=datetime(2023, 1, 25, 18, 0, 0, 0, tzinfo=timezone.utc),
        event_creator_id__event_id__title=EVENT_3_TITLE
    )
    return possible_meeting


@pytest.fixture
def get_event():
    event = Event.objects.filter(title=EVENT_3_TITLE).first()
    return event


@pytest.fixture
def get_possible_event_participants():
    return [PossibleParticipant.objects.get(id=f'{id}') for id in
            range(MIN_POSSIBLE_EVENT_PARTICIPANT_ID, MAX_POSSIBLE_EVENT_PARTICIPANT_ID)]


@pytest.fixture
def get_possible_meeting_participants():
    return [PossibleParticipant.objects.get(id=i) for i in
            range(MIN_POSSIBLE_MEETING_PARTICIPANT_ID, MAX_POSSIBLE_MEETING_PARTICIPANT_ID)]


@pytest.mark.django_db
class TestPossibleParticipant():

    def test_row_duplication(self):
        event_participant = EventParticipant.objects.filter(is_creator=True).first()
        possible_meeting = OptionalMeetingDates.objects.get(event_creator_id=event_participant.id)

        with pytest.raises(ValidationError, match=ROW_DUPLICATION_ERROR):
            create_possible_participant(event_participant, possible_meeting).save()
            create_possible_participant(event_participant, possible_meeting).save()

    def test_invalid_registration_of_participant_to_meeting(self):
        participant_of_event1 = EventParticipant.objects.filter(is_creator=True, event_id__title='event1').first()
        possible_meeting_of_event2 = OptionalMeetingDates.objects.get(event_creator_id__event_id__title='event2')

        with pytest.raises(ValidationError, match=INVALID_PARTICIPANT_REGISTRATION):
            create_possible_participant(participant_of_event1, possible_meeting_of_event2).save()

    def test_get_all_possible_participants_of_optional_date(self, get_possible_meeting,
                                                            get_possible_meeting_participants):
        expected_participants_in_current_meeting = get_possible_meeting_participants
        participants_in_current_meeting = \
            PossibleParticipant.objects.get_all_possible_participants_of_optional_date(get_possible_meeting)
        assert list(participants_in_current_meeting) == list(expected_participants_in_current_meeting)

    def test_get_all_possible_participants(self, get_event, get_possible_event_participants):
        expected_participants_in_event3 = get_possible_event_participants
        all_participants_in_event3 = PossibleParticipant.objects.get_all_possible_participants(get_event)
        assert list(expected_participants_in_event3) == list(all_participants_in_event3)

    def test_remove_all_possible_meeting_participants(self, get_possible_meeting, get_possible_meeting_participants):
        expected_deleted_participants = get_possible_meeting_participants
        PossibleParticipant.objects.remove_all_possible_meeting_participants(get_possible_meeting)
        assert expected_deleted_participants not in PossibleParticipant.objects.all()

    def test_remove_all_event_participants(self, get_event, get_possible_event_participants):
        expected_deleted_participants = get_possible_event_participants
        PossibleParticipant.objects.remove_all_event_participants(get_event)
        assert expected_deleted_participants not in PossibleParticipant.objects.all()
