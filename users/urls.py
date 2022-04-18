from . import views
from django.urls import path


urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("register/", views.register_page, name="register"),
    path("logout/", views.user_logout, name="logout"),
    path("main/", views.main_page, name="home")
]
