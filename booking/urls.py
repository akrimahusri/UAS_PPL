from django.urls import path

from . import views

app_name = "booking"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about, name="about"),
    path("courts/", views.court_list, name="courts"),
    path("register/", views.register, name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/user/", views.user_dashboard, name="user_dashboard"),
    path("dashboard/profile/", views.profile, name="profile"),
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/admin/courts/", views.admin_courts, name="admin_courts"),
    path("dashboard/admin/courts/create/", views.admin_create_court, name="admin_create_court"),
    path("dashboard/admin/courts/<int:court_id>/edit/", views.admin_edit_court, name="admin_edit_court"),
    path("dashboard/admin/courts/<int:court_id>/toggle/", views.admin_toggle_court, name="admin_toggle_court"),
    path("dashboard/admin/users/", views.admin_users, name="admin_users"),
    path("dashboard/admin/users/<int:user_id>/toggle_active/", views.admin_toggle_user, name="admin_toggle_user"),
    path("dashboard/admin/users/<int:user_id>/toggle_staff/", views.admin_toggle_staff, name="admin_toggle_staff"),
    path("dashboard/admin/users/<int:user_id>/delete/", views.admin_delete_user, name="admin_delete_user"),
    path("dashboard/admin/bookings/", views.admin_bookings, name="admin_bookings"),
    path("dashboard/admin/bookings/<int:booking_id>/", views.admin_update_booking_status, name="admin_update_booking_status"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("booking/", views.booking_create, name="create"),
    path("booking/success/<int:booking_id>/", views.booking_success, name="success"),
]
