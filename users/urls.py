from . import views
from django.urls import path


urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("main/", views.main_page, name="home"),
    path("main/<str:date>", views.main_page, name="home"),
    path("register/", views.register_page, name="register"),
    path("update-profile/", views.update_user, name="update-user")
]
