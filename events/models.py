from django.db import models
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.db.models.signals import pre_save


class Event(models.Model):
    class Colors(models.TextChoices):
        RED = "#FF0000", "Red"
        PINK = "#FFC0CB", "Pink"
        ORANGE = "#FFA500", "Orange"
        YELLOW = "#FFFF00", "Yellow"
        PURPLE = "#800080", "Purple"
        GREEN = "#008000", "Green"
        BLUE = "#0000FF", "Blue"
        BROWN = "#A52A2A", "Brown"
        WHITE = "#FFFFFF", "White"
        GRAY = "#808080", "Gray"
        BLACK = "#000000", "Black"

    title = models.CharField(max_length=50)
    location = models.CharField(blank=True, max_length=50)
    description = models.TextField(blank=True)
    date_time_start = models.DateTimeField(null=True, blank=True)
    date_time_end = models.DateTimeField(null=True, blank=True)
    color = models.CharField(
        max_length=7,
        choices=Colors.choices,
        default=Colors.BLACK,
    )

    def __str__(self) -> str:
        return f"{self.title} - {self.date_time_start}"


class User(models.Model):
    username = models.CharField(max_length=50)


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


def date_validator(start_date, end_date):
    if ((start_date is None and end_date is not None)
            or (end_date is None and start_date is not None)):
        raise ValidationError('start and end date_time - one field not filled')

    if ((start_date is not None and end_date is not None) and start_date >= end_date):
        raise ValidationError('date_time_start is equal or greater than date_time_end')


def validate_date_time(date_time_start, date_time_end):
    if date_time_start is None:
        raise ValidationError('Starting date cannot be blank')
    if date_time_end is None:
        raise ValidationError('Ending date cannot be blank')
    if date_time_start >= date_time_end:
        raise ValidationError(f'{date_time_start} must be smaller than {date_time_end}')
