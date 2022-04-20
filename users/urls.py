from . import views
from django.urls import path


urlpatterns = [
    path("main/", views.main_page, name="home"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("main/<str:date>", views.main_page, name="home"),
    path("register/", views.register_page, name="register")
]
