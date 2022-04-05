from django.db import migrations, transaction


class Migration(migrations.Migration):

    dependencies = [
        ('eventfiles', '0001_initial'),
    ]

    def generate_event_file_data(apps, schema_editor):
        from eventfiles.models import EventFile
        from events.models import EventParticipant
        from django.core.files import File

        f0 = File(open('static/test_files/testFile1.txt'))
        f1 = File(open('static/test_files/testFile2.txt'))
        f2 = File(open('static/test_files/testFile3.txt'))

        event_participant_data = [
            (EventParticipant.objects.filter(is_creator=True)[0], f0),
            (EventParticipant.objects.filter(is_creator=True)[1], f1),
            (EventParticipant.objects.filter(is_creator=False)[0], f2)
        ]

        with transaction.atomic():
            for data_participant_id, data_file in event_participant_data:
                event_file = EventFile(participant_id=data_participant_id, file=data_file)
                event_file.save()

    operations = [
        migrations.RunPython(generate_event_file_data),
    ]
