from django.db import migrations, transaction


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    def generate_event_test_data(apps, schema_editor):
        from events.models import Event
        from datetime import datetime
        from django.utils import timezone

        events_test_data = [
            ('event1', datetime(2022, 3, 24, 11, 11, 11, 0, tzinfo=timezone.utc),
             datetime(2022, 3, 24, 12, 12, 12, 0, tzinfo=timezone.utc)),
            ('event2', datetime(2022, 8, 14, 13, 13, 13, 0, tzinfo=timezone.utc),
             datetime(2022, 8, 14, 15, 15, 15, 0, tzinfo=timezone.utc)),
            ('event3', datetime(2023, 1, 24, 13, 13, 13, 0, tzinfo=timezone.utc),
             datetime(2023, 1, 24, 15, 15, 15, 0, tzinfo=timezone.utc))
        ]

        with transaction.atomic():
            for title, date_time_start, date_time_end in events_test_data:
                event = Event(title=title, date_time_start=date_time_start, date_time_end=date_time_end)
                event.save()

    operations = [
        migrations.RunPython(generate_event_test_data),
    ]
