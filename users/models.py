from django.db import models
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


def validate_email_addr(email):
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError('Email is not valid')


def validate_phone_number(phone_number):
    if phone_number is not None:
        if phone_number[0] == '+':
            if phone_number[:4] != '+972':
                raise ValidationError(
                    _(f'{phone_number} is not supported'),
                    params={'phone_number': phone_number},
                )
            if len(phone_number) != 13:
                raise ValidationError(
                    _(f'{phone_number} is not a valid phone number. The number should have 13 digits'),
                    params={'phone_number': phone_number},
                )
            phone_number = phone_number[1:]
        else:
            if phone_number[:2] != '05':
                raise ValidationError(
                    _(f'{phone_number} is not a valid phone number. The number should start with 05'),
                    params={'phone_number': phone_number},
                )
            if len(phone_number) != 10:
                raise ValidationError(
                    _(f'{phone_number} is not a valid phone number. The number should have 10 digits'),
                    params={'phone_number': phone_number},
                )
        if not phone_number.isnumeric():
            raise ValidationError(
                _(f'{phone_number} has at least one character'),
                params={'phone_number': phone_number},
            )


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, validators=[validate_email_addr])
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=13, unique=True, blank=True, null=True,
                                    validators=[validate_phone_number])
    profile_pic = models.ImageField(default='profile_pic.svg', upload_to='profiles/')

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


def user_fields_validation(sender, instance, **kwargs):
    validate_email_addr(instance.email)
    validate_phone_number(instance.phone_number)


pre_save.connect(user_fields_validation, sender=User)
