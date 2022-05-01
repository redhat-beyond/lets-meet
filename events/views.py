from users.models import User
from django.utils import timezone
from django.contrib import messages
from reminders.models import Reminder
from main.utilities import time_format
from django.forms import formset_factory
from reminders.models import Notification
from reminders.views import seen_notification
from django.views.generic import TemplateView
from main.utilities import convert_time_delta
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from reminders.forms import ReminderCreationForm, ReminderUpdateForm
from events.models import Event, EventParticipant, OptionalMeetingDates, PossibleParticipant
from events.forms import (
    VoteForm,
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

            title = event_form.cleaned_data.get('title')
            messages.success(request, f'Event: {title} created!')
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
               request, event_instance, event_creator, self.optional_meetings_formset):
                if self.check_participant_formset(request, event_instance, self.meeting_participants_formset):
                    # all the forms are valid and all the data saved in the DB
                    is_valid_formsets = True
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
    def check_dates_constraint(form, event_instance, request):
        """ checking if the event dates are the same as one of the optional meeting dates
            and if the chosen event dates are not in the past """

        form_start_time = form.cleaned_data.get('date_time_start')
        form_end_time = form.cleaned_data.get('date_time_end')

        if(event_instance.date_time_start, event_instance.date_time_end) == (form_start_time, form_end_time):
            messages.warning(request, "The optional meeting dates should be different")
            return True
        if event_instance.date_time_start < timezone.now() or event_instance.date_time_end < timezone.now():
            messages.warning(request, "Optional meeting dates cannot be in the past")
            return True
        return False

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

    def check_optional_meeting_dates_formset(self, request, event_instance, event_creator, optional_meetings_formset):
        if optional_meetings_formset.is_valid():
            is_meeting_formset_invalid = False
            for form in optional_meetings_formset:
                is_meeting_formset_invalid = self.check_dates_constraint(form, event_instance, request)
                if is_meeting_formset_invalid:
                    break
            if is_meeting_formset_invalid:
                event_instance.delete()
                return False
            else:
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


def get_latest_meeting(user):
    """ return the lateset meeting that the user given has not vote in """
    users_meetings = Event.objects.get_all_user_meetings(user)

    chosen_event = None
    possible_meeting_dates = None

    for meeting in users_meetings:
        possible_meeting_dates = OptionalMeetingDates.objects.get_meeting_dates(meeting)
        did_user_vote = PossibleParticipant.objects.did_user_vote(possible_meeting_dates, user)

        if not did_user_vote:
            chosen_meeting_dates = possible_meeting_dates
            chosen_event = meeting
            break

    return chosen_event, chosen_meeting_dates


@login_required(login_url=LOGIN_PAGE)
def meeting_vote(request):

    user_id = request.user
    chosen_event, chosen_meeting_dates = get_latest_meeting(user_id)

    if not chosen_event:
        return redirect('home')

    title = f"{chosen_event.title} Vote Meeting"
    voteFormset = formset_factory(VoteForm, extra=chosen_meeting_dates.count())
    meetings_dates = list(
        map(lambda meeting: f"{time_format(meeting.date_time_start)} - {time_format(meeting.date_time_end)}",
            chosen_meeting_dates)
    )

    if request.method == 'POST':
        form = voteFormset(request.POST, request.FILES)

        if form.is_valid():
            for field, meeting in zip(form, chosen_meeting_dates):
                field_value = field.cleaned_data.get('date_vote')
                if field_value:
                    # add possible participant to this meeting date
                    participant = EventParticipant.objects.get(user_id=user_id, event_id=chosen_event)
                    PossibleParticipant(participant_id=participant, possible_meeting_id=meeting).save()
                else:
                    print(f"{time_format(meeting.date_time_start)} - {time_format(meeting.date_time_end)} - False")

            # send a seen request
            notification_id = Notification.objects.filter(participant_id=participant, seen_time__isnull=True).first()
            seen_notification(request, notification_id.id)
            return redirect('home')
        else:
            form = voteFormset()
    else:
        form = voteFormset()

    return render(request, 'events/meeting_vote.html', {'form': form, 'meetings_dates': meetings_dates, 'title': title})


@login_required(login_url=LOGIN_PAGE)
def remove_participant_from_meeting(request):
    user = request.user

    try:
        meeting_id, _ = get_latest_meeting(user)
        participant = EventParticipant.objects.get(user_id=user, event_id=meeting_id)
        notification_id = Notification.objects.filter(participant_id=participant, seen_time__isnull=True).first()
        seen_notification(request, notification_id.id)
        participant.delete()

        return redirect('home')
    except EventParticipant.DoesNotExist:
        return meeting_vote(request)
