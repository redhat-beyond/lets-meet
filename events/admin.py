from django.contrib import admin
from .models import EventParticipant, Event, OptionalMeetingDates

admin.site.register(Event)
admin.site.register(EventParticipant)
admin.site.register(OptionalMeetingDates)
