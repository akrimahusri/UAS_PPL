from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from .models import Booking, Court


def landing(request):
    context = {
        "court_count": Court.objects.filter(is_active=True).count(),
        "booking_count": Booking.objects.count(),
    }
    return render(request, "booking/landing.html", context)


def about(request):
    return render(request, "booking/about.html")


def court_list(request):
    courts = Court.objects.filter(is_active=True).order_by("name")
    return render(request, "booking/courts.html", {"courts": courts})


def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            return redirect("booking:success", booking_id=booking.id)
    else:
        form = BookingForm()
    return render(request, "booking/booking_form.html", {"form": form})


def booking_success(request, booking_id: int):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, "booking/booking_success.html", {"booking": booking})
