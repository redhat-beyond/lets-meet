from django.db import models
from .event_models import validate_date_time, time_format
from .participant_model import EventParticipant
from django.core.exceptions import ValidationError


class PossibleMeeting(models.Model):
    participant_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.participant_id} - {time_format(self.date_time_start)} - {time_format(self.date_time_end)}"

    def clean(self) -> None:
        validate_date_time(self.date_time_start, self.date_time_end)
        validate_unique_possible_meeting(self.participant_id, self.date_time_start, self.date_time_end)
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


def validate_unique_possible_meeting(participant_id, date_time_start, date_time_end):
    if PossibleMeeting.objects.filter(participant_id=participant_id, date_time_start=date_time_start,
                                      date_time_end=date_time_end):
        raise ValidationError('meeting hours already exists')
