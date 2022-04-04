import pytest
from .models import EventFile
from django.core.files import File
from django.core.exceptions import ValidationError
from events.tests import event_participant_not_creator, new_event, user0  # noqa: F401


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

    def test_read_event_file_in_table(self, persist_event_file, file0):
        assert persist_event_file in EventFile.objects.filter(file=persist_event_file)

    def test_delete_event_file_from_table(self, persist_event_file):
        persist_event_file.delete()
        assert persist_event_file not in EventFile.objects.all()

    def test_not_unique_event_file(self, persist_event_file):
        with pytest.raises(ValidationError, match=FILE_ALREADY_EXISTS):
          persist_event_file.save()
