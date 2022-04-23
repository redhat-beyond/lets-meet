from events.models import Event
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from events.forms import EventCreationForm, EventUpdateForm


LOGIN_PAGE = 'login'
HOME_PAGE = 'home'


@login_required(login_url=LOGIN_PAGE)
def create_event(request):

    if request.method == 'POST':
        event_form = EventCreationForm(request.POST, user_id=request.user)

        if event_form.is_valid():
            event_form.save()

            title = event_form.cleaned_data.get('title')
            messages.success(request, f'Event: {title} created!')
            return redirect(HOME_PAGE)
    else:
        event_form = EventCreationForm(user_id=request.user)

    return render(request, 'events/create_event.html', {'event_form': event_form, 'title': 'Create Event'})


@login_required(login_url=LOGIN_PAGE)
def update_event(request, pk):

    event_instance = Event.objects.get(id=pk)

    if request.method == 'POST':
        event_form = EventUpdateForm(request.POST, user_id=request.user, instance=event_instance)

        if event_form.is_valid():
            event_form.save()
            return redirect(HOME_PAGE)

    event_form = EventUpdateForm(user_id=request.user, instance=event_instance)
    return render(request, 'events/create_event.html', {'event_form': event_form, 'title': 'Update Event'})
