from django.db import models
from django_db.models.signals import pre_save

class EventParticipant(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_creator = models.BooleanField(default=False, null=False)




class PossibleMeeting(models.Model):
    participant_id=models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()
