from django.conf import settings
from django.core.mail import send_mail


def mail(message, reciever_email):
    title = "title"
    reciever_email = "tamirsr@mta.ac.il"
    send_mail(title, message, settings.EMAIL_HOST_USER, [reciever_email])


def notifie(message, reviever_id):
    # title,
    print(f"notification -> {message} - {reviever_id}")


# TODO: pre built notifications


def time_format(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")
