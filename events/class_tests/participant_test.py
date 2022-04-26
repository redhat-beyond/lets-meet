import pytest
from users.models import User
from users.tests import user0  # noqa:F811, F401
from events.tests import new_event  # noqa: F401
from events.models import Event, EventParticipant
from django.core.exceptions import ValidationError


def create_event_participant(event, user, is_creator):
    return EventParticipant(event_id=event, user_id=user, is_creator=is_creator)


@pytest.fixture
def event_participant_creator(new_event, user0):  # noqa: F811
    return create_event_participant(new_event, user0, True)


@pytest.fixture
def event_participant_not_creator(new_event, user0):  # noqa: F811
    return create_event_participant(new_event, user0, False)


@pytest.fixture
def persist_event_participant(event_participant_creator):
    event_participant_creator.event_id.save()
    event_participant_creator.user_id.save()
    event_participant_creator.save()
    return event_participant_creator


@pytest.mark.django_db
class TestParticipant():

    def test_persist_event_participant(self, persist_event_participant):
        assert persist_event_participant in EventParticipant.objects.all()

    def test_delete_event_participant(self, persist_event_participant):
        persist_event_participant.delete()
        assert persist_event_participant not in EventParticipant.objects.all()

    def test_delete_user_deletes_participant(self, persist_event_participant):
        persist_event_participant.user_id.delete()
        assert persist_event_participant not in EventParticipant.objects.all()

    def test_exist_event_participant(self):
        assert EventParticipant.objects.filter(event_id=Event.objects.get(title='event1'))
        assert EventParticipant.objects.filter(event_id=Event.objects.get(title='event2'))

    def test_invalid_register_user_twice(self, persist_event_participant):
        with pytest.raises(ValidationError, match='user already exist in meeting'):
            persist_event_participant.save()

    def test_get_an_event_participants(self):
        event = Event.objects.get(title="event1")
        expected_participants = [EventParticipant.objects.get(id=i) for i in range(1, 3)]
        all_participants_in_event1 = EventParticipant.objects.get_an_event_participants(event)
        assert expected_participants == list(all_participants_in_event1)

    def test_get_creator_of_event(self):
        event = Event.objects.get(title="event1")
        expected_participants = EventParticipant.objects.get(id=1)
        creator_of_event1 = EventParticipant.objects.get_creator_of_event(event)
        assert expected_participants == creator_of_event1

    def test_remove_participant_from_event(self):
        event = Event.objects.get(title="event2")
        user = User.objects.get(id=3)
        expected_deleted_participants = EventParticipant.objects.get(id=3)
        EventParticipant.objects.remove_participant_from_event(event, user)
        assert expected_deleted_participants not in EventParticipant.objects.all()
