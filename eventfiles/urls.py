from . import views
from django.urls import path

urlpatterns = [
    path('event_file/download/', views.download, name="download"),
    path("event_file/<str:event_id>", views.file_page_per_event, name="main"),
]
