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
