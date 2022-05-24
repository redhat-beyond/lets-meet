import pytest
from events.forms import VoteForm
from django.forms import formset_factory
from events.planner import EventPlanner
from pytest_django.asserts import assertTemplateUsed
from events.models import PossibleParticipant, OptionalMeetingDates


@pytest.mark.django_db
class TestMeetingVote:

    def test_create_valid_meeting_vote(self, get_event_participant, valid_meeting_vote_data):
        form = VoteForm(data=valid_meeting_vote_data)

        assert form.is_valid()
        meeting = OptionalMeetingDates.objects.get(id=6)
        instance = PossibleParticipant(participant_id=get_event_participant, possible_meeting_id=meeting)
        instance.save()
        assert instance in PossibleParticipant.objects.all()

    def test_meeting_vote_creation_form(self, client, sign_in):
        response = client.get(pytest.meeting_vote_url.format(4))
        assert response.status_code == 200
        assert isinstance(type(response.context['form']), type(formset_factory(VoteForm)))

    def test_renders_add_reminder_template(self, client, sign_in):
        response = client.get(pytest.meeting_vote_url.format(4))
        assert response.status_code == 200
        assertTemplateUsed(response, pytest.meeting_vote_html_path)

    def test_post_valid_reminder_creation(self, client, sign_in, valid_meeting_vote_data):
        response = client.post(pytest.meeting_vote_url.format(4), data=valid_meeting_vote_data)
        assert response.status_code == 200

    @pytest.mark.parametrize(
        ('meeting_id'), [
            2, 3
        ],
        ids=[
            "meeting 2: not invited to the meeting",
            "meeting 3: user has already voted"
        ]
    )
    def test_redirect_of_vote_page(self, client, sign_in, meeting_id):
        response = client.get(pytest.meeting_vote_url.format(meeting_id))
        assert response.status_code == 302
        assert response.url == pytest.home_url

    def test_remove_participant(self, client, sign_in):
        EventPlanner.send_invite_notification(4)
        response = client.get(pytest.remove_participant_url.format(4))
        assert response.status_code == 302
        assert response.url == pytest.home_url
