import pytest
from eventfiles.models import EventFile
from users.tests import user0  # noqa: F401
from django.core.files import File
from django.core.exceptions import ValidationError
from events.tests import event_participant_not_creator, new_event  # noqa: F401
from eventfiles.form import MyEventFileCreationForm
from events.models import EventParticipant

TEST_FILE_PATH = 'static/test_files/testFile.txt'
FILE_ALREADY_EXISTS = 'that file already exist in meeting'


@pytest.fixture()
def file0():
    return File(open(TEST_FILE_PATH))


@pytest.fixture()
def event_file0(file0, event_participant_not_creator):  # noqa: F811
    return EventFile(file=file0, participant_id=event_participant_not_creator)


@pytest.fixture()
def persist_event_file(event_file0):
    event_file0.participant_id.event_id.save()
    event_file0.participant_id.user_id.save()
    event_file0.participant_id.save()
    event_file0.save()
    return event_file0


@pytest.mark.django_db()
class TestEventFile:

    def test_new_event_file(self, event_file0, file0, event_participant_not_creator):  # noqa: F811
        assert event_file0.file == file0
        assert event_file0.participant_id == event_participant_not_creator

    def test_persist_event_file(self, persist_event_file):
        assert persist_event_file in EventFile.objects.all()

    def test_read_event_file_in_table(self, persist_event_file):
        assert persist_event_file in EventFile.objects.filter(file=persist_event_file.file)

    def test_delete_event_file_from_table(self, persist_event_file):
        persist_event_file.delete()
        assert persist_event_file not in EventFile.objects.all()

    def test_not_unique_event_file(self, persist_event_file):
        with pytest.raises(ValidationError, match=FILE_ALREADY_EXISTS):
            persist_event_file.save()


FILE_CREATION_URL = '/file/event_file'
INVALID_FILE_CREATION_URL = '/file/event_file/8'
FILE_CREATION_HTML_PATH = "file/event_files.html"


@pytest.mark.django_db
class TestEventFileForm:
    @pytest.fixture
    def signed_up_user_details(self):
        return {'email': 'testUser1@mta.ac.il', 'password': 'PasswordU$er123'}

    @pytest.fixture
    def sign_in(self, client, signed_up_user_details):
        return client.post('/login/', data=signed_up_user_details)

    @pytest.fixture
    def get_event_participant(self):
        return EventParticipant.objects.get(id=1)

    @pytest.fixture
    def valid_file_data(self,get_event_participant,file0):
        return {'file': file0, 'participant_id': get_event_participant}

    def test_valid_files_form(self, client, sign_in):
        response = client.get(f'{FILE_CREATION_URL}/1')
        assert response.status_code == 200
        assert isinstance(response.context['form'], MyEventFileCreationForm)

    def test_invalid_event_id_in_file_url(self, client, sign_in):
        response = client.get(f'{FILE_CREATION_URL}/8')
        assert response.status_code == 302

    def test_access_to_event_files_not_relevant_to_user(self, client, sign_in):
        response = client.get(f'{FILE_CREATION_URL}/2')
        assert response.status_code == 302

    def test_unauthorized_user(self, client):
        response = client.get(f'{FILE_CREATION_URL}/1')
        assert response.status_code == 302
        assert response['Location'] == '/?next=/file/event_file/1'

    def test_post_file(self, client, sign_in, valid_file_data,file0):
        form = MyEventFileCreationForm(data=valid_file_data)
        form.file=File(open(TEST_FILE_PATH))
        if form.is_valid():
            form.save()
        else:
            print(form.file)
            print(form.participant_id)
            # print(form.errors)
            assert False
