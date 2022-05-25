from . import views
from django.urls import path


urlpatterns = [
    path("create/", views.create_event, name="create_event"),
    path('update/<str:event_id>', views.update_event, name='update_event'),
    path("meeting/", views.CreateMeetingView.as_view(), name="create_meeting"),
    path("show_meeting/<str:meeting_id>", views.show_meeting, name='show_meeting'),
    path("add_participants/<str:meeting_id>", views.add_participants, name='add_participants'),
    path("update_meeting/<str:meeting_id>", views.CreateMeetingView.as_view(), name='update_meeting'),
    path("delete_participant/<str:participant_id>", views.delete_participant, name="delete_participant"),
    path("get_participants/<str:meeting_id>", views.get_meeting_participants, name="get_meeting_participants"),
    path("meeting/<str:day>/<str:month>/<str:year>/", views.CreateMeetingView.as_view(), name="create_meeting"),
    path('delete_event/<str:event_id>', views.delete_event, name='delete_event'),
    path("create/<str:day>/<str:month>/<str:year>/", views.create_event, name="create_event"),
]
