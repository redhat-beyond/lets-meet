from django import forms
from django.forms import ModelForm
from reminders.models import Reminder


class DataTimePickerInput(forms.DateTimeInput):
    input_type = "datetime-local"


class ReminderCreationForm(ModelForm):

    class Meta:
        model = Reminder
        exclude = ['participant_id', 'messages']
        fields = '__all__'
        widgets = {
            'date_time': DataTimePickerInput()
        }


class ReminderUpdateForm(ModelForm):

    class Meta:
        model = Reminder
        exclude = ['participant_id', 'messages']
        fields = '__all__'
        widgets = {
            'date_time': forms.DateInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            )
        }
