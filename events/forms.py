from django import forms
from .class_models.event_models import Event
from .class_models.participant_model import EventParticipant
from users.models import User

TIME_FORMAT = ['%I:%M %p %d-%b-%Y']


class EventCreationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id')
        super(EventCreationForm, self).__init__(*args, **kwargs)

    title = forms.CharField(initial="", required=True, max_length=50)
    location = forms.CharField(initial="", required=False, max_length=50)
    description = forms.CharField(initial="", required=False)
    date_time_start = date_time_end = forms.DateTimeField(
        input_formats=TIME_FORMAT,
    )

    class Meta:
        model = Event
        fields = '__all__'

    def save(self, commit=True):
        instance = super(EventCreationForm, self).save(commit=False)
        if commit:
            current_user = User.objects.get(email=self.user_id)
            instance.save()
            event_participant = EventParticipant(event_id=instance, user_id=current_user, is_creator=True)
            event_participant.save()
        return instance
