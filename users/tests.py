# from django.test import TestCase
# from asyncio import FastChildWatcher
import pytest
from django.core.exceptions import ValidationError
from . import models


PHONE_NUM = "0528883333"
EMAIL = "user@gmail.com"
PASSWORD = "password"
NAME = "user"


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
    (create_user(EMAIL, "090398", PASSWORD, NAME),
     "090398 is not a valid phone number. The number should start with 05"),
    (create_user(EMAIL, "05987983", PASSWORD, NAME),
     "05987983 is not a valid phone number. The number should have 10 digits"),
    (create_user(EMAIL, "05111111111", PASSWORD, NAME),
     "05111111111 is not a valid phone number. The number should have 10 digits"),
    (create_user(EMAIL, "++97255347", PASSWORD, NAME),
     "++97255347 is not supported"),
    (create_user(EMAIL, "+978509154161", PASSWORD, NAME),
     "+978509154161 is not supported"),
    (create_user(EMAIL, "+9725091541614", PASSWORD, NAME),
     "+9725091541614 is not a valid phone number. The number should have 13 digits"),
    (create_user(EMAIL, "05hbjhbwfh", PASSWORD, NAME), "05hbjhbwfh has at least one character"),
    (create_user("jnkjn;lk", PHONE_NUM, PASSWORD, NAME), "Email is not valid"),
    (create_user("user@", PHONE_NUM, PASSWORD, NAME), "Email is not valid"),
    (create_user("user@com", PHONE_NUM, PASSWORD, NAME), "Email is not valid")
])
def test_invalid_phone_number(users, excpected_error):
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
