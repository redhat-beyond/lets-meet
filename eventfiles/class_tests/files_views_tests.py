import pytest
from events.tests import event_participant_not_creator, new_event  # noqa: F401
from eventfiles.form import MyEventFileCreationForm
from pytest_django.asserts import assertTemplateUsed

FILE_CREATION_URL = '/file/event_file'
INVALID_FILE_CREATION_URL = '/file/event_file/8'
FILE_CREATION_HTML_PATH = "file/event_files.html"
HOME_HTML_PATH = 'user_site/home.html'


@pytest.mark.django_db
class TestEventFileForm:
    @pytest.fixture
    def signed_up_user_details(self):
        return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}

    @pytest.fixture
    def sign_in(self, client, signed_up_user_details):
        return client.post('/login/', data=signed_up_user_details)

    def test_valid_files_form(self, client, sign_in):
        response = client.get(f'{FILE_CREATION_URL}/1')
        assert response.status_code == 200
        assert isinstance(response.context['form'], MyEventFileCreationForm)

    def test_render_files_template(self, client, sign_in):
        response = client.get(f'{FILE_CREATION_URL}/1')
        assert response.status_code == 200
        assertTemplateUsed(response, FILE_CREATION_HTML_PATH)

    def test_invalid_event_id_in_file_url(self, client, sign_in):
        response = client.get(f'{FILE_CREATION_URL}/8')
        assert response.status_code == 302
        response = client.get(response.url)
        assert response.status_code == 200
        assertTemplateUsed(response, HOME_HTML_PATH)

    def test_access_to_event_files_not_relevant_to_user(self, client, sign_in):
        response = client.get(f'{FILE_CREATION_URL}/2')
        assert response.status_code == 302
        response = client.get(response.url)
        assert response.status_code == 200
        assertTemplateUsed(response, HOME_HTML_PATH)

    def test_unauthorized_user(self, client):
        response = client.get(f'{FILE_CREATION_URL}/1')
        assert response.status_code == 302
        response = client.get(response.url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'main/index.html')
