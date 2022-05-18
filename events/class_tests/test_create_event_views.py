import pytest
from pytest_django.asserts import assertTemplateUsed
from events.class_tests.create_events import DATE_TIME_START, DATE_TIME_END, COLOR, TITLE
from reminders.class_models.reminder_models import ReminderType
from events.models import Event, Colors

CREATE_EVENT_URL = "/event/create/"
CREATE_EVENT_TEMPLATE = 'events/create_event.html'
LOGIN_PAGE_TEMPLATE = 'login/register_login.html'


@pytest.mark.django_db
class TestCreateEventViews:

    def test_logged_user_success_enter_the_create_event_page(self, sign_in, client):
        response = client.get(path=CREATE_EVENT_URL)
        assert response.status_code == 200
        assertTemplateUsed(response, CREATE_EVENT_TEMPLATE)

    def test_unlogged_user_fail_to_enter_the_create_event_page(self, client):
        response = client.get(path=CREATE_EVENT_URL)
        assert response.status_code == 302
        response = client.get(response.url)
        assertTemplateUsed(response, LOGIN_PAGE_TEMPLATE)

    def test_logged_user_success_create_event(self, sign_in, valid_event_data_and_reminder, client):
        assert not Event.objects.filter(title=TITLE)
        client.post(path=CREATE_EVENT_URL, data=valid_event_data_and_reminder)
        assert Event.objects.get(title=TITLE)

    @pytest.mark.parametrize("expected_error_message,invalid_data", [
        ('Title cannot be blank',
            {'title': "", 'date_time_start': pytest.date_time_start,
                'date_time_end': pytest.date_time_end, 'color': Colors.BLACK,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}),
        ('Starting date cannot be blank',
            {'title': TITLE, 'date_time_start': "",
                'date_time_end': DATE_TIME_END, 'color': COLOR,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}),
        ('Ending date cannot be blank',
            {'title': TITLE, 'date_time_start': DATE_TIME_START,
                'date_time_end': "", 'color': COLOR,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}),
        ('2012-12-12 12:12:00 must be smaller than 2012-11-11 11:11:00',
            {'title': TITLE, 'date_time_start': DATE_TIME_END,
                'date_time_end': DATE_TIME_START, 'color': COLOR,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}),
        ('2012-11-11 11:11:00 must be smaller than 2012-11-11 11:11:00',
            {'title': TITLE, 'date_time_start': DATE_TIME_START,
                'date_time_end': DATE_TIME_START, 'color': COLOR,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL})
        ], ids=[
           "title is blank",
           "start time is blank",
           "end time is blank",
           "end time is not bigger then start time",
           "start time and end time are equal"
        ]
     )
    def test_event_creation_form_errors(self, client, sign_in, invalid_data, expected_error_message):
        response = client.post(path=CREATE_EVENT_URL, data=invalid_data)
        errors = response.context["event_form"].errors.as_data()
        assert expected_error_message in f'{errors}'
