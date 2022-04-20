from datetime import datetime
from calendar import Calendar
from users.models import User
from events.models import Event
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from users.forms import MyUserCreationForm, UserUpdateForm
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

        the user will have to input: username, email, password, confirmation password,
        and optionally a photo for there profile and a phone number.
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
def update_user(request):
    user = request.user
    form = UserUpdateForm(instance=user)

    if request.method == "POST":
        form = UserUpdateForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            form.save()
            return redirect('update-user')

    return render(request, "update_profile/update_form.html", {'form': form})


@login_required(login_url="login")
def main_page(request, date=None):

    if not date:
        year, month = None, None
    else:
        year, month = date.split("|")
        year = int(year)
        month = int(month)

    cal = get_calendar_days(year, month)
    current_month = get_current_month_name(month)
    current_date = (datetime.now().year, datetime.now().month, datetime.now().day)
    current_events = Event.objects.filter(eventparticipant__user_id=request.user.id)
    table_measurements = get_table_measurements(current_events)
    week_days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    print(f"next: {get_dates(year, month, True)} || pre: {get_dates(year, month, False)}")

    return render(
        request, "user_site/home.html",
        {'week_days': week_days, 'calendar': cal, 'month_name': current_month,
         'next_date': get_dates(year, month, True), 'previous_date': get_dates(year, month, False),
         'max_height': table_measurements[0], 'max_margin': table_measurements[1],
         'max_margin_events': table_measurements[2], 'max_padding': table_measurements[3],
         'current_date': current_date, 'current_events': current_events}
    )


def get_dates(year=None, month=None, next=True):
    """ return the next or previous date.
        next: if true the next date will be returned otherwise the previous
    """

    if not year:
        year = int(datetime.now().year)
    if not month:
        month = int(datetime.now().month)

    if next:
        action = 1
    else:
        action = -1

    if month + action > 12:
        year += 1
        month -= 11
    elif month + action < 1:
        year -= 1
        month += 11
    else:
        month += action

    return f"{year}|{month}"


def get_max_day_events(events):
    """ return the maximum events count in one day over all the events given """

    events_count = {}
    if len(events) == 0:
        return 0

    for event in events:
        if not events_count.get(event.date_time_start.date()):
            events_count[event.date_time_start.date()] = 1
        else:
            events_count[event.date_time_start.date()] += 1

    return max(events_count.values())


def get_table_measurements(events):
    """ get each tab in the table a measurement for the positioning

        maximum row height, tab_top_positioning, event_margin_top, event_maring_bottom
    """

    max_amount_of_events = get_max_day_events(events)  # get max events in one day

    if max_amount_of_events > 2:
        tab_top_positioning = max_amount_of_events * 2
        maximum_row_height = max_amount_of_events * 5
    else:
        maximum_row_height = 13
        tab_top_positioning = 4

    maximum_row_height = min(maximum_row_height, 30)
    tab_top_positioning = min(tab_top_positioning, 13)

    event_margin_top = min(tab_top_positioning, 13) - 4
    event_maring_bottom = event_margin_top + 0.5

    return (maximum_row_height, tab_top_positioning, event_margin_top, event_maring_bottom)


def get_current_month_name(month=None):
    """ get the current month name.

        if month is given then get the name of that month
        otherwise get this month name
    """
    current_date = datetime.now()
    if month:
        current_date = datetime(current_date.year, month, current_date.day)
    return current_date.strftime("%B")


def get_calendar_days(year=None, month=None):
    """ return a matrix of dates. Each sublist is a week in the month, each week has 7 dates.
        This list will include dates from the month before if the current month hasn't started with sunday """

    current_week = list()
    calendar_dates = list()
    current_date = datetime.now()
    if not year:
        year = current_date.year
    if not month:
        month = current_date.month

    # iterate over the list of all the current month dates.
    # divide the list to each week and return the resulting matrix
    for index, date_index in enumerate(cal.itermonthdays3(year, month)):
        current_week.append(date_index)
        if (index + 1) != 1 and (index + 1) % 7 == 0:
            calendar_dates.append(current_week)
            current_week = list()
    calendar_dates.append(current_week)
    return calendar_dates
