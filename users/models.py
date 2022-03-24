from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


def validate_email_addr(value):
    try:
        validate_email(value)
    except ValidationError:
        raise ValidationError('Email is not valid')


def validate_phone_number(value):
    if not value.isnumeric() or value[:2] != '05':
        raise ValidationError(
            _('%(value)s is not a valid phone number'),
            params={'value': value},
            )


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, validators=[validate_email_addr])
    name = models.CharField(max_length=50, blank=True, default="User")
    phone_number = models.CharField(max_length=10, unique=True, blank=True, null=True,
                                    validators=[validate_phone_number])
    profile_pic = models.ImageField(default='profile_pic.svg', upload_to='profiles/')

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
