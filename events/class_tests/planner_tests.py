import pytest
from events.planner import EventPlanner
from events.models import OptionalMeetingDates, PossibleParticipant, Event


planner = EventPlanner()


@pytest.mark.django_db
class TestEventPanner:

    @pytest.mark.parametrize(
        'event_title, expected_meeting_id',
        [("event3", 4)],
        ids=["find event3"]
    )
    def test_find_meeting(self, event_title, expected_meeting_id):
        event = Event.objects.get(title=event_title)
        expected_meeting_date = OptionalMeetingDates.objects.get(id=expected_meeting_id)
        assert [expected_meeting_date] == list(planner.find_meeting(event))

    @pytest.mark.parametrize(
        ('original_event_title, chosen_meeting_id, '
         'expected_meeting_deleted_ids, expected_possible_participants_deleted_ids'),
        [("event3", 4, range(3, 6), range(3, 7))],
        ids=["excute event3"]
    )
    def test_execute_choice(self, original_event_title, chosen_meeting_id,
                            expected_meeting_deleted_ids, expected_possible_participants_deleted_ids):

        if type(chosen_meeting_id) is int:
            chosen_meeting_date = OptionalMeetingDates.objects.get(id=chosen_meeting_id)
        else:
            chosen_meeting_date = chosen_meeting_id

        planner.execute_choice(chosen_meeting_date)

        for meeting_id in expected_meeting_deleted_ids:
            with pytest.raises(OptionalMeetingDates.DoesNotExist):
                OptionalMeetingDates.objects.get(id=meeting_id)

        for participant_id in expected_possible_participants_deleted_ids:
            with pytest.raises(PossibleParticipant.DoesNotExist):
                PossibleParticipant.objects.get(id=participant_id)

        original_event = Event.objects.get(title=original_event_title)
        assert original_event.date_time_start == chosen_meeting_date.date_time_start
        assert original_event.date_time_end == chosen_meeting_date.date_time_end

    @pytest.mark.parametrize(
        ('original_event_title, chosen_meeting_id, '
         'expected_meeting_deleted_ids, expected_possible_participants_deleted_ids'),
        [("event3", 4, range(3, 6), range(3, 7))],
        ids=["run on event 3"]
    )
    def test_run(self, original_event_title, chosen_meeting_id,
                 expected_meeting_deleted_ids, expected_possible_participants_deleted_ids):

        original_event = Event.objects.get(title=original_event_title)
        chosen_meeting = OptionalMeetingDates.objects.get(id=chosen_meeting_id)
        planner.run(original_event)
        self.test_execute_choice(
            original_event_title, chosen_meeting,
            expected_meeting_deleted_ids, expected_possible_participants_deleted_ids
        )
