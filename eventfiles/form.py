from .models import EventFile
from django.forms import ModelForm
from events.models import EventParticipant


class MyEventFileCreationForm(ModelForm):
    class Meta:
        model = EventFile
        fields = '__all__'
        exclude = ['participant_id']

