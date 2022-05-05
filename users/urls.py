from . import views
from django.urls import path


urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register_page, name="register"),
    path("main/", views.MainPageView.as_view(), name="home"),
    path("update-profile/", views.update_user, name="update-user"),
    path("main/<str:date>", views.MainPageView.as_view(), name="home"),
    path("get_day_events/<str:day>/<str:month>/<str:year>", views.get_day_events, name="get_day_events")
]
