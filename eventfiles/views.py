from django.shortcuts import redirect, render
from .models import EventFile
from django.http import HttpResponse, Http404
from .form import MyEventFileCreationForm
from os import path
from django.conf import settings
from django.views.generic import CreateView
from django.contrib import messages
from events.class_models.participant_model import EventParticipant,Event


FILE_PATH = settings.MEDIA_ROOT / "files"


def file_page(request):
    context = {'files': EventFile.objects.all()}
    return render(request, "file/file_upload.html", context)

def file_page_per_event(request,event):
    if not request.user.is_authenticated:
        return redirect("welcome_page")
    form = MyEventFileCreationForm()
    messages.success(request, 'first step')
    if request.method == 'POST':
        messages.warning(request, 'post type')
        print(request.POST)
        form = MyEventFileCreationForm(request.POST,request.FILES)
        form.participant_id=EventParticipant.objects.get(pk=1)
        if form.is_valid():
            print("Valid form")
            event_file = form.save()
            messages.warning(request, 'uploaded.')
        else:
            messages.warning(request, 'missing arguments')
    context = {'files': EventFile.get_files_by_event(event), 'event': event,'form':form}
    return render(request, "file/event_files.html", context)






    #context = {'files': EventFile.get_files_by_event(event),'event':event}
    #return render(request, "file/event_files.html", context)

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


def upload(request):
    if not request.user.is_authenticated:
        return redirect("welcome_page")
    form = MyEventFileCreationForm()
    messages.success(request, 'first step')
    if request.method == 'POST':
        messages.warning(request, 'post type')
        print(request.POST)
        form = MyEventFileCreationForm(request.POST,request.FILES)
        form.participant_id=EventParticipant.objects.get(pk=1)
        if form.is_valid():
            print("Valid form")
            event_file = form.save()
            messages.warning(request, 'uploaded.')
        else:
            messages.warning(request, 'missing arguments')
    return render(request, "file/file.html", {'form': form})


def events(request):
    context = {'events': Event.objects.all()}
    return render(request, "file/all_events.html", context)





