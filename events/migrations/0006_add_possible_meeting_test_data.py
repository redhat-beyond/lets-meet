from django.db import migrations, transaction


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_possiblemeeting'),
    ]

    def generate_possible_meeting_data(apps, schema_editor):
        from datetime import datetime
        from events.models import EventParticipant
        from events.models import PossibleMeeting
        from django.utils import timezone

        possible_meeting_data = [
            (EventParticipant.objects.filter(is_creator=True)[0],
             datetime(2022, 7, 24, 11, 11, 11, 0, tzinfo=timezone.utc),
             datetime(2022, 8, 24, 12, 12, 12, 0, tzinfo=timezone.utc)),
            (EventParticipant.objects.filter(is_creator=True)[1],
             datetime(2022, 8, 14, 15, 15, 15, 0, tzinfo=timezone.utc),
             datetime(2022, 10, 14, 15, 15, 15, 0, tzinfo=timezone.utc))
        ]

        with transaction.atomic():
            for participant_id, date_time_start, date_time_end in possible_meeting_data:
                event_participant = PossibleMeeting(participant_id=participant_id,
                                                    date_time_start=date_time_start, date_time_end=date_time_end)
                event_participant.save()

    operations = [
        migrations.RunPython(generate_possible_meeting_data),
    ]
