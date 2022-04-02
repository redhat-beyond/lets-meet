from django.db import models
from django.core.exceptions import ValidationError
from users.models import User


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

    def clean(self):
        if not self.title:
            raise ValidationError('Title cannot be blank')
        validate_date_time(self.date_time_start, self.date_time_end)

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} - {time_format(self.date_time_start)}"


class EventParticipant(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_creator = models.BooleanField(null=False)

    def __str__(self) -> str:
        return f"{self.user_id} - {self.event_id}"

    def clean(self) -> None:
        validate_unique_user(self.event_id, self.user_id)

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


def validate_unique_user(event, user):
    if EventParticipant.objects.filter(event_id=event, user_id=user):
        raise ValidationError('user already exist in meeting')


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


def validate_date_time(starting_date, ending_date):
    if not starting_date:
        raise ValidationError('Starting date cannot be blank')
    if not ending_date:
        raise ValidationError('Ending date cannot be blank')
    if starting_date >= ending_date:
        raise ValidationError(f'{time_format(starting_date)} must be smaller than {time_format(ending_date)}')


def time_format(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")
