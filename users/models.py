from django.db import models
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password


def validate_email_addr(email):
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError('Email is not valid')


def validate_phone_number(phone_number):
    def get_phone_number():
        return "+972" + phone_number[1:] if is_international else phone_number

    is_international = False

    if phone_number is not None:
        if phone_number[0] == '+':
            is_international = True
            if phone_number[:4] != '+972':
                raise ValidationError(
                    _(f'{phone_number} is not supported'),
                    params={'phone_number': phone_number},
                )
            phone_number = "0" + phone_number[4:]

        if phone_number[:2] != '05':
            raise ValidationError(
                _(f'{get_phone_number()} is not a valid phone number. The number should start with 05'),
                params={'phone_number': get_phone_number()},
            )

        if phone_number[2] == '7':
            raise ValidationError(
                _(f'{get_phone_number()} is not a valid phone number. ' +
                  'The number should start with 05 and a number that is not 7'),
                params={'phone_number': get_phone_number()},
            )

        if len(phone_number) != 10:
            digit_amount = 13 if is_international else 10

            raise ValidationError(
                _(f'{get_phone_number()} is not a valid phone number. The number should have {digit_amount} digits'),
                params={'phone_number': get_phone_number()},
            )

        if not phone_number.isnumeric():
            raise ValidationError(
                _(f'{get_phone_number()} has at least one character'),
                params={'phone_number': get_phone_number()},
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


    validate_password(instance.password)
    validate_email_addr(instance.email)
    validate_phone_number(instance.phone_number)


pre_save.connect(user_fields_validation, sender=User)
