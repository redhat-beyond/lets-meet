from django.utils import timezone
from django.http import JsonResponse
from reminders.models import Notification
from django.contrib.auth.decorators import login_required


@login_required(login_url="login")
def get_notification(request):
    user = request.user

    user_notifications = list(
        Notification.objects.filter(
            participant_id__user_id=user,
            seen_time__isnull=True
        ).values('id', 'message', 'notification_type')
    )

    return JsonResponse(user_notifications, safe=False)


@login_required(login_url="login")
def seen_notification(request, notification_id):

    user = request.user
    user_notification = Notification.objects.get(id=notification_id, participant_id=user, seen_time__isnull=True)
    user_notification.seen_time = timezone.now()
    user_notification.save()

    return JsonResponse([], safe=False)
