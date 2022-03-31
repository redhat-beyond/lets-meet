from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.password_validation import validate_password


def validate_email_addr(email):
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError('Email is not valid')


class User(AbstractUser):
    email = models.EmailField(unique=True, validators=[validate_email_addr])
    username = models.CharField(max_length=30)
    phone_number = PhoneNumberField(max_length=13, unique=True, blank=True, null=True, region="IL")
    profile_pic = models.ImageField(default='profile_pic.svg', upload_to='profiles/')

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def clean(self) -> None:
        validate_email(self.email)
        validate_password(self.password)
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
