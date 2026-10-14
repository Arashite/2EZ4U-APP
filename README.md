# 2EZ4U APP

Final Proyek dari kelas Struktur Data & Analisa Algoritma (EC234303): *engine backend* layanan antar
makanan/barang versi mini (seperti GoFood/GrabFood) dengan satu jendela Tkinter.

## Menjalankan

Python 3.11+, tanpa pustaka tambahan.
```powershell
python app.py
```

## Struktur repositori

```
README.md
app.py                 entry point ("python app.py")
data/pesanan.csv       200.000 pesanan
data/peta.csv          data lokasi (untuk M6)
backend/m1_pesanan.py  M1: Array + Linked List          (selesai)
backend/m2_antrean.py  M2: Queue + Stack (undo/redo)    (selesai)
backend/m3_laporan.py  M3: Sort + Search                (berikutnya)
backend/m4_pencarian.py M4: PetaHash + merge sort
backend/m5_katalog.py  M5: Katalog (BST) + MinHeap
backend/m6_peta.py     M6: Peta (graf) + BFS + Dijkstra
frontend/ui.py         jendela Tkinter
tests/test_m1.py       pengujian M1
tests/test_m2.py       pengujian M2
```

Tampilan: daftar menu di kiri, form parameter + hasil di kanan, panel **COMMAND** di bawah
yang mencatat perintah, modul, dan waktu backend.

## M1: Array vs Linked List

Data yang sama dimuat ke dua struktur buatan sendiri (`Array` dan `LinkedList`), keduanya
melayani lima operasi yang sama:

| Operasi | Letak | Array | Linked List |
|---|---|---|---|
| Lihat pesanan ke-i | indeks i | O(1) | O(n) |
| Tambah REGULER (3) | paling belakang | O(1) amortized | O(1) via `tail` |
| Tambah PRIORITAS (2) | tengah, indeks n // 2 | O(n) geser | O(n) telusur |
| Tambah VIP (1) | paling depan, indeks 0 | O(n) geser | O(1) via `head` |
| Hapus pesanan ke-i | indeks i | O(n) geser | O(n) telusur |

- **Array**: saat penuh, dibuat petak baru 2× lalu seluruh isi disalin, jadi `append`
  amortized O(1).
- **Linked List**: simpul tunggal dengan penunjuk `head` dan `tail`.
- Setiap operasi melaporkan biayanya (elemen digeser / simpul ditelusuri) dan waktunya.

Contoh hasil pada 200.000 baris:

| Jenis | Array | Linked List |
|---|---|---|
| REGULER | 0 elemen digeser | 0 simpul ditelusuri |
| PRIORITAS | ±100.000 elemen digeser | ±100.000 simpul ditelusuri |
| VIP | 200.000 elemen digeser | 0 simpul ditelusuri |

## Aturan implementasi

Struktur data inti dibuat manual. Tidak memakai `dict`, `set`, `sorted`, `.sort()`,
`heapq`, `bisect`, `collections.*`, literal `{}`, maupun comprehension dict/set.
`list` hanya dipakai sebagai larik primitif.

## M2: Stack & Queue

M2 memakai stack buatan sendiri di atas `Array` M1 serta dua antrean yang selalu menerima
pesanan yang sama berstatus `ANTRE`.

| Fitur | Implementasi |
|---|---|
| Kasir | `ke_postfix(ekspresi)` lalu `hitung(postfix)` dengan dua stack; visualisasi jejak langkah Tahap 1 (1.x) dan Tahap 2 (2.x) pada tabel |
| Undo / redo | Dua stack riwayat; aksi baru mengosongkan redo |
| Antrean naif | Larik biasa, dequeue indeks 0 sehingga sisa elemen bergeser O(n) |
| Antrean circular | `data`, `front`, `rear`, `count`; dequeue O(1), bertumbuh saat penuh |

### Mengapa Antrean Melingkar Memerlukan `count`?
Bila hanya menyimpan pointer `front` dan `rear`, keadaan **antrean kosong** (`count == 0`) dan keadaan **antrean penuh** (`count == kapasitas`) sama-sama menghasilkan kondisi `front == rear`. Untuk membedakan kedua kondisi tersebut tanpa ambiguitas dan tanpa menyia-nyiakan satu slot kosong memori, pencacah `count` disimpan secara eksplisit. Pengecekan kosong dilakukan dengan `count == 0` dan penuh dengan `count == kapasitas`.

Enam menu M2 tersedia di aplikasi: 
**STACK - POSTFIX (MESIN KASIR)**, **STACK - UNDO**, **STACK - REDO**, **QUEUE - ENQUEUE**, **QUEUE - DEQUEUE NAIF**, dan **QUEUE - DEQUEUE CIRCULAR**. Status menampilkan panjang dua antrean, kapasitas circular, penunjuk `front` & `rear`, total pergeseran naif, serta kedalaman undo/redo.

## Screenshot & video demo

