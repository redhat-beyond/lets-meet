from users.models import User
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from reminders.models import Reminder
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
    BaseParticipantFormSet,
    MeetingUpdateForm,
    ShowMeetingUpdateForm,
    SetMeetingUpdateForm
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

    if event_instance in Event.objects.get_all_meetings():
        return redirect('update_meeting', meeting_id=event_id)

    try:
        participant = EventParticipant.objects.get(user_id=request.user, event_id=event_instance)
        reminder_instance = Reminder.objects.get(participant_id=participant)
    except Reminder.DoesNotExist:
        reminder_instance = None

    if request.method == 'POST':
        event_form = EventUpdateForm(request.POST, instance=event_instance)
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
        event_form = EventUpdateForm(instance=event_instance)

    return render(request, 'events/create_event.html',
                  {'event_form': event_form, 'reminder_form': reminder_form, 'title': 'Update Event',
                   'event_id': event_id})


class CreateMeetingView(TemplateView):

    template_name = "meetings/create_meeting.html"

    def __init__(self, **kwargs) -> None:
        self.title = "Create meeting"
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

    def dispatch(self, request, meeting_id=None, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(LOGIN_PAGE)

        if meeting_id:
            try:
                participant = EventParticipant.objects.get(event_id__id=meeting_id, user_id=request.user)

                # if meeting_id not in Event.objects.get_all_meetings().values("id"):
                #     return redirect('update_event', event_id=meeting_id)

                if OptionalMeetingDates.objects.get_all_event_dates(meeting_id).count() == 0:
                    return redirect('show_meeting', meeting_id=meeting_id)

                if not participant.is_creator:
                    return redirect('show_meeting', meeting_id=meeting_id)  # redirect to static meeting page

            except EventParticipant.DoesNotExist:
                return redirect(HOME_PAGE)

        # check if this is the creator
        return super(CreateMeetingView, self).dispatch(request, meeting_id, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context = {
            'title': self.title,
            'create_event_form': self.create_event_form,
            'optional_meetings_formset': self.optional_meetings_formset,
            'meeting_participants_formset': self.meeting_participants_formset,
            'formset_meeting_data': self.formset_meeting_data,
            'total_meeting_forms': len(self.formset_meeting_data),
            'formset_participant_data': self.formset_participant_data,
            'total_participant_forms': len(self.formset_participant_data)
        }
        return context

    def get(self, request, meeting_id=None):

        if meeting_id:
            self.title = "Update meeting"
            meeting_instance = Event.objects.get(id=meeting_id)
            self.create_event_form = SetMeetingUpdateForm(instance=meeting_instance)

            self.formset_meeting_data = list(
                OptionalMeetingDates.objects.get_all_event_dates(meeting_id).exclude(
                    date_time_start=meeting_instance.date_time_start, date_time_end=meeting_instance.date_time_end
                    )
                )

            for index, possible_date in enumerate(self.formset_meeting_data):
                possible_date.id = index
                possible_date.date_time_start = timezone.localtime(possible_date.date_time_start).strftime("%Y-%m-%dT%H:%M:%S")
                possible_date.date_time_end = timezone.localtime(possible_date.date_time_end).strftime("%Y-%m-%dT%H:%M:%S")

            all_participants_ids = EventParticipant.objects.filter(event_id=meeting_id, is_creator=False)
            self.formset_participant_data = list()

            for index, participant in enumerate(all_participants_ids):
                self.formset_participant_data.append({"id": index, "email": participant.user_id.email})

        else:
            self.create_event_form = EventCreationForm(user_id=request.user)

        self.optional_meetings_formset = self.OptionalMeetingDateFormSet(prefix='optional_meetings')
        self.meeting_participants_formset = self.MeetingParticipantsFormset(prefix='participants', user_id=request.user)
        return super().get(request)

    def post(self, request, meeting_id=None):
        meeting_instance = None

        if meeting_id:
            meeting_instance = Event.objects.get(id=meeting_id)
            self.create_event_form = SetMeetingUpdateForm(request.POST,instance=meeting_instance)
        else:
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
               request, event_instance, event_creator, self.optional_meetings_formset, meeting_instance):
                if self.check_participant_formset(request, event_instance, self.meeting_participants_formset, meeting_instance):
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

    def saving_all_optional_meeting_dates(self, event_creator, event_instance, optional_meetings_formset, meeting_instance=None):

        if meeting_instance:
            OptionalMeetingDates.objects.remove_all_possible_dates(event_instance)

        _ = list(map(lambda form: self.adding_event_creator(form, event_creator), optional_meetings_formset))

        # add the event time to the optional meeting dates
        OptionalMeetingDates(
            event_creator_id=event_creator,
            date_time_start=event_instance.date_time_start,
            date_time_end=event_instance.date_time_end).save()

    def check_optional_meeting_dates_formset(self, request, event_instance, event_creator, optional_meetings_formset, meeting_instance=None):
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
                self.saving_all_optional_meeting_dates(event_creator, event_instance, optional_meetings_formset, meeting_instance)
        else:
            event_instance.delete()
            return False
        return True

    @staticmethod
    def check_participant_formset(request, event_instance, meeting_participants_formset, meeting_instance=None):
        event_participants = EventParticipant.objects.filter(event_id=event_instance, is_creator=False)
        print(request.POST)
        if meeting_instance:
            event_participants.delete()

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

                            if participant not in event_participants:
                                pass  # send notification

                    except User.DoesNotExist:
                        messages.warning(request, f"There is no user with the email: {participant_email}")
                        event_instance.delete()
                        return False
                    except ValidationError:  # duplication of the same participant email
                        pass
        else:
            print(meeting_participants_formset.non_form_errors())
            event_instance.delete()
            return False
        return True

@login_required(login_url=LOGIN_PAGE)
def show_meeting(request, meeting_id):

    try:
        participant = EventParticipant.objects.get(user_id=request.user, event_id__id=meeting_id)
        is_creator = "true" if participant.is_creator else False
    except EventParticipant.DoesNotExist:
        return redirect(HOME_PAGE)
    
    event_instance = Event.objects.get(id=meeting_id)

    if request.method == 'POST':

        if participant.is_creator:
            event_form = SetMeetingUpdateForm(request.POST, instance=event_instance)
        else:
            event_form = ShowMeetingUpdateForm(request.POST, instance=event_instance)
        reminder_form = ReminderCreationForm(request.POST)

        if event_form.is_valid() and reminder_form.is_valid():
            event = event_form.save()

            participant = EventParticipant.objects.get(user_id=request.user, event_id=event)
            reminder = reminder_form.save(commit=False)

            if reminder.date_time:
                reminder.participant_id = participant
                reminder.messages = convert_time_delta(event.date_time_start - reminder.date_time)
                reminder.save()
            else:
                if reminder:
                    reminder.delete()
    else:
        if participant.is_creator:
            event_form = SetMeetingUpdateForm(instance=event_instance)
        else:
            event_form = ShowMeetingUpdateForm(instance=event_instance)
        reminder_form = ReminderCreationForm()

    return render(request, 'meetings/show_meeting.html',
                  {'event_form': event_form, 'reminder_form': reminder_form,
                   'title': 'Show Meeting', 'event_id': meeting_id, 'is_creator': is_creator})


@login_required(login_url=LOGIN_PAGE)
def add_participants(request, meeting_id):

    MeetingParticipantsFormset = formset_factory(
        ParticipantForm, formset=BaseParticipantFormSet,
        max_num=10, extra=0
    )

    if request.method == 'POST':
        try:
            event_instance = Event.objects.get(id=meeting_id)
            is_creator = EventParticipant.objects.get(user_id=request.user, event_id=event_instance).is_creator
        except Event.DoesNotExist:
            return redirect(HOME_PAGE)

        meeting_participants_formset = MeetingParticipantsFormset(
            request.POST, prefix='participants', user_id=request.user
        )

        if CreateMeetingView.check_participant_formset(request, event_instance, meeting_participants_formset, None):
            if is_creator:
                return redirect(HOME_PAGE)

    return redirect('show_meeting', meeting_id=meeting_id)


@login_required(login_url=LOGIN_PAGE)
def get_meeting_participants(request, meeting_id):
    user = request.user

    try:
        participant = EventParticipant.objects.get(user_id=user, event_id=meeting_id)
    except EventParticipant.DoesNotExist:
        return JsonResponse({})

    if participant.is_creator:
        participants = EventParticipant.objects.get_an_event_participants_without_creator(meeting_id)
    else:
        participants = EventParticipant.objects.get_an_event_participants(meeting_id)
    return JsonResponse(list(participants.values('id', 'user_id__username', 'user_id__email', 'user_id__phone_number')), safe=False)


@login_required(login_url=LOGIN_PAGE)
def delete_participant(request, participant_id):

    try:
        participant = EventParticipant.objects.get(id=participant_id)

        if EventParticipant.objects.get(user_id=request.user, event_id=participant.event_id).is_creator:
            if EventParticipant.objects.get_an_event_participants().count() > 2:
                participant.delete()
                return JsonResponse({"result": "success"})
            else:
                return JsonResponse({"result": "You cant remove the last participant."})
        else:
            return JsonResponse({"result": "You are not the event creator so you can't remove participants."})
    except EventParticipant.DoesNotExist:
        return JsonResponse({"result": "You are not a participant of this meeting"})
