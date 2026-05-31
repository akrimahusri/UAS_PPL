# MyCourt

MyCourt adalah aplikasi booking lapangan badminton dengan halaman publik dan dashboard admin.

## Fitur

- Landing page, informasi, daftar lapangan, dan form booking.
- Dashboard admin (Django Admin) untuk CRUD data lapangan dan booking.
- Validasi dasar untuk jam dan tanggal booking.

## Instalasi

1. Masuk ke folder proyek:
   ```bash
   cd MyCourt
   ```
2. Buat virtual environment (opsional) dan install dependensi:
   ```bash
   pip install django
   ```
3. Migrasi database:
   ```bash
   python manage.py migrate
   ```
4. Buat superuser untuk login admin:
   ```bash
   python manage.py createsuperuser
   ```
5. Jalankan server:
   ```bash
   python manage.py runserver
   ```

## Akses Aplikasi

- Halaman publik: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## Catatan

- Halaman publik: `http://127.0.0.1:8000/` (landing, daftar lapangan, booking)
- Dashboard in-app untuk pengelola (admin) tersedia di `http://127.0.0.1:8000/dashboard/admin/` — gunakan menu *Kelola Lapangan* dan *Booking* untuk manajemen.
- Halaman pengelolaan akun admin baru: `http://127.0.0.1:8000/dashboard/admin/users/` (promote/demote admin, aktif/non-aktif, hapus - dengan proteksi).
- Halaman profil pengguna: `http://127.0.0.1:8000/dashboard/profile/` (lihat ringkasan akun dan booking terbaru).
- Beberapa file override admin tema telah dihapus (project/app `templates/admin/base_site.html` dan `booking/static/booking/admin-theme.css`) karena pengelolaan kini tersedia dalam aplikasi.
- Untuk mengarahkan langsung ke section "Tentang" pada landing page dari tempat lain, gunakan anchor: `"{% url 'booking:landing' %}#about"`.

## Media & Static

- Jika menambahkan gambar lapangan, simpan di `media/` dan pastikan `MEDIA_URL`/`MEDIA_ROOT` dikonfigurasi di `MyCourt/settings.py`.
- Untuk development, Django akan melayani `MEDIA_URL` ketika `DEBUG=True`.
