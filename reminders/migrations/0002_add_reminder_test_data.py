from django.db import migrations, transaction


class Migration(migrations.Migration):
    dependencies = [
        ('reminders', '0001_initial'),
        ('users', '0003_createsuperuser'),
        ('events', '0004_add_event_participant_test_data')
    ]

    def generate_reminder_test_data(apps, schema_editor):
        from reminders.models import Reminder, ReminderType
        from events.models import EventParticipant
        from django.utils import timezone
        from datetime import datetime
        JOIN_MEETING = 'Joined Meeting in {} minutes'

        reminder_data = [
            (EventParticipant.objects.get(event_id__title="event1", user_id__username="testUser1"),
             datetime(2022, 4, 24, 11, 11, 11, 0, tzinfo=timezone.utc),
             JOIN_MEETING.format(15),
             ReminderType.WEBSITE_EMAIL,
             ),

            (EventParticipant.objects.get(event_id__title="event2", user_id__username="testUser3"),
             datetime(2022, 8, 14, 13, 13, 13, 0, tzinfo=timezone.utc),
             JOIN_MEETING.format(30),
             ReminderType.WEBSITE,
             ),

            (EventParticipant.objects.get(event_id__title="event1", user_id__username="testUser2"),
             datetime(2022, 8, 24, 13, 13, 13, 0, tzinfo=timezone.utc),
             JOIN_MEETING.format(50),
             ReminderType.WEBSITE,
             ),

        ]

        with transaction.atomic():
            for participant_id, date_time, messages, method in reminder_data:
                reminder = Reminder(participant_id=participant_id, date_time=date_time, messages=messages,
                                    method=method)
                reminder.save()

    operations = [
        migrations.RunPython(generate_reminder_test_data),
    ]
