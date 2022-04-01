from django.contrib import admin
from .models import EventParticipant, Event


admin.site.register(EventParticipant)
admin.site.register(Event)
