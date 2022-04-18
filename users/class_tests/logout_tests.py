import pytest
from users.models import User
from .constants import (
    VALID_USERNAME2, HOMEPAGE_URL,
    VALID_USERNAME, VALID_EMAIL, VALID_PASSWORD
)


@pytest.mark.django_db
class TestLogout:

    @pytest.fixture
    def sign_in_user(self, client):
        User.objects.create_user(username=VALID_USERNAME, email=VALID_EMAIL, password=VALID_PASSWORD)
        client.post('/register/', data={'username': VALID_USERNAME2, 'password': VALID_PASSWORD})

    def test_sign_out_user_with_client(self, client, sign_in_user):
        response = client.post('/logout/')
        assert not response.wsgi_request.user.is_authenticated

    def test_sign_out_redirect(self, client):
        response = client.get('/logout/')
        assert response.url == HOMEPAGE_URL
