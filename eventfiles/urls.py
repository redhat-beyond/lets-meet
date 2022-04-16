from . import views
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


urlpatterns = [
    path("event_files", views.file_page, name="main"),
    re_path(r'^event_file/download/$', views.download, name="download"),
    path('upload/', views.upload, name='upload'),
    path('events/', views.events, name='events'),
    path("event_file/<event>", views.file_page_per_event, name="main"),

]

# url(r'^download/(?P<path>.*)', serve, {'document_root:'
# settings.MEDIA_ROOT}) re_path(r'^download/(?P<path>.*)', serve),
