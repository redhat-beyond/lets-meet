from django import forms
from django.forms import ModelForm
from reminders.models import Reminder, BasicReminderType


class DataTimePickerInput(forms.DateTimeInput):
    input_type = "datetime-local"


class ReminderCreationForm(ModelForm):
    method = forms.ChoiceField(choices=BasicReminderType.choices)

    class Meta:
        model = Reminder
        exclude = ['participant_id', 'messages']
        fields = '__all__'
        widgets = {
            'date_time': DataTimePickerInput()
        }


class ReminderUpdateForm(ModelForm):
    method = forms.ChoiceField(choices=BasicReminderType.choices)

    class Meta:
        model = Reminder
        exclude = ['participant_id', 'messages']
        fields = '__all__'
        widgets = {
            'date_time': forms.DateInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            )
        }
