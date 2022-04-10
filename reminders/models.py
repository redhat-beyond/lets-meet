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


def validate_date(date_time):
    if timezone.now() > date_time:
        raise ValidationError('date time should be bigger than the current date_time')


class ReminderType(models.TextChoices):
    EMAIL = "ema", "Email"
    WEBSITE = "web", "Website"
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
            models.CheckConstraint(check=Q(date_time__gte=Now()), name="date_time__gte_currnet_time")
        ]

    def __str__(self):
        return f"{self.participant_id} - {self.date_time}"

    def save(self, *args, **kwargs):
        time_validation_error = "CHECK constraint failed: date_time__gte_currnet_time"
        row_duplication_error = ("UNIQUE constraint failed: "
                                 "reminders_reminder.participant_id_id, "
                                 "reminders_reminder.date_time")

        try:
            result = super().save(*args, **kwargs)

        except IntegrityError as error:
            if row_duplication_error in error.args:
                raise IntegrityError("reminder already exists")
            elif time_validation_error in error.args:
                raise IntegrityError("date time should be bigger than the current date_time")
            raise error
        return result


def validate_seen_date(time_seen, time_sent):
    if time_seen < time_sent:
        raise ValidationError('seen time cannot be earlier than time of creation.')


def validate_sent_date(time_sent):
    validate_date(time_sent)


class Notification(models.Model):
    participant_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    seen_time = models.DateTimeField(default=timezone.now)
    sent_time = models.DateTimeField(default=timezone.now, validators=[validate_sent_date])
    message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.participant_id} - {self.message}"

    def clean(self):
        self.validate_unique_notification(self.participant_id, self.sent_time)
        validate_seen_date(self.seen_time, self.sent_time)
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    @staticmethod
    def validate_unique_notification(participant, seen_time):
        if Notification.objects.filter(
                participant_id__user_id=participant.user_id,
                participant_id__event_id=participant.event_id,
                seen_time=seen_time
        ):
            raise ValidationError('notification already exists')
