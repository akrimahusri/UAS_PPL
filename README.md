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
            
   ```

## Akses Aplikasi

- Halaman publik: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## Catatan

- Tambahkan data lapangan terlebih dulu lewat admin agar daftar lapangan tampil.
- CRUD data dilakukan melalui Django Admin.
