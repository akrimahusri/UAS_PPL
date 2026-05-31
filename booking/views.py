from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from .forms import BookingForm, CourtForm, LoginForm, RegistrationForm
from .models import Booking, Court


def landing(request):
    if request.user.is_authenticated:
        return redirect("booking:admin_dashboard" if is_admin_user(request.user) else "booking:user_dashboard")

    context = {
        "court_count": Court.objects.filter(is_active=True).count(),
        "booking_count": Booking.objects.count(),
        "courts": Court.objects.filter(is_active=True).order_by("name")[:3],
    }
    return render(request, "booking/landing.html", context)


def about(request):
    return redirect("booking:landing")


def is_admin_user(user):
    return user.is_staff or user.is_superuser


def redirect_admin_user(request):
    messages.warning(request, "Akun admin menggunakan dashboard pengelola.")
    return redirect("booking:admin_dashboard")


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm

    def form_invalid(self, form):
        messages.error(self.request, "Login gagal. Cek username, password, dan role yang dipilih.")
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        selected_role = form.cleaned_data.get("role")
        user = form.get_user()

        if selected_role == LoginForm.ROLE_ADMIN and not (user.is_staff or user.is_superuser):
            form.add_error(None, "Akun ini tidak memiliki akses admin.")
            return self.form_invalid(form)

        login(self.request, user)
        if form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(1209600)
        else:
            self.request.session.set_expiry(0)

        messages.success(self.request, "Login berhasil. Selamat datang kembali di MyCourt.")

        if selected_role == LoginForm.ROLE_ADMIN:
            return redirect("booking:admin_dashboard")
        return redirect("booking:user_dashboard")


def court_list(request):
    courts = Court.objects.filter(is_active=True).order_by("name")
    return render(request, "booking/courts.html", {"courts": courts})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("booking:user_dashboard")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("booking:landing")


@login_required
def user_dashboard(request):
    if is_admin_user(request.user):
        return redirect_admin_user(request)

    courts = Court.objects.filter(is_active=True).order_by("name")[:6]
    bookings = Booking.objects.filter(user=request.user).select_related("court").order_by("-created_at")[:5]
    context = {
        "courts": courts,
        "bookings": bookings,
        "booking_count": Booking.objects.filter(user=request.user).count(),
    }
    return render(request, "booking/dashboard_user.html", context)


@login_required
def admin_dashboard(request):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    context = {
        "court_count": Court.objects.count(),
        "active_court_count": Court.objects.filter(is_active=True).count(),
        "booking_count": Booking.objects.count(),
        "pending_count": Booking.objects.filter(status=Booking.STATUS_PENDING).count(),
        "recent_bookings": Booking.objects.select_related("user", "court").order_by("-created_at")[:6],
        "recent_courts": Court.objects.order_by("-created_at")[:4],
    }
    return render(request, "booking/dashboard_admin.html", context)


@login_required
def admin_courts(request):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    context = {
        "court_form": CourtForm(),
        "courts": Court.objects.order_by("-created_at"),
        "court_count": Court.objects.count(),
        "active_court_count": Court.objects.filter(is_active=True).count(),
        "inactive_court_count": Court.objects.filter(is_active=False).count(),
    }
    return render(request, "booking/admin_courts.html", context)


@login_required
def admin_create_court(request):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    if request.method == "POST":
        form = CourtForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Lapangan berhasil ditambahkan.")
        else:
            messages.error(request, "Gagal menambahkan lapangan. Cek kembali isian form.")
            return render(
                request,
                "booking/admin_courts.html",
                {
                    "court_form": form,
                    "courts": Court.objects.order_by("-created_at"),
                    "court_count": Court.objects.count(),
                    "active_court_count": Court.objects.filter(is_active=True).count(),
                    "inactive_court_count": Court.objects.filter(is_active=False).count(),
                },
            )

    return redirect("booking:admin_courts")


@login_required
def admin_edit_court(request, court_id: int):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    court = get_object_or_404(Court, pk=court_id)
    if request.method == "POST":
        form = CourtForm(request.POST, request.FILES, instance=court)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lapangan {court.name} berhasil diperbarui.")
            return redirect("booking:admin_courts")
    else:
        form = CourtForm(instance=court)

    return render(
        request,
        "booking/admin_court_form.html",
        {"court_form": form, "court": court},
    )


@login_required
def admin_toggle_court(request, court_id: int):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    court = get_object_or_404(Court, pk=court_id)
    if request.method == "POST":
        court.is_active = not court.is_active
        court.save(update_fields=["is_active"])
        messages.success(request, f"Status lapangan {court.name} berhasil diperbarui.")

    return redirect("booking:admin_courts")


@login_required
def admin_bookings(request):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    bookings = Booking.objects.select_related("user", "court").order_by("-created_at")
    context = {
        "bookings": bookings,
        "booking_count": bookings.count(),
        "pending_count": bookings.filter(status=Booking.STATUS_PENDING).count(),
        "confirmed_count": bookings.filter(status=Booking.STATUS_CONFIRMED).count(),
        "cancelled_count": bookings.filter(status=Booking.STATUS_CANCELLED).count(),
    }
    return render(request, "booking/admin_bookings.html", context)


@login_required
def admin_update_booking_status(request, booking_id: int):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    booking = get_object_or_404(Booking, pk=booking_id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        allowed_statuses = {choice for choice, _ in Booking.STATUS_CHOICES}
        if new_status in allowed_statuses and new_status != booking.status:
            booking.status = new_status
            booking.save(update_fields=["status"])
            messages.success(request, f"Status booking {booking.full_name} berhasil diperbarui.")
        elif new_status not in allowed_statuses:
            messages.error(request, "Status booking tidak valid.")

    return redirect("booking:admin_bookings")


@login_required
def admin_users(request):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    users = User.objects.order_by("username")
    context = {
        "users": users,
        "user_count": users.count(),
    }
    return render(request, "booking/admin_users.html", context)


@login_required
def admin_toggle_user(request, user_id: int):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    user_obj = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        # Prevent admin from deactivating themselves
        if user_obj == request.user:
            messages.error(request, "Tidak dapat mengubah status akun sendiri.")
        else:
            user_obj.is_active = not user_obj.is_active
            user_obj.save(update_fields=["is_active"])
            messages.success(request, f"Status akun {user_obj.username} berhasil diperbarui.")

    return redirect("booking:admin_users")


@login_required
def admin_toggle_staff(request, user_id: int):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    user_obj = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        # Prevent changing own staff status
        if user_obj == request.user:
            messages.error(request, "Tidak dapat mengubah peran akun sendiri.")
        else:
            # Protect superuser flag: do not promote/demote superusers via this action
            if user_obj.is_superuser:
                messages.error(request, "Tidak dapat mengubah peran superuser melalui halaman ini.")
            else:
                user_obj.is_staff = not user_obj.is_staff
                user_obj.save(update_fields=["is_staff"])
                messages.success(request, f"Peran admin untuk {user_obj.username} berhasil diperbarui.")

    return redirect("booking:admin_users")



@login_required
def admin_delete_user(request, user_id: int):
    if not is_admin_user(request.user):
        return redirect("booking:user_dashboard")

    user_obj = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        if user_obj == request.user:
            messages.error(request, "Tidak dapat menghapus akun sendiri.")
        elif user_obj.is_superuser:
            messages.error(request, "Tidak dapat menghapus akun superuser melalui halaman ini.")
        else:
            username = user_obj.username
            user_obj.delete()
            messages.success(request, f"Akun {username} berhasil dihapus.")

    return redirect("booking:admin_users")


@login_required
def booking_create(request):
    if is_admin_user(request.user):
        messages.warning(request, "Admin tidak dapat membuat booking. Gunakan halaman pengelola booking.")
        return redirect("booking:admin_dashboard")

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, "Booking berhasil dibuat. Kamu kembali ke dashboard.")
            return redirect("booking:user_dashboard")
    else:
        form = BookingForm()
    return render(request, "booking/booking_form.html", {"form": form})


@login_required
def my_bookings(request):
    if is_admin_user(request.user):
        return redirect_admin_user(request)

    bookings = Booking.objects.filter(user=request.user).select_related("court").order_by("-created_at")
    return render(request, "booking/my_bookings.html", {"bookings": bookings})


@login_required
def cancel_booking(request, booking_id: int):
    if is_admin_user(request.user):
        return redirect_admin_user(request)

    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.user != request.user:
        return redirect("booking:my_bookings")

    if request.method == "POST" and booking.status in [Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]:
        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=["status"])

    return redirect("booking:my_bookings")


def booking_success(request, booking_id: int):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, "booking/booking_success.html", {"booking": booking})


@login_required
def profile(request):
    if is_admin_user(request.user):
        return redirect_admin_user(request)

    bookings = Booking.objects.filter(user=request.user).select_related("court").order_by("-date", "-start_time")
    context = {
        "bookings": bookings,
        "booking_count": bookings.count(),
    }
    return render(request, "booking/profile.html", context)
