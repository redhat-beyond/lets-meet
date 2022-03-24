import pytest
from django.core.exceptions import ValidationError

from . import models


PHONE_NUM = "0528883333"
EMAIL = "user@gmail.com"
PASSWORD = "AdminU$er123"
NAME = "user"

VALID_PREFIX_ERROR = "{} is not a valid phone number. The number should start with 05"
NOT_VALID_PREFIX_ENDING_ERROR = "{} is not a valid phone number. " + \
                                "The number should start with 05 and a number that is not 7"
NOT_SUPPORTED_ERROR = "{} is not supported"
PHONE_NUMBER_LENGTH = "{} is not a valid phone number. The number should have {} digits"
CHERECTERS_ERROR = "{} has at least one character"
EMAIL_ERROR = "Email is not valid"


@pytest.fixture
def user0():
    return models.User(email=EMAIL, phone_number=PHONE_NUM, password=PASSWORD, name=NAME)


def test_new_user(user0):
    assert user0.email == EMAIL
    assert user0.phone_number == PHONE_NUM
    assert user0.name == NAME
    assert user0.profile_pic == 'profile_pic.svg'
    assert user0.password == PASSWORD


def create_user(email, phone_number, password, name):
    return models.User(email=email, phone_number=phone_number, password=password, name=name)


@pytest.mark.parametrize("users, excpected_error", [
    (create_user(EMAIL, "090398", PASSWORD, NAME), VALID_PREFIX_ERROR.format("090398")),
    (create_user(EMAIL, "05987983", PASSWORD, NAME), PHONE_NUMBER_LENGTH.format("05987983", "10")),
    (create_user(EMAIL, "0574601223", PASSWORD, NAME), NOT_VALID_PREFIX_ENDING_ERROR.format("0574601223")),
    (create_user(EMAIL, "05111111111", PASSWORD, NAME), PHONE_NUMBER_LENGTH.format("05111111111", "10")),
    (create_user(EMAIL, "++97255347", PASSWORD, NAME), NOT_SUPPORTED_ERROR.format("++97255347")),
    (create_user(EMAIL, "+978509154161", PASSWORD, NAME), NOT_SUPPORTED_ERROR.format("+978509154161")),
    (create_user(EMAIL, "+9725091541614", PASSWORD, NAME), PHONE_NUMBER_LENGTH.format("+9725091541614", "13")),
    (create_user(EMAIL, "05hbjhbwfh", PASSWORD, NAME), CHERECTERS_ERROR.format("05hbjhbwfh")),
    (create_user("jnkjn;lk", PHONE_NUM, PASSWORD, NAME), EMAIL_ERROR),
    (create_user("user@", PHONE_NUM, PASSWORD, NAME), EMAIL_ERROR),
    (create_user("user@com", PHONE_NUM, PASSWORD, NAME), EMAIL_ERROR)
])
def test_invalidation(users, excpected_error):
    try:
        users.save()
    except ValidationError as error:
        assert excpected_error in error  # The user was not! created successfully
    else:
        assert False  # The user was created successfully


@pytest.fixture
def persist_user(db, user0):
    user0.save()
    return user0


@pytest.mark.django_db()
def test_persist_user(persist_user):
    assert persist_user in models.User.objects.all()


@pytest.mark.django_db()
def test_delete_user(persist_user):
    persist_user.delete()
    assert persist_user not in models.User.objects.all()
