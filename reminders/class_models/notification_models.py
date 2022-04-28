from django.db.models import Q
from django.utils import timezone
from django.db.models.functions import Now
from events.models import EventParticipant
from django.db import models, IntegrityError
from django.core.exceptions import ValidationError


class Notification(models.Model):
    participant_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    seen_time = models.DateTimeField(default=timezone.now, null=True)
    sent_time = models.DateTimeField(default=timezone.now)
    message = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['participant_id', 'sent_time'], name='unique notification'),
            models.CheckConstraint(check=Q(sent_time__gte=Now()), name="sent_time__gte_current_time")
        ]

    @staticmethod
    def validate_seen_date(time_seen, time_sent):
        if time_seen:
            if time_seen < time_sent:
                raise ValidationError('seen time cannot be earlier than time of creation.')

    def save(self, *args, **kwargs):
        time_validation_error = "CHECK constraint failed: sent_time__gte_current_time"
        row_duplication_error = ("UNIQUE constraint failed: "
                                 "reminders_notification.participant_id_id, "
                                 "reminders_notification.sent_time")
        self.clean()
        try:
            result = super().save(*args, **kwargs)
        except IntegrityError as error:
            if row_duplication_error in error.args:
                raise IntegrityError("notification already exists")
            elif time_validation_error in error.args:
                raise IntegrityError("sent time should be bigger than the current date")
            raise error
        return result

    def __str__(self):
        return f"{self.participant_id} - {self.message}"

    def clean(self):
        self.validate_seen_date(self.seen_time, self.sent_time)
        return super().clean()
