from .models import EventFile
from django.forms import ModelForm


class MyEventFileCreationForm(ModelForm):
    class Meta:
        model = EventFile
        fields = '__all__'
        exclude = ['participant_id']
