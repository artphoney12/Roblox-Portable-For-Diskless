# Roblox Portable For Diskless

Roblox Portable For Diskless adalah sebuah *launcher* dan pengelola instansi Roblox yang dirancang khusus untuk lingkungan **Warnet Diskless** (Cybercafe) maupun PC Virtual. Aplikasi ini memastikan pemain selalu mendapatkan versi Roblox terbaru secara efisien tanpa harus menginstal ulang secara manual pada setiap *client*.

## 🌟 Fitur Utama

- **Bypass & Portabilitas**: Menjalankan Roblox secara portabel dari satu lokasi (Game Disk) tanpa perlu instalasi di setiap PC Klien.
- **Auto-Update Cerdas**: Launcher akan secara otomatis (*silent*) memeriksa pembaruan di GitHub Releases saat pertama kali dibuka. Jika ada versi terbaru, sistem akan mengunduh dan memperbarui dirinya sendiri di latar belakang.
- **Sistem Lisensi HWID**: Dilengkapi dengan sistem penguncian lisensi berbasis *Hardware ID* (HWID) PC Server, mencegah penyalahgunaan *launcher* di luar lingkungan yang diizinkan.
- **Pembayaran QRIS Otomatis**: Integrasi langsung dengan API Pakasir (Webhook PHP) untuk aktivasi lisensi secara *real-time*. Lisensi akan langsung diterbitkan ke server FTP saat pembayaran terkonfirmasi.
- **Penyesuaian Visual**: Tampilan antarmuka *console* yang interaktif, halaman donasi (*web payment*) yang elegan, dan fitur deteksi sukses yang dinamis.

## 🚀 Cara Kerja Auto-Update (Bagi Developer)

Launcher menggunakan fungsi internal untuk memeriksa versi terbarunya melalui [GitHub API](https://api.github.com/repos/artphoney12/Roblox-Portable-For-Diskless/releases/latest). 
Jika versi di GitHub (contoh: `270823.1000`) lebih tinggi dari versi *hardcoded* di dalam `.exe`:
1. Launcher akan mencari file berekstensi `.zip` di dalam *Release* tersebut.
2. File diunduh dan diekstrak secara otomatis ke dalam folder *temporary*.
3. Sistem akan mengganti file `RobloxPortable.exe` lama dengan yang baru.
4. Launcher lama ditutup, dan launcher baru otomatis dijalankan kembali tanpa memerlukan campur tangan pengguna.

## 🛠️ Persyaratan Sistem & Instalasi

- **OS**: Windows 10/11 (64-bit)
- Sistem dirancang khusus untuk berjalan di *PC Server Diskless* (mode *SuperClient*) agar file konfigurasi dan versi Roblox tersimpan secara permanen di Game Disk.

## 💻 Struktur Kode Utama
- `launcher.py` - Inti program (Python) yang mengurus bypass instalasi Roblox, pengecekan lisensi, dan auto-update.
- `webhook.php` - Skrip *backend* untuk menerima *callback* dari gerbang pembayaran (Pakasir) dan mem-validasi transaksi.
- `web_donation.html` & `success.html` - Halaman antarmuka pengguna untuk memproses pembayaran dan menampilkan status donasi.

## 📄 Lisensi
Proyek ini dilisensikan di bawah **MIT License**. Anda bebas untuk menggunakan, menyalin, memodifikasi, dan mendistribusikan perangkat lunak ini dengan menyertakan salinan lisensi asli.
