from django.db import models
from django.db.models.signals import pre_save
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
    if value is not None:
        if not value.isnumeric():
            raise ValidationError(
                _(f'{value} has at least one character'),
                params={'value': value},
            )
        if value[:2] != '05':
            raise ValidationError(
                _(f'{value} is not a valid phone number. The number should start with 05'),
                params={'value': value},
            )
        if len(value) != 10:
            raise ValidationError(
                _('%(value)s is not a valid phone number. The number should have 10 digits'),
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


def user_fields_validation(sender, instance, **kwargs):
    validate_email_addr(instance.email)
    validate_phone_number(instance.phone_number)


pre_save.connect(user_fields_validation, sender=User)
