from django.core.exceptions import ValidationError
from ..models import PossibleMeeting, EventParticipant, PossibleParticipant, Event
from django.utils import timezone
from datetime import datetime
import pytest


ROW_DUPLICATION_ERROR = "The User is already registered in this possible meeting date"
INVALID_PARTICIPANT_REGISTRATION = "The participant is not part of this event"


def create_possible_participant(participant_id, possible_meeting_id):
    return PossibleParticipant(participant_id=participant_id, possible_meeting_id=possible_meeting_id)


@pytest.mark.django_db
class TestPossibleParticipant():

    def test_row_duplication(self):
        event_participant = EventParticipant.objects.filter(is_creator=True).first()
        possible_meeting = PossibleMeeting.objects.get(participant_id=event_participant.id)

        with pytest.raises(ValidationError, match=ROW_DUPLICATION_ERROR):
            create_possible_participant(event_participant, possible_meeting).save()
            create_possible_participant(event_participant, possible_meeting).save()

    def test_invalid_registeration_of_pareticipant_to_meeting(self):
        participant_of_event1 = EventParticipant.objects.filter(is_creator=True, event_id__title='event1')[0]
        possible_meeting_of_event2 = PossibleMeeting.objects.get(participant_id__event_id__title='event2')

        with pytest.raises(ValidationError, match=INVALID_PARTICIPANT_REGISTRATION):
            create_possible_participant(participant_of_event1, possible_meeting_of_event2).save()

    def test_get_all_date_participants(self):
        possible_meeting = PossibleMeeting.objects.get(
            date_time_start=datetime(2023, 1, 25, 18, 0, 0, 0, tzinfo=timezone.utc),
            participant_id__event_id__title="event3"
        )
        expected_participants_in_curr_meeting = [
            PossibleParticipant.objects.get(id=4),
            PossibleParticipant.objects.get(id=5)
        ]
        participants_in_curr_meeting = PossibleParticipant.objects.get_all_date_participants(possible_meeting)
        assert list(participants_in_curr_meeting) == list(expected_participants_in_curr_meeting)

    def test_get_all_possible_participants(self):
        event = Event.objects.filter(title='event3')[0]
        expected_participants_in_event3 = [
            PossibleParticipant.objects.get(id=3),
            PossibleParticipant.objects.get(id=4),
            PossibleParticipant.objects.get(id=5),
            PossibleParticipant.objects.get(id=6)
        ]
        all_participants_in_event3 = PossibleParticipant.objects.get_all_possible_participants(event)
        assert list(expected_participants_in_event3) == list(all_participants_in_event3)

    def test_remove_all_possible_meeting_participants(self):
        possible_meeting = PossibleMeeting.objects.get(
            date_time_start=datetime(2023, 1, 25, 18, 0, 0, 0, tzinfo=timezone.utc),
            participant_id__event_id__title="event3"
        )
        expected_deleted_participants = [
            PossibleParticipant.objects.get(id=4),
            PossibleParticipant.objects.get(id=5)
        ]
        PossibleParticipant.objects.remove_all_possible_meeting_participants(possible_meeting)
        assert expected_deleted_participants not in PossibleParticipant.objects.all()

    def test_remove_all_event_participants(self):
        event = Event.objects.filter(title='event3')[0]
        expected_deleted_participants = [
            PossibleParticipant.objects.get(id=3),
            PossibleParticipant.objects.get(id=4),
            PossibleParticipant.objects.get(id=5),
            PossibleParticipant.objects.get(id=6)
        ]
        PossibleParticipant.objects.remove_all_event_participants(event)
        assert expected_deleted_participants not in PossibleParticipant.objects.all()
