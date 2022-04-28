from django.shortcuts import redirect, render
from .models import EventFile
from django.http import HttpResponse, Http404
from os import path
from django.conf import settings
from events.models import EventParticipant, Event
from django.contrib.auth.decorators import login_required
from eventfiles.form import MyEventFileCreationForm

FILE_PATH = settings.MEDIA_ROOT / "files"


@login_required(login_url='welcome_page')
def file_page_per_event(request, event_id):
    user_id = request.user
    try:
        current_event = Event.objects.get(pk=event_id)
        participant_id = EventParticipant.objects.get(event_id=current_event, user_id=user_id)
    except EventParticipant.DoesNotExist:
        return redirect("home")
    except Event.DoesNotExist:
        return redirect("home")

    title = current_event.title

    if request.method == 'POST':
        form = MyEventFileCreationForm(request.POST, request.FILES)
        event_form = form.save(commit=False)
        event_form.participant_id = participant_id
        event_form.save()
    else:
        form = MyEventFileCreationForm()
    context = {'files': EventFile.get_files_by_event(event_id), 'event': event_id, 'form': form, 'title': title}
    return render(request, "file/event_files.html", context)


def download(request):
    event = request.GET.get('event')
    file_name = request.GET.get('file_name')
    file_path = path.join(FILE_PATH / event, file_name)
    if path.exists(file_path):
        with open(file_path, 'rb')as fh:
            response = HttpResponse(fh.read(), content_type="/application/adminupload")
            response['Content-Disposition'] = 'inline;filename=' + path.basename(file_path)
            return response
    raise Http404
