import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Court(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=255)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    open_time = models.TimeField(default=datetime.time(6, 0))
    close_time = models.TimeField(default=datetime.time(23, 0))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name


class Booking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="bookings")
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "Jam selesai harus lebih besar dari jam mulai."})
        if self.date and self.date < timezone.localdate():
            raise ValidationError({"date": "Tanggal booking tidak boleh di masa lalu."})

    def __str__(self) -> str:
        return f"{self.full_name} - {self.court.name} ({self.date})"
