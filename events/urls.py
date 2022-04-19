from . import views
from django.urls import path


urlpatterns = [
    path("create/", views.create_event, name="create_event"),
    path('update/<str:pk>', views.update_event, name='update_event'),
    path("create/meeting", views.create_meeting, name="create_meeting")
]
