from django import forms
from users.models import User
from django.contrib.auth.forms import UserCreationForm


class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User

        fields = ("username", "email", "phone_number", "password1", "password2", "profile_pic")


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "phone_number", "profile_pic")
