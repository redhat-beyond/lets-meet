import pytest
from json import loads
from reminders.models import Notification


@pytest.mark.django_db
class TestUserNotification:

    def test_get_notification(self, client, sign_in):
        expected_response = list(
            Notification.objects.filter(id=3).values('id', 'message', 'notification_type', 'participant_id__event_id')
        )

        response = client.get(pytest.get_notification_url)
        assert response.status_code == 200
        assert loads(response.content) == expected_response

    def test_seen_notification(self, client, sign_in, notification_id=3):
        assert not Notification.objects.get(id=notification_id).seen_time

        response = client.get(pytest.seen_notification_url.format(notification_id))
        assert response.status_code == 200
        assert Notification.objects.get(id=notification_id).seen_time
