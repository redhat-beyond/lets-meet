from django.contrib import admin
from .models import EventParticipant, Event, OptionalMeetingDates, PossibleParticipant

admin.site.register(Event)
admin.site.register(EventParticipant)
admin.site.register(OptionalMeetingDates)
admin.site.register(PossibleParticipant)
