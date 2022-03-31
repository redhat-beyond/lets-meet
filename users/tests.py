import pytest
from random import randint as rand
from phonenumber_field.phonenumber import PhoneNumber

from . import models


NAME = "user"
EMAIL = "user@gmail.com"
PASSWORD = "AdminU$er123"
PHONE_NUM = "+972544651892"

MISSING_REGION = "Missing or invalid default region."
NOT_VALID_PHONE = "The phone number entered is not valid."
NOT_INTERPRETED = "Could not interpret numbers after plus-sign."
NOT_PHONE_NUMBER = "The string supplied did not seem to be a phone number."
NAME_LENGTH_ERROR = "Ensure this value has at most 30 characters."
EMAIL_ERROR = "Email is not valid"


@pytest.fixture
def user0():
    return models.User(email=EMAIL, phone_number=PHONE_NUM, password=PASSWORD, name=NAME)


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


def test_new_user(user0):
    assert user0.email == EMAIL
    assert user0.phone_number.as_e164 == PHONE_NUM
    assert user0.name == NAME
    assert user0.profile_pic == 'profile_pic.svg'
    assert user0.password == PASSWORD


def create_user(email, phone_number, password, name):
    return models.User(email=email, phone_number=phone_number, password=password, name=name)


def get_long_string(length=31, lower=True, upper=True, special=True, digits=True):
    from random import choice
    from string import ascii_lowercase, ascii_uppercase, digits

    special_cherectes = "!@#$%^&*()_+-=[]|"

    dictionary = ""

    if lower:
        dictionary += ascii_lowercase
    if upper:
        dictionary += ascii_uppercase
    if special:
        dictionary += special_cherectes
    if digits:
        dictionary += digits

    return "".join([choice(dictionary) for _ in range(length)])


@pytest.mark.django_db()
@pytest.mark.parametrize("email, phone_num, password, name, excpected_error", [
    (EMAIL, "0544601142", PASSWORD, NAME, MISSING_REGION),
    (EMAIL, "05987983", PASSWORD, NAME, MISSING_REGION),
    (EMAIL, "0574601223", PASSWORD, NAME, MISSING_REGION),
    (EMAIL, "05111111111", PASSWORD, NAME, MISSING_REGION),
    (EMAIL, "++97255347", PASSWORD, NAME, NOT_VALID_PHONE),
    (EMAIL, "+978509154161", PASSWORD, NAME, NOT_INTERPRETED),
    (EMAIL, "+9725091541614", PASSWORD, NAME, NOT_VALID_PHONE),
    (EMAIL, "05hbjhbwfh", PASSWORD, NAME, NOT_PHONE_NUMBER),
    ("jnkjn;lk", PHONE_NUM, PASSWORD, NAME, EMAIL_ERROR),
    ("user@", PHONE_NUM, PASSWORD, NAME, EMAIL_ERROR),
    ("user@com", PHONE_NUM, PASSWORD, NAME, EMAIL_ERROR),
    (EMAIL, PHONE_NUM, PASSWORD, get_long_string(length=rand(31, 100)), NAME_LENGTH_ERROR),
    (EMAIL, PHONE_NUM, PASSWORD, get_long_string(length=rand(31, 100)), NAME_LENGTH_ERROR),
    (EMAIL, PHONE_NUM, PASSWORD, get_long_string(length=rand(31, 100)), NAME_LENGTH_ERROR)
])
def test_invalid_user_values(email, phone_num, password, name, excpected_error):
    with pytest.raises(Exception, match=excpected_error):
        phone_number = PhoneNumber.from_string(phone_number=phone_num)
        user = create_user(email, phone_number, password, name)
        user.save()


@pytest.mark.django_db
def test_user_existence():
    assert models.User.objects.get(name="testUser1")
    assert models.User.objects.get(name="testUser2")
    assert models.User.objects.get(name="testUser3")
