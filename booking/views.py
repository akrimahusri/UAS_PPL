from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from .models import Booking, Court


def landing(request):
    context = {
        "court_count": Court.objects.filter(is_active=True).count(),
        "booking_count": Booking.objects.count(),
        "courts": Court.objects.filter(is_active=True).order_by("name")[:3],
    }
    return render(request, "booking/landing.html", context)


def about(request):
    return render(request, "booking/about.html")


def court_list(request):
    courts = Court.objects.filter(is_active=True).order_by("name")
    return render(request, "booking/courts.html", {"courts": courts})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("booking:landing")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def booking_create(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return redirect("booking:success", booking_id=booking.id)
    else:
        form = BookingForm()
    return render(request, "booking/booking_form.html", {"form": form})


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("court").order_by("-created_at")
    return render(request, "booking/my_bookings.html", {"bookings": bookings})


def booking_success(request, booking_id: int):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, "booking/booking_success.html", {"booking": booking})
