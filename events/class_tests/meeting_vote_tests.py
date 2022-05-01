import pytest
from events.forms import VoteForm
from django.forms import formset_factory
from pytest_django.asserts import assertTemplateUsed
from events.models import PossibleParticipant, OptionalMeetingDates


@pytest.mark.django_db
class TestMeetingvote:

    def test_create_valid_meeting_vote(self, get_event_participant, valid_meeting_vote_data):
        form = VoteForm(data=valid_meeting_vote_data)

        assert form.is_valid()
        meeting = OptionalMeetingDates.objects.get(id=1)
        instance = PossibleParticipant(participant_id=get_event_participant, possible_meeting_id=meeting)
        instance.save()
        assert instance in PossibleParticipant.objects.all()

    def test_meeting_vote_creation_form(self, client, sign_in):
        response = client.get(pytest.meeting_vote_url)
        assert response.status_code == 200
        assert isinstance(type(response.context['form']), type(formset_factory(VoteForm)))

    def test_renders_add_reminder_template(self, client, sign_in):
        response = client.get(pytest.meeting_vote_url)
        assert response.status_code == 200
        assertTemplateUsed(response, pytest.meeting_vote_html_path)

    def test_post_valid_reminder_creation(self, client, sign_in, valid_meeting_vote_data):
        response = client.post(pytest.meeting_vote_url, data=valid_meeting_vote_data)
        assert response.status_code == 200

    def test_remove_participant(self, client, sign_in):
        response = client.get(pytest.remove_participant_url)
        assert response.status_code == 302
        assert response.url == pytest.home_url
