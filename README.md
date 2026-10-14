# 2EZ4U APP — Backend Engine Layanan Antar

Proyek Akhir untuk mata kuliah **Struktur Data & Analisa Algoritma (EC234303)**  
Departemen Teknik Komputer, FTEIC — Institut Teknologi Sepuluh Nopember  
Dosen Pengampu: **Ir. Arta Kusuma Hernanda, S.T., M.T.**

---

## Sekilas Tentang Proyek

Bayangkan kita sedang membangun mesin utama (*backend engine*) untuk aplikasi layanan pesan-antar makanan berskala besar, mirip seperti GoFood, GrabFood, atau ShopeeFood versi mini. Di sistem ini, terdapat **200.000 data pesanan** yang masuk dan harus dikelola dengan cepat dan andal.

Bagi pengguna, yang terlihat mungkin hanyalah tombol pesan dan estimasi waktu. Namun di balik layar, efisiensi struktur data menentukan segalanya: apakah server bisa merespons dalam hitungan milidetik, atau justru melambat ketika pesanan membludak.

Melalui proyek **2EZ4U APP**, seluruh struktur data inti kami bangun **murni dari nol (from scratch)** tanpa mengandalkan fitur instan Python. Kami menguji langsung performa teori kompleksitas ($O(1)$, $O(n)$, amortized cost) menggunakan data sungguhan, lalu menampilkan perilakunya lewat satu antarmuka desktop sederhana berbasis **Tkinter**.

---

## Cara Menjalankan

Aplikasi ini menggunakan **Python 3.11+** standar. Tidak perlu install library tambahan (*zero external dependencies*).

### 1. Menjalankan Aplikasi
Buka terminal di folder proyek, lalu ketik:
```powershell
python app.py
```
> **Tips:** Saat aplikasi pertama kali dibuka, data 200.000 pesanan akan dimuat di latar belakang (*background thread*). Antarmuka tetap responsif dan status pemuatan bisa dipantau langsung di baris bawah.

### 2. Menjalankan Unit Test
Untuk memastikan seluruh struktur data dan algoritma bekerja dengan benar:
```powershell
python -m unittest discover -s tests -v
```

---

## Struktur Repositori

Struktur folder dirancang modular agar setiap milestone berdiri sendiri dengan rapi:

```text
2ez4u/
|-- README.md              <- Catatan dan laporan proyek
|-- app.py                 <- Entry point utama ("python app.py")
|
|-- data/
|   |-- pesanan.csv        <- Dataset 200.000 data pesanan
|   |-- peta.csv           <- Dataset peta lokasi (disiapkan untuk M6)
|
|-- backend/
|   |-- m1_pesanan.py      <- M1: Array Dinamis vs Singly Linked List (selesai)
|   |-- m2_antrean.py      <- M2: Stack (Kasir & Undo/Redo) + Queue Melingkar (selesai)
|   |-- m3_laporan.py      <- M3: Insertion Sort, Merge Sort, Binary Search (tahap berikutnya)
|   |-- m4_pencarian.py    <- M4: PetaHash (Hash Table) + Merge Sort
|   |-- m5_katalog.py      <- M5: Katalog Menu (BST) + MinHeap Prioritas
|   |-- m6_peta.py         <- M6: Peta Graf, BFS, dan Dijkstra
|
|-- frontend/
|   |-- ui.py              <- Antarmuka Tkinter (3 panel: Menu, Form/Hasil, COMMAND)
|
|-- tests/
|   |-- test_m1.py         <- Pengujian unit untuk M1 (11 pengujian)
|   |-- test_m2.py         <- Pengujian unit untuk M2 (8 pengujian)
```

---

## Aturan Main: Membangun Tanpa "Jalan Pintas"

Agar esensi pembelajaran struktur data benar-benar tercapai, proyek ini mematuhi batasan ketat:
- **Tanpa fungsi dan struktur instan:** Kami tidak menggunakan `dict`, `set`, `sorted`, `.sort()`, `heapq`, `bisect`, `collections.*`, literal kamus/set `{}`, maupun comprehension dict/set.
- **Larik Primitif:** Tipe `list` bawaan Python hanya difungsikan sebagai wadah memori tetap (*primitive fixed array*) dengan inisialisasi awal `[None] * kapasitas`.
- **Objek Ramping:** Setiap kelas data menggunakan `__slots__` agar Python tidak diam-diam membuat kamus `__dict__` di balik layar.

---

## M1: Pertarungan Array Dinamis vs Linked List

### Cerita di Balik Fitur
Hari pertama layanan dibuka, hal paling mendasar yang harus diselesaikan adalah: pesanan masuk harus tersimpan dengan aman, bisa dibuka kembali detailnya, bisa ditambah, dan bisa dicabut jika batal.

Namun, di warung kami ada aturan bisnis unik berdasarkan jenis pelanggan:
1. **REGULER (Prioritas 3):** Pelanggan biasa yang antre tertib di barisan paling belakang.
2. **PRIORITAS (Prioritas 2):** Pelanggan yang membayar ekstra untuk menyerobot langsung ke tengah barisan (`indeks = n // 2`).
3. **VIP (Prioritas 1):** Pelanggan istimewa yang langsung melesat ke urutan pertama (`indeks = 0`).

Tiga letak penyisipan yang berbeda inilah yang menjadi panggung adu performa antara **Array Dinamis** dan **Singly Linked List**:

| Operasi | Lokasi di Barisan | Array Dinamis | Singly Linked List |
|---|---|---|---|
| **Lihat pesanan ke-$i$** | Indeks $i$ | **$O(1)$** — Alamat slot langsung dihitung via rumus indeks. | **$O(n)$** — Harus menelusuri simpul satu demi satu dari `head`. |
| **Tambah REGULER** | Paling belakang | **$O(1)$ amortized** — Tinggal isi slot kosong berikutnya. | **$O(1)$** — Cepat berkat penunjuk `tail`. |
| **Tambah PRIORITAS** | Tengah ($n // 2$) | **$O(n)$** — Harus menggeser separuh isi larik ke kanan. | **$O(n)$** — Harus menelusuri separuh simpul lalu menyambung pointer. |
| **Tambah VIP** | Paling depan (0) | **$O(n)$** — Seluruh elemen harus digeser satu langkah ke kanan. | **$O(1)$** — Sangat murah, cukup ganti pointer `head`. |
| **Hapus pesanan ke-$i$** | Indeks $i$ | **$O(n)$** — Sisa elemen di sebelah kanan digeser ke kiri. | **$O(n)$** — Menelusuri ke simpul sebelum target lalu memutus rantai. |

### Bukti Nyata pada 200.000 Data
Saat diuji langsung pada dataset 200.000 pesanan, perbedaan teori ini terlihat jelas di panel COMMAND:
- **REGULER:** Keduanya sama-sama kilat ($\approx 0.01 - 0.02\text{ ms}$). Array tinggal mengisi ruang cadangan, Linked List tinggal menempel di `tail`.
- **PRIORITAS:** Waktunya hampir berimbang ($\approx 2 - 3.7\text{ ms}$), tetapi alasan internalnya berbeda: Array sibuk menggeser $\pm 100.000$ elemen di memori, sementara Linked List sibuk menelusuri $\pm 100.000$ simpul sebelum menyambung pointer baru.
- **VIP:** Linked List menang mutlak ($\approx 0.00\text{ ms}$ berbanding $\approx 6.8\text{ ms}$). Array harus memindahkan seluruh 200.000 elemen, sementara Linked List hanya mengubah satu alamat referensi pada `head`.

> **Mengapa Array Tetap Cepat (*Amortized $O(1)$*)?**  
> Saat kapasitas habis, array menyiapkan petak baru berukuran **dua kali lipat ($2\times$)** dan menyalin seluruh isi lama. Meskipun penyalinan memakan biaya $O(n)$, proses ini terjadi makin jarang seiring membesarnya ukuran array, sehingga biaya rata-rata per operasi penambahan tetap konstan.

---

## M2: Stack Kasir & Antrean Dapur

Milestone kedua menangani dua denyut nadi operasional:
1. **Di Meja Kasir:** Menghitung total belanja dari struk pesanan seperti `( 3 * 12000 ) + ( 2 * 8500 ) - 5000`.
2. **Di Dapur:** Mengatur urutan antrean pengiriman secara adil (*First-In, First-Out* / FIFO), serta menyediakan tombol sakti **Undo** dan **Redo** bila kasir salah input.

### 1. Mesin Kasir: Dari Infix ke Postfix hingga Total
Komputer tidak bisa menghitung ekspresi matematika manusia (*infix*) begitu saja dari kiri ke kanan karena ada aturan kurung dan derajat operator. Solusinya adalah mengubahnya ke bentuk **postfix** menggunakan *Stack* operator:
- Angka langsung keluar ke hasil.
- Tanda kurung buka `(` didorong ke stack, dan kurung tutup `)` akan menguras isi stack hingga kurung buka pasangannya ditemukan.
- Operator perkalian dan pembagian (`*`, `/`) didahulukan daripada penjumlahan dan pengurangan (`+`, `-`).

Setelah menjadi postfix, nilainya dihitung dengan *Stack* angka.
> **Pelajaran Penting Soal Urutan Pop:**  
> Ketika operator biner dievaluasi, angka yang pertama kali keluar dari stack adalah **operand kanan**. Untuk pengurangan dan pembagian, urutannya adalah `kanan = pop()`, `kiri = pop()`, lalu dihitung `kiri - kanan`. Jika terbalik, perkalian dan penjumlahan tetap benar karena sifat komutatif, tetapi pengurangan dan pembagian akan menghasilkan nilai yang salah.

### 2. Duel Antrean: Naif vs Melingkar (Circular)
Untuk menguji teori FIFO secara jujur, pesanan berstatus `ANTRE` dimasukkan ke dua antrean sekaligus:
- **Antrean Naif (Larik Biasa):** Setiap kali satu pesanan dilayani (`dequeue`), elemen indeks 0 diambil dan seluruh sisa elemen di belakangnya digeser satu langkah ke kiri. Pada 19.852 pesanan antre, satu kali klik saja memakan biaya $\approx 19.850$ kali geser elemen di memori ($O(n)$) dengan waktu $\approx 4.88\text{ ms}$.
- **Antrean Melingkar (*Circular Queue*):** Menggunakan array berputar dengan penunjuk `front` dan `rear`. Saat melayani pesanan, elemen tidak ada yang digeser sama sekali. Cukup memajukan penunjuk `front = (front + 1) % kapasitas`. Waktunya instan $\approx 0.01\text{ ms}$ ($O(1)$).

Adanya versi naif membuat perbandingan efisiensi bukan lagi sekadar hafalan rumus di buku, melainkan fakta yang terbaca langsung di layar.

### 3. Mengapa Antrean Melingkar Memerlukan Pencacah `count`?
Dalam antrean melingkar, ketika antrean **sedang kosong** dan ketika antrean **sedang penuh**, kedua kondisi tersebut sama-sama menghasilkan posisi pointer yang identik:
$$\text{front} == \text{rear}$$

Tanpa informasi tambahan, program tidak bisa membedakan apakah antrean sedang kosong atau penuh. Kami memilih solusi paling bersih dan hemat memori, yaitu menyimpan variabel pencacah eksplisit `count`:
- Pengecekan kosong: `count == 0`
- Pengecekan penuh: `count == kapasitas`
Dengan cara ini, seluruh slot larik dapat dimanfaatkan optimal tanpa harus mengorbankan satu slot kosong sebagai tumbal penanda.

### 4. Mekanisme Undo dan Redo
- Setiap aksi (`enqueue` atau `dequeue`) dicatat ke stack `undo`.
- Membatalkan `dequeue` berarti mengembalikan pesanan yang tadi dilayani kembali ke **depan** antrean.
- Membatalkan `enqueue` berarti mencabut kembali pesanan dari **belakang** antrean.
- **Aturan Percabangan Riwayat:** Bila pengguna sudah melakukan *undo*, lalu tiba-tiba mengeksekusi aksi baru, tumpukan `redo` akan **langsung dikosongkan**. Ini penting agar riwayat aksi tidak bercabang dan data antrean tidak kacau.

---

## Antarmuka Aplikasi

Antarmuka desktop 2EZ4U APP dirancang dalam satu jendela Tkinter dengan tata letak tiga bagian:
1. **Menu di Kiri:** Mengelompokkan seluruh operasi berdasarkan milestone (M1 s.d. M6).
2. **Form & Hasil di Kanan:** Menyediakan input parameter sesuai kebutuhan menu dan menampilkan tabel hasil interaktif.
3. **Panel COMMAND di Bawah:** Berfungsi sebagai konsol terminal visual berwarna gelap yang mencatat setiap perintah yang dieksekusi, modul penanggung jawab, serta lama waktu eksekusi di backend.

---

## Hasil Pengujian Unit

Seluruh logika inti telah teruji melalui 19 pengujian unit otomatis di folder `tests/`:

```text
test_get_O1 (test_m1.TestArray) ........................................ ok
test_indeks_tidak_valid (test_m1.TestArray) ............................ ok
test_insert_dan_remove_menggeser (test_m1.TestArray) ................... ok
test_resize_berlipat_dua_dan_menyalin (test_m1.TestArray) .............. ok
test_muat_csv_dan_oid_otomatis (test_m1.TestLayanan) ................... ok
test_alias_sesuai_panduan (test_m1.TestLinkedList) ..................... ok
test_get_menelusuri (test_m1.TestLinkedList) ........................... ok
test_head_tail_terjaga (test_m1.TestLinkedList) ........................ ok
test_array (test_m1.TestTigaLetakPenyisipan) ........................... ok
test_biaya_sesuai_teori (test_m1.TestTigaLetakPenyisipan) .............. ok
test_linked_list (test_m1.TestTigaLetakPenyisipan) ..................... ok
test_circular_berputar_dan_tumbuh (test_m2.TestAntrean) ................ ok
test_kosong_dan_is_empty (test_m2.TestAntrean) ......................... ok
test_naif_menggeser_sedangkan_circular_tidak (test_m2.TestAntrean) ..... ok
test_kurung_dan_urutan_pengurangan_pembagian (test_m2.TestKasir) ....... ok
test_langkah_kasir_sesuai_transkrip_pdf (test_m2.TestKasir) ............ ok
test_postfix_dan_total_contoh_pdf (test_m2.TestKasir) .................. ok
test_alias (test_m2.TestPanduanAlias) .................................. ok
test_undo_redo_dan_cabang_baru (test_m2.TestUndoRedo) .................. ok

Ran 19 tests in 0.003s — OK
```

---

## Screenshot & Video Demo
*(Bagian ini dapat diisi dengan tangkapan layar antarmuka Tkinter dan tautan rekaman demonstrasi aplikasi).*

