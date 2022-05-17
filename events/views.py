from users.models import User
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from reminders.models import Reminder
from events.planner import EventPlanner
from django.forms import formset_factory
from django.views.generic import TemplateView
from main.utilities import convert_time_delta
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from reminders.forms import ReminderCreationForm, ReminderUpdateForm
from events.models import Event, EventParticipant, OptionalMeetingDates
from events.forms import (
    EventCreationForm,
    EventUpdateForm,
    OptionalMeetingDateForm,
    ParticipantForm,
    BaseOptionalMeetingDateFormSet,
    BaseParticipantFormSet
)

HOME_PAGE = 'home'
LOGIN_PAGE = 'login'


@login_required(login_url=LOGIN_PAGE)
def create_event(request):
    if request.method == 'POST':
        event_form = EventCreationForm(request.POST, user_id=request.user)
        reminder_form = ReminderCreationForm(request.POST)

        if event_form.is_valid() and reminder_form.is_valid():
            event = event_form.save()

            participant = EventParticipant.objects.get(user_id=request.user, event_id=event)
            reminder = reminder_form.save(commit=False)

            if reminder.date_time:
                reminder.participant_id = participant
                reminder.messages = convert_time_delta(event.date_time_start - reminder.date_time)
                reminder.save()
            return redirect(HOME_PAGE)
    else:
        event_form = EventCreationForm(user_id=request.user)
        reminder_form = ReminderCreationForm()

    return render(request, 'events/create_event.html',
                  {'event_form': event_form, 'reminder_form': reminder_form, 'title': 'Create Event', 'event_id': None})


@login_required(login_url=LOGIN_PAGE)
def update_event(request, event_id):
    event_instance = Event.objects.get(id=event_id)

    try:
        participant = EventParticipant.objects.get(user_id=request.user, event_id=event_instance)
        reminder_instance = Reminder.objects.get(participant_id=participant)
    except Reminder.DoesNotExist:
        reminder_instance = None

    if request.method == 'POST':
        event_form = EventUpdateForm(request.POST, user_id=request.user, instance=event_instance)
        reminder_form = ReminderUpdateForm(request.POST, instance=reminder_instance)

        if event_form.is_valid() and reminder_form.is_valid():
            event = event_form.save()

            if reminder_form.instance.date_time:
                reminder = reminder_form.save(commit=False)
                reminder.messages = convert_time_delta(event.date_time_start - reminder.date_time)
                reminder.participant_id = participant
                reminder.save()
            else:
                if reminder_instance:
                    reminder_instance.delete()

            return redirect(HOME_PAGE)
    else:
        reminder_form = ReminderUpdateForm(instance=reminder_instance)
        event_form = EventUpdateForm(user_id=request.user, instance=event_instance)

    return render(request, 'events/create_event.html',
                  {'event_form': event_form, 'reminder_form': reminder_form, 'title': 'Update Event',
                   'event_id': event_id})


class CreateMeetingView(TemplateView):

    template_name = "meetings/create_meeting.html"

    def __init__(self, **kwargs) -> None:
        self.create_event_form = None
        self.formset_meeting_data = []
        self.formset_participant_data = []
        self.optional_meetings_formset = None
        self.meeting_participants_formset = None
        self.OptionalMeetingDateFormSet = formset_factory(
            OptionalMeetingDateForm, formset=BaseOptionalMeetingDateFormSet,
            max_num=10, extra=0
        )
        self.MeetingParticipantsFormset = formset_factory(
            ParticipantForm, formset=BaseParticipantFormSet,
            max_num=10, extra=0
        )
        super().__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(LOGIN_PAGE)
        return super(CreateMeetingView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context = {
            'create_event_form': self.create_event_form,
            'optional_meetings_formset': self.optional_meetings_formset,
            'meeting_participants_formset': self.meeting_participants_formset,
            'formset_meeting_data': self.formset_meeting_data,
            'total_meeting_forms': len(self.formset_meeting_data),
            'formset_participant_data': self.formset_participant_data,
            'total_participant_forms': len(self.formset_participant_data),
            'title': 'Create meeting'
        }
        return context

    def get(self, request):
        self.create_event_form = EventCreationForm(user_id=request.user)
        self.optional_meetings_formset = self.OptionalMeetingDateFormSet(prefix='optional_meetings')
        self.meeting_participants_formset = self.MeetingParticipantsFormset(prefix='participants', user_id=request.user)
        return super().get(request)

    def post(self, request):
        self.create_event_form = EventCreationForm(request.POST, user_id=request.user)
        self.optional_meetings_formset = self.OptionalMeetingDateFormSet(request.POST, prefix='optional_meetings')
        self.meeting_participants_formset = self.MeetingParticipantsFormset(
            request.POST, prefix='participants', user_id=request.user
        )

        is_valid_formsets = False
        if self.create_event_form.is_valid():
            event_instance = self.create_event_form.save()
            event_creator = EventParticipant.objects.get(event_id=event_instance, user_id=request.user, is_creator=True)

            if self.check_optional_meeting_dates_formset(
               event_instance, event_creator, self.optional_meetings_formset):
                if self.check_participant_formset(request, event_instance, self.meeting_participants_formset):
                    # all the forms are valid and all the data saved in the DB
                    is_valid_formsets = True

                    timeout = EventPlanner.get_timeout(event_instance)
                    EventPlanner.creating_meeting_reminders(event_creator, timeout)
                    for message in EventPlanner.get_timeout_message(timeout).split("\n"):
                        messages.success(request, message)
                    EventPlanner.send_invite_notification(event_instance)
                    EventPlanner.send_meeting_invitation_email_to_participants(event_instance, event_creator)
                    return redirect('home')
            if not is_valid_formsets:
                # getting all the data that the user entered in the forms
                self.formset_meeting_data = self.get_formset_meeting_date(self.optional_meetings_formset)
                self.formset_participant_data = self.get_formset_participant_date(request)
        return self.render_to_response(self.get_context_data())

    @staticmethod
    def adding_event_creator(form, event_participant):
        """ adding event creator to each optional meeting date
            and saving this optional date in the DB """
        if not form.cleaned_data.get('date_time_start') and not form.cleaned_data.get('date_time_end'):
            # if the current optional meeting form is empty
            return
        instance = form.save(commit=False)
        instance.event_creator_id = event_participant
        instance.save()

    @staticmethod
    def get_formset_meeting_date(formset):
        result = []
        for index, form in enumerate(formset):
            form_data = {'id': 0, 'date_time_end': None, 'date_time_start': None}
            form_data['id'] = index
            if form.cleaned_data.get('date_time_end'):
                form_data['date_time_end'] = form.cleaned_data.get('date_time_end').strftime("%Y-%m-%dT%H:%M")
            if form.cleaned_data.get('date_time_start'):
                form_data['date_time_start'] = form.cleaned_data.get('date_time_start').strftime("%Y-%m-%dT%H:%M")
            result.append(form_data)
        return result

    @staticmethod
    def get_formset_participant_date(request):
        result = []
        keys = list(filter(lambda x: "participants-" in x, request.POST.keys()))[4:-1]
        for index, key in enumerate(keys):
            form_data = {}
            form_data['id'] = index
            form_data['email'] = request.POST[key]
            result.append(form_data)
        return result

    def saving_all_optional_meeting_dates(self, event_creator, event_instance, optional_meetings_formset):
        _ = list(map(lambda form: self.adding_event_creator(form, event_creator), optional_meetings_formset))

        # add the event time to the optional meeting dates
        OptionalMeetingDates(
            event_creator_id=event_creator,
            date_time_start=event_instance.date_time_start,
            date_time_end=event_instance.date_time_end).save()

    def check_optional_meeting_dates_formset(self, event_instance, event_creator, optional_meetings_formset):
        optional_meetings_formset.set_event_instance(event_instance)
        if optional_meetings_formset.is_valid():
            self.saving_all_optional_meeting_dates(event_creator, event_instance, optional_meetings_formset)
        else:
            event_instance.delete()
            return False
        return True

    @staticmethod
    def check_participant_formset(request, event_instance, meeting_participants_formset):
        if meeting_participants_formset.is_valid():
            for form in meeting_participants_formset:
                if form.is_valid():
                    try:
                        participant_email = form.cleaned_data.get('participant_email')
                        if participant_email:
                            user_instance = User.objects.get(email=participant_email)
                            participant = EventParticipant(
                                event_id=event_instance, user_id=user_instance, is_creator=False
                            )
                            participant.save()
                    except User.DoesNotExist:
                        messages.warning(request, f"There is no user with the email: {participant_email}")
                        event_instance.delete()
                        return False
                    except ValidationError:  # duplication of the same participant email
                        pass
        else:
            event_instance.delete()
            return False
        return True
