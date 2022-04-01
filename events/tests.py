from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Event
from .models import EventParticipant
from datetime import datetime
from users.models import User


import pytest


DATE_TIME_START = datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
DATE_TIME_END = datetime(2022, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)
TITLE = 'new_title'
LOCATION = 'new_location'
DESCRIPTION = 'new_description'
NAME = "user"
EMAIL = "user@gmail.com"
PASSWORD = "AdminU$er123"
PHONE_NUM = "+972544651892"


@pytest.fixture
def new_event():
    return Event(
        title=TITLE, location=LOCATION, description=DESCRIPTION,
        date_time_start=DATE_TIME_START, date_time_end=DATE_TIME_END
    )


@pytest.fixture
def user0():
    return User(email=EMAIL, phone_number=PHONE_NUM, password=PASSWORD, username=NAME)


@pytest.fixture
def persist_event(db, new_event):
    new_event.save()
    return new_event


@pytest.mark.django_db
def test_add_event(persist_event):
    assert persist_event in Event.objects.all()


@pytest.mark.django_db
def test_delete_event(persist_event):
    persist_event.delete()
    assert persist_event not in Event.objects.all()


@pytest.mark.django_db
def test_exist_event():
    assert Event.objects.get(title='event1')
    assert Event.objects.get(title='event2')
    assert Event.objects.get(title='event3')


def create_event(title, date_time_start, date_time_end):
    return Event(title=title, date_time_start=date_time_start, date_time_end=date_time_end)


@pytest.mark.parametrize('title, date_time_start, date_time_end, expected_error', [
    (None, DATE_TIME_START, DATE_TIME_END, 'Title cannot be blank'),
    ('', DATE_TIME_START, DATE_TIME_END, 'Title cannot be blank'),
    (TITLE, None, DATE_TIME_END, 'Starting date cannot be blank'),
    (TITLE, DATE_TIME_START, None, 'Ending date cannot be blank'),
    (TITLE, DATE_TIME_START, DATE_TIME_START, f'{DATE_TIME_START} must be smaller than {DATE_TIME_START}'),
    (TITLE, DATE_TIME_END, DATE_TIME_START, f'{DATE_TIME_END} must be smaller than {DATE_TIME_START}')
])
def test_invalidation(title, date_time_start, date_time_end, expected_error):
    current_error = ''
    try:
        create_event(title, date_time_start, date_time_end).save()
    except ValidationError as error:
        current_error = error.messages[0]
    assert expected_error == current_error


def create_event_participant(event, user, is_creator):
    return EventParticipant(event_id=event, user_id=user, is_creator=is_creator)


@pytest.fixture
def event_participant_creator(new_event, user0):
    return create_event_participant(new_event, user0, True)


@pytest.fixture
def event_participant_not_creator(new_event, user0):
    return create_event_participant(new_event, user0, False)


@pytest.fixture
def persist_event_participant(event_participant_creator):
    event_participant_creator.event_id.save()
    event_participant_creator.user_id.save()
    event_participant_creator.save()
    return event_participant_creator


@pytest.mark.django_db
def test_persist_event_participant(persist_event_participant):
    assert persist_event_participant in EventParticipant.objects.all()


@pytest.mark.django_db
def test_delete_event_participant(persist_event_participant):
    persist_event_participant.delete()
    assert persist_event_participant not in EventParticipant.objects.all()


@pytest.mark.django_db
def test_delete_user_deletes_participant(persist_event_participant):
    persist_event_participant.user_id.delete()
    assert persist_event_participant not in EventParticipant.objects.all()


@pytest.mark.django_db
def test_exist_event_participant():
    assert EventParticipant.objects.filter(event_id=Event.objects.get(title='event1'))
    assert EventParticipant.objects.filter(event_id=Event.objects.get(title='event2'))


@pytest.mark.django_db
def test_invalid_register_user_twice(persist_event_participant):
    with pytest.raises(Exception, match='user already exist in meeting'):
        persist_event_participant.save()
