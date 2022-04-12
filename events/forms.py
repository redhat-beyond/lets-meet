from django import forms
from django.forms import ModelForm
from .class_models.event_models import Event


class EventCreationForm(ModelForm):

    title = forms.CharField(initial="", required=True, max_length=50)

    location = forms.CharField(initial="", required=False, max_length=50)

    description = forms.CharField(initial="", required=False)

    date_time_start = date_time_end = forms.DateTimeField(input_formats=['%I:%M %p %d-%b-%Y'],
                                                          widget=forms.DateTimeInput(
                                                            attrs={'type': 'datetime-local'},
                                                            format='%I:%M %p %d-%b-%Y'))

    class Meta:
        model = Event
        fields = (
            'title',
            'location',
            'description',
            'date_time_start',
            'date_time_end',
            'color',
        )
