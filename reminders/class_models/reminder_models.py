from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.db.utils import IntegrityError
from events.models import EventParticipant
from django.db.models.functions import Now
from django.core.exceptions import ValidationError


class ReminderQuerySet(models.QuerySet):
    def get_next_reminder(self):
        """ get the next reminder.
            Using an order function on the Reminder table with the key date_time
            and returning the first instance
        """
        return self.order_by('date_time').first()

    def remove_algorithm_reminder(self, event_creator):
        self.filter(participant_id=event_creator, method__in=(
            ReminderType.EXPIRATION_VOTING_TIME, ReminderType.RUN_ALGORITHM)).delete()


def validate_date(date_time):
    if date_time:
        if timezone.now() > date_time:
            raise ValidationError('date time should be bigger than the current date_time')


def time_format(date_time):
    return timezone.localtime(date_time).strftime("%Y-%m-%d %H:%M:%S")


class ReminderType(models.TextChoices):
    EMAIL = "ema", "Email"
    WEBSITE = "web", "Website"
    WEBSITE_EMAIL = "wae", "Website and Email"
    RUN_ALGORITHM = "run", "Run algorithm"
    EXPIRATION_VOTING_TIME = "evt", "Voting timeout"


class BasicReminderType(models.TextChoices):
    EMAIL = "ema", "Email"
    WEBSITE = "web", "Website"
    WEBSITE_EMAIL = "wae", "Website and Email"


class Reminder(models.Model):
    participant_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    date_time = models.DateTimeField(blank=True, null=True, validators=[validate_date])
    messages = models.TextField(null=True, blank=True)

    method = models.CharField(
        max_length=3,
        choices=ReminderType.choices,
        default=ReminderType.WEBSITE,
    )

    objects = ReminderQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['participant_id', 'date_time', 'messages'], name='unique reminder'),
            models.CheckConstraint(check=Q(date_time__gte=Now()), name="date_time__gte_current_time")
        ]

    def __str__(self):
        return f"{self.participant_id} - {time_format(self.date_time)}"

    def clean(self):
        validate_date(self.date_time)
        return super().clean()

    def save(self, *args, **kwargs):
        time_validation_error = "CHECK constraint failed: date_time__gte_current_time"
        row_duplication_error = ("UNIQUE constraint failed: "
                                 "reminders_reminder.participant_id_id, "
                                 "reminders_reminder.date_time, "
                                 "reminders_reminder.messages")
        self.clean()
        try:
            result = super().save(*args, **kwargs)

        except IntegrityError as error:
            if row_duplication_error in error.args:
                raise IntegrityError("reminder already exists")
            elif time_validation_error in error.args:
                raise IntegrityError("date time should be bigger than the current date_time")
            raise error
        return result
