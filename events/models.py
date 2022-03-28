from django.db import models
from django.core.exceptions import ValidationError
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
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()
    color = models.CharField(
        max_length=7,
        choices=Colors.choices,
        default=Colors.BLACK,
    )

    def __str__(self) -> str:
        return f"{self.title} - {self.date_time_start}"


def validate_blank_title(title):
    if title is None:
        raise ValidationError('title cannot be blank')


def validate_date_time(date_time_start, date_time_end):
    if date_time_start is None:
        raise ValidationError('Starting date cannot be blank')
    if date_time_end is None:
        raise ValidationError('Ending date cannot be blank')
    if date_time_start >= date_time_end:
        raise ValidationError(f'{date_time_start} must be smaller than {date_time_end}')


def event_fields_validation(sender, instance, **kwargs):
    validate_blank_title(instance.title)
    validate_date_time(instance.date_time_start, instance.date_time_end)


pre_save.connect(event_fields_validation, sender=Event)
