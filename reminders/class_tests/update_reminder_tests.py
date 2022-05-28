import pytest
from reminders.forms import ReminderUpdateForm
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
class TestUpdateReminder:

    @pytest.mark.parametrize("invalid_user_credentials", [
        # method cannot be None
        {'participant_id': None, 'date_time': pytest.valid_date_time,
         'messages': pytest.message, 'method': None
         },
        # method can be only from ReminderType
        {'participant_id': None, 'date_time': pytest.valid_date_time,
         'messages': pytest.message, 'method': pytest.invalid_method
         },
        # datetime should be greater then the present time
        {'participant_id': None, 'date_time': pytest.invalid_date_time,
         'messages': pytest.message, 'method': pytest.valid_method
         }
    ], ids=[
        "method is none",
        "method is not from ReminderType",
        "date is before the current time"
        ]
    )
    def test_create_reminder(self, get_event_participant, invalid_user_credentials):
        invalid_user_credentials['participant_id'] = get_event_participant

        form = ReminderUpdateForm(data=invalid_user_credentials)

        with pytest.raises(ValueError):
            if form.is_valid():
                form.save
            else:
                raise ValueError()

    def test_update_reminder_form(self, client, sign_in_user_3):
        response = client.get(pytest.reminder_update_url_event2)
        assert response.status_code == 200
        assert isinstance(response.context['reminder_form'], ReminderUpdateForm)

    def test_renders_update_reminder_template(self, client, sign_in_user_3):
        response = client.get(pytest.reminder_update_url_event2)
        assert response.status_code == 200
        assertTemplateUsed(response, pytest.reminder_creation_html_path)
