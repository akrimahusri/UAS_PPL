from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

from .models import Booking, Court


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "court",
            "full_name",
            "email",
            "phone",
            "date",
            "start_time",
            "end_time",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        if start_time and end_time and end_time <= start_time:
            self.add_error("end_time", "Jam selesai harus lebih besar dari jam mulai.")
        return cleaned_data


class CourtForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = [
            "name",
            "location",
            "price_per_hour",
            "image",
            "description",
            "is_active",
            "open_time",
            "close_time",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "open_time": forms.TimeInput(attrs={"type": "time"}),
            "close_time": forms.TimeInput(attrs={"type": "time"}),
        }


class LoginForm(AuthenticationForm):
    ROLE_USER = "user"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ADMIN, "Admin"),
    ]

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"placeholder": "Masukkan username"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Masukkan password"}),
    )
    role = forms.ChoiceField(label="Role", choices=ROLE_CHOICES, initial=ROLE_USER)
    remember_me = forms.BooleanField(required=False, initial=True, label="Ingat saya")


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Masukkan email"}),
    )

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()

        return user
