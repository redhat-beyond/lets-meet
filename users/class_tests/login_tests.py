import pytest
from users.models import User
from collections import namedtuple
from django.contrib.auth import authenticate
from pytest_django.asserts import assertTemplateUsed
from users.forms import MyUserCreationForm as LoginForm
from .constants import (
    VALID_USERNAME, VALID_EMAIL, VALID_PASSWORD,
    NOT_VALID_EMAIL, NOT_VALID_PASSWORD, LOGIN_HTML_PATH
)


USER_CREDENTIALS = namedtuple("USER_CREDENTIALS", "email password")


@pytest.mark.django_db
class TestLogin:

    @pytest.fixture
    def signed_up_credentials(self):
        User.objects.create_user(username=VALID_USERNAME, email=VALID_EMAIL, password=VALID_PASSWORD)
        return USER_CREDENTIALS(VALID_EMAIL, VALID_PASSWORD)

    @pytest.fixture
    def not_signed_up_credentials(self):
        return USER_CREDENTIALS(NOT_VALID_EMAIL, NOT_VALID_PASSWORD)

    def test_sign_in_invalid(self, not_signed_up_credentials):
        user = authenticate(email=not_signed_up_credentials.email, password=not_signed_up_credentials.password)
        assert user is None

    def test_sign_in_valid(self, signed_up_credentials):
        user = authenticate(email=signed_up_credentials.email, password=signed_up_credentials.password)
        assert user

    def test_post_valid_sign_in_with_client(self, client, signed_up_credentials):
        response = client.post(
            '/login/', data={'username': signed_up_credentials.email, 'password': signed_up_credentials.password})
        assert response.status_code == 200

    def test_invalid_sign_in_redirect(self, client, not_signed_up_credentials):
        response = client.post(
            '/login/',
            data={'username': not_signed_up_credentials.email, 'password': not_signed_up_credentials.password}
        )
        assert response.request['PATH_INFO'] == '/login/'

    def test_renders_add_sign_in_template(self, client):
        response = client.get('/login/')
        assert response.status_code == 200
        assertTemplateUsed(response, LOGIN_HTML_PATH)

    def test_uses_authenticate_form(self, client):
        response = client.get('/login/')
        assert response.status_code == 200
        assert isinstance(response.context['form'], LoginForm)
