from . import views
from django.urls import path


urlpatterns = [
    path("create/", views.create_event, name="create_event"),
    path('update/<str:event_id>', views.update_event, name='update_event'),
    path("meeting/", views.CreateMeetingView.as_view(), name="create_meeting"),
    path("update_meeting/<str:meeting_id>", views.CreateMeetingView.as_view(), name='update_meeting'),
    path("show_meeting/<str:meeting_id>", views.show_meeting, name='show_meeting'),
    path("get_participants/<str:meeting_id>", views.get_meeting_participants, name="get_meeting_participants")
]
