import pytest
from datetime import datetime
from django.utils import timezone
from events.models import Event, time_format
from django.core.exceptions import ValidationError


TITLE = 'new_title'
LOCATION = 'new_location'
DESCRIPTION = 'new_description'
DATE_TIME_END = datetime(2022, 3, 24, 14, 12, 12, 0, tzinfo=timezone.utc)
DATE_TIME_START = datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)


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

    def test_delete_event(self, persist_event):
        persist_event.delete()
        assert persist_event not in Event.objects.all()

    def test_exist_event(self):
        for title_id in range(1, 4):
            assert Event.objects.get(title=f'event{title_id}')

    @pytest.mark.parametrize('title, date_time_start, date_time_end, expected_error', [
        (None, DATE_TIME_START, DATE_TIME_END, 'Title cannot be blank'),
        ('', DATE_TIME_START, DATE_TIME_END, 'Title cannot be blank'),
        (TITLE, None, DATE_TIME_END, 'Starting date cannot be blank'),
        (TITLE, DATE_TIME_START, None, 'Ending date cannot be blank'),
        (TITLE, DATE_TIME_START, DATE_TIME_START,
         f'{time_format(DATE_TIME_START)} must be smaller than {time_format(DATE_TIME_START)}'),
        (TITLE, DATE_TIME_END, DATE_TIME_START,
         f'{time_format(DATE_TIME_END)} must be smaller than {time_format(DATE_TIME_START)}')
    ], ids=[
        "title is none",
        "title is blank",
        "star time is none",
        "end time is none",
        "end time is not bigger then start time",
        "start time and end time are equal"
    ])
    def test_invalidation(self, title, date_time_start, date_time_end, expected_error):
        with pytest.raises(ValidationError, match=expected_error):
            create_event(title, date_time_start, date_time_end).save()

    def test_get_all_meetings(self):
        result = Event.objects.get_all_meetings()
        for title_id in ['1', '3']:
            assert Event.objects.get(title=f"event{title_id}") in result
        assert result.count() == 3

    def test_get_all_user_meetings(self, user_id=1):
        result = Event.objects.get_all_user_meetings(user_id)
        for title_id in ['1', '3']:
            assert Event.objects.get(title=f"event{title_id}") in result
        assert Event.objects.get(title="event2") not in result
        assert result.count() == 3

    @pytest.mark.parametrize('event_title, user_id, year, month', [
        ("event1", 1, 2022, 3),
        ("event3", 1, 2023, 1)
    ], ids=[
        "get all users month meeting of event 1",
        "get all users month meeting of event 3"
    ])
    def test_get_all_user_month_meetings(self, event_title, user_id, year, month):
        assert Event.objects.get(title=event_title) in Event.objects.get_all_user_month_meetings(user_id, year, month)

    @pytest.mark.parametrize('event_title, user_id, date', [
        ("event1", 1, datetime(2022, 3, 24)),
        ("event3", 1, datetime(2023, 1, 24))
    ], ids=[
        "get all users month meeting of event 1",
        "get all users month meeting of event 3"
    ])
    def test_get_all_user_day_meetings(self, event_title, user_id, date):
        assert Event.objects.get(title=event_title) in Event.objects.get_all_user_day_meetings(user_id, date)

    def test_get_all_user_events(self):
        event2 = Event.objects.get(title='event2')
        assert [event2] == list(Event.objects.get_all_user_events(user_id=3))
