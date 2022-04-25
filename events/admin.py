from django.contrib import admin
from .models import EventParticipant, Event, PossibleMeeting, PossibleParticipant

admin.site.register(PossibleMeeting)
admin.site.register(EventParticipant)
admin.site.register(Event)
admin.site.register(PossibleParticipant)
