from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import Event, time_format
from datetime import datetime

import pytest

DATE_TIME_START = datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
DATE_TIME_END = datetime(2022, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)
TITLE = 'new_title'
LOCATION = 'new_location'
DESCRIPTION = 'new_description'


@pytest.fixture
def new_event():
    return Event(
        title=TITLE, location=LOCATION, description=DESCRIPTION,
        date_time_start=DATE_TIME_START, date_time_end=DATE_TIME_END
    )


@pytest.fixture
def persist_event(db, new_event):
    new_event.save()
    return new_event


def create_event(title, date_time_start, date_time_end):
    return Event(title=title, date_time_start=date_time_start, date_time_end=date_time_end)


@pytest.mark.django_db
class TestEvent():

    def test_add_event(self, persist_event):
        assert persist_event in Event.objects.all()

    @pytest.mark.django_db
    def test_delete_event(self, persist_event):
        persist_event.delete()
        assert persist_event not in Event.objects.all()

    @pytest.mark.django_db
    def test_exist_event(self):
        assert Event.objects.get(title='event1')
        assert Event.objects.get(title='event2')
        assert Event.objects.get(title='event3')

    @pytest.mark.parametrize('title, date_time_start, date_time_end, expected_error', [
        (None, DATE_TIME_START, DATE_TIME_END, 'Title cannot be blank'),
        ('', DATE_TIME_START, DATE_TIME_END, 'Title cannot be blank'),
        (TITLE, None, DATE_TIME_END, 'Starting date cannot be blank'),
        (TITLE, DATE_TIME_START, None, 'Ending date cannot be blank'),
        (TITLE, DATE_TIME_START, DATE_TIME_START,
         f'{time_format(DATE_TIME_START)} must be smaller than {time_format(DATE_TIME_START)}'),
        (TITLE, DATE_TIME_END, DATE_TIME_START,
         f'{time_format(DATE_TIME_END)} must be smaller than {time_format(DATE_TIME_START)}')
    ])
    def test_invalidation(self, title, date_time_start, date_time_end, expected_error):
        current_error = ''
        try:
            create_event(title, date_time_start, date_time_end).save()
        except ValidationError as error:
            current_error = error.messages[0]
        assert expected_error == current_error
