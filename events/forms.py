from django import forms
from django.forms import ModelForm
from .class_models.event_models import Event
from .class_models.participant_model import EventParticipant


class EventCreationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id')
        super(EventCreationForm, self).__init__(*args, **kwargs)

    title = forms.CharField(initial="", required=True, max_length=50)
    location = forms.CharField(initial="", required=False, max_length=50)
    description = forms.CharField(initial="", required=False)
    date_time_start = date_time_end = forms.DateTimeField(
        input_formats=['%I:%M %p %d-%b-%Y'],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%I:%M %p %d-%b-%Y'
         )
     )

    class Meta:
        model = Event
        fields = ["title", "location", "description", "date_time_start", "date_time_end"]

    def save(self, commit=True):
        instance = super(EventCreationForm, self).save(commit=False)
        if commit:
            instance.save()
            self.user_id.save()
            event_participant = EventParticipant(event_id=instance, user_id=self.user_id, is_creator=True)
            event_participant.save()
        return instance
