from django.db import models
from .participant_model import EventParticipant
from events.models import validate_date_time, time_format


class PossibleMeetingsQuerySet(models.QuerySet):
    def get_all_event_dates(self, event_id):
        return self.filter(event_creator_id__event_id=event_id)

    def remove_all_possible_dates(self, event_id):
        return self.get_all_event_dates(event_id).delete()


class PossibleMeetingManager(models.Manager):
    def get_queryset(self):
        return PossibleMeetingsQuerySet(self.model, using=self._db)

    def get_all_event_dates(self, event_id):
        return self.get_queryset().get_all_event_dates(event_id)

    def remove_all_possible_dates(self, event_id):
        return self.get_queryset().remove_all_possible_dates(event_id)

    def save_multiple_dates(self, possible_dates):
        # check bulk_create
        for meeting in possible_dates:
            OptionalMeetingDates(
                event_creator_id=meeting.event_creator_id,
                date_time_start=meeting.date_time_start,
                date_time_end=meeting.date_time_end).save()


class OptionalMeetingDates(models.Model):
    event_creator_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event_creator_id', 'date_time_start', 'date_time_end'],
                                    name='unique optional meeting')
        ]

    objects = PossibleMeetingManager()

    def __str__(self) -> str:
        return f"{self.event_creator_id} - {time_format(self.date_time_start)} - {time_format(self.date_time_end)}"

    def clean(self) -> None:
        validate_date_time(self.date_time_start, self.date_time_end)
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
