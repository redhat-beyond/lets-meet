from . import views
from django.urls import path


urlpatterns = [
    path("get-notification/", views.get_notification, name="get_notification"),
    path("seen-notification/<str:pk>", views.seen_notification, name="seen_notification")
]
