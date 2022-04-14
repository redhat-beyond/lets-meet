import pytest
from users.models import User


@pytest.mark.django_db
class TestLogout:

    @pytest.fixture
    def sign_in_user(self, client):
        User.objects.create_user(username='valid_username', email='valid@mta.ac.il', password='pw123123')
        client.post('/register/', data={'username': 'valid_username2', 'password': 'pw123123'})

    def test_sign_out_user_with_client(self, client, sign_in_user):
        response = client.post('/logout/')
        assert not response.wsgi_request.user.is_authenticated

    def test_sign_out_redirect(self, client):
        response = client.get('/logout/')
        HOMEPAGE_URL = '/accounts/login/?next=/logout/'
        assert response.url == HOMEPAGE_URL
