from django.db import migrations, transaction


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_eventparticipant'),
        ('users', '0003_createsuperuser'),
    ]

    def generate_event_participant_data(apps, schema_editor):
        from users.models import User
        from events.models import Event
        from events.models import EventParticipant

        event_participant_data = [
            (Event.objects.get(title='event1'), User.objects.get(username="testUser1"), True),
            (Event.objects.get(title='event1'), User.objects.get(username="testUser2"), False),
            (Event.objects.get(title='event2'), User.objects.get(username="testUser3"), True)
        ]

        with transaction.atomic():
            for event_id, user_id, is_creator in event_participant_data:
                event_participant = EventParticipant(event_id=event_id, user_id=user_id, is_creator=is_creator)
                event_participant.save()

    operations = [
        migrations.RunPython(generate_event_participant_data),
    ]
