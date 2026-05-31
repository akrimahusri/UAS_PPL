import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Booking, Court


class BookingViewsTests(TestCase):
    def test_landing_page_ok(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected_from_landing(self):
        self.client.force_login(self.user)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard/user/", response.url)

    def test_authenticated_admin_redirected_from_landing(self):
        admin_user = User.objects.create_user(username="adminlanding", password="secret12345")
        admin_user.is_staff = True
        admin_user.save(update_fields=["is_staff"])

        self.client.force_login(admin_user)

        response = self.client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard/admin/", response.url)


class BookingValidationTests(TestCase):
    def setUp(self):
        self.court = Court.objects.create(
            name="Court A",
            location="Jakarta",
            price_per_hour=100000,
            open_time=datetime.time(8, 0),
            close_time=datetime.time(22, 0),
        )
        self.booking_date = timezone.localdate() + datetime.timedelta(days=1)

    def test_rejects_overlapping_booking_with_active_status(self):
        Booking.objects.create(
            court=self.court,
            full_name="Existing User",
            email="existing@example.com",
            phone="08123456789",
            date=self.booking_date,
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
            status=Booking.STATUS_CONFIRMED,
        )

        booking = Booking(
            court=self.court,
            full_name="New User",
            email="new@example.com",
            phone="08987654321",
            date=self.booking_date,
            start_time=datetime.time(10, 30),
            end_time=datetime.time(11, 30),
        )

        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_rejects_booking_outside_operating_hours(self):
        booking = Booking(
            court=self.court,
            full_name="New User",
            email="new@example.com",
            phone="08987654321",
            date=self.booking_date,
            start_time=datetime.time(7, 30),
            end_time=datetime.time(9, 0),
        )

        with self.assertRaises(ValidationError):
            booking.full_clean()


class BookingAuthenticationTests(TestCase):
    def setUp(self):
        self.court = Court.objects.create(
            name="Court A",
            location="Jakarta",
            price_per_hour=100000,
        )
        self.user = User.objects.create_user(username="member1", password="secret12345")

    def test_booking_is_attached_to_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/booking/",
            {
                "court": self.court.id,
                "full_name": "Member One",
                "email": "member@example.com",
                "phone": "08123456789",
                "date": (timezone.localdate() + datetime.timedelta(days=1)).isoformat(),
                "start_time": "10:00",
                "end_time": "11:00",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard/user/", response.url)
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)

    def test_admin_cannot_access_booking_form(self):
        admin_user = User.objects.create_user(username="staff2", password="secret12345")
        admin_user.is_staff = True
        admin_user.save(update_fields=["is_staff"])

        self.client.force_login(admin_user)
        response = self.client.get("/booking/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard/admin/", response.url)

    def test_admin_cannot_access_my_bookings(self):
        admin_user = User.objects.create_user(username="staff3", password="secret12345")
        admin_user.is_staff = True
        admin_user.save(update_fields=["is_staff"])

        self.client.force_login(admin_user)
        response = self.client.get("/my-bookings/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard/admin/", response.url)

    def test_admin_can_update_booking_status(self):
        admin_user = User.objects.create_user(username="staff4", password="secret12345")
        admin_user.is_staff = True
        admin_user.save(update_fields=["is_staff"])
        booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            full_name="Member One",
            email="member@example.com",
            phone="08123456789",
            date=timezone.localdate() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
            status=Booking.STATUS_PENDING,
        )

        self.client.force_login(admin_user)
        response = self.client.post(
            f"/dashboard/admin/bookings/{booking.id}/",
            {"status": Booking.STATUS_CONFIRMED},
        )

        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CONFIRMED)

    def test_register_creates_user_without_role_field(self):
        response = self.client.post(
            "/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_register_redirects_to_user_dashboard(self):
        response = self.client.post(
            "/register/",
            {
                "username": "dashboarduser",
                "email": "dashboarduser@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard/user/", response.url)

    def test_login_rejects_admin_role_for_non_staff_user(self):
        response = self.client.post(
            "/login/",
            {
                "username": self.user.username,
                "password": "secret12345",
                "role": "admin",
                "remember_me": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Akun ini tidak memiliki akses admin.")

    def test_login_failure_shows_message(self):
        response = self.client.post(
            "/login/",
            {
                "username": self.user.username,
                "password": "wrong-password",
                "role": "user",
                "remember_me": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login gagal. Cek username, password, dan role yang dipilih.")

    def test_login_redirects_user_to_user_dashboard(self):
        response = self.client.post(
            "/login/",
            {
                "username": self.user.username,
                "password": "secret12345",
                "role": "user",
                "remember_me": True,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/dashboard/user/", target_status_code=200)
        self.assertContains(response, "Login berhasil. Selamat datang kembali di MyCourt.")

    def test_login_redirects_staff_to_admin_dashboard(self):
        admin_user = User.objects.create_user(username="staff1", password="secret12345")
        admin_user.is_staff = True
        admin_user.save(update_fields=["is_staff"])

        response = self.client.post(
            "/login/",
            {
                "username": admin_user.username,
                "password": "secret12345",
                "role": "admin",
                "remember_me": True,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/dashboard/admin/", target_status_code=200)
        self.assertContains(response, "Login berhasil. Selamat datang kembali di MyCourt.")

    def test_logout_redirects_to_landing(self):
        self.client.force_login(self.user)

        response = self.client.get("/logout/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_anonymous_user_is_redirected_from_booking_form(self):
        response = self.client.get("/booking/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_my_bookings_shows_only_current_user_bookings(self):
        other_user = User.objects.create_user(username="member2", password="secret12345")
        Booking.objects.create(
            user=self.user,
            court=self.court,
            full_name="Member One",
            email="member@example.com",
            phone="08123456789",
            date=timezone.localdate() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
        )
        Booking.objects.create(
            user=other_user,
            court=self.court,
            full_name="Member Two",
            email="other@example.com",
            phone="08987654321",
            date=timezone.localdate() + datetime.timedelta(days=2),
            start_time=datetime.time(12, 0),
            end_time=datetime.time(13, 0),
        )

        self.client.force_login(self.user)
        response = self.client.get("/my-bookings/")

        self.assertContains(response, "Member One")
        self.assertNotContains(response, "Member Two")

    def test_can_cancel_own_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            court=self.court,
            full_name="Member One",
            email="member@example.com",
            phone="08123456789",
            date=timezone.localdate() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
            status=Booking.STATUS_CONFIRMED,
        )

        self.client.force_login(self.user)
        response = self.client.post(f"/booking/{booking.id}/cancel/")

        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CANCELLED)

    def test_cannot_cancel_other_users_booking(self):
        other_user = User.objects.create_user(username="member2", password="secret12345")
        booking = Booking.objects.create(
            user=other_user,
            court=self.court,
            full_name="Member Two",
            email="other@example.com",
            phone="08987654321",
            date=timezone.localdate() + datetime.timedelta(days=1),
            start_time=datetime.time(12, 0),
            end_time=datetime.time(13, 0),
            status=Booking.STATUS_CONFIRMED,
        )

        self.client.force_login(self.user)
        response = self.client.post(f"/booking/{booking.id}/cancel/")

        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.STATUS_CONFIRMED)
