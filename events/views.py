from django.contrib import messages
from reminders.models import Reminder
from django.shortcuts import render, redirect
from events.models import Event, EventParticipant
from django.contrib.auth.decorators import login_required
from events.forms import EventCreationForm, EventUpdateForm
from reminders.forms import ReminderCreationForm, ReminderUpdateForm

from main.utilities import convert_time_delta

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
