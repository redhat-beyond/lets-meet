import pytest
from users.tests import persist_user  # noqa: F401
from events.models import Event


def assert_left_event_is_saved_and_right_is_not(left_event_title, right_event_title):
    assert Event.objects.filter(title=left_event_title)
    assert not Event.objects.filter(title=right_event_title)


@pytest.mark.django_db
class TestCreateEventForm:
    def test_updating_event_via_views(self, sign_in, client,
                                      valid_event_data_and_reminder, updated_event_data_and_reminder):

        client.post(path=pytest.create_event_url, data=valid_event_data_and_reminder)
        assert_left_event_is_saved_and_right_is_not(pytest.valid_event_title, pytest.updated_event_title)
        event_id = Event.objects.get(title=pytest.valid_event_title).id
        client.post(path=f'{pytest.update_event_url + str(event_id)}', data=updated_event_data_and_reminder)
        assert_left_event_is_saved_and_right_is_not(pytest.updated_event_title, pytest.valid_event_title)
