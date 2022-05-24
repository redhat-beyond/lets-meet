import pytest
from pytest_django.asserts import assertTemplateUsed
from reminders.class_models.reminder_models import ReminderType
from events.models import Event


@pytest.mark.django_db
class TestCreateEventViews:

    def test_logged_user_success_enter_the_create_event_page(self, sign_in, client):
        response = client.get(path=pytest.create_event_url)
        assert response.status_code == 200
        assertTemplateUsed(response, pytest.create_event_template)

    def test_unlogged_user_fail_to_enter_the_create_event_page(self, client):
        response = client.get(path=pytest.create_event_url)
        assert response.status_code == 302
        response = client.get(response.url)
        assertTemplateUsed(response, pytest.login_page_template)

    def test_logged_user_success_create_event(self, sign_in, valid_event_data_and_reminder, client):
        assert not Event.objects.filter(title=pytest.valid_event_title)
        client.post(path=pytest.create_event_url, data=valid_event_data_and_reminder)
        assert Event.objects.get(title=pytest.valid_event_title)

    @pytest.mark.parametrize("expected_error_message,invalid_data", [
        ('Title cannot be blank',
            {'title': "", 'date_time_start': pytest.event_date_time_start,
                'date_time_end': pytest.event_date_time_end, 'color': pytest.valid_event_color,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}),
        ('Starting date cannot be blank',
            {'title': pytest.valid_event_title, 'date_time_start': "",
                'date_time_end': pytest.valid_event_date_time_end, 'color': pytest.valid_event_color,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}),
        ('Ending date cannot be blank',
            {'title': pytest.valid_event_title, 'date_time_start': pytest.valid_event_date_time_start,
                'date_time_end': "", 'color': pytest.valid_event_color,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}),
        ('2012-12-12 12:12:00 must be smaller than 2012-11-11 11:11:00',
            {'title': pytest.valid_event_title, 'date_time_start': pytest.valid_event_date_time_end,
                'date_time_end': pytest.valid_event_date_time_start, 'color': pytest.valid_event_color,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL}),
        ('2012-12-12 12:12:00 must be smaller than 2012-11-11 11:11:00',
            {'title': pytest.valid_event_title, 'date_time_start': pytest.valid_event_date_time_end,
                'date_time_end': pytest.valid_event_date_time_start, 'color': pytest.valid_event_color,
                'date_time': pytest.reminder_date_time, 'method': ReminderType.EMAIL})
        ], ids=[
           "title is blank",
           "start time is blank",
           "end time is blank",
           "end time is not bigger then start time",
           "start time and end time are equal"
        ])
    def test_event_creation_form_errors(self, client, sign_in, invalid_data, expected_error_message):
        response = client.post(path=pytest.create_event_url, data=invalid_data)
        errors = response.context["event_form"].errors.as_data()
        assert expected_error_message in f'{errors}'
