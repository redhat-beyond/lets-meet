from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils import timezone
from .models import Event
from datetime import datetime

import pytest


DATE_TIME_EARLY = datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)
DATE_TIME_LATER = datetime(2022, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)
ERROR = 'ValidationError not raised'


@pytest.fixture
def new_event():
    return Event(title='new_title', location='new_location', description='new_description',
                 date_time_start=DATE_TIME_EARLY, date_time_end=DATE_TIME_LATER)


@pytest.mark.django_db
class TestEvent:

    def test_create_delete_event(self, new_event):
        new_event.save()
        assert new_event in Event.objects.all()
        new_event.delete()
        assert new_event not in Event.objects.all()

    def test_blank_title_event(self):
        try:
            Event.objects.create()
            assert False, ERROR
        except ValidationError as e:
            assert 'This field cannot be blank.' in e.message_dict['title']

    def test_blank_date_time_event(self, new_event):
        try:
            new_event.date_time_start, new_event.date_time_end = DATE_TIME_EARLY, None
            new_event.save()
            assert False, ERROR
        except ValidationError as e:
            assert 'start and end date_time - one field not filled' in e.message_dict[NON_FIELD_ERRORS]

        try:
            new_event.date_time_start, new_event.date_time_end = None, DATE_TIME_EARLY
            new_event.save()
            assert False, ERROR
        except ValidationError as e:
            assert 'start and end date_time - one field not filled' in e.message_dict[NON_FIELD_ERRORS]

    def test_start_bigger_equal_end_event(self, new_event):
        try:
            new_event.date_time_start, new_event.date_time_end = DATE_TIME_LATER, DATE_TIME_EARLY
            new_event.save()
            assert False, ERROR
        except ValidationError as e:
            assert 'date_time_start is equal or greater than date_time_end' in e.message_dict[NON_FIELD_ERRORS]
