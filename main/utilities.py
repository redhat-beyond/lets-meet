from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from reminders.models import Notification


def send_mail_notification(title, message, receiver_email):
    """ send an email notification with the title and message to the receiver email given """
    send_mail(title, message, settings.EMAIL_HOST_USER, [receiver_email])


def create_notification(message, receiver_id):
    """ create a notification with the receiver id the message given using the site notification """
    Notification(participant_id=receiver_id, sent_time=timezone.now(),  message=message).save()


# pre built notifications

def send_reminder_email(message, receiver_id):
    """ default reminder email message for calendar alert """
    title = "Lets Meet Calendar Alert"
    receiver_email = receiver_id.user_id.email
    send_mail_notification(title, message, receiver_email)


def time_format(date_time):
    return timezone.localtime(date_time).strftime("%Y-%m-%d %H:%M:%S")


def convert_time_delta(time_delta, starting_text="You have a meeting in "):
    """ convert time delta to a message of how much time is left """

    days = time_delta.days
    seconds = time_delta.seconds
    converted_result = starting_text

    result = {"years": 0, "months": 0, "weeks": 0, "days": 0,
              "hours": 0, "minuts": 0, "seconds": 0}

    days = check_and_get_time(days, result, "years", 365)
    days = check_and_get_time(days, result, "months", 30)
    days = check_and_get_time(days, result, "weeks",  7)
    result["days"] = days

    seconds = check_and_get_time(seconds, result, "hours", 60 * 60)
    seconds = check_and_get_time(seconds, result, "minuts", 60)
    result["seconds"] = seconds

    for field_name in result:
        if result[field_name] == 0:
            continue

        converted_result += f"{field_name}: {result[field_name]} "

    return converted_result


def check_and_get_time(time, result, field, time_delta):
    """ return the amount of times that the 'time_delta' can fit inside 'time'

        variables: time - the total amount to check
                   result - a dictionary with at least the field as a key
                   field - a key to the dictionary result
                   time_delta - the amount to check on time """

    if time > time_delta:
        result[field] = 0
        while time > time_delta:
            result[field] += 1
            time -= time_delta

    return time
