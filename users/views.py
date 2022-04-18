from datetime import datetime
from calendar import Calendar
from users.models import User
from django.contrib import messages
from users.forms import MyUserCreationForm
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

cal = Calendar(6)  # 6 => means that the week start with Sunday


def login_page(request):
    """ return the login-register page with the login tab opened.

        the user will have to login with his email and password,
        an error message will show up if the user doesn't exists.
    """

    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
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
    return render(request, "login/register_login.html", {'form': form, 'page': 'login'})


def register_page(request):
    """ return the login-register page with the register tab opened.

        the user will have to input: username, email, password, confremation password,
        and optionaly a photo for there profile and a phone number.
    """

    if request.method == "POST":
        form = MyUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            return redirect("home")
        else:
            for errorKey in form.errors.keys():
                value = form.errors[errorKey].get_context()["errors"][0]
                if errorKey == "__all__":
                    messages.error(request, f"{value}")
                else:
                    messages.error(request, f"{errorKey}: {value}")
    form = MyUserCreationForm()
    return render(request, "login/register_login.html", {'form': form, 'page': 'register'})


@login_required(login_url="login")
def user_logout(request):
    """ user logout """

    logout(request)
    return redirect('login')


@login_required(login_url="login")
def main_page(request):
    calandar = get_calandar_days()
    current_month = get_current_month_name()
    current_date = (datetime.now().month, datetime.now().day)
    week_days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return render(
        request, "user_site/home.html",
        {'week_days': week_days, 'calandar': calandar, 'month_name': current_month, 'current_date': current_date}
    )


def get_current_month_name(month=None):
    """ get the current month name.

        if month is given then get the name of that month
        otherwise get this month name
    """
    current_date = datetime.now()
    if month is not None:
        current_date = datetime(current_date.year, month, current_date.day)
    return current_date.strftime("%B")


def get_calandar_days(year=None, month=None):
    """ return a matrix of dates. Each sublist is a week in the month, each week has 7 dates.
        This list will include dates from the month before if the current month hasn't started with sunday """

    current_week = list()
    calendar = cal
    calandar_dates = list()
    current_date = datetime.now()
    if not year:
        year = current_date.year
    if not month:
        month = current_date.month
    # iterate over the list of all the current month dates.
    # divide the list to each week and return the resulting matrix
    for index, date_index in enumerate(calendar.itermonthdays3(year, month)):
        current_week.append(date_index)
        if (index + 1) != 1 and (index + 1) % 7 == 0:
            calandar_dates.append(current_week)
            current_week = list()
    calandar_dates.append(current_week)
    return calandar_dates
