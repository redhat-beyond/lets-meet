# from django.test import TestCase
# from asyncio import FastChildWatcher
import pytest
from django.core.exceptions import ValidationError
from . import models


PHONE_NUM = "0528305110"
EMAIL = "yael@gmail.com"
PASSWORD = "password"


@pytest.fixture
def user0():
    return models.User(email=EMAIL, phone_number=PHONE_NUM, password=PASSWORD)


def test_new_user(user0):
    assert user0.email == EMAIL
    assert user0.phone_number == PHONE_NUM
    assert user0.name == 'User'
    assert user0.profile_pic == 'profile_pic.svg'
    assert user0.password == PASSWORD


@pytest.mark.django_db
def test_failed_creation_user1():
    try:
        user = models.User(email="ilan@gmail.com", phone_number="090398a", password=PASSWORD)
        user.full_clean()
    except ValidationError:
        assert True  # The user was not! created successfully
    else:
        assert False  # The user was created successfully


@pytest.mark.django_db
def test_failed_creation_user2():
    try:
        user = models.User(email="jnkjnf", phone_number=PHONE_NUM, password=PASSWORD)
        user.full_clean()
    except ValidationError:
        assert True  # The user was not! created successfully
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
