from users.models import User
from django.contrib import messages
from users.forms import MyUserCreationForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


def login_page(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(f"username: {email}\npassword: {password}")

        try:
            user = User.objects.get(email=email)
        except Exception:
            messages.error(request, "user does not exist")

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            return redirect("home")

        else:
            messages.error(request, "username or password does not exists")

    form = MyUserCreationForm()

    return render(request, "login/register_login.html", {'form': form})


def reqister_page(request):

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)

            return redirect("home")

        else:
            for errorKey in form.errors.keys():
                value = str(form.errors[errorKey]).split("<li>")[1].split("</li>")[0]

                if errorKey == "__all__":
                    messages.error(request, f"{value}")
                else:
                    messages.error(request, f"{errorKey}: {value}")

    form = MyUserCreationForm()

    return render(request, "login/register_login.html", {'form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def main_page(request):
    return render(request, "user_site/home.html")
