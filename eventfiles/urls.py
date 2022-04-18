from . import views
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


urlpatterns = [
    re_path(r'^event_file/download/$', views.download, name="download"),
    path('events/', views.events, name='events'),
    path("event_file/<event_id>", views.file_page_per_event, name="main"),
]
