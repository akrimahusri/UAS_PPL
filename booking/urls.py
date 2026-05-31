from django.urls import path

from . import views

app_name = "booking"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about, name="about"),
    path("courts/", views.court_list, name="courts"),
    path("booking/", views.booking_create, name="create"),
    path("booking/success/<int:booking_id>/", views.booking_success, name="success"),
]
