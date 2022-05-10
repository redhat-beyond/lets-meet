from django.shortcuts import render, get_object_or_404, redirect
from .models import EventFile
from django.http import HttpResponse, Http404
from os import path
from django.conf import settings
from events.models import EventParticipant, Event
from django.contrib.auth.decorators import login_required
from eventfiles.form import MyEventFileCreationForm

FILE_PATH = settings.MEDIA_ROOT / "files"
LOGIN_PAGE = 'login'


@login_required(login_url=LOGIN_PAGE)
def view_all_event_files_with_upload_and_download_option_page(request, event_id):
    """ if the user is logged in, render all files relevant to the event with the option to upload and download  """
    try:
        current_event = get_object_or_404(Event, pk=event_id)
        participant = EventParticipant.objects.get_participant_from_event(event_id, request.user)
        event_participant_creator = EventParticipant.objects.get_creator_of_event(event_id)
        is_event_creator = event_participant_creator == participant
    except EventParticipant.DoesNotExist:
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        form = MyEventFileCreationForm(request.POST, request.FILES)
        event_form = form.save(commit=False)
        event_form.participant_id = participant
        event_form.save()
    else:
        form = MyEventFileCreationForm()
    context = {'files': EventFile.objects.get_files_by_event(event_id), 'event': current_event, 'form': form,
               'is_event_creator': is_event_creator, 'user_participant': participant, }
    return render(request, "file/event_files.html", context)


@login_required(login_url=LOGIN_PAGE)
def download_files(request):
    event = request.GET.get('event')
    file_name = request.GET.get('file_name')
    file_path = path.join(FILE_PATH / event, file_name)
    if path.exists(file_path):
        with open(file_path, 'rb')as fh:
            response = HttpResponse(fh.read(), content_type="/application/adminupload")
            response['Content-Disposition'] = 'inline;filename=' + path.basename(file_path)
            return response
    raise Http404


@login_required(login_url=LOGIN_PAGE)
def delete_file(request, event_id, file_id):
    try:
        current_event = get_object_or_404(Event, pk=event_id)
        current_file = get_object_or_404(EventFile, pk=file_id)
        participant = EventParticipant.objects.get_participant_from_event(current_event, request.user)
        event_participant_creator = EventParticipant.objects.get_creator_of_event(event_id)
        is_event_creator = event_participant_creator == participant
    except EventParticipant.DoesNotExist:
        return HttpResponse('Unauthorized', status=401)

    if is_event_creator or current_file.participant_id.id is participant.id:
        current_file.delete()
        return redirect(view_all_event_files_with_upload_and_download_option_page, event_id=event_id)
    return HttpResponse('Unauthorized', status=401)
