from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Event
from datetime import datetime

import pytest


DATE_TIME_EARLY = datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
DATE_TIME_LATER = datetime(2022, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)
TITLE = 'new_title'


@pytest.fixture
def new_event():
    return Event(title='new_title', location='new_location', description='new_description',
                 date_time_start=DATE_TIME_EARLY, date_time_end=DATE_TIME_LATER)


@pytest.fixture
def persist_event(db, new_event):
    new_event.save()
    return new_event


@pytest.mark.django_db
def test_persist_event(persist_event):
    assert persist_event in Event.objects.all()


@pytest.mark.django_db
def test_delete_event(persist_event):
    persist_event.delete()
    assert persist_event not in Event.objects.all()


def create_event(title, date_time_start, date_time_end):
    return Event(title=title, date_time_start=date_time_start, date_time_end=date_time_end)


@pytest.mark.parametrize('events, excpected_error', [
    (create_event(None, DATE_TIME_EARLY, DATE_TIME_LATER), 'title cannot be blank'),
    (create_event(TITLE, None, DATE_TIME_LATER), 'Starting date cannot be blank'),
    (create_event(TITLE, DATE_TIME_EARLY, None), 'Ending date cannot be blank'),
    (create_event(TITLE, DATE_TIME_EARLY, DATE_TIME_EARLY),
     f'{DATE_TIME_EARLY} must be smaller than {DATE_TIME_EARLY}'),
    (create_event(TITLE, DATE_TIME_LATER, DATE_TIME_EARLY), f'{DATE_TIME_LATER} must be smaller than {DATE_TIME_EARLY}')
])
def test_invalidation(events, excpected_error):
    try:
        events.save()
    except ValidationError as error:
        assert excpected_error in error  # The event was not created successfully
    else:
        assert False  # The event was created successfully
