<<<<<<< HEAD
from django.contrib import messages
from django.shortcuts import render, redirect
from events.models import Event
from django.contrib.auth.decorators import login_required
from events.forms import EventCreationForm, EventUpdateForm


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
=======
from django.shortcuts import render, redirect
from events.forms import EventCreationForm
from django.contrib import messages


def create_event(request):
    if not request.user.is_authenticated:
        return redirect("welcome_page")

    if request.method == 'POST':
        print(request.POST)
        form = EventCreationForm(request.POST, user_id=request.user)
        if form.is_valid():
            print("Valid form")
            form.save()

            title = form.cleaned_data.get('title')
            messages.success(request, f'Event: {title} created!')
            return redirect('welcome_page')

    else:
        form = EventCreationForm(user_id=request.user)

    return render(request, 'events/create_event.html', {'form': form})
>>>>>>> b81ad64 (Add create event page)
