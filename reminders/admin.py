from django.contrib import admin
from .models import Reminder, Notification

admin.site.register(Reminder)
admin.site.register(Notification)