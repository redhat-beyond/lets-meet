from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save


class EventParticipant(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_creator = models.BooleanField(default=False, null=False)


class PossibleMeeting(models.Model):
    participant_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    date_time_start = models.DateTimeField(null=False, blank=False)
    date_time_end = models.DateTimeField(null=False, blank=False)


@receiver(pre_save, sender=PossibleMeeting)
def save_possible_meeting(sender, instance, **kwargs):
    validate_date_time(instance.date_time_start, instance.date_time_end)
