# from django.test import TestCase

# Create your tests here.
import pytest
from . import models


@pytest.fixture
def event_participant_creator0(event0, user0):
    return models.EventParticipant(event_id=event0, user_id=user0, is_creator=True)


@pytest.fixture
def event_participant_not_creator0(event0, user0):
    return models.EventParticipant(event_id=event0, user_id=user0, is_creator=False)


@pytest.fixture
def persist_event_participant(event_participant_creator0):
    event_participant_creator0.event_id.save()
    event_participant_creator0.user_id.save()
    event_participant_creator0.save()
    return event_participant_creator0


class TestEventParticipantModel:
    def test_event_participan_is_creator(self, event_participant_creator0):
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
