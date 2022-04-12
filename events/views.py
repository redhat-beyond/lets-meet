from django.shortcuts import render, redirect
from events.forms import EventCreationForm
from django.contrib import messages
from events.class_models.participant_model import EventParticipant


def create_event(request):
    if not request.user.is_authenticated:
        return redirect("welcome_page")

    if request.method == 'POST':
        print(request.POST)
        form = EventCreationForm(request.POST)
        if form.is_valid():
            print("Valid form")
            new_event = form.save()

            event_participant = EventParticipant(event_id=new_event, user_id=request.user, is_creator=True)
            event_participant.save()

            title = form.cleaned_data.get('title')
            messages.success(request, f'Event: {title} created!')
            return redirect('welcome_page')

    else:
        form = EventCreationForm()

    return render(request, 'events/create_event.html', {'form': form})
