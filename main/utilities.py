from django.conf import settings
from django.core.mail import send_mail


def send_mail_notification(title, message, reciever_email):
    """ send an email notification with the title and message to the reciver email given """
    send_mail(title, message, settings.EMAIL_HOST_USER, [reciever_email])


def send_site_notification(message, reviever_id):
    """ notifie the reciver id the message given using the site notification """
    print(f"notification -> {message} - {reviever_id}")  # for debug only


# pre built notifications

def send_reminder_email(message, reciever_email):
    """ default reminder email message for calendar alert """
    title = "Lets Meet Calendar Alert"
    send_mail_notification(title, message, reciever_email)


def time_format(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")
