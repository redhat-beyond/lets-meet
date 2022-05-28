from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from events.models import OptionalMeetingDates, EventParticipant
from .event_models import time_format


class PossibleParticipantsQuerySet(models.QuerySet):

    def get_all_possible_participants_of_optional_date(self, meeting_id):
        return self.filter(possible_meeting_id=meeting_id)

    def get_all_event_participants_ids_of_optional_date(self, meeting_id):
        return self.get_all_possible_participants_of_optional_date(meeting_id).values_list('participant_id', flat=True)

    def get_all_possible_participants(self, event_id):
        return self.filter(possible_meeting_id__event_creator_id__event_id=event_id)

    def get_all_meeting_participants(self, possible_meeting_dates):
        return self.filter(Q(possible_meeting_id__in=possible_meeting_dates))

    def did_user_vote(self, possible_meeting_dates, user):
        return self.get_all_meeting_participants(possible_meeting_dates).filter(participant_id__user_id=user).exists()

    def get_all_possible_participants_of_event(self, event_id):
        return self.get_all_possible_participants(event_id).values('participant_id').distinct()

    def remove_all_possible_meeting_participants(self, meeting_id):
        return self.get_all_possible_participants_of_optional_date(meeting_id).delete()

    def remove_all_event_participants(self, event_id):
        return self.get_all_possible_participants(event_id).delete()

    def remove_possible_participant(self, participant_id):
        return self.filter(participant_id=participant_id).delete()


class PossibleParticipant(models.Model):
    participant_id = models.ForeignKey(EventParticipant, on_delete=models.CASCADE)
    possible_meeting_id = models.ForeignKey(OptionalMeetingDates, on_delete=models.CASCADE)

    objects = PossibleParticipantsQuerySet.as_manager()

    def clean(self) -> None:
        validate_unique_possible_participant(self.participant_id, self.possible_meeting_id)
        validate_event_participant(self.participant_id.event_id, self.possible_meeting_id.event_creator_id.event_id)
        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (f"participant: {self.participant_id.user_id.email}"
                f" event: {self.possible_meeting_id.event_creator_id.event_id.title}"
                f" {time_format(self.possible_meeting_id.date_time_start)} -"
                f" {time_format(self.possible_meeting_id.date_time_end)} ")


def validate_event_participant(participant_event, event):
    """ validate if the current participant is participanting in the current event """
    if participant_event != event:
        raise ValidationError("The participant is not part of this event")


def validate_unique_possible_participant(participant, possible_meeting):
    if PossibleParticipant.objects.filter(
        participant_id=participant,
        possible_meeting_id=possible_meeting
    ):
        raise ValidationError("The User is already registered in this possible meeting date")
