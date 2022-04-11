from django.db import models
from django.db.models import Q
from django.utils import timezone
from main.utilities import time_format
from django.db.utils import IntegrityError
from events.models import EventParticipant
from django.core.exceptions import ValidationError


class ReminderQuerySet(models.QuerySet):
    def get_next_reminder(self):
        """ get the next reminder.
            Using an order function on the Reminder table with the key date_time
            and returning the first instance
        """
        return self.order_by('date_time').first()


def validate_date(date_time):
    if timezone.now() > date_time:
        raise ValidationError(f'{time_format(date_time)} should be bigger than current date_time')


class ReminderType(models.TextChoices):
    WEBSITE = "web", "Website"
    EMAIL = "ema", "Email"
    WEBSITE_EMAIL = "wae", "Website and Email"


class Reminder(models.Model):
    participant_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now, validators=[validate_date])
    messages = models.TextField(null=True, blank=True)

    method = models.CharField(
        max_length=3,
        choices=ReminderType.choices,
        default=ReminderType.WEBSITE,
    )

    objects = ReminderQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['participant_id', 'date_time'], name='unique reminder'),
            # models.CheckConstraint(check=Q(date_time__gte=get_current_time), name="date_time__gte_currnet_time")
        ]

    def __str__(self):
        return f"{self.participant_id} - {self.date_time}"

    def clean(self):
        validate_date(self.date_time)
        return super().clean()

    def save(self, *args, **kwargs):
        unique_row_duplication = "UNIQUE constraint failed: reminders_reminder.participant_id_id, reminders_reminder.date_time"

        self.clean()

        try:
            result = super().save(*args, **kwargs)
        except IntegrityError as error:
            if unique_row_duplication in error.args:
                raise IntegrityError("reminder already exists")
            raise error
        else:
            return result
