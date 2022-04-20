from . import views
from django.urls import path


urlpatterns = [
    path("create/", views.create_event, name="create_event"),
]
