# 2EZ4U APP

Proyek Struktur Data & Analisa Algoritma (EC234303) berupa backend layanan antar makanan/barang versi mini.

## Cakupan proyek sampai M3

Proyek dibangun bertahap menggunakan dataset pesanan dan implementasi struktur data manual.

### M1 — Pesanan: Array dan Linked List

Modul: `backend/m1_pesanan.py`

M1 menyimpan data pesanan ke dua struktur sekaligus:

- Array dinamis dengan kapasitas yang bertambah dua kali lipat saat penuh.
- Linked list dengan node, `head`, dan `tail`.
- Operasi melihat, menambah, dan menghapus pesanan.
- Aturan prioritas: VIP (`1`) masuk paling depan; prioritas (`2`) masuk setelah VIP dan sebelum reguler; reguler (`3`) masuk paling belakang.

Tujuannya adalah membandingkan biaya operasi array dan linked list pada kasus yang sama.

### M2 — Stack, Queue, dan Undo/Redo

Modul: `backend/m2_antrean.py`

M2 mencakup:

- Stack manual dengan operasi `push`, `pop`, `peek`, dan `is_empty`.
- Konversi ekspresi infix menjadi postfix.
- Evaluasi ekspresi postfix menggunakan stack angka.
- Queue naif dengan pergeseran elemen saat `dequeue`.
- Circular queue dengan indeks `front`, `rear`, dan `count`.
- Undo dan redo untuk aksi antrean.

Queue naif dan circular queue dipertahankan bersama agar perbedaan performanya dapat diukur.

### M3 — Sort dan Search

Modul: `backend/m3_laporan.py`

M3 menyediakan empat algoritma:

- Insertion sort yang stabil dan bekerja in-place.
- Merge sort yang stabil untuk data besar.
- Linear search tanpa syarat data terurut.
- Binary search pada data yang sudah terurut.

Setiap algoritma mencatat jumlah perbandingan. Kunci data yang direncanakan adalah `oid`, `harga`, dan `t_selesai_detik`.

## Kompleksitas algoritma

| Fitur | Kompleksitas umum |
|---|---:|
| Array: akses indeks | O(1) |
| Array: sisip/hapus di tengah | O(n) |
| Linked list: akses indeks | O(n) |
| Linked list: tambah di belakang | O(1) |
| Stack push/pop | O(1) |
| Circular queue enqueue/dequeue | O(1) |
| Queue naif dequeue | O(n) |
| Insertion sort | O(n²) |
| Merge sort | O(n log n) |
| Linear search | O(n) |
| Binary search | O(log n) |

## Struktur repository

```text
2ez4u/
├── README.md
├── data/
│   ├── peta.csv
│   └── pesanan.csv
├── backend/
│   ├── m1_pesanan.py
│   ├── m2_antrean.py
│   └── m3_laporan.py
├── frontend/
│   └── ui.py
└── app.py
```

## Dataset

`data/pesanan.csv` berisi 200.000 pesanan dengan kolom:

`oid`, `pelanggan`, `resto`, `menu`, `harga`, `prioritas`, `t_masuk_detik`, `t_selesai_detik`, dan `status`.

`data/peta.csv` berisi koneksi lokasi dan waktu tempuh. Dataset ini disiapkan untuk milestone peta setelah M3.

## Aturan implementasi

Struktur data dan algoritma inti dibuat manual sesuai tugas. Tidak menggunakan `dict`, `set`, `sorted`, `.sort()`, `heapq`, `bisect`, atau `collections.*` untuk menggantikan struktur yang dinilai.

## Menjalankan aplikasi

Gunakan Python 3.11 atau lebih baru:

```powershell
python app.py
```

Implementasi penuh M1–M3 akan diisi bertahap pada modul backend masing-masing dan dihubungkan melalui `frontend/ui.py`.

## Checklist sampai M3

- [x] Struktur repository dan dataset disiapkan.
- [x] Scaffold modul M1–M3 dibuat.
- [ ] Implementasi array dan linked list.
- [ ] Implementasi stack, queue, undo, dan redo.
- [ ] Implementasi insertion sort, merge sort, linear search, dan binary search.
- [ ] Pengujian dan benchmark M1–M3.
