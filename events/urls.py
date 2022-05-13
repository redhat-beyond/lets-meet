from . import views
from django.urls import path


urlpatterns = [
    path("create/", views.create_event, name="create_event"),
    path('update/<str:event_id>', views.update_event, name='update_event'),
    path("meeting/", views.CreateMeetingView.as_view(), name="create_meeting"),
    path('delete_event/<str:event_id>', views.delete_event, name='delete_event'),
    path("create/<str:day>/<str:month>/<str:year>/", views.create_event, name="create_event"),
]
