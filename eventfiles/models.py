from os import path
from django.db import models
from events.models import EventParticipant
from django.core.exceptions import ValidationError


def upload_to_function(instance, filename):
    return path.join('files', str(instance.participant_id.event_id.id), path.basename(filename))


class EventFile(models.Model):
    participant_id = models.ForeignKey(EventParticipant, models.SET_NULL, null=True)
    file = models.FileField(upload_to=upload_to_function)

    @staticmethod
    def validate_unique_file(up_file, up_participant_id):
        if EventFile.objects.filter(file=up_file, participant_id=up_participant_id):
            raise ValidationError('that file already exist in meeting')

    @staticmethod
    def get_files_by_event(event_id):
        participants = EventParticipant.objects.filter(event_id=event_id)
        files = []
        for participant in participants:
            files.extend(EventFile.objects.filter(participant_id=participant))

        return files

    def __str__(self):
        return f"{path.basename(self.file.name)}"

    def clean(self) -> None:
        EventFile.validate_unique_file(self.file, self.participant_id)
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
