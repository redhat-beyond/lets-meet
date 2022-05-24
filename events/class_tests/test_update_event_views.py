import pytest
from users.tests import persist_user  # noqa: F401
from events.models import Event


def update_the_data_of_the_event(original_event_instance_data):
    original_event_instance_data = list(Event.objects.filter(title=pytest.valid_event_title).values
                                        ("title", "date_time_start", "date_time_end", "color"))[0]
    original_event_instance_data["title"] = pytest.updated_event_title
    original_event_instance_data["date_time_start"] = pytest.updated_event_date_time_start
    original_event_instance_data["date_time_end"] = pytest.updated_event_date_time_end
    original_event_instance_data["color"] = pytest.updated_event_color


def assert_left_event_is_saved_and_right_is_not(left_event_title, right_event_title):
    assert Event.objects.filter(title=left_event_title)
    assert not Event.objects.filter(title=right_event_title)


@pytest.mark.django_db
class TestCreateEventForm:
    def test_updating_event_via_views(self, sign_in, client,
                                      valid_event_data_and_reminder, updated_event_data_and_reminder):

        client.post(path=pytest.create_event_url, data=valid_event_data_and_reminder)
        assert_left_event_is_saved_and_right_is_not(pytest.valid_event_title, pytest.updated_event_title)
        event_data = list(Event.objects.filter(title=pytest.valid_event_title).values
                                              ("id", "title", "date_time_start", "date_time_end", "color"))[0]
        update_the_data_of_the_event(event_data)
        client.post(path=f'{pytest.update_event_url + str(event_data["id"])}', data=updated_event_data_and_reminder)
        assert_left_event_is_saved_and_right_is_not(pytest.updated_event_title, pytest.valid_event_title)
