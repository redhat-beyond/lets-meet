from django import forms
from users.models import User
from django.forms import ModelForm, Textarea
from .class_models.event_models import Event
from .class_models.participant_model import EventParticipant
from users.models import User


class DataTimePickerInput(forms.DateTimeInput):
    input_type = "datetime-local"


class EventCreationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id')
        super(EventCreationForm, self).__init__(*args, **kwargs)

<<<<<<< HEAD
=======
    title = forms.CharField(initial="", required=True, max_length=50)
    location = forms.CharField(initial="", required=False, max_length=50)
    description = forms.CharField(initial="", required=False)
    date_time_start = date_time_end = forms.DateTimeField(
        input_formats=['%I:%M %p %d-%b-%Y'],
    )

>>>>>>> 6a3359a (add css anf minor fixes)
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'description': Textarea(attrs={'cols': 50, 'rows': 3}),
            'date_time_start': DataTimePickerInput(),
            'date_time_end': DataTimePickerInput()
        }

    def save(self, commit=True):
        instance = super(EventCreationForm, self).save(commit=False)
        current_user = User.objects.get(email=self.user_id)
        if commit:
            instance.save()
            event_participant = EventParticipant(event_id=instance, user_id=current_user, is_creator=True)
            event_participant.save()
        return instance


class EventUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id')
        super(EventUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'description': Textarea(attrs={'cols': 50, 'rows': 3}),
            'date_time_start': forms.DateInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            'date_time_end': forms.DateInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            )
        }
