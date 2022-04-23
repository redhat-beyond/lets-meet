from django import forms
from .models import EventFile
from django.forms import ModelForm
from events.models import EventParticipant
from django import forms


class MyEventFileCreationForm(ModelForm):

    class Meta:
        model = EventFile
        fields = '__all__'

    def save(self, commit=True):
        data = self.data.copy()
        data['participant_id'] = EventParticipant.objects.get(id=1)
        self.data = data
        instance = super(MyEventFileCreationForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance
