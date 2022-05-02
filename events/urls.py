from . import views
from django.urls import path


urlpatterns = [
    path("create/", views.create_event, name="create_event"),
    path('update/<str:pk>', views.update_event, name='update_event'),
    path("meeting/", views.CreateMeetingView.as_view(), name="create_meeting"),
]
