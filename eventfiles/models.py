from os import path
from django.db import models
from events.models import EventParticipant
from django.core.exceptions import ValidationError


def upload_to_function(instance, filename):
    return path.join('files', str(instance.participant_id.event_id.id), path.basename(filename))


class EventFileQuerySet(models.QuerySet):

    def get_files_by_event(self, event_id):
        return self.filter(participant_id__event_id=event_id)


class EventFile(models.Model):
    participant_id = models.ForeignKey(EventParticipant, models.SET_NULL, null=True)
    file = models.FileField(upload_to=upload_to_function)

    objects = EventFileQuerySet.as_manager()

    @staticmethod
    def validate_unique_file(up_file, up_participant_id):
        if EventFile.objects.filter(file=up_file, participant_id=up_participant_id):
            raise ValidationError('that file already exist in meeting')

    def __str__(self):
        return f"{path.basename(self.file.name)}"

    def clean(self) -> None:
        self.validate_unique_file(self.file, self.participant_id)
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
