from django.db import models
from .participant_model import EventParticipant
from django.core.exceptions import ValidationError
from .event_models import validate_date_time, time_format


class OptionalMeetingDates(models.Model):
    event_creator_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.event_creator_id} - {time_format(self.date_time_start)} - {time_format(self.date_time_end)}"

    def clean(self) -> None:
        validate_date_time(self.date_time_start, self.date_time_end)
        validate_unique_possible_meeting(self.event_creator_id, self.date_time_start, self.date_time_end)
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


def validate_unique_possible_meeting(event_creator_id, date_time_start, date_time_end):
    if OptionalMeetingDates.objects.filter(
            event_creator_id=event_creator_id,
            date_time_start=date_time_start,
            date_time_end=date_time_end
    ):
        raise ValidationError('meeting hours already exists')
