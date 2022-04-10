from django.db import migrations, transaction


class Migration(migrations.Migration):
    dependencies = [
        ('reminders', '0001_initial'),
        ('users', '0003_createsuperuser'),
        ('events', '0004_add_event_participant_test_data')
    ]

    def generate_notification_test_data(apps, schema_editor):
        from reminders.models import Reminder, Notification
        from events.models import EventParticipant
        from django.utils import timezone
        from datetime import datetime
        JOIN_MEETING = 'Joined Meeting in {} minutes'


        notification_data = [
            (EventParticipant.objects.get(event_id__title="event1", user_id__username="testUser1"),
             datetime(2023, 4, 24, 11, 11, 11, 0, tzinfo=timezone.utc),
             datetime(2022, 6, 24, 11, 11, 11, 0, tzinfo=timezone.utc),
             JOIN_MEETING.format(25),
             ),

            (EventParticipant.objects.get(event_id__title="event2", user_id__username="testUser3"),
             datetime(2033, 3, 24, 11, 11, 11, 0, tzinfo=timezone.utc),
             datetime(2032, 2, 24, 11, 11, 11, 0, tzinfo=timezone.utc),
             JOIN_MEETING.format(35),
             ),

            (EventParticipant.objects.get(event_id__title="event1", user_id__username="testUser2"),
             datetime(2025, 1, 2, 11, 11, 11, 0, tzinfo=timezone.utc),
             datetime(2025, 1, 1, 11, 11, 11, 0, tzinfo=timezone.utc),
             JOIN_MEETING.format(45),
             ),
        ]

        with transaction.atomic():
            for participant_id, seen_time, sent_time, message in notification_data:
                notification = Notification(participant_id=participant_id, seen_time=seen_time, sent_time=sent_time,
                                    message=message)
                notification.save()

    operations = [
        migrations.RunPython(generate_notification_test_data),
    ]
