import pytest
from datetime import datetime
from django.utils import timezone
from django.db import IntegrityError
from events.models import OptionalMeetingDates, EventParticipant, Event
from events.tests import (  # noqa:F811, F401
    new_event, user0,
    event_participant_not_creator
)


DATE_TIME_END = datetime(2022, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)
DATE_TIME_START = datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def possible_meeting0(event_participant_not_creator):  # noqa: F811
    return OptionalMeetingDates(
        event_creator_id=event_participant_not_creator,
        date_time_start=DATE_TIME_START, date_time_end=DATE_TIME_END
    )


@pytest.fixture
def persist_possible_meeting(possible_meeting0):
    possible_meeting0.event_creator_id.user_id.save()
    possible_meeting0.event_creator_id.event_id.save()
    possible_meeting0.event_creator_id.save()
    possible_meeting0.save()
    return possible_meeting0


def get_event_participant_from_db():
    return EventParticipant.objects.filter(is_creator=True).first()


@pytest.mark.django_db
class TestMeeting():

    @pytest.fixture
    def expected_meeting_results(self):
        return [OptionalMeetingDates.objects.get(id=f"{id}") for id in range(3, 6)]

    def test_persist_possible_meeting(self, persist_possible_meeting):
        assert persist_possible_meeting in OptionalMeetingDates.objects.all()

    def test_delete_persist_possible_meeting(self, persist_possible_meeting):
        persist_possible_meeting.delete()
        assert persist_possible_meeting not in OptionalMeetingDates.objects.all()

    def test_delete_participant_deletes_possible_meeting(self, persist_possible_meeting):
        persist_possible_meeting.event_creator_id.delete()
        assert persist_possible_meeting not in OptionalMeetingDates.objects.all()

    def test_persist_possible_meeting_in_db(self):
        assert OptionalMeetingDates.objects.filter(event_creator_id=get_event_participant_from_db())

    def test_duplicate_possible_meeting(self):
        participant_event3_creator = EventParticipant.objects.get(event_id__title="event3", is_creator=True)
        date_time_start = datetime(2023, 1, 24, 13, 13, 13, 0, tzinfo=timezone.utc)
        date_time_end = datetime(2023, 1, 24, 15, 15, 15, 0, tzinfo=timezone.utc)

        with pytest.raises(IntegrityError):
            OptionalMeetingDates(
                event_creator_id=participant_event3_creator,
                date_time_start=date_time_start,
                date_time_end=date_time_end
            ).save()

    def test_get_all_event_dates(self, expected_meeting_results, event_title="event3"):
        event = Event.objects.get(title=event_title)
        assert expected_meeting_results == list(OptionalMeetingDates.objects.get_all_event_dates(event))

    def test_remove_all_possible_dates(self, expected_meeting_results, event_title="event3"):
        event = Event.objects.get(title=event_title)
        OptionalMeetingDates.objects.remove_all_possible_dates(event)
        assert expected_meeting_results not in list(OptionalMeetingDates.objects.all())
