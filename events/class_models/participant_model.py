from django.db import models
from users.models import User
from .event_models import Event
from django.core.exceptions import ValidationError


class EventParticipantQuerySet(models.QuerySet):

    def get_an_event_participants(self, event):
        return self.filter(event_id=event)

    def get_an_event_participants_without_creator(self, event):
        return self.filter(event_id=event, is_creator=False)

    def get_creator_of_event(self, event):
        return self.get(event_id=event, is_creator=True)

    def get_participant_from_event(self, event, user):
        return self.get(event_id=event, user_id=user)

    def remove_participant_from_event(self, event, user):
        return self.get_participant_from_event(event, user).delete()


class EventParticipant(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_creator = models.BooleanField(null=False)

    objects = EventParticipantQuerySet.as_manager()

    def __str__(self) -> str:
        return f"{self.user_id} - {self.event_id}"

    def clean(self) -> None:
        validate_unique_user(self.event_id, self.user_id)
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


def validate_unique_user(event, user):
    if EventParticipant.objects.filter(event_id=event, user_id=user):
        raise ValidationError('user already exist in meeting')
