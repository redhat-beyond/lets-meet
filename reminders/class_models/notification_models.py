from django.utils import timezone
from events.models import EventParticipant
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError


class NotificationType(models.TextChoices):
    WEBSITE = "website", "Website"
    MEETING = "meeting", "Meeting"


class Notification(models.Model):
    participant_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    seen_time = models.DateTimeField(null=True, blank=True)
    sent_time = models.DateTimeField(default=timezone.now)
    message = models.TextField(null=True, blank=True)
    notification_type = models.CharField(
        max_length=7,
        choices=NotificationType.choices,
        default=NotificationType.WEBSITE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['participant_id', 'sent_time'], name='unique notification')
        ]

    @staticmethod
    def validate_seen_date(time_seen, time_sent):
        if time_seen:
            if time_seen < time_sent:
                raise ValidationError('seen time cannot be earlier than time of creation.')

    def save(self, *args, **kwargs):
        row_duplication_error = ("UNIQUE constraint failed: "
                                 "reminders_notification.participant_id_id, "
                                 "reminders_notification.sent_time")
        self.clean()
        try:
            result = super().save(*args, **kwargs)
        except IntegrityError as error:
            if row_duplication_error in error.args:
                raise IntegrityError("notification already exists")
            raise error
        return result

    def __str__(self):
        return f"{self.participant_id} - {self.message}"

    def clean(self):
        self.validate_seen_date(self.seen_time, self.sent_time)
        return super().clean()
