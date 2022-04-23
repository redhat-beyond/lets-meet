from . import views
from django.urls import path, re_path

urlpatterns = [
    re_path(r'^event_file/download/$', views.download, name="download"),
    path('events/', views.events, name='events'),
    path("event_file/<str:event_id>", views.file_page_per_event, name="main"),
]
