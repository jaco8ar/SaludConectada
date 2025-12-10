from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import home, register_patient, CustomLoginView, logout_view

app_name = "accounts"

urlpatterns = [
    path("", home, name="home"),
    path("registro/", register_patient, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
]
