from users.models import User
from events.models import Event
from django.utils import timezone
from django.contrib import messages
from django.forms import formset_factory
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from events.models import EventParticipant, OptionalMeetingDates
from events.forms import (
    EventCreationForm,
    EventUpdateForm,
    OptionalMeetingDateForm,
    ParticipantForm,
    BaseOptionalMeetingDateFormSet,
    BaseParticipantFormSet
)

LOGIN_PAGE = 'login'
HOME_PAGE = 'home'


@login_required(login_url=LOGIN_PAGE)
def create_event(request):

    if request.method == 'POST':
        form = EventCreationForm(request.POST, user_id=request.user)

        if form.is_valid():
            form.save()

            title = form.cleaned_data.get('title')
            messages.success(request, f'Event: {title} created!')
            return redirect(HOME_PAGE)
    else:
        form = EventCreationForm(user_id=request.user)

    return render(request, 'events/create_event.html',
                  {'form': form, 'title': 'Create Event'})


@login_required(login_url=LOGIN_PAGE)
def update_event(request, pk):

    event_instance = Event.objects.get(id=pk)

    if request.method == 'POST':
        form = EventUpdateForm(request.POST, user_id=request.user, instance=event_instance)

        if form.is_valid():
            form.save()

            return redirect(HOME_PAGE)
    else:
        form = EventUpdateForm(user_id=request.user, instance=event_instance)

    return render(request, 'events/create_event.html',
                  {'form': form, 'title': 'Update Event'})


def adding_event_creator(form, event_participant):
    """ adding event creator to each optional meeting date
        and saving this optional date in the DB """
    if not form.cleaned_data.get('date_time_start') and not form.cleaned_data.get('date_time_end'):
        # if the current optional meeting form is empty
        return
    instance = form.save(commit=False)
    instance.event_creator_id = event_participant
    instance.save()


def check_dates_constraint(form, event_instance, request):
    """ checking if the event dates are similar to one of the optional meeting dates and if the """

    form_start_time = form.cleaned_data.get('date_time_start')
    form_end_time = form.cleaned_data.get('date_time_end')

    if(event_instance.date_time_start, event_instance.date_time_end) == (form_start_time, form_end_time):
        messages.warning(request, "The optional meeting dates should be different")
        return True
    if event_instance.date_time_start < timezone.now() or event_instance.date_time_end < timezone.now():
        messages.warning(request, "Optional meeting dates cannot be in the past")
        return True
    return False


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


def get_formset_participant_date(request):
    result = []
    keys = list(filter(lambda x: "participants-" in x, request.POST.keys()))[4:-1]
    for index, key in enumerate(keys):
        form_data = {}
        form_data['id'] = index
        form_data['email'] = request.POST[key]
        result.append(form_data)
    return result


def saving_all_optional_meeting_dates(event_creator, event_instance, optional_meetings_formset):
    _ = list(map(lambda form: adding_event_creator(form, event_creator), optional_meetings_formset))

    # add the event time to the optional meeting dates
    OptionalMeetingDates(
        event_creator_id=event_creator,
        date_time_start=event_instance.date_time_start,
        date_time_end=event_instance.date_time_end).save()


def check_optional_meeting_dates_formset(request, event_instance, event_creator,
                                         optional_meetings_formset, is_valid_formsets):
    if optional_meetings_formset.is_valid():
        is_meeting_formset_invalid = False
        for form in optional_meetings_formset:
            is_meeting_formset_invalid = check_dates_constraint(form, event_instance, request)
            if is_meeting_formset_invalid:
                break
        if is_meeting_formset_invalid:
            event_instance.delete()
            is_valid_formsets[0] = False
        else:
            saving_all_optional_meeting_dates(event_creator, event_instance, optional_meetings_formset)
    else:
        event_instance.delete()
        is_valid_formsets[0] = False


def check_participant_formset(request, event_instance, meeting_participants_formset, is_valid_formsets):
    if meeting_participants_formset.is_valid():
        for form in meeting_participants_formset:
            if form.is_valid():
                try:
                    participant_email = form.cleaned_data.get('participant_email')
                    if participant_email:
                        user_instance = User.objects.get(email=participant_email)
                        participant = EventParticipant(event_id=event_instance, user_id=user_instance, is_creator=False)
                        participant.save()
                except User.DoesNotExist:
                    messages.warning(request, f"There is not user with the email: {participant_email}")
                    event_instance.delete()
                    is_valid_formsets[0] = False
                except ValidationError:  # duplication of the same participant email
                    pass
    else:
        event_instance.delete()
        is_valid_formsets[0] = False


@login_required(login_url=LOGIN_PAGE)
def create_meeting(request):

    OptionalMeetingDateFormSet = formset_factory(OptionalMeetingDateForm,
                                                 formset=BaseOptionalMeetingDateFormSet,
                                                 max_num=10, extra=0)
    MeetingParticipantsFormset = formset_factory(ParticipantForm,
                                                 formset=BaseParticipantFormSet,
                                                 max_num=10, extra=0)
    if request.method == 'POST':
        create_event_form = EventCreationForm(request.POST, user_id=request.user)
        optional_meetings_formset = OptionalMeetingDateFormSet(request.POST, prefix='optional_meetings')
        meeting_participants_formset = MeetingParticipantsFormset(request.POST,
                                                                  prefix='participants', user_id=request.user)

        is_valid_formsets = [True]
        if create_event_form.is_valid():
            event_instance = create_event_form.save()
            event_creator = EventParticipant.objects.get(event_id=event_instance, user_id=request.user, is_creator=True)

            check_optional_meeting_dates_formset(request, event_instance,
                                                 event_creator, optional_meetings_formset, is_valid_formsets)
            if is_valid_formsets[0] is True:
                check_participant_formset(request, event_instance, meeting_participants_formset, is_valid_formsets)
        else:
            is_valid_formsets[0] = False

        if is_valid_formsets[0] is True:
            # all the forms are valid and all the data saved in the DB
            return redirect('home')
        else:
            # getting all the data that the user entered in the forms
            formset_meeting_data = get_formset_meeting_date(optional_meetings_formset)
            formset_participant_data = get_formset_participant_date(request)

            # rendering back the html file with the appropriate errors and all the data that the user enter
            return render(request, 'meetings/create_meeting.html',
                          {'create_event_form': create_event_form,
                           'optional_meetings_formset': optional_meetings_formset,
                           'meeting_participants_formset': meeting_participants_formset,
                           'formset_meeting_data': formset_meeting_data,
                           'total_meeting_forms': len(formset_meeting_data),
                           'formset_participant_data': formset_participant_data,
                           'total_participant_forms': len(formset_participant_data),
                           'title': 'Create meeting'})

    else:
        create_event_form = EventCreationForm(user_id=request.user)
        optional_meetings_formset = OptionalMeetingDateFormSet(prefix='optional_meetings')
        meeting_participants_formset = MeetingParticipantsFormset(prefix='participants', user_id=request.user)

    return render(request, 'meetings/create_meeting.html',
                  {'create_event_form': create_event_form,
                   'optional_meetings_formset': optional_meetings_formset,
                   'meeting_participants_formset': meeting_participants_formset,
                   'formset_meeting_data': [],
                   'total_meeting_forms': 0,
                   'formset_participant_data': [],
                   'total_participant_forms': 0,
                   'title': 'Create meeting'})
