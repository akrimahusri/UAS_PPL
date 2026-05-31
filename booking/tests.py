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
        booking = Booking.objects.get()
        self.assertEqual(booking.user, self.user)

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
