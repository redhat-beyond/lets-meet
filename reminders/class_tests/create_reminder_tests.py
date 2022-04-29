import pytest
from reminders.models import Reminder
from reminders.forms import ReminderCreationForm
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
class TestCreateReminder:

    @pytest.mark.parametrize("invalid_data", [
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
    def test_create_invalid_reminder(self, get_event_participant, invalid_data):
        invalid_data['participant_id'] = get_event_participant
        form = ReminderCreationForm(data=invalid_data)

        with pytest.raises(ValueError):
            if form.is_valid():
                form.save
            else:
                raise ValueError()

    def test_create_valid_reminder(self, get_event_participant):
        valid_data = {
            'participant_id': None, 'date_time': pytest.valid_date_time,
            'messages': pytest.message, 'method': pytest.valid_method
        }
        form = ReminderCreationForm(data=valid_data)

        assert form.is_valid()

        instance = form.save(commit=False)
        instance.participant_id = get_event_participant
        instance.messages = pytest.message
        instance.save()
        assert instance in Reminder.objects.all()

    def test_reminder_creation_form(self, client, sign_in):
        response = client.get(pytest.reminder_creation_url)
        assert response.status_code == 200
        assert isinstance(response.context['reminder_form'], ReminderCreationForm)

    def test_renders_add_reminder_template(self, client, sign_in):
        response = client.get(pytest.reminder_creation_url)
        assert response.status_code == 200
        assertTemplateUsed(response, pytest.reminder_creation_html_path)

    def test_post_valid_reminder_creation(self, client, sign_in, valid_event_data):
        response = client.post(pytest.reminder_creation_url, data=valid_event_data)
        assert response.status_code == 200
