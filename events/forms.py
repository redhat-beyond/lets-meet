from django import forms
from users.models import User
from django.utils import timezone
from django.forms import ModelForm, Textarea, BaseFormSet
from .class_models.event_models import Event
from .class_models.participant_model import EventParticipant
from .class_models.meeting_models import OptionalMeetingDates
from django.core.exceptions import ValidationError


class DataTimePickerInput(forms.DateTimeInput):
    input_type = "datetime-local"


class EventCreationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id')
        super(EventCreationForm, self).__init__(*args, **kwargs)

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


class BaseOptionalMeetingDateFormSet(BaseFormSet):
    def clean(self):
        """checks that no two optional meetings dates with the same dates"""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        dates = []
        for form in self.forms:
            if form.cleaned_data.get('date_time_start') and form.cleaned_data.get('date_time_end'):
                start_date = form.cleaned_data.get('date_time_start')
                end_date = form.cleaned_data.get('date_time_end')
                if (start_date, end_date) in dates:
                    raise ValidationError("The optional meeting dates should be different")
                if start_date < timezone.now() or end_date < timezone.now():
                    raise ValidationError("Optional meeting dates cannot be in the past")
                dates.append((start_date, end_date))
            elif not form.cleaned_data.get('date_time_start') and not form.cleaned_data.get('date_time_end'):
                pass
            else:
                raise ValidationError("Some date fields are blank")


class OptionalMeetingDateForm(ModelForm):

    class Meta:
        model = OptionalMeetingDates
        exclude = ['event_creator_id']
        fields = ['date_time_start', 'date_time_end']
        widgets = {
            'date_time_start': forms.DateInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            'date_time_end': forms.DateInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            )
        }


class BaseParticipantFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id')
        super(BaseParticipantFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        """ Checking if there is at least one participant """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        num_of_prticipants = 0
        if(len(self.forms) >= 1):
            for form in self.forms:
                email_participant = form.cleaned_data.get('participant_email')
                if email_participant:
                    try:
                        user_instance = User.objects.get(email=email_participant)
                        creator = User.objects.get(email=self.user_id)
                        if user_instance == creator:
                            raise ValidationError("You can't add yourself as participant")
                        num_of_prticipants = 1
                    except User.DoesNotExist:
                        raise ValidationError(f"There is not user with the email: {email_participant}")
        if num_of_prticipants == 0:
            raise ValidationError("You have to enter at least one participant in the meeting")


class ParticipantForm(forms.Form):
    participant_email = forms.EmailField()
