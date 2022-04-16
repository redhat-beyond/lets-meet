from django import forms
from .models import EventFile
from django.forms import ModelForm
from events.class_models.participant_model import EventParticipant
from django import forms

class MyEventFileCreationForm(ModelForm):
    #file = forms.FileField()
    #participant_id=forms.ModelChoiceField(queryset=EventParticipant.objects.all(), empty_label=None)


    class Meta:
        model = EventFile
        fields = '__all__'
