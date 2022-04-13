from django.db import migrations, transaction


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_possibleparticipant'),
    ]

    def generate_possible_meeting_data(apps, schema_editor):
        from events.models import EventParticipant
        from events.models import PossibleMeeting
        from events.models import PossibleParticipant

        test_participant1 = EventParticipant.objects.filter(is_creator=True)[0]
        test_participant2 = EventParticipant.objects.filter(is_creator=True)[1]

        possible_meetings_arr_for_event3 = PossibleMeeting.objects.filter(
            participant_id__is_creator=True, participant_id__event_id__title="event3")

        possible_participant_data = [
            (test_participant1,
             PossibleMeeting.objects.get(participant_id__id=test_participant1.id)),

            (test_participant2,
             PossibleMeeting.objects.get(participant_id__id=test_participant2.id)),

            (EventParticipant.objects.get(
                event_id__title='event3',
                user_id__username='testUser1'),
                possible_meetings_arr_for_event3[0]
             ),
            (EventParticipant.objects.get(
                event_id__title='event3',
                user_id__username='testUser2'),
                possible_meetings_arr_for_event3[1]
             ),
            (EventParticipant.objects.get(
                event_id__title='event3',
                user_id__username='testUser3'),
                possible_meetings_arr_for_event3[1]
             ),
            (EventParticipant.objects.get(
                event_id__title='event3',
                user_id__username='testUser3'),
                possible_meetings_arr_for_event3[2]
             )
        ]

        with transaction.atomic():
            for participant_id, possible_meeting_id in possible_participant_data:
                possible_participant = PossibleParticipant(
                    participant_id=participant_id,
                    possible_meeting_id=possible_meeting_id
                 )
                possible_participant.save()

    operations = [
        migrations.RunPython(generate_possible_meeting_data),
    ]
