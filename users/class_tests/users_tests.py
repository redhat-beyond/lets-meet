import pytest
from users.models import User
from phonenumber_field.phonenumber import PhoneNumber
from .constants import (
    NAME, EMAIL, PASSWORD, PHONE_NUM,
    MISSING_REGION, NOT_VALID_PHONE, NOT_INTERPRETED,
    NOT_PHONE_NUMBER, NAME_LENGTH_ERROR, EMAIL_ERROR
)


@pytest.fixture
def user0():
    return User(email=EMAIL, phone_number=PHONE_NUM, password=PASSWORD, username=NAME)


@pytest.fixture
def persist_user(db, user0):
    user0.save()
    return user0


@pytest.mark.django_db()
class TestUser:

    def test_persist_user(self, persist_user):
        assert persist_user in User.objects.all()

    def test_delete_user(self, persist_user):
        persist_user.delete()
        assert persist_user not in User.objects.all()

    def test_new_user(self, user0):
        assert user0.email == EMAIL
        assert user0.username == NAME
        assert user0.password == PASSWORD
        assert user0.phone_number.as_e164 == PHONE_NUM
        assert user0.profile_pic == 'images/profile_pic.svg'

    def create_user(self, email, phone_number, password, username):
        return User(email=email, phone_number=phone_number, password=password, username=username)

    @pytest.mark.parametrize("email, phone_num, password, username, excpected_error", [
        (EMAIL, "05111111111", PASSWORD, NAME, MISSING_REGION),
        (EMAIL, "++97255347", PASSWORD, NAME, NOT_VALID_PHONE),
        (EMAIL, "+978509154161", PASSWORD, NAME, NOT_INTERPRETED),
        (EMAIL, "+9725091541614", PASSWORD, NAME, NOT_VALID_PHONE),
        (EMAIL, "05hbjhbwfh", PASSWORD, NAME, NOT_PHONE_NUMBER),
        ("jnkjn;lk", PHONE_NUM, PASSWORD, NAME, EMAIL_ERROR),
        ("user@", PHONE_NUM, PASSWORD, NAME, EMAIL_ERROR),
        ("user@com", PHONE_NUM, PASSWORD, NAME, EMAIL_ERROR),
        (EMAIL, PHONE_NUM, PASSWORD, "agyT02!@9#" * 15, NAME_LENGTH_ERROR),
        (EMAIL, PHONE_NUM, PASSWORD, "16%$-7jkd@!?" * 15, NAME_LENGTH_ERROR)
        ], ids=[
            "phone is too long",
            "phone number has two ++",
            "phone number start with an unknown international extention ",
            "international phone number is too long",
            "phone number with letters",
            "junk email",
            "email without <provider>.com",
            "email with out .com",
            "username too long", "username too long with special cherecters"
        ]
    )
    def test_invalid_user_values(self, email, phone_num, password, username, excpected_error):
        with pytest.raises(Exception, match=excpected_error):
            phone_number = PhoneNumber.from_string(phone_number=phone_num)
            user = self.create_user(email, phone_number, password, username)
            user.save()

    def test_user_existence(self):
        for id in range(1, 4):
            assert User.objects.get(username=f"testUser{id}")
