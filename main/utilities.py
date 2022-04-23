from django.conf import settings
from django.core.mail import send_mail


def send_mail_notification(title, message, receiver_email):
    """ send an email notification with the title and message to the receiver email given """
    send_mail(title, message, settings.EMAIL_HOST_USER, [receiver_email])


def send_site_notification(message, receiver_id):
    """ notifiy the receiver id the message given using the site notification """
    print(f"notification -> {message} - {receiver_id}")  # for debug only


# pre built notifications

def send_reminder_email(message, receiver_email):
    """ default reminder email message for calendar alert """
    title = "Lets Meet Calendar Alert"
    send_mail_notification(title, message, receiver_email)


def time_format(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")
