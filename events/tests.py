# from django.test import TestCase

# Create your tests here.
import pytest
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from . import models

USERNAME = "ed"
TITLE = "title"
DATE_TIME_EARLY = datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
DATE_TIME_LATER = datetime(2022, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def event0():
    return models.Event(title=TITLE, location='new_location', description='new_description',
                        date_time_start=DATE_TIME_EARLY, date_time_end=DATE_TIME_LATER)


@pytest.fixture
def user0():
    return models.User(username=USERNAME)


@pytest.fixture
def event_participant_creator0(event0, user0):
    return models.EventParticipant(event_id=event0, user_id=user0, is_creator=True)


@pytest.fixture
def event_participant_not_creator0(event0, user0):
    return models.EventParticipant(event_id=event0, user_id=user0, is_creator=False)


@pytest.fixture
def possible_meeting0(event_participant_not_creator0):
    return models.PossibleMeeting(participant_id=event_participant_not_creator0,
                                  date_time_start=DATE_TIME_EARLY, date_time_end=DATE_TIME_LATER)


@pytest.fixture
def persist_event_participant(event_participant_creator0):
    event_participant_creator0.event_id.save()
    event_participant_creator0.user_id.save()
    event_participant_creator0.save()
    return event_participant_creator0


@pytest.fixture
def persist_possible_meeting0(persist_event_participant):
    possible_meeting = models.PossibleMeeting(participant_id=persist_event_participant,
                                              date_time_start=DATE_TIME_EARLY, date_time_end=DATE_TIME_LATER)
    possible_meeting.save()
    return possible_meeting


class TestEventParticipantModel:
    def test_event_participant_is_creator(self, event_participant_creator0):
        assert event_participant_creator0.user_id.username == USERNAME
        assert event_participant_creator0.event_id.title == TITLE
        assert event_participant_creator0.is_creator is True

    def test_event_participant_not_creator(self, event_participant_not_creator0):
        assert event_participant_not_creator0.user_id.username == USERNAME
        assert event_participant_not_creator0.event_id.title == TITLE
        assert event_participant_not_creator0.is_creator is False

    @pytest.mark.django_db
    def test_persist_event_participant(self, persist_event_participant):
        assert persist_event_participant in models.EventParticipant.objects.all()

    @pytest.mark.django_db
    def test_delete_event_participant(self, persist_event_participant):
        persist_event_participant.delete()
        assert persist_event_participant not in models.EventParticipant.objects.all()


class TestPossibleMeetingModel:
    def save_to_db(self, possible_meeting):
        possible_meeting.participant_id.user_id.save()
        possible_meeting.participant_id.event_id.save()
        possible_meeting.participant_id.save()
        possible_meeting.save()

    def test_possible_meeting_creation(self, possible_meeting0):
        assert possible_meeting0.participant_id.user_id.username == USERNAME
        assert possible_meeting0.participant_id.event_id.title == TITLE
        assert possible_meeting0.date_time_start == DATE_TIME_EARLY
        assert possible_meeting0.date_time_end == DATE_TIME_LATER

    @pytest.mark.django_db
    def test_persist_possible_meeting(self, possible_meeting0):
        self.save_to_db(possible_meeting0)
        assert possible_meeting0 in models.PossibleMeeting.objects.all()
        possible_meeting0.delete()
        assert possible_meeting0 not in models.PossibleMeeting.objects.all()

    @pytest.mark.django_db
    def test_persist_possible_meeting_Validation_Error(self, possible_meeting0):
        with pytest.raises(ValidationError):
            possible_meeting0.date_time_start = DATE_TIME_LATER
            possible_meeting0.date_time_end = DATE_TIME_EARLY
            self.save_to_db(possible_meeting0)
