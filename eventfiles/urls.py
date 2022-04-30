from . import views
from django.urls import path

urlpatterns = [
    path('event_file/download/', views.download, name="download"),
    path("event_file/<str:event_id>",
         views.view_all_event_files_with_upload_and_download_option_page,
         name="event_files"),
]
