from datetime import datetime
from calendar import Calendar
from users.models import User
from django.contrib import messages
from django.http import JsonResponse
from main.utilities import time_format
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from events.models import Event, OptionalMeetingDates
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
        if user:
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
            return redirect('home')

    return render(request, "update_profile/update_form.html", {'form': form})


@login_required(login_url="login")
def get_day_events(request, day, month, year):
    def convert_events(event_list):
        events = list()
        for event in event_list:
            events.append(
                {'id': event.id,
                 'title': event.title,
                 'date_time_start': event.date_time_start,
                 'date_time_end': event.date_time_end,
                 'color': event.color,
                 'description': event.description}
            )
        return events

    def check_date(start_date, end_date):
        return start_date <= datetime(year, month, day).date() <= end_date

    def check_event(event):
        return check_date(event.date_time_start.date(), event.date_time_end.date())

    def check_optional_meeting(meeting):
        return check_date(meeting["date_time_start"].date(), meeting["date_time_end"].date())

    day, month, year = int(day), int(month), int(year)
    result = {"events": list(), "meetings": list(), "optional_dates": list()}
    result["events"] = list(
        Event.objects.get_all_user_day_events(
            request.user, datetime(year, month, day)
        ).values('id', 'title', 'date_time_start', 'date_time_end', 'color', 'description')
    )

    result["events"] = fix_events(
        list(
            Event.objects.get_all_user_day_events(
                request.user, datetime(year, month, day)
            ).values('id', 'title', 'date_time_start', 'date_time_end', 'color', 'description')
        )
    )

    result["meetings"] = fix_events((
        convert_events(
            list(
                filter(
                    check_event,
                    MainPageView.get_set_meetings(request.user)
                )
            )
        )
    ))

    result["optional_dates"] = fix_events((
        list(
            filter(
                check_optional_meeting,
                MainPageView.get_optional_meetings(Event.objects.get_all_user_meetings(request.user))
            )
        )
    ))

    return JsonResponse(result, safe=False)


def fix_events(events_list):

    for event in events_list:
        event["date_time_end"] = time_format(event["date_time_end"]).split(" ")[1]
        event["date_time_start"] = time_format(event["date_time_start"]).split(" ")[1]
        event["end_hour"] = event['date_time_end'].split(":")[0]
        event["start_hour"] = event['date_time_start'].split(":")[0]
        event["end_minute"] = event['date_time_end'].split(":")[1]
        event["start_minute"] = event['date_time_start'].split(":")[1]

    return events_list


class MainPageView(TemplateView):

    template_name = "user_site/home.html"

    def __init__(self, **kwargs) -> None:
        self.user = None
        self.year = None
        self.month = None
        super().__init__(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        return super(MainPageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_meetings = Event.objects.get_all_user_meetings(self.user)
        table_measurements = self.get_table_measurements(
            Event.objects.filter(eventparticipant__user_id=self.user)
        )

        if not self.year:
            self.year = datetime.now().year

        context = {
            'hours': range(0, 24),
            'current_year': self.year,
            'max_height': table_measurements[0],
            'max_margin': table_measurements[1],
            'max_padding': table_measurements[3],
            'max_margin_events': table_measurements[2],
            'current_meetings': self.get_set_meetings(self.user),
            'month_name': self.get_current_month_name(self.month),
            'next_date': self.get_dates(self.year, self.month, True),
            'calendar': self.get_calendar_days(self.year, self.month),
            'previous_date': self.get_dates(self.year, self.month, False),
            'current_events': Event.objects.get_all_user_events(self.user),
            'all_possible_dates': self.get_optional_meetings(current_meetings),
            'current_date': (datetime.now().year, datetime.now().month, datetime.now().day),
            'week_days': ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        }

        return context

    def get(self, request, month=None, year=None):
        self.user = request.user
        self.year, self.month = year, month

        if month and year:
            self.year = int(year)
            self.month = int(month)

        return super().get(request)

    @staticmethod
    def get_set_meetings(user):
        set_meetings = list()
        all_user_meetings = Event.objects.get_all_user_meetings(user)

        for meeting in all_user_meetings:
            if not OptionalMeetingDates.objects.get_all_event_dates(meeting).count():  # eq to 0
                set_meetings.append(meeting)

        return set_meetings

    @staticmethod
    def get_optional_meetings(current_meetings):
        all_possible_dates = []

        for meeting in current_meetings:
            optional_meetings = OptionalMeetingDates.objects.get_all_event_dates(meeting)
            for optional_meeting in optional_meetings:
                event_dict = {'id': optional_meeting.event_creator_id.event_id.id,
                              'title': optional_meeting.event_creator_id.event_id.title,
                              'date_time_start': optional_meeting.date_time_start,
                              'date_time_end': optional_meeting.date_time_end,
                              'color': optional_meeting.event_creator_id.event_id.color}
                all_possible_dates.append(event_dict)

        return all_possible_dates

    @staticmethod
    def get_dates(year=None, month=None, next=True):
        """ return the next or previous date.
            next: if true the next date will be returned otherwise the previous
        """

        if not year:
            year = int(datetime.now().year)

        if not month:
            month = int(datetime.now().month)

        action = 1 if next else -1

        if month + action > 12:
            year += 1
            month -= 11
        elif month + action < 1:
            year -= 1
            month += 11
        else:
            month += action

        return f"{year}/{month}"

    @staticmethod
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

    def get_table_measurements(self, events):
        """ get each tab in the table a measurement for the positioning

            maximum row height, tab_top_positioning, event_margin_top, event_maring_bottom
        """

        max_amount_of_events = self.get_max_day_events(events)  # get max events in one day

        tab_top_positioning = max_amount_of_events * 2 if max_amount_of_events > 2 else 4
        maximum_row_height = max_amount_of_events * 5 if max_amount_of_events > 2 else 13

        maximum_row_height = min(maximum_row_height, 30)
        tab_top_positioning = min(tab_top_positioning, 13)

        event_margin_top = min(tab_top_positioning, 13) - 4
        event_maring_bottom = event_margin_top + 0.5

        return (maximum_row_height, tab_top_positioning, event_margin_top, event_maring_bottom)

    @staticmethod
    def get_current_month_name(month=None):
        """ get the current month name.

            if month is given then get the name of that month
            otherwise get this month name
        """
        current_date = datetime.now()
        if month:
            current_date = datetime(current_date.year, month, current_date.day)
        return current_date.strftime("%B")

    @staticmethod
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
