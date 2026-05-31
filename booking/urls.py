from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "booking"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about, name="about"),
    path("courts/", views.court_list, name="courts"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("booking/", views.booking_create, name="create"),
    path("booking/success/<int:booking_id>/", views.booking_success, name="success"),
]
