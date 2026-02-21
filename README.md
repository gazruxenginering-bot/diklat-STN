# STN-DIKLAT Web Application

Aplikasi web untuk STN-DIKLAT.

## Menjalankan Aplikasi

Ada beberapa cara untuk menjalankan aplikasi ini, tergantung pada preferensi Anda.

### 1. Menjalankan Secara Otomatis dengan Nix (Direkomendasikan)

Cara ini akan secara otomatis menyiapkan lingkungan dan menjalankan aplikasi untuk Anda.

1.  **Install Nix:**
    Jika Anda belum menginstal Nix, ikuti petunjuk di [situs web Nix](https://nixos.org/download.html).

2.  **Jalankan Aplikasi:**
    Buka terminal di direktori proyek dan jalankan:
    ```bash
    nix-shell dev.nix
    ```
    Perintah ini akan secara otomatis mengunduh semua dependensi dan menjalankan aplikasi.

3.  **Akses aplikasi:**
    Buka browser Anda dan navigasikan ke [http://localhost:8000](http://localhost:8000). Untuk menghentikan aplikasi, tekan `Ctrl+C`.

### 2. Menjalankan dengan Docker Compose

Cara ini mengemas aplikasi dalam sebuah kontainer, memastikan konsistensi di berbagai lingkungan.

1.  **Prasyarat:**
    *   [Docker](https://docs.docker.com/get-docker/)
    *   [Docker Compose](https://docs.docker.com/compose/install/)

2.  **Build dan jalankan container:**
    ```bash
    docker-compose up -d --build
    ```

3.  **Akses aplikasi:**
    Buka browser Anda dan navigasikan ke [http://localhost:8000](http://localhost:8000).

### 3. Menjalankan Secara Manual dengan Nix

Cara ini akan menyiapkan lingkungan, tetapi Anda perlu menjalankan aplikasi secara manual.

1.  **Masuk ke Nix Shell:**
    ```bash
    nix-shell
    ```

2.  **Jalankan aplikasi:**
    Setelah Anda berada di dalam `nix-shell`, jalankan `honcho start` atau `python run.py`:
    ```bash
    honcho start
    ```

3.  **Akses aplikasi:**
    Buka browser Anda dan navigasikan ke [http://localhost:8000](http://localhost:8000).

---

**Catatan:** Menjalankan aplikasi secara langsung dengan `python run.py` tanpa menggunakan Nix atau Docker **tidak disarankan** karena kemungkinan besar akan gagal jika dependensi sistem tidak cocok.
