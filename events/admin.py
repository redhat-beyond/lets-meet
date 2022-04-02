from django.contrib import admin
from .models import EventParticipant, Event, PossibleMeeting

admin.site.register(PossibleMeeting)
admin.site.register(EventParticipant)
admin.site.register(Event)
