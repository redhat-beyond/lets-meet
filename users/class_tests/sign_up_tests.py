import pytest
from users.models import User
from pytest_django.asserts import assertTemplateUsed
from users.forms import MyUserCreationForm as SignUpForm
from .constants import (
    LOGIN_HTML_PATH, VALID_EMAIL, VALID_USERNAME,
    VALID_PASSWORD, NOT_VALID_PASSWORD
)


@pytest.mark.django_db
class TestSignUp:

    @pytest.fixture
    def valid_users_credentials(self):
        return {'username': 'testUser', 'email': 'user@mta.ac.il',
                'password1': 'PasswordU$er123', 'password2': 'PasswordU$er123'}

    @pytest.fixture
    def valid_users(self):
        return {'username': 'testUser1', 'email': 'testUser1@mta.ac.il',
                'password1': 'PasswordU$er123', 'password2': 'PasswordU$er123'}

    @pytest.mark.parametrize("invalid_user_credentials", [
        # username cannot be None
        {'username': None, 'email': VALID_EMAIL, 'password1': VALID_PASSWORD, 'password2': VALID_PASSWORD},
        # password cannot be None
        {'username': VALID_USERNAME, 'email': VALID_EMAIL, 'password1': None, 'password2': None},
        # passowrds do not match
        {'username': VALID_USERNAME, 'email': VALID_EMAIL, 'password1': NOT_VALID_PASSWORD, 'password2': VALID_PASSWORD}
    ])
    def test_sign_up_invalid(self, invalid_user_credentials):
        form = SignUpForm(data=invalid_user_credentials)

        with pytest.raises(ValueError):
            if form.is_valid():
                form.save
            else:
                raise ValueError()

    def test_sign_up_valid(self, valid_users_credentials):
        form = SignUpForm(data=valid_users_credentials)

        if form.is_valid():
            user = form.save()
            assert User.objects.filter(pk=user.id).exists()
        else:
            assert False

    def test_uses_sign_up_form(self, client):
        response = client.get('/register/')
        assert response.status_code == 200
        assert isinstance(response.context['form'], SignUpForm)

    def test_renders_add_sign_up_template(self, client):
        response = client.get('/register/')
        assert response.status_code == 200
        assertTemplateUsed(response, LOGIN_HTML_PATH)

    def test_post_valid_sign_up_with_client(self, client, valid_users):
        response = client.post('/register/', data=valid_users)
        assert response.status_code == 200
