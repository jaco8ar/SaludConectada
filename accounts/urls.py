from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import home, register_patient, CustomLoginView

app_name = "accounts"

urlpatterns = [
    path("", home, name="home"),
    path("registro/", register_patient, name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="accounts:home"), name="logout"),
]
