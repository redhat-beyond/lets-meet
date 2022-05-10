import pytest
import re
from events.tests import event_participant_not_creator, new_event  # noqa: F401
from eventfiles.form import MyEventFileCreationForm
from pytest_django.asserts import assertTemplateUsed
from django.urls import reverse
from eventfiles.models import EventFile

FILE_CREATION_URL = '/file/event_file'
INVALID_FILE_CREATION_URL = '/file/event_file/8'
FILE_CREATION_HTML_PATH = "file/event_files.html"
FILE_DELETE_URL = "/file/event_file/1/delete"
FILE_CREATED_BY_USER2 = 3
FILE_CREATED_BY_EVENT_CREATOR = 1
DELETE_USER2_FILE_URL = f'{FILE_DELETE_URL}/{FILE_CREATED_BY_USER2}'
DELETE_EVENT_CREATOR_FILE_URL = f'{FILE_DELETE_URL}/{FILE_CREATED_BY_EVENT_CREATOR}'


@pytest.mark.django_db
class TestEventFileFormView:
    @pytest.fixture
    def signed_up_user_details(self):
        return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}

    @pytest.fixture
    def signed_up_user2_details(self):
        return {'email': 'testUser2@mta.ac.il', 'password': 'PasswordU$er456'}

    @pytest.fixture
    def sign_in_with_creator(self, client, signed_up_user_details):
        return client.post('/login/', data=signed_up_user_details)

    @pytest.fixture
    def sign_in_with_user2(self, client, signed_up_user2_details):
        return client.post('/login/', data=signed_up_user2_details)

    def test_valid_files_form(self, client, sign_in_with_creator):
        response = client.get(f'{FILE_CREATION_URL}/1')
        assert response.status_code == 200
        assert isinstance(response.context['form'], MyEventFileCreationForm)

    def test_render_files_template(self, client, sign_in_with_creator):
        response = client.get(f'{FILE_CREATION_URL}/1')
        assert response.status_code == 200
        assertTemplateUsed(response, FILE_CREATION_HTML_PATH)

    @pytest.mark.parametrize('url_path,status_code', [
        (f'{FILE_CREATION_URL}/8', 404),
        (f'{FILE_CREATION_URL}/2', 401)

    ], ids=[
        "event doesnt exist",
        "user not a participant in the event",
    ])
    def test_invalid_event_id_in_file_url(self, client, sign_in_with_creator, url_path, status_code):
        response = client.get(url_path)
        assert response.status_code == status_code

    def test_unauthorized_user_redirected_to_main_page(self, client):
        response = client.get(f'{FILE_CREATION_URL}/1')
        assert response.status_code == 302
        response = client.get(response.url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'login/register_login.html')

    def test_delete_button_visible_for_file_user_created(self, sign_in_with_user2, client):
        """ test that an ordinary user can delete only files he created """
        response = client.get(reverse("event_files", args=[1]))
        char_content = response.content.decode(response.charset)
        found_file3 = re.search(f'delete testFile{FILE_CREATED_BY_USER2}', char_content)
        found_file1 = re.search(f'delete testFile{FILE_CREATED_BY_EVENT_CREATOR}', char_content)
        print(char_content)
        assert found_file3 and not found_file1

    def test_unauthorized_user_delete(self, sign_in_with_user2, client):
        response = client.get(DELETE_EVENT_CREATOR_FILE_URL)
        assert response.status_code == 401

    def test_delete_file_created_by_user(self, sign_in_with_user2, client):
        client.get(DELETE_USER2_FILE_URL)
        assert not EventFile.objects.all().filter(id=FILE_CREATED_BY_USER2).exists()

    def test_all_delete_buttons_visible_for_event_creator(self, sign_in_with_creator, client):
        """ test that the event creator can delete all files """
        response = client.get(reverse("event_files", args=[1]))
        char_content = response.content.decode(response.charset)
        found_file3 = re.search(f'delete testFile{FILE_CREATED_BY_USER2}', char_content)
        found_file1 = re.search(f'delete testFile{FILE_CREATED_BY_EVENT_CREATOR}', char_content)
        assert found_file3 and found_file1

    def test_event_creator_delete_any_file(self, sign_in_with_creator, client):
        client.get(DELETE_USER2_FILE_URL)
        assert not EventFile.objects.all().filter(id=FILE_CREATED_BY_USER2).exists()

    def test_unsigned_user_delete(self, client):
        response = client.get(DELETE_USER2_FILE_URL)
        assert response.status_code == 302
        response = client.get(response.url)
        assert response.status_code == 200
        assertTemplateUsed(response, 'login/register_login.html')

    def test_redirection_to_file_page_after_delete(self, sign_in_with_user2, client):
        response = client.get(DELETE_USER2_FILE_URL)
        assert response.status_code == 302
        response = client.get(response.url)
        assert response.status_code == 200
        assertTemplateUsed(response, FILE_CREATION_HTML_PATH)
