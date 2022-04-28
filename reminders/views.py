# from django.utils import timezone
from django.http import JsonResponse
from reminders.models import Reminder  # , Notification
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def get_notification(request):

    user = request.user

    print(user)

    # user_notifications = list(
    #     Notification.objects.filter(
    #         participant_id__user_id=user,
    #         seen_time__is_null=True
    #     ).values('id', 'message', 'notification_type')
    # )
    user_notifications = list(Reminder.objects.all().values('id', 'messages', 'method'))

    return JsonResponse(user_notifications, safe=False)


@login_required(login_url="login")
def seen_notification(request, pk):
    print(Reminder.objects.get(id=pk))

    # user = request.user
    # # user_notification = Notification.objects.filter(participant_id=user, seen_time__is_null=True)
    # user_notification = Notification.objects.get(id=pk, participant_id=user, seen_time__is_null=True)
    # user_notification.seen_time = timezone.now()
    # user_notification.save()

    return JsonResponse([], safe=False)
