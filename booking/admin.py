from django.contrib import admin

from .models import Booking, Court


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "price_per_hour", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "location")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("full_name", "court", "date", "start_time", "end_time", "status")
    list_filter = ("status", "date", "court")
    search_fields = ("full_name", "email", "phone")
