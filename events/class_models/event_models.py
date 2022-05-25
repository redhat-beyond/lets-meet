from django.db import models
from django.utils import timezone
from django.db.models import Q, Count
from django.core.exceptions import ValidationError


class EventQuerySet(models.QuerySet):
    def get_all_meetings(self):
        """ get all the meetings from all the users """
        return self.alias(participant_amount=Count('eventparticipant__event_id')).filter(participant_amount__gte=2)

    def get_all_events(self):
        """ get all the events from all the users """
        return self.alias(participant_amount=Count('eventparticipant__event_id')).filter(participant_amount=1)

    def get_all_user_events(self, user_id):
        """ get all the events that the user_id is part of """
        meetings_ids = self.get_all_user_meetings(user_id).values('id')
        return self.filter(eventparticipant__user_id=user_id).exclude(Q(id__in=meetings_ids))

    def get_all_user_meetings(self, user_id):
        """ get only the meetings that the user_id is a participant """
        return self.get_all_meetings().filter(eventparticipant__user_id=user_id)

    def get_all_user_month_meetings(self, user_id, year, month):
        """ get only the meetings for the user given in the month given """
        return self.__date_filter(
            self.get_all_user_meetings(user_id),
            start_year=year, start_month=month
        )

    def get_all_user_month_events(self, user_id, year, month):
        """ get only the events for the user given in the month given """
        return self.__date_filter(
            self.get_all_user_events(user_id),
            start_year=year, start_month=month
        )

    def get_all_user_day_meetings(self, user_id, date):
        """ get only the meeting for the user at the date given """
        year, month, day = date.year, date.month, date.day

        return self.__date_filter(
            self.get_all_user_meetings(user_id),
            start_year=year, start_month=month, start_day=day,
            end_year=year, end_month=month, end_day=day
        )

    def get_all_user_day_events(self, user_id, date):
        """ get only the events for the user at the date given """
        year, month, day = date.year, date.month, date.day

        return self.__date_filter(
            self.get_all_user_events(user_id),
            start_year=year, start_month=month, start_day=day,
            end_year=year, end_month=month, end_day=day
        )

    def __date_filter(self, query, start_year=None, end_year=None,
                      start_month=None, end_month=None, start_day=None, end_day=None):
        """ helper query.
            get the events in the dates between the given variables """
        result = query

        if start_year:
            result = result.filter(date_time_start__year__lte=start_year)

            if end_year:
                result = result.filter(date_time_end__year__gte=end_year)

        if start_month:
            result = result.filter(date_time_start__month__lte=start_month)

            if end_month:
                result = result.filter(date_time_end__month__gte=end_month)

        if start_day:
            result = result.filter(date_time_start__day__lte=start_day)

            if end_day:
                result = result.filter(date_time_end__day__gte=end_day)

        return result


class Colors(models.TextChoices):
    RED = "#FF0000", "Red"
    PINK = "#FFC0CB", "Pink"
    ORANGE = "#FFA500", "Orange"
    YELLOW = "#FFFF00", "Yellow"
    PURPLE = "#800080", "Purple"
    GREEN = "#008000", "Green"
    BLUE = "#0000FF", "Blue"
    BROWN = "#A52A2A", "Brown"
    WHITE = "#FFFFFF", "White"
    GRAY = "#808080", "Gray"
    BLACK = "#000000", "Black"


class Event(models.Model):
    title = models.CharField(max_length=50)
    location = models.CharField(blank=True, max_length=50)
    description = models.TextField(blank=True)
    date_time_start = models.DateTimeField()
    date_time_end = models.DateTimeField()
    color = models.CharField(
        max_length=7,
        choices=Colors.choices,
        default=Colors.BLACK,
    )

    objects = EventQuerySet.as_manager()

    def clean(self):
        if not self.title:
            raise ValidationError('Title cannot be blank')
        validate_date_time(self.date_time_start, self.date_time_end)

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} - {time_format(timezone.localtime(self.date_time_start))}"


def time_format(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


def validate_date_time(starting_date, ending_date):
    if not starting_date:
        raise ValidationError('Starting date cannot be blank')
    if not ending_date:
        raise ValidationError('Ending date cannot be blank')
    if starting_date >= ending_date:
        raise ValidationError(f'{time_format(starting_date)} must be smaller than {time_format(ending_date)}')
