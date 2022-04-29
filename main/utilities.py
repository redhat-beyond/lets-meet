from django.conf import settings
from django.core.mail import send_mail


def send_mail_notification(title, message, receiver_email):
    """ send an email notification with the title and message to the receiver email given """
    send_mail(title, message, settings.EMAIL_HOST_USER, [receiver_email])


def send_site_notification(message, receiver_id):
    """ notify the receiver by his id with the message given by the site notification """
    print(f"notification -> {message} - {receiver_id}")  # for debug only


# pre built notifications

def send_reminder_email(message, receiver_email):
    """ default reminder email message for calendar alert """
    title = "Lets Meet Calendar Alert"
    send_mail_notification(title, message, receiver_email)


def time_format(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")


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
    """ get a time variable that holds amount of the time wanted to check
        result dictionary and the field name relevent to counting the time_delta in time
        and the time_delta """

    if time > time_delta:
        result[field] = 0
        while time > time_delta:
            result[field] += 1
            time -= time_delta

    return time
