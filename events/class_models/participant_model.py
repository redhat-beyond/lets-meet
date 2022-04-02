from users.models import User
from django.db import models
from .event_models import Event
from django.core.exceptions import ValidationError


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
